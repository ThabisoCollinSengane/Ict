"""ICT intermarket day-trading algorithm for QuantConnect / LEAN.

Pairs traded: GBPUSD, EURUSD.
Confirmation:  synthetic DXY + EURGBP relative strength.
Entry:         LTF (5m) FVG inside an HTF-aligned, killzone-gated window after a
               15m liquidity sweep.
Targets:       nearest HTF (4H) FVG / Order Block / equal-high or equal-low,
               minimum 20 pips.
Pyramiding:    up to 3 legs, each new leg requires a fresh continuation FVG and
               promotes the previous leg's stop to break-even (via order update).
News filter:   blocks entries +/-15 min around High/Medium USD/EUR/GBP events
               sourced from the ForexFactory weekly XML calendar.
"""

from AlgorithmImports import *
from datetime import timedelta

import config
from ict.killzones import can_open_new_trade
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.bias import htf_bias
from ict.dxy_synthetic import compute_dxy, compute_dxy_range
from ict.amd import detect_consolidation, detect_manipulation, detect_amd_setup
from ict.dealing_range import (
    detect_dealing_range,
    is_valid_entry_zone,
    is_valid_target_zone,
    is_nfp_week_low_probability,
    is_post_fomc_low_probability,
)
from intermarket import resolve as resolve_intermarket
from news_filter import NewsCalendar
from risk import position_size, pip_size, TradeState


class _SynBar:
    """Lightweight bar shim used to feed htf_bias() with a synthetic DXY series."""
    __slots__ = ("Open", "High", "Low", "Close")

    def __init__(self, o, h, l, c):
        self.Open, self.High, self.Low, self.Close = o, h, l, c


class ICTIntermarketAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 6, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(config.STARTING_CASH)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage, AccountType.Margin)
        self.SetTimeZone(TimeZones.Utc)

        all_syms = set(config.PAIRS) | {config.REF_EURGBP} | set(config.DXY_CONSTITUENTS)
        self.symbols: dict = {}
        self.sym_by_qc: dict = {}
        for sym in all_syms:
            qc_sym = self.AddForex(sym, Resolution.Minute, Market.Oanda).Symbol
            self.symbols[sym] = qc_sym
            self.sym_by_qc[qc_sym] = sym

        self.bars_5m  = {s: RollingWindow[QuoteBar](300) for s in all_syms}
        self.bars_15m = {s: RollingWindow[QuoteBar](300) for s in all_syms}
        self.bars_1h  = {s: RollingWindow[QuoteBar](300) for s in all_syms}
        self.bars_4h  = {s: RollingWindow[QuoteBar](300) for s in all_syms}
        self.bars_1d  = {s: RollingWindow[QuoteBar](300) for s in all_syms}
        self.bars_1w  = {s: RollingWindow[QuoteBar](200) for s in all_syms}

        for sym, qc_sym in self.symbols.items():
            self._wire_consolidator(sym, qc_sym,     5, self.bars_5m,  is_entry_tf=True)
            self._wire_consolidator(sym, qc_sym,    15, self.bars_15m, is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,    60, self.bars_1h,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,   240, self.bars_4h,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,  1440, self.bars_1d,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym, 10080, self.bars_1w,  is_entry_tf=False)

        self.news = NewsCalendar()
        self._refresh_news()
        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.At(0, 5),
            self._refresh_news,
        )

        self.active: dict = {}
        self.last_price: dict = {}
        # Reverse index: order id -> (pair, role) where role in {"entry","sl","tp"}.
        self.order_index: dict = {}

        self.SetWarmUp(timedelta(days=90))

    def _wire_consolidator(self, sym, qc_sym, minutes, store, is_entry_tf):
        cons = QuoteBarConsolidator(timedelta(minutes=minutes))

        def handler(_sender, bar, _sym=sym, _store=store, _entry=is_entry_tf):
            _store[_sym].Add(bar)
            if _entry and _sym in config.PAIRS:
                self._on_5m_close(_sym)

        cons.DataConsolidated += handler
        self.SubscriptionManager.AddConsolidator(qc_sym, cons)

    def _refresh_news(self):
        if config.NEWS_SOURCE == "csv":
            self._load_news_csv()
            return
        try:
            xml = self.Download(config.FOREXFACTORY_XML_URL)
            n = self.news.load(xml)
            self.Debug(f"News (XML) refreshed: {n} events kept")
        except Exception as exc:
            self.Debug(f"News XML refresh failed: {exc}")

    def _load_news_csv(self):
        # Only load once per session - the CSV is static historical data.
        if self.news.events:
            return
        try:
            text = self.ObjectStore.Read(config.NEWS_CSV_PATH) \
                if self.ObjectStore.ContainsKey(config.NEWS_CSV_PATH) else None
        except Exception:
            text = None
        if not text:
            # QC Cloud also exposes uploaded files via the project filesystem.
            try:
                with open(config.NEWS_CSV_PATH, "r") as f:
                    text = f.read()
            except Exception as exc:
                self.Debug(f"News CSV load failed ({config.NEWS_CSV_PATH}): {exc}")
                return
        n = self.news.load_csv(text)
        self.Debug(f"News (CSV) loaded: {n} events kept")

    def OnData(self, data: Slice):
        # OnData fires every minute. We only update last_price here; entry/pyramid
        # decisions fire from the 5m consolidator handler to avoid duplicate orders.
        for qc_sym, sym in self.sym_by_qc.items():
            if qc_sym in data and data[qc_sym] is not None:
                px = data[qc_sym].Price
                if px:
                    self.last_price[sym] = px

    def _on_5m_close(self, pair: str):
        if self.IsWarmingUp:
            return
        if pair in self.active:
            self._maybe_pyramid(pair)
        else:
            self._maybe_open(pair)

    def _maybe_open(self, pair: str):
        now = self.UtcTime
        if not can_open_new_trade(now):
            return
        if self.news.is_blocked(now):
            return

        # --- Low Probability Conditions (from case study: Low Probability Conditions) ---
        # 1. NFP week: Wednesday, Thursday, Friday are low probability.
        if is_nfp_week_low_probability(now, self.news.is_nfp_week(now)):
            return
        # 2. FOMC whipsaw day: London and AM session are low probability that day.
        if is_post_fomc_low_probability(now, self.news.fomc_whipsaw_date):
            return
        # 3. Trading against the daily trend is handled below via REQUIRE_DAILY_BIAS.

        dxy_bias = self._dxy_bias_1h()
        eurgbp_bias = self._sym_bias(config.REF_EURGBP, self.bars_1h)
        signal = resolve_intermarket(dxy_bias, eurgbp_bias)
        if signal is None or signal.pair != pair:
            return

        # Episode 12+18: Daily is the primary bias timeframe. Must agree first.
        if config.REQUIRE_DAILY_BIAS:
            if self._sym_bias(pair, self.bars_1d) != signal.direction:
                return
        if self._sym_bias(pair, self.bars_1h) != signal.direction:
            return
        # H4 is long-term context; M15 AMD provides the intraday direction.

        # --- AMD on M15: identify accumulation + manipulation in our direction ---
        bars15 = self._asc(self.bars_15m[pair])
        amd = detect_amd_setup(bars15, pair)
        if amd is None:
            return
        rng, sweep_dir = amd
        if sweep_dir != signal.direction:
            return
        # Stop sits beyond the manipulation extreme (which IS the swept range edge).
        sweep_price = rng.low if signal.direction > 0 else rng.high

        # --- Dealing Range: confirm entry is in the correct premium/discount zone ---
        # Use the HTF (1H) bars to detect the dealing range. A buy must come from
        # discount (below 50% of the DR); a sell must come from premium (above 50%).
        cur_price = self.last_price.get(pair)
        if cur_price is not None:
            bars1h = self._asc(self.bars_1h[pair])
            dr = detect_dealing_range(bars1h, lookback=100)
            if dr is not None:
                if not is_valid_entry_zone(cur_price, dr.high, dr.low, signal.direction):
                    return

        # --- M5 distribution trigger: fresh FVG in trade direction ---
        bars5 = self._asc(self.bars_5m[pair])
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != signal.direction:
            return

        target = self._find_target(pair, signal.direction)
        if target is None:
            return

        pip = pip_size(pair)
        # Enter at the near edge of the FVG (less retrace than the midpoint).
        entry = fvg.top if signal.direction > 0 else fvg.bottom
        stop = (fvg.bottom - pip) if signal.direction > 0 else (fvg.top + pip)

        risk_pips = abs(entry - stop) / pip
        reward_pips = abs(target - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return
        if risk_pips <= 0 or (reward_pips / risk_pips) < config.MIN_RR:
            return

        units_raw = position_size(self.Portfolio.TotalPortfolioValue, entry, stop, pair)
        units = int(units_raw) * signal.direction
        if units == 0:
            return

        qc_sym = self.symbols[pair]
        entry_ticket = self.LimitOrder(qc_sym, units, entry, tag=f"{pair}-L1-entry")

        st = TradeState(symbol=pair, direction=signal.direction,
                        target=target, initial_stop=stop)
        st.pending[entry_ticket.OrderId] = {
            "stop": stop, "units": abs(units), "leg_idx": 1, "entry": entry,
        }
        self.active[pair] = st
        self.order_index[entry_ticket.OrderId] = (pair, "entry")

    def _maybe_pyramid(self, pair: str):
        st = self.active[pair]
        if not st.can_add():
            return
        if self.news.is_blocked(self.UtcTime):
            return
        # Don't stack a new leg while a prior entry is still pending.
        if st.pending:
            return

        bars5 = self._asc(self.bars_5m[pair])
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != st.direction:
            return

        cur_price = self.last_price.get(pair)
        if cur_price is None:
            return
        pip = pip_size(pair)
        last_entry = st.legs[-1]["entry"]
        favour_pips = (cur_price - last_entry) * st.direction / pip
        if favour_pips < 10:
            return

        entry = fvg.mid
        stop = st.legs[-1]["entry"]   # promotes prior leg to break-even
        units_raw = position_size(self.Portfolio.TotalPortfolioValue, entry, stop, pair)
        units = int(units_raw) * st.direction
        if units == 0:
            return

        reward_pips = abs(st.target - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return

        qc_sym = self.symbols[pair]
        leg_idx = len(st.legs) + 1
        entry_ticket = self.LimitOrder(qc_sym, units, entry, tag=f"{pair}-L{leg_idx}-entry")
        st.pending[entry_ticket.OrderId] = {
            "stop": stop, "units": abs(units), "leg_idx": leg_idx, "entry": entry,
        }
        self.order_index[entry_ticket.OrderId] = (pair, "entry")

    def _sym_bias(self, sym, store) -> int:
        bars = self._asc(store[sym])
        return htf_bias(bars)

    def _dxy_bias_1h(self) -> int:
        rolls = {s: self._asc(self.bars_1h[s]) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        if n < config.SWING_LOOKBACK + 2:
            return 0
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS}
            high_px  = {s: rolls[s][i].High  for s in config.DXY_CONSTITUENTS}
            low_px   = {s: rolls[s][i].Low   for s in config.DXY_CONSTITUENTS}
            c = compute_dxy(close_px)
            o = compute_dxy({s: rolls[s][i].Open for s in config.DXY_CONSTITUENTS})
            h, l = compute_dxy_range(high_px, low_px)
            if None in (c, o, h, l):
                continue
            series.append(_SynBar(o, h, l, c))
        if len(series) < config.SWING_LOOKBACK + 2:
            return 0
        return htf_bias(series)

    def _find_target(self, pair, direction):
        stores = (self.bars_4h, self.bars_1d, self.bars_1w)
        candidates = []
        price = self.last_price.get(pair)
        if price is None:
            return None

        for store in stores:
            bars = self._asc(store[pair])
            if len(bars) < 5:
                continue
            candidates += self._targets_in_series(bars, pair, direction, price)

        if direction > 0:
            candidates = [c for c in candidates if c > price]
        else:
            candidates = [c for c in candidates if c < price]
        if not candidates:
            return None

        # Premium/Discount filter on targets: when buying in discount we want a
        # target in premium; when selling in premium we want a target in discount.
        # Use the 1H dealing range if one is detected; otherwise accept any target.
        bars1h = self._asc(self.bars_1h[pair])
        dr = detect_dealing_range(bars1h, lookback=100)
        if dr is not None:
            filtered = [
                c for c in candidates
                if is_valid_target_zone(c, dr.high, dr.low, direction)
            ]
            if filtered:
                candidates = filtered
            # If no targets fall in the correct zone fall back to unfiltered list
            # (avoids blocking all trades when DR is stale or very wide).

        return min(candidates, key=lambda x: abs(x - price))

    @staticmethod
    def _targets_in_series(bars, pair, direction, price):
        fvgs = []
        for i in range(2, len(bars)):
            g = detect_new_fvg(bars[: i + 1], pair)
            if g is not None:
                fvgs.append(g)
        for g in fvgs:
            for c in bars[g.bar_index + 1:]:
                if g.direction > 0 and c.Low <= g.top:
                    g.mitigated = True
                    break
                if g.direction < 0 and c.High >= g.bottom:
                    g.mitigated = True
                    break
        out = []
        tgt_fvg = nearest_unmitigated(fvgs, price, direction)
        if tgt_fvg is not None:
            out.append(tgt_fvg.mid)

        tgt_ob = nearest_unmitigated_ob(detect_order_blocks(bars), price, direction)
        if tgt_ob is not None:
            out.append(tgt_ob.mid)

        if direction > 0:
            out += find_equal_highs(bars, pair, lookback=200)
        else:
            out += find_equal_lows(bars, pair, lookback=200)
        return out

    def OnOrderEvent(self, ev: OrderEvent):
        if ev.Status != OrderStatus.Filled:
            return
        oid = ev.OrderId
        role_entry = self.order_index.get(oid)
        if role_entry is None:
            return
        pair, role = role_entry
        st = self.active.get(pair)
        if st is None:
            self.order_index.pop(oid, None)
            return
        if role == "entry":
            self._on_entry_fill(pair, st, oid)
        elif role in ("sl", "tp"):
            self._on_exit_fill(pair, st, oid)

    def _on_entry_fill(self, pair, st, entry_id):
        info = st.pending.pop(entry_id, None)
        if info is None:
            return
        qc_sym = self.symbols[pair]
        signed_units = info["units"] * st.direction
        sl_ticket = self.StopMarketOrder(qc_sym, -signed_units, info["stop"],
                                         tag=f"{pair}-L{info['leg_idx']}-sl")
        tp_ticket = self.LimitOrder(qc_sym, -signed_units, st.target,
                                    tag=f"{pair}-L{info['leg_idx']}-tp")
        leg = {
            "entry": info["entry"], "stop": info["stop"], "units": info["units"],
            "leg_idx": info["leg_idx"], "entry_id": entry_id,
            "sl_id": sl_ticket.OrderId, "tp_id": tp_ticket.OrderId,
        }
        # Pyramid leg: promote prior leg's broker stop to break-even.
        if st.legs:
            prior = st.legs[-1]
            sl_id = prior.get("sl_id")
            if sl_id is not None:
                ticket = self.Transactions.GetOrderTicket(sl_id)
                if ticket is not None and ticket.Status not in (
                    OrderStatus.Filled, OrderStatus.Canceled
                ):
                    ticket.UpdateStopPrice(prior["entry"])
                    prior["stop"] = prior["entry"]
        st.legs.append(leg)
        self.order_index[sl_ticket.OrderId] = (pair, "sl")
        self.order_index[tp_ticket.OrderId] = (pair, "tp")
        self.order_index.pop(entry_id, None)

    def _on_exit_fill(self, pair, st, exit_id):
        for leg in st.legs:
            if exit_id == leg.get("sl_id") or exit_id == leg.get("tp_id"):
                sibling = leg["tp_id"] if exit_id == leg["sl_id"] else leg["sl_id"]
                ticket = self.Transactions.GetOrderTicket(sibling)
                if ticket is not None and ticket.Status not in (
                    OrderStatus.Filled, OrderStatus.Canceled
                ):
                    ticket.Cancel("sibling exit filled")
                self.order_index.pop(sibling, None)
                break
        self.order_index.pop(exit_id, None)
        qc_sym = self.symbols[pair]
        if not self.Portfolio[qc_sym].Invested:
            self.Transactions.CancelOpenOrders(qc_sym)
            for leg in st.legs:
                for k in ("entry_id", "sl_id", "tp_id"):
                    self.order_index.pop(leg.get(k), None)
            for pid in list(st.pending.keys()):
                self.order_index.pop(pid, None)
            self.active.pop(pair, None)

    @staticmethod
    def _asc(rw):
        """RollingWindow yields newest-first; we want oldest-first lists."""
        out = list(rw)
        out.reverse()
        return out

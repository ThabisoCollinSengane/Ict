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
from ict.liquidity import detect_sweep, find_equal_highs, find_equal_lows
from ict.bias import htf_bias
from ict.dxy_synthetic import compute_dxy
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
        try:
            xml = self.Download(config.FOREXFACTORY_XML_URL)
            n = self.news.load(xml)
            self.Debug(f"News refreshed: {n} events kept")
        except Exception as exc:
            self.Debug(f"News refresh failed: {exc}")

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

        dxy_bias = self._dxy_bias_1h()
        eurgbp_bias = self._sym_bias(config.REF_EURGBP, self.bars_1h)
        signal = resolve_intermarket(dxy_bias, eurgbp_bias)
        if signal is None or signal.pair != pair:
            return

        if self._sym_bias(pair, self.bars_1h) != signal.direction:
            return
        if self._sym_bias(pair, self.bars_4h) != signal.direction:
            return

        bars15 = self._asc(self.bars_15m[pair])
        sweep_price = detect_sweep(bars15, signal.direction)
        if sweep_price is None:
            return

        bars5 = self._asc(self.bars_5m[pair])
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != signal.direction:
            return

        target = self._find_target(pair, signal.direction)
        if target is None:
            return

        pip = pip_size(pair)
        entry = fvg.mid
        stop = (sweep_price - pip) if signal.direction > 0 else (sweep_price + pip)

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
            c = compute_dxy(close_px)
            if c is None:
                continue
            series.append(_SynBar(c, c, c, c))
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

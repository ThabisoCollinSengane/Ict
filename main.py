"""ICT intermarket day-trading algorithm for QuantConnect / LEAN.

Pairs traded: GBPUSD, EURUSD.
Confirmation:  synthetic DXY + EURGBP relative strength.
Entry:         LTF (5m) FVG inside an HTF-aligned, killzone-gated window after a
               15m liquidity sweep.
Targets:       nearest HTF (4H) FVG / Order Block / equal-high or equal-low,
               minimum 20 pips.
Pyramiding:    up to 3 legs, each new leg requires a fresh continuation FVG.
News filter:   blocks entries ±15 min around High/Medium USD/EUR/GBP events
               sourced from the ForexFactory weekly XML calendar.
"""

from AlgorithmImports import *
from collections import defaultdict
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
    # =====================================================================
    # Initialise
    # =====================================================================
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2025, 4, 30)
        self.SetCash(config.STARTING_CASH)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage, AccountType.Margin)
        self.SetTimeZone(TimeZones.Utc)

        all_syms = set(config.PAIRS) | {config.REF_EURGBP} | set(config.DXY_CONSTITUENTS)
        self.symbols: dict[str, Symbol] = {}
        for sym in all_syms:
            self.symbols[sym] = self.AddForex(
                sym, Resolution.Minute, Market.Oanda
            ).Symbol

        self.bars_5m  = defaultdict(lambda: RollingWindow[TradeBar](300))
        self.bars_15m = defaultdict(lambda: RollingWindow[TradeBar](300))
        self.bars_1h  = defaultdict(lambda: RollingWindow[TradeBar](300))
        self.bars_4h  = defaultdict(lambda: RollingWindow[TradeBar](300))
        self.bars_1d  = defaultdict(lambda: RollingWindow[TradeBar](300))
        self.bars_1w  = defaultdict(lambda: RollingWindow[TradeBar](200))

        for sym, qc_sym in self.symbols.items():
            self._wire_consolidator(sym, qc_sym,     5, self.bars_5m)
            self._wire_consolidator(sym, qc_sym,    15, self.bars_15m)
            self._wire_consolidator(sym, qc_sym,    60, self.bars_1h)
            self._wire_consolidator(sym, qc_sym,   240, self.bars_4h)
            self._wire_consolidator(sym, qc_sym,  1440, self.bars_1d)
            self._wire_consolidator(sym, qc_sym, 10080, self.bars_1w)

        # News calendar
        self.news = NewsCalendar()
        self._refresh_news()
        self.Schedule.On(
            self.DateRules.WeekStart(),
            self.TimeRules.At(0, 5),
            self._refresh_news,
        )

        # Per-pair active trade state
        self.active: dict[str, TradeState] = {}
        self.last_price: dict[str, float] = {}

        self.SetWarmUp(timedelta(days=20))

    def _wire_consolidator(self, sym, qc_sym, minutes, store):
        cons = TradeBarConsolidator(timedelta(minutes=minutes))

        def handler(_sender, bar, _sym=sym, _store=store):
            _store[_sym].Add(bar)

        cons.DataConsolidated += handler
        self.SubscriptionManager.AddConsolidator(qc_sym, cons)

    def _refresh_news(self):
        try:
            xml = self.Download(config.FOREXFACTORY_XML_URL)
            n = self.news.load(xml)
            self.Debug(f"News refreshed: {n} events in window")
        except Exception as exc:
            self.Debug(f"News refresh failed: {exc}")

    # =====================================================================
    # Per-bar driver
    # =====================================================================
    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return

        for sym, qc_sym in self.symbols.items():
            if qc_sym in data and data[qc_sym] is not None:
                self.last_price[sym] = data[qc_sym].Price

        for pair in config.PAIRS:
            if pair in self.active:
                self._maybe_pyramid(pair)
            else:
                self._maybe_open(pair)

    # =====================================================================
    # Entry logic
    # =====================================================================
    def _maybe_open(self, pair: str):
        if not can_open_new_trade(self.UtcTime):
            return
        if self.news.is_blocked(self.UtcTime):
            return

        # --- Intermarket gating ---
        dxy_bias = self._dxy_bias_1h()
        eurgbp_bias = self._sym_bias(config.REF_EURGBP, self.bars_1h)
        signal = resolve_intermarket(dxy_bias, eurgbp_bias)
        if signal is None or signal.pair != pair:
            return

        # --- Pair HTF agreement (4H + 1H must match signal direction) ---
        if self._sym_bias(pair, self.bars_1h) != signal.direction:
            return
        if self._sym_bias(pair, self.bars_4h) != signal.direction:
            return

        # --- 15m liquidity sweep ---
        bars15 = self._asc(self.bars_15m[pair])
        sweep_price = detect_sweep(bars15, signal.direction)
        if sweep_price is None:
            return

        # --- 5m FVG in trade direction (most recent 3 closed bars) ---
        bars5 = self._asc(self.bars_5m[pair])
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != signal.direction:
            return

        # --- HTF target ---
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
        self.LimitOrder(qc_sym, units, entry, tag=f"{pair}-L1-entry")
        self.StopMarketOrder(qc_sym, -units, stop, tag=f"{pair}-L1-sl")
        self.LimitOrder(qc_sym, -units, target, tag=f"{pair}-L1-tp")

        st = TradeState(symbol=pair, direction=signal.direction,
                        target=target, initial_stop=stop)
        st.legs.append({"entry": entry, "stop": stop, "units": abs(units), "leg_idx": 1})
        self.active[pair] = st

    # =====================================================================
    # Pyramiding
    # =====================================================================
    def _maybe_pyramid(self, pair: str):
        st = self.active[pair]
        if not st.can_add():
            return
        if self.news.is_blocked(self.UtcTime):
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
        self.LimitOrder(qc_sym, units, entry, tag=f"{pair}-L{leg_idx}-entry")
        self.StopMarketOrder(qc_sym, -units, stop, tag=f"{pair}-L{leg_idx}-sl")
        self.LimitOrder(qc_sym, -units, st.target, tag=f"{pair}-L{leg_idx}-tp")
        st.legs.append({"entry": entry, "stop": stop, "units": abs(units), "leg_idx": leg_idx})

    # =====================================================================
    # Bias helpers
    # =====================================================================
    def _sym_bias(self, sym: str, store) -> int:
        bars = self._asc(store[sym])
        return htf_bias(bars)

    def _dxy_bias_1h(self) -> int:
        rolls = {s: self._asc(self.bars_1h[s]) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        if n < config.SWING_LOOKBACK + 2:
            return 0
        series: list[_SynBar] = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS}
            high_px  = {s: rolls[s][i].High  for s in config.DXY_CONSTITUENTS}
            low_px   = {s: rolls[s][i].Low   for s in config.DXY_CONSTITUENTS}
            c = compute_dxy(close_px)
            h = compute_dxy(high_px)
            l = compute_dxy(low_px)
            if None in (c, h, l):
                return 0
            series.append(_SynBar(c, max(h, l, c), min(h, l, c), c))
        return htf_bias(series)

    # =====================================================================
    # Target search across H4 / Daily / Weekly
    # =====================================================================
    def _find_target(self, pair: str, direction: int) -> float | None:
        stores = (self.bars_4h, self.bars_1d, self.bars_1w)
        candidates: list[float] = []
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
    def _targets_in_series(bars, pair, direction, price) -> list[float]:
        # Unmitigated FVGs on this TF
        fvgs = []
        for i in range(2, len(bars)):
            g = detect_new_fvg(bars[: i + 1], pair)
            if g is not None:
                fvgs.append(g)
        for g in fvgs:
            for c in bars[g.bar_index + 1 :]:
                if g.direction > 0 and c.Low <= g.top:
                    g.mitigated = True
                    break
                if g.direction < 0 and c.High >= g.bottom:
                    g.mitigated = True
                    break
        out: list[float] = []
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

    # =====================================================================
    # Order lifecycle — clean up state when flat
    # =====================================================================
    def OnOrderEvent(self, ev: OrderEvent):
        if ev.Status != OrderStatus.Filled:
            return
        for pair in list(self.active.keys()):
            qc_sym = self.symbols[pair]
            if not self.Portfolio[qc_sym].Invested:
                self.Transactions.CancelOpenOrders(qc_sym)
                self.active.pop(pair, None)

    # =====================================================================
    # Utility
    # =====================================================================
    @staticmethod
    def _asc(rw) -> list:
        """RollingWindow yields newest-first; we want oldest-first lists."""
        out = list(rw)
        out.reverse()
        return out

"""ICT intermarket day-trading algorithm for QuantConnect / LEAN.

Pairs traded : GBPUSD, EURUSD, NZDUSD.
Confirmation : real UDXUSD (DXY) + EURGBP / AUDNZD relative strength.
Entry        : market order at 5m bar close, patterned stop (FVG/OB/Breaker).
News         : High-impact = distribution catalyst (fixed 10-pip SL, full pyramid).
               Medium-impact = hard block (spread risk without catalyst).
Pyramiding   : up to 3 legs; new leg requires pattern + 15-pip favour + IM score.
Circuit breakers:
  - Peak drawdown > MAX_DRAWDOWN_HALT_PCT  → pause DRAWDOWN_PAUSE_DAYS days.
  - Session equity drop > SESSION_DRAWDOWN_PCT → halt rest of day.
  - Daily loss > MAX_DAILY_LOSS_PCT         → no new entries today.
  - Consecutive losses ≥ MAX_CONSECUTIVE_LOSSES → pause today.
Trade log    : every closed leg written to ObjectStore JSON (recoverable).
"""

from AlgorithmImports import *
from datetime import timedelta
import json
import pytz

try:
    from scripts.notify import send_message as _notify
except Exception:
    def _notify(msg): return False  # noqa: E731

import config
from ict.killzones import can_open_new_trade, current_killzone
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob, find_breaker_zone
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.bias import htf_bias
from ict.dxy_synthetic import compute_dxy, compute_dxy_range
from ict.amd import detect_amd_setup, detect_breakout
from ict.ote import in_ote, find_swing
from ict.fib_targets import nearest_fib_target
from ict.htf_draw import draw_cascade_score
from ict.market_profile import detect_weekly_amd, profile_score
from ict import market_structure as mstruct
from ict.dealing_range import (
    detect_dealing_range, is_valid_entry_zone, is_valid_target_zone,
    is_nfp_week_low_probability, is_post_fomc_low_probability,
)
from intermarket import resolve as resolve_intermarket, resolve_pair_direction
from news_filter import NewsCalendar
from risk import position_size, pip_size

_NY = pytz.timezone("America/New_York")
_UTC = pytz.UTC


class _SynBar:
    __slots__ = ("Open", "High", "Low", "Close")
    def __init__(self, o, h, l, c):
        self.Open, self.High, self.Low, self.Close = o, h, l, c


class ICTIntermarketAlgorithm(QCAlgorithm):

    # ──────────────────────────────────────────────────────────────────────────
    # Initialization
    # ──────────────────────────────────────────────────────────────────────────

    def Initialize(self):
        self.SetStartDate(2022, 1, 1)
        self.SetEndDate(2025, 12, 31)
        self.SetCash(config.STARTING_CASH)
        self.SetBrokerageModel(BrokerageName.OandaBrokerage, AccountType.Margin)
        self.SetTimeZone(TimeZones.Utc)

        all_syms = set(config.PAIRS) | {config.REF_EURGBP} | set(config.DXY_CONSTITUENTS)
        # Add AUDNZD for NZD intermarket scoring.
        if hasattr(config, "REF_AUDNZD"):
            all_syms.add(config.REF_AUDNZD)

        self.symbols: dict = {}
        self.sym_by_qc: dict = {}
        for sym in all_syms:
            qc_sym = self.AddForex(sym, Resolution.Minute, Market.Oanda).Symbol
            self.symbols[sym] = qc_sym
            self.sym_by_qc[qc_sym] = sym

        self.bars_1m  = {s: RollingWindow[QuoteBar](200)  for s in all_syms}
        self.bars_5m  = {s: RollingWindow[QuoteBar](500)  for s in all_syms}
        self.bars_15m = {s: RollingWindow[QuoteBar](300)  for s in all_syms}
        self.bars_1h  = {s: RollingWindow[QuoteBar](300)  for s in all_syms}
        self.bars_4h  = {s: RollingWindow[QuoteBar](200)  for s in all_syms}
        self.bars_1d  = {s: RollingWindow[QuoteBar](300)  for s in all_syms}
        self.bars_1w  = {s: RollingWindow[QuoteBar](200)  for s in all_syms}

        for sym, qc_sym in self.symbols.items():
            self._wire_consolidator(sym, qc_sym,     1, self.bars_1m,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,     5, self.bars_5m,  is_entry_tf=True)
            self._wire_consolidator(sym, qc_sym,    15, self.bars_15m, is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,    60, self.bars_1h,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,   240, self.bars_4h,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym,  1440, self.bars_1d,  is_entry_tf=False)
            self._wire_consolidator(sym, qc_sym, 10080, self.bars_1w,  is_entry_tf=False)

        # News calendar
        self.news = NewsCalendar()
        self._refresh_news()
        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.At(0, 5),
            self._refresh_news,
        )

        # Reference open prices (maintained by scheduled events)
        self._daily_opens   = {}   # pair -> float
        self._weekly_opens  = {}   # pair -> float
        self._session_opens = {}   # pair -> float

        # Notification dedup: track which circuit-breaker alerts have been sent
        # so we don't spam on every 5m bar while the halt is active.
        self._notified_halt_until: str | None = None
        self._notified_day_halt  = False

        # Weekly and daily trade budgets
        self._week_key       = None
        self._week_total     = 0
        self._week_pair      = {}   # pair -> int
        self._day_key        = None
        self._day_total      = 0
        self._day_pair       = {}   # pair -> int

        # Circuit breaker state
        self._peak_equity         = config.STARTING_CASH
        self._consec_losses       = 0
        self._day_open_equity     = config.STARTING_CASH
        self._session_open_equity = config.STARTING_CASH
        self._halt_until_date     = None   # drawdown halt (date string "YYYY-MM-DD")
        self._day_halted          = False  # session drawdown or daily loss halt today

        # Active positions: pair -> state dict (mirrors backtest.py structure)
        self.active: dict = {}
        # Pending entry order info: order_id -> {pair, stop, units, leg_idx, news_impact}
        self._pending_entry: dict = {}
        # Order routing: order_id -> (pair, "sl"/"tp")
        self._order_index: dict = {}

        # Trade log (ObjectStore JSON)
        self._trade_log_key = "ict_trade_log.jsonl"
        self._trade_buffer  = []

        # Scheduled resets
        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.At(0, 0),
            self._daily_reset,
        )
        self.Schedule.On(
            self.DateRules.Every(DayOfWeek.Monday),
            self.TimeRules.At(0, 0),
            self._weekly_reset,
        )

        self.SetWarmUp(timedelta(days=90))

    # ──────────────────────────────────────────────────────────────────────────
    # Consolidator wiring
    # ──────────────────────────────────────────────────────────────────────────

    def _wire_consolidator(self, sym, qc_sym, minutes, store, is_entry_tf):
        cons = QuoteBarConsolidator(timedelta(minutes=minutes))

        def handler(_sender, bar, _sym=sym, _store=store, _entry=is_entry_tf):
            _store[_sym].Add(bar)
            if _entry and _sym in config.PAIRS:
                self._on_5m_close(_sym)

        cons.DataConsolidated += handler
        self.SubscriptionManager.AddConsolidator(qc_sym, cons)

    # ──────────────────────────────────────────────────────────────────────────
    # News
    # ──────────────────────────────────────────────────────────────────────────

    def _refresh_news(self):
        if config.NEWS_SOURCE == "csv":
            self._load_news_csv()
            return
        try:
            xml = self.Download(config.FOREXFACTORY_XML_URL)
            n = self.news.load(xml)
            self.Debug(f"News (XML) refreshed: {n} events")
        except Exception as exc:
            self.Debug(f"News XML refresh failed: {exc}")

    def _load_news_csv(self):
        if self.news.events:
            return
        text = None
        try:
            if self.ObjectStore.ContainsKey(config.NEWS_CSV_PATH):
                text = self.ObjectStore.Read(config.NEWS_CSV_PATH)
        except Exception:
            pass
        if not text:
            try:
                with open(config.NEWS_CSV_PATH, "r") as f:
                    text = f.read()
            except Exception as exc:
                self.Debug(f"News CSV load failed: {exc}")
                return
        n = self.news.load_csv(text)
        self.Debug(f"News (CSV) loaded: {n} events")

    # ──────────────────────────────────────────────────────────────────────────
    # Scheduled resets
    # ──────────────────────────────────────────────────────────────────────────

    def _daily_reset(self):
        equity = self.Portfolio.TotalPortfolioValue
        today = self.UtcTime.strftime("%Y-%m-%d")
        self._day_open_equity = equity
        self._session_open_equity = equity
        self._day_key   = today
        self._day_total = 0
        self._day_pair  = {}
        self._day_halted = False
        self._notified_day_halt = False
        self._peak_equity = max(self._peak_equity, equity)
        # Record reference opens for all tradeable pairs at session start
        for pair in config.PAIRS:
            bars5 = self._asc(self.bars_5m[pair])
            if bars5:
                self._daily_opens[pair] = bars5[-1].Close
        dd_pct = ((self._peak_equity - equity) / self._peak_equity * 100
                  if self._peak_equity > 0 else 0.0)
        _notify(
            f"DAY START: {today}\n"
            f"Equity:  R{equity:,.2f}\n"
            f"Peak:    R{self._peak_equity:,.2f}\n"
            f"DD from peak: {dd_pct:.1f}%"
        )

    def _weekly_reset(self):
        equity = self.Portfolio.TotalPortfolioValue
        self._week_key   = self.UtcTime.isocalendar()[:2]
        self._week_total = 0
        self._week_pair  = {}
        for pair in config.PAIRS:
            bars5 = self._asc(self.bars_5m[pair])
            if bars5:
                self._weekly_opens[pair] = bars5[-1].Close
        _notify(
            f"WEEK START\n"
            f"Equity: R{equity:,.2f}\n"
            f"Peak:   R{self._peak_equity:,.2f}\n"
            f"Consecutive losses: {self._consec_losses}"
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Main bar trigger
    # ──────────────────────────────────────────────────────────────────────────

    def OnData(self, data: Slice):
        # Detect gaps: if a bar is missing for more than 2 × its interval, log a warning.
        pass

    def _on_5m_close(self, pair: str):
        if self.IsWarmingUp:
            return

        # Update session open on killzone open bar
        now = self.UtcTime
        ny_dt = now.astimezone(_NY)
        h, m = ny_dt.hour, ny_dt.minute
        is_london_open = (h == 2 and 0 <= m <= 5)
        is_ny_open     = (h == 7 and 0 <= m <= 5)
        if is_london_open or is_ny_open:
            bars5 = self._asc(self.bars_5m[pair])
            if bars5:
                self._session_opens[pair] = bars5[-1].Close
            # Session handover: close positions fighting weekly AMD
            self._check_session_handover(pair)

        if pair in self.active:
            self._update_open_stops(pair)
            self._maybe_pyramid(pair)
        else:
            self._maybe_open(pair)

    # ──────────────────────────────────────────────────────────────────────────
    # Circuit breaker check
    # ──────────────────────────────────────────────────────────────────────────

    def _circuit_breakers_ok(self) -> bool:
        equity = self.Portfolio.TotalPortfolioValue
        today  = self.UtcTime.strftime("%Y-%m-%d")

        # 1. Rolling drawdown halt
        if self._halt_until_date and today <= self._halt_until_date:
            return False
        if self._peak_equity > 0:
            dd = (self._peak_equity - equity) / self._peak_equity * 100
            if dd >= config.MAX_DRAWDOWN_HALT_PCT:
                resume = (self.UtcTime + timedelta(days=config.DRAWDOWN_PAUSE_DAYS))
                self._halt_until_date = resume.strftime("%Y-%m-%d")
                self.Debug(f"Drawdown halt: {dd:.1f}% — resume {self._halt_until_date}")
                if self._notified_halt_until != self._halt_until_date:
                    self._notified_halt_until = self._halt_until_date
                    _notify(
                        f"CIRCUIT BREAKER: MAX DRAWDOWN HALT\n"
                        f"Drawdown: {dd:.1f}% from peak\n"
                        f"Equity:   R{equity:,.2f}\n"
                        f"Halt until: {self._halt_until_date}"
                    )
                return False

        # 2. Daily halt flag (set by session drawdown or daily loss)
        if self._day_halted:
            return False

        # 3. Daily loss cap
        if self._day_open_equity > 0:
            day_loss = (self._day_open_equity - equity) / self._day_open_equity * 100
            if day_loss >= config.MAX_DAILY_LOSS_PCT:
                self._day_halted = True
                self.Debug(f"Daily loss cap hit: {day_loss:.1f}%")
                if not self._notified_day_halt:
                    self._notified_day_halt = True
                    _notify(
                        f"CIRCUIT BREAKER: DAILY LOSS CAP\n"
                        f"Daily loss: {day_loss:.1f}%\n"
                        f"Equity: R{equity:,.2f}\n"
                        f"No new entries until tomorrow"
                    )
                return False

        # 4. Session drawdown kill switch
        if self._session_open_equity > 0:
            sess_loss = (self._session_open_equity - equity) / self._session_open_equity * 100
            if sess_loss >= config.SESSION_DRAWDOWN_PCT:
                self._day_halted = True
                self.Debug(f"Session drawdown kill: {sess_loss:.1f}% — halting day")
                if not self._notified_day_halt:
                    self._notified_day_halt = True
                    _notify(
                        f"CIRCUIT BREAKER: SESSION KILL SWITCH\n"
                        f"Session loss: {sess_loss:.1f}%\n"
                        f"Equity: R{equity:,.2f}\n"
                        f"All positions closed — halted for the day"
                    )
                self._close_all_positions()
                return False

        # 5. Consecutive loss pause
        if self._consec_losses >= config.MAX_CONSECUTIVE_LOSSES:
            self._day_halted = True
            if not self._notified_day_halt:
                self._notified_day_halt = True
                _notify(
                    f"CIRCUIT BREAKER: CONSECUTIVE LOSSES\n"
                    f"{self._consec_losses} losses in a row\n"
                    f"Equity: R{equity:,.2f}\n"
                    f"Paused for the rest of the day"
                )
            return False

        return True

    def _close_all_positions(self):
        for pair in list(self.active.keys()):
            qc_sym = self.symbols[pair]
            if self.Portfolio[qc_sym].Invested:
                self.Liquidate(qc_sym)
            for k in ("sl_ids", "tp_ids"):
                for oid in self.active[pair].get(k, []):
                    self._order_index.pop(oid, None)
            self.active.pop(pair, None)

    # ──────────────────────────────────────────────────────────────────────────
    # Entry
    # ──────────────────────────────────────────────────────────────────────────

    def _maybe_open(self, pair: str):
        now = self.UtcTime

        if not self._circuit_breakers_ok():
            return
        if not can_open_new_trade(now, pair):
            return

        # Weekly / daily budget gates
        week_key = now.isocalendar()[:2]
        if self._week_key != week_key:
            self._week_key = week_key
        week_total = self._week_total
        if week_total >= config.MAX_TRADES_PER_WEEK:
            return
        day_key = now.strftime("%Y-%m-%d")
        day_total  = self._day_total
        day_pair   = self._day_pair.get(pair, 0)
        if day_total >= config.MAX_TRADES_PER_DAY:
            return
        if day_pair >= config.MAX_PAIR_TRADES_PER_DAY:
            return
        week_pair = self._week_pair.get(pair, 0)
        if week_pair >= config.MAX_PAIR_TRADES_PER_WEEK:
            return

        # News gate: block Critical (CPI/NFP/FOMC) and Medium; allow other High.
        news_impact = self.news.nearest_impact(now)
        if news_impact in ("Medium", "Critical"):
            return

        # Low-probability conditions
        if is_nfp_week_low_probability(now, self.news.is_nfp_week(now)):
            return
        if is_post_fomc_low_probability(now, self.news.fomc_whipsaw_date):
            return

        # ── Intermarket signal ────────────────────────────────────────────────
        dxy_bias = self._dxy_bias_1h()
        if pair in ("EURUSD", "GBPUSD"):
            eurgbp_bias = self._sym_bias(config.REF_EURGBP, self.bars_1h)
            direction, im_score = resolve_pair_direction(dxy_bias, eurgbp_bias, pair, "EURUSD")
        else:
            audnzd_bias = self._sym_bias(getattr(config, "REF_AUDNZD", "AUDNZD"), self.bars_1h)
            direction, im_score = resolve_pair_direction(dxy_bias, audnzd_bias, pair, "AUDUSD")
        if direction is None:
            return

        # ── MSS / bias hierarchy ──────────────────────────────────────────────
        bars1h = self._asc(self.bars_1h[pair])
        bars1d = self._asc(self.bars_1d[pair])
        if config.REQUIRE_DAILY_BIAS:
            if htf_bias(bars1d) != direction:
                return
        if htf_bias(bars1h) != direction:
            return
        bars4h = self._asc(self.bars_4h[pair])
        if htf_bias(bars4h) != direction:
            return
        bars15 = self._asc(self.bars_15m[pair])
        bars5  = self._asc(self.bars_5m[pair])
        mss_ok = (
            self._bias_stk(bars15, config.SWING_LOOKBACK_STH) == direction
            or self._bias_stk(bars5, config.SWING_LOOKBACK_STH) == direction
        )
        if not mss_ok:
            return

        # ── Conviction scoring ────────────────────────────────────────────────
        conviction = 0

        # Intermarket (0-2)
        if im_score >= 1.0:
            conviction += 2
        elif im_score >= 0.75:
            conviction += 1

        # Intermarket breakout: triple-confirmed continuation (EURUSD + GBPUSD + DXY
        # all clear their M15 ranges in agreement). When it fires in the trade
        # direction the setup is a continuation/expansion, not a reversal — it earns
        # extra conviction, a "breakout" entry_model tag, and an exemption from the
        # inverted-draw 0/3 hard gate below (which is reversal logic).
        _brk_dir = self._intermarket_breakout()
        _is_breakout = (_brk_dir != 0 and _brk_dir == direction)

        # MSS (0-2): M15 + M5 structure
        if self._bias_stk(bars15, config.SWING_LOOKBACK_STH) == direction:
            conviction += 1
        if self._bias_stk(bars5, config.SWING_LOOKBACK_STH) == direction:
            conviction += 1

        # Weekly AMD (0-2)
        bars1d_full = self._asc(self.bars_1d[pair])
        bars1w = self._asc(self.bars_1w[pair])
        wamd = self._get_weekly_amd_live(pair, bars1d_full)
        weekly_amd_dir = wamd.direction if wamd is not None else 0
        if wamd is not None and wamd.direction == direction:
            conviction += 2

        # HTF Draw on Liquidity cascade: W → D → H4 (0-3). The single most important
        # directional factor. Each TF that agrees with trade direction adds +1.
        # 0/3 = no HTF draw alignment → hard gate (reversal logic): skip unless this
        # is a breakout continuation (which runs WITH the HTF and scores 0 by design).
        pip_v0  = pip_size(pair)
        bars_h4_d = self._asc(self.bars_4h[pair])
        _draw_score = draw_cascade_score(bars1w, bars1d_full, bars_h4_d, pair, direction, pip_v0)
        if _draw_score == 0 and not _is_breakout:
            return
        conviction += _draw_score

        # Breakout continuation conviction credit (continuation runs WITH the draw).
        if _is_breakout:
            conviction += config.BREAKOUT_CONVICTION

        # Profile score + session open (0-2)
        cur_price = bars5[-1].Close if bars5 else None
        if cur_price is None:
            return
        p_score, _session_open = self._profile_score_live(pair, direction, cur_price)
        conviction += min(p_score, 1)

        # AMD M15 (0-1)
        amd = detect_amd_setup(bars15, pair)
        amd_score = 0
        if amd is not None:
            rng, sweep_dir = amd
            if sweep_dir == direction:
                amd_score = 1
                conviction += 1

        # OTE (0-1)
        pip_v = pip_size(pair)
        if (in_ote(cur_price, bars15, direction, lookback=config.SWING_LOOKBACK, pip_tol=3*pip_v)
                or in_ote(cur_price, bars1h, direction, lookback=config.SWING_LOOKBACK//2, pip_tol=3*pip_v)):
            conviction += 1

        # CHoCH (0-1)
        lb = config.SWING_LOOKBACK_STH
        if len(bars15) >= lb * 3 + 2:
            if htf_bias(bars15[:-lb], lookback=lb) == -direction and htf_bias(bars15, lookback=lb) == direction:
                conviction += 1

        # Judas-swing bonus (+1 if price on correct side of session open)
        if _session_open is not None:
            if (direction > 0 and cur_price < _session_open) or (direction < 0 and cur_price > _session_open):
                conviction += 1

        # Ep 12 market structure: pair fractal + DXY fractal alignment
        _ms = self._structure_conviction(pair, direction)
        conviction += _ms["points"]

        # Conviction gate
        min_conv = (config.MIN_CONVICTION_LATE_WEEK
                    if week_total >= config.WEEKLY_SOFT_CAP
                    else config.MIN_CONVICTION)
        if conviction < min_conv:
            return

        # Max legs from conviction
        if conviction <= 2:
            max_legs = 1
        elif conviction <= 4:
            max_legs = 2
        else:
            max_legs = config.MAX_LEGS
        if news_impact == "High":
            max_legs = config.MAX_LEGS

        # ── Pattern gate ──────────────────────────────────────────────────────
        bars1m = self._asc(self.bars_1m[pair])
        _level, stop, pattern_tag = self._get_limit_entry(
            bars5, bars15, bars1h, pair, direction, cur_price, bars1m=bars1m
        )
        if pattern_tag is None:
            return

        pip = pip_size(pair)

        # Stop placement: anchor to M1 market structure (nearest M1 swing). Entry
        # pattern came from M5/M15/H1; the stop comes from the 1-minute structure.
        _m1_stop = self._m1_structure_stop(bars1m, direction, cur_price, pip)
        if _m1_stop is not None:
            stop = _m1_stop

        # News High: override to fixed 10-pip stop
        if news_impact == "High":
            stop = (cur_price - config.FIXED_STOP_PIPS * pip if direction > 0
                    else cur_price + config.FIXED_STOP_PIPS * pip)

        # Universal stop cap: never risk more than FIXED_STOP_PIPS on any trade.
        # Applied here so position sizing below uses the capped distance; the final
        # stop is re-derived from the actual fill price in _on_entry_fill. Only
        # stops wider than the cap are pulled in; tighter structural stops are kept.
        _max_stop = config.FIXED_STOP_PIPS * pip
        if abs(cur_price - stop) > _max_stop:
            stop = (cur_price - _max_stop if direction > 0
                    else cur_price + _max_stop)

        target, _target_score = self._find_target(pair, direction, cur_price)
        if target is None:
            return

        reward_pips = abs(target - cur_price) / pip
        if reward_pips < self._min_pips_target():
            return

        equity_usd = self.Portfolio.TotalPortfolioValue / config.USD_ZAR
        units_raw  = int(position_size(equity_usd, cur_price, stop, pair))
        tier_lots  = self._pyramid_lots()
        min_units  = int(tier_lots[0] * config.LOT_UNITS)
        units      = max(units_raw, min_units)
        if units == 0:
            return

        # ── Sizing levers (ported from backtest — match the compounding path) ────
        # Account is ZAR-denominated, so TotalPortfolioValue is already in ZAR and
        # compares directly to DRAW_SIZE_MIN_EQUITY (the R3,000 multiplier floor).
        # _draw_score and _is_breakout were computed during conviction scoring above.
        # P41: did the AMD manipulation sweep run prior-day liquidity (PDH/PDL)?
        # Prior-day H/L = the last completed daily candle (bars1d_full[-1], ascending).
        # rng/sweep_dir exist only when amd fired; guard on it. Computed here so the
        # analytics flag is set even when equity is below the multiplier floor.
        _amd_swept_pdliq = False
        if amd is not None and len(bars1d_full) >= 1:
            _swept_lvl = rng.low if sweep_dir > 0 else rng.high
            _tol = 5 * pip_v
            _pdh, _pdl = bars1d_full[-1].High, bars1d_full[-1].Low
            _amd_swept_pdliq = (abs(_swept_lvl - _pdh) <= _tol
                                or abs(_swept_lvl - _pdl) <= _tol)

        equity_zar = self.Portfolio.TotalPortfolioValue
        if equity_zar >= config.DRAW_SIZE_MIN_EQUITY:
            # Draw-cascade 2×/3×: HTF W→D→H4 draw agreeing with the trade.
            _draw_mult = config.DRAW_SIZE_MULT.get(_draw_score, 1.0)
            if _draw_mult != 1.0:
                units = max(int(units * _draw_mult), min_units)

            # P9 HTF-FVG 1.25× — breakout/continuation anchored at an HTF FVG 50%.
            # Now active: the breakout model is ported (_is_breakout above).
            _htf_fvg_pts, _ = self._htf_fvg_conviction(pair, direction, cur_price)
            if _is_breakout and _htf_fvg_pts:
                units = max(int(units * config.HTF_FVG_BREAKOUT_MULT), min_units)

            # P18 score≥4 confluence 1.25× — ≥4 source families cluster at the TP.
            if _target_score >= config.TARGET_SCORE_MULT_THRESHOLD:
                units = max(int(units * config.TARGET_SCORE_MULT), min_units)

            # P19 H4-CRT 1.25× — H4 Turtle Soup (HTF Judas swing) in our direction.
            _crt_pts, _crt_tf = self._htf_crt_sweep(pair, direction, cur_price)
            if _crt_tf == config.CRT_SWEEP_MULT_TF and config.CRT_SWEEP_MULT != 1.0:
                units = max(int(units * config.CRT_SWEEP_MULT), min_units)

            # P41 PDH/PDL-sweep 1.25× — the raid ran prior-day liquidity (55/53% WR).
            if _amd_swept_pdliq and config.PDLIQ_SWEEP_MULT != 1.0:
                units = max(int(units * config.PDLIQ_SWEEP_MULT), min_units)

        # ── Place market order ────────────────────────────────────────────────
        qc_sym       = self.symbols[pair]
        signed_units = units * direction
        entry_ticket = self.MarketOrder(qc_sym, signed_units,
                                        tag=f"{pair}-L1-entry")

        # Session-open side analytics
        if _session_open is None:
            so_side = "no_open"
        elif (direction > 0 and cur_price < _session_open) or (direction < 0 and cur_price > _session_open):
            so_side = "judas"
        else:
            so_side = "momentum"

        base_type  = "amd" if amd_score else "mss"
        entry_type = f"{'news' if news_impact == 'High' else base_type}_{pattern_tag}"

        self.active[pair] = {
            "direction": direction,
            "target": target,
            "max_legs": max_legs,
            "legs": [],
            "weekly_amd_dir": weekly_amd_dir,
            "news_impact": news_impact,
            "entry_model": "breakout" if _is_breakout else "judas",
            "draw_score": _draw_score,
            "amd_swept_pdliq": _amd_swept_pdliq,
        }
        self._pending_entry[entry_ticket.OrderId] = {
            "pair": pair, "stop": stop, "units": units,
            "leg_idx": 1, "entry_type": entry_type, "session_side": so_side,
        }
        self.order_index = getattr(self, "order_index", {})

        # Update budget counters immediately (before fill confirmation)
        self._week_total = week_total + 1
        self._week_pair[pair] = week_pair + 1
        self._day_total  = day_total + 1
        self._day_pair[pair] = day_pair + 1

    # ──────────────────────────────────────────────────────────────────────────
    # Pyramid
    # ──────────────────────────────────────────────────────────────────────────

    def _maybe_pyramid(self, pair: str):
        st = self.active.get(pair)
        if st is None:
            return
        if len(st["legs"]) >= st.get("max_legs", config.MAX_LEGS):
            return

        now = self.UtcTime
        if not can_open_new_trade(now, pair):
            return

        pyr_news = self.news.nearest_impact(now)
        if pyr_news in ("Medium", "Critical"):
            return

        # Intermarket score for this pyramid leg
        dxy_bias = self._dxy_bias_1h()
        if pair in ("EURUSD", "GBPUSD"):
            eurgbp_bias = self._sym_bias(config.REF_EURGBP, self.bars_1h)
            dir_check, im_score = resolve_pair_direction(dxy_bias, eurgbp_bias, pair, "EURUSD")
        else:
            audnzd_bias = self._sym_bias(getattr(config, "REF_AUDNZD", "AUDNZD"), self.bars_1h)
            dir_check, im_score = resolve_pair_direction(dxy_bias, audnzd_bias, pair, "AUDUSD")

        if dir_check is None:
            im_score = 0.5
        elif dir_check != st["direction"]:
            return

        # Weekly AMD upgrade — runs FIRST so the draw-unlock gate below sees the
        # promoted score (P21 fix: the upgrade must precede the im_score < 1.0 check).
        if config.WEEKLY_AMD_FULL_PYRAMID and st.get("weekly_amd_dir") == st["direction"]:
            im_score = 1.0

        # Block neutral pyramid
        if config.BLOCK_NEUTRAL_PYRAMID and im_score == 0.5:
            return

        # Weekly AMD hard gate
        if config.PYRAMID_REQUIRE_WEEKLY_AMD and st.get("weekly_amd_dir") != st["direction"]:
            return

        # P22: im_score < 1.0 is allowed when draw_score >= PYRAMID_DRAW_UNLOCK_MIN.
        # Any HTF draw alignment (≥1) is sufficient when DXY agrees with the trade.
        if im_score < 1.0:
            if st.get("draw_score", 0) < config.PYRAMID_DRAW_UNLOCK_MIN:
                return

        bars5  = self._asc(self.bars_5m[pair])
        if not bars5:
            return
        cur_price = bars5[-1].Close
        pip = pip_size(pair)

        # Minimum favour pips before adding
        last_entry = st["legs"][-1]["entry"] if st["legs"] else cur_price
        favour_pips = (cur_price - last_entry) * st["direction"] / pip
        if favour_pips < config.PYRAMID_MIN_FAVOUR_PIPS:
            return

        bars15 = self._asc(self.bars_15m[pair])
        bars1h = self._asc(self.bars_1h[pair])
        bars1m = self._asc(self.bars_1m[pair])
        _level, stop, pyr_pattern = self._get_limit_entry(
            bars5, bars15, bars1h, pair, st["direction"], cur_price,
            bars1m=bars1m, for_pyramid=True,
        )
        if pyr_pattern is None:
            return

        entry = cur_price
        # Ep 12 Stage 3: prefer intact M1 ITL/ITH over raw STL/STH.
        _struct_stop = self._structure_stop(pair, st["direction"], entry, pip)
        if _struct_stop is not None:
            stop = _struct_stop
        else:
            _m1_stop = self._m1_structure_stop(bars1m, st["direction"], entry, pip)
            if _m1_stop is not None:
                stop = _m1_stop
        if pyr_news == "High":
            stop = (entry - config.FIXED_STOP_PIPS * pip if st["direction"] > 0
                    else entry + config.FIXED_STOP_PIPS * pip)
            im_score = 1.0

        # Universal stop cap: never risk more than FIXED_STOP_PIPS on a pyramid leg.
        _max_stop = config.FIXED_STOP_PIPS * pip
        if abs(entry - stop) > _max_stop:
            stop = (entry - _max_stop if st["direction"] > 0
                    else entry + _max_stop)

        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < self._min_pips_target():
            return

        tier_lots = self._pyramid_lots()
        leg_num   = len(st["legs"]) + 1
        lot_idx   = min(leg_num - 1, len(tier_lots) - 1)
        base_units = int(tier_lots[lot_idx] * config.LOT_UNITS)
        units      = max(int(base_units * im_score), int(tier_lots[-1] * config.LOT_UNITS))

        qc_sym       = self.symbols[pair]
        signed_units = units * st["direction"]
        entry_ticket = self.MarketOrder(qc_sym, signed_units,
                                        tag=f"{pair}-L{leg_num}-pyr")

        wamd_tag   = "wamd" if st.get("weekly_amd_dir") == st["direction"] else "im"
        news_tag   = "news" if pyr_news == "High" else ""
        entry_type = f"pyramid_{wamd_tag}{news_tag}{im_score:.1f}_{pyr_pattern}"

        self._pending_entry[entry_ticket.OrderId] = {
            "pair": pair, "stop": stop, "units": units,
            "leg_idx": leg_num, "entry_type": entry_type,
            "session_side": "no_open",
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Order event handler
    # ──────────────────────────────────────────────────────────────────────────

    def OnOrderEvent(self, ev: OrderEvent):
        if ev.Status != OrderStatus.Filled:
            return
        oid = ev.OrderId
        fill = ev.FillPrice

        if oid in self._pending_entry:
            self._on_entry_fill(oid, fill)
            return

        if oid in self._order_index:
            pair, role = self._order_index.pop(oid)
            if role in ("sl", "tp"):
                self._on_exit_fill(pair, oid, fill, role)

    def _on_entry_fill(self, entry_id: int, fill_price: float):
        info = self._pending_entry.pop(entry_id)
        pair = info["pair"]
        st   = self.active.get(pair)
        if st is None:
            return

        stop = info["stop"]
        pip  = pip_size(pair)
        # For news High entries, recalculate fixed stop from actual fill price
        if st.get("news_impact") == "High":
            stop = (fill_price - config.FIXED_STOP_PIPS * pip if st["direction"] > 0
                    else fill_price + config.FIXED_STOP_PIPS * pip)
        else:
            # Ep 12 Stage 3: re-anchor stop to intact M1 ITL/ITH (survives Judas sweeps).
            # Falls back to the M1 STL/STH raw-swing stop when no intermediate swing
            # is within the 10-pip cap. News entries always use the fixed stop above.
            _struct_stop = self._structure_stop(pair, st["direction"], fill_price, pip)
            if _struct_stop is not None:
                stop = _struct_stop
            else:
                bars1m = self._asc(self.bars_1m[pair])
                _m1_stop = self._m1_structure_stop(bars1m, st["direction"], fill_price, pip)
                if _m1_stop is not None:
                    stop = _m1_stop

        # Universal stop cap measured from the ACTUAL broker fill price.
        _max_stop = config.FIXED_STOP_PIPS * pip
        if abs(fill_price - stop) > _max_stop:
            stop = (fill_price - _max_stop if st["direction"] > 0
                    else fill_price + _max_stop)

        qc_sym       = self.symbols[pair]
        signed_units = info["units"] * st["direction"]

        sl_ticket = self.StopMarketOrder(qc_sym, -signed_units, stop,
                                         tag=f"{pair}-L{info['leg_idx']}-sl")
        tp_ticket = self.LimitOrder(qc_sym, -signed_units, st["target"],
                                    tag=f"{pair}-L{info['leg_idx']}-tp")

        # Promote prior leg stop to break-even
        if st["legs"]:
            prior = st["legs"][-1]
            sl_id = prior.get("sl_id")
            if sl_id is not None:
                ticket = self.Transactions.GetOrderTicket(sl_id)
                if ticket is not None and ticket.Status not in (
                    OrderStatus.Filled, OrderStatus.Canceled
                ):
                    ticket.UpdateStopPrice(prior["entry"])
                    prior["stop"] = prior["entry"]

        leg = {
            "entry": fill_price, "stop": stop, "units": info["units"],
            "leg_idx": info["leg_idx"], "entry_id": entry_id,
            "sl_id": sl_ticket.OrderId, "tp_id": tp_ticket.OrderId,
            "entry_type": info.get("entry_type", "unknown"),
            "session_side": info.get("session_side", "no_open"),
            "opened_at": str(self.UtcTime),
        }
        st["legs"].append(leg)
        if not hasattr(self, "_order_index"):
            self._order_index = {}
        self._order_index[sl_ticket.OrderId] = (pair, "sl")
        self._order_index[tp_ticket.OrderId] = (pair, "tp")

        _pip       = pip_size(pair)
        _stop_pips = abs(fill_price - stop) / _pip
        _rwd_pips  = abs(st["target"] - fill_price) / _pip
        _dir_str   = "LONG" if st["direction"] > 0 else "SHORT"
        _leg_n     = info["leg_idx"]
        _equity    = self.Portfolio.TotalPortfolioValue
        _notify(
            f"TRADE OPENED\n"
            f"{pair} {_dir_str} | Leg {_leg_n}/{st['max_legs']}\n"
            f"Entry:  {fill_price:.5f}\n"
            f"Stop:   {stop:.5f} ({_stop_pips:.1f} pips)\n"
            f"Target: {st['target']:.5f} ({_rwd_pips:.1f} pips)\n"
            f"Equity: R{_equity:,.2f}"
        )

    def _on_exit_fill(self, pair: str, exit_id: int, fill_price: float, role: str):
        st = self.active.get(pair)
        if st is None:
            return

        for leg in list(st["legs"]):
            sl_id = leg.get("sl_id")
            tp_id = leg.get("tp_id")
            if exit_id not in (sl_id, tp_id):
                continue
            # Cancel the sibling order
            sibling = tp_id if exit_id == sl_id else sl_id
            ticket = self.Transactions.GetOrderTicket(sibling)
            if ticket is not None and ticket.Status not in (
                OrderStatus.Filled, OrderStatus.Canceled
            ):
                ticket.Cancel("sibling exit filled")
            self._order_index.pop(sibling, None)

            # Log closed leg
            pnl_est = (fill_price - leg["entry"]) * leg["units"] * st["direction"]
            reason  = "stop" if role == "sl" else "target"
            record  = {
                "pair": pair, "leg_idx": leg["leg_idx"], "direction": st["direction"],
                "entry": leg["entry"], "exit": fill_price, "units": leg["units"],
                "pnl_usd_approx": pnl_est,
                "opened_at": leg.get("opened_at"), "closed_at": str(self.UtcTime),
                "reason": reason, "entry_type": leg.get("entry_type", "unknown"),
                "session_side": leg.get("session_side", "no_open"),
            }
            self._write_trade_log(record)

            # Update consecutive loss counter
            if pnl_est <= 0:
                self._consec_losses += 1
            else:
                self._consec_losses = 0

            _pnl_zar   = pnl_est * config.USD_ZAR
            _sign      = "+" if _pnl_zar >= 0 else ""
            _dir_str   = "LONG" if st["direction"] > 0 else "SHORT"
            _reason_str = "TARGET" if role == "tp" else "STOP"
            _equity    = self.Portfolio.TotalPortfolioValue
            _notify(
                f"TRADE CLOSED [{_reason_str}]\n"
                f"{pair} {_dir_str} | Leg {leg['leg_idx']}\n"
                f"Entry: {leg['entry']:.5f} | Exit: {fill_price:.5f}\n"
                f"P&L:  {_sign}R{_pnl_zar:,.2f}\n"
                f"Equity: R{_equity:,.2f}"
            )

            st["legs"].remove(leg)
            break

        # If no open legs remain, clean up
        qc_sym = self.symbols[pair]
        if not self.Portfolio[qc_sym].Invested:
            self.Transactions.CancelOpenOrders(qc_sym)
            for lg in st.get("legs", []):
                self._order_index.pop(lg.get("sl_id"), None)
                self._order_index.pop(lg.get("tp_id"), None)
            self.active.pop(pair, None)

    # ──────────────────────────────────────────────────────────────────────────
    # Stop management — TRAIL_BE / TRAIL_LOCK / P23 milestone trail
    # ──────────────────────────────────────────────────────────────────────────

    def _update_open_stops(self, pair: str):
        """Ratchet stops for all open legs on every 5m bar close.

        +10 pips → move stop to break-even (TRAIL_BE_PIPS).
        +20 pips → lock stop at entry + 10 pips (TRAIL_LOCK_PIPS).
        +40/60/80… pips → milestone trail: stop at entry + (milestone − 10) pips.

        Every update calls UpdateStopPrice on the live SL order so the broker
        reflects the new level immediately.
        """
        st = self.active.get(pair)
        if st is None:
            return
        bars5 = self._asc(self.bars_5m[pair])
        if not bars5:
            return
        cur_price = bars5[-1].Close
        pip       = pip_size(pair)
        direction = st["direction"]

        for leg in st["legs"]:
            entry       = leg["entry"]
            pips_profit = (cur_price - entry) * direction / pip

            new_stop = leg["stop"]

            # Step 1: TRAIL_BE — move stop to entry at +TRAIL_BE_PIPS
            if pips_profit >= config.TRAIL_BE_PIPS:
                if direction > 0:
                    new_stop = max(new_stop, entry)
                else:
                    new_stop = min(new_stop, entry)

            # Step 2: TRAIL_LOCK — lock +10 pips at +TRAIL_LOCK_PIPS
            if pips_profit >= config.TRAIL_LOCK_PIPS:
                locked = entry + 10 * pip * direction
                if direction > 0:
                    new_stop = max(new_stop, locked)
                else:
                    new_stop = min(new_stop, locked)

            # Step 3: P23 milestone trail — every MILESTONE_TRAIL_STEP pips beyond
            # TRAIL_LOCK_PIPS, ratchet the stop to (milestone − MILESTONE_TRAIL_BUFFER).
            if (config.MILESTONE_TRAIL_ENABLED
                    and pips_profit >= config.TRAIL_LOCK_PIPS + config.MILESTONE_TRAIL_STEP):
                _step      = config.MILESTONE_TRAIL_STEP
                _buf       = config.MILESTONE_TRAIL_BUFFER
                _milestone = int(pips_profit / _step) * _step
                _lock_ms   = entry + (_milestone - _buf) * pip * direction
                if direction > 0:
                    new_stop = max(new_stop, _lock_ms)
                else:
                    new_stop = min(new_stop, _lock_ms)

            # Only update the broker order when the stop has moved in our favour.
            if new_stop != leg["stop"]:
                sl_id  = leg.get("sl_id")
                if sl_id is not None:
                    ticket = self.Transactions.GetOrderTicket(sl_id)
                    if ticket is not None and ticket.Status not in (
                        OrderStatus.Filled, OrderStatus.Canceled
                    ):
                        ticket.UpdateStopPrice(new_stop)
                leg["stop"] = new_stop

    # ──────────────────────────────────────────────────────────────────────────
    # Session handover
    # ──────────────────────────────────────────────────────────────────────────

    def _check_session_handover(self, pair: str):
        if not config.SESSION_HANDOVER_CLOSE:
            return
        st = self.active.get(pair)
        if st is None:
            return
        bars1d = self._asc(self.bars_1d[pair])
        wamd   = self._get_weekly_amd_live(pair, bars1d)
        if wamd is None or wamd.direction == st["direction"]:
            return
        bars5 = self._asc(self.bars_5m[pair])
        if not bars5:
            return
        cur_price  = bars5[-1].Close
        pip        = pip_size(pair)
        first_entry = st["legs"][0]["entry"] if st["legs"] else cur_price
        pips_profit = (cur_price - first_entry) * st["direction"] / pip
        if pips_profit < 0:
            qc_sym = self.symbols[pair]
            self.Liquidate(qc_sym, tag=f"{pair}-session_handover")
            self.active.pop(pair, None)
            self.Debug(f"Session handover close: {pair} fighting weekly AMD")

    # ──────────────────────────────────────────────────────────────────────────
    # Ep 12 fractal market structure (P16) — conviction + stop placement
    # ──────────────────────────────────────────────────────────────────────────

    _MSTRUCT_TFS = (
        ("W",    3),
        ("D",    2),
        ("240T", 1),
        ("60T",  1),
        ("15T",  1),
    )
    _DXY_MSTRUCT_TFS = ("W", "D", "240T", "60T")

    def _dxy_bars_for(self, store) -> list:
        """Build a synthetic DXY bar list from the given rolling-window store."""
        rolls = {s: self._asc(store[s]) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        out = []
        for i in range(-n, 0):
            c = compute_dxy({s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS})
            o = compute_dxy({s: rolls[s][i].Open  for s in config.DXY_CONSTITUENTS})
            h, l = compute_dxy_range(
                {s: rolls[s][i].High for s in config.DXY_CONSTITUENTS},
                {s: rolls[s][i].Low  for s in config.DXY_CONSTITUENTS},
            )
            if None in (c, o, h, l):
                continue
            out.append(_SynBar(o, h, l, c))
        return out

    _TF_TO_STORE = None  # lazily built in _structure_conviction

    def _structure_conviction(self, pair: str, direction: int) -> dict:
        """Read fractal market structure on the traded pair AND on DXY.

        DXY is the primary USD driver:
          DXY higher ITLs = USD strong = pairs fall → agrees when direction == -1
          DXY lower ITHs  = USD weak   = pairs rise → agrees when direction == +1
        """
        tf_to_store = {
            "W":    (self.bars_1w,  None),
            "D":    (self.bars_1d,  None),
            "240T": (self.bars_4h,  None),
            "60T":  (self.bars_1h,  None),
            "15T":  (self.bars_15m, None),
        }
        dxy_tf_to_store = {
            "W":    self.bars_1w,
            "D":    self.bars_1d,
            "240T": self.bars_4h,
            "60T":  self.bars_1h,
        }

        align = []
        weight = 0
        htf_dir = 0
        minor_sweep = False
        intact_tf = ""

        for tf, w in self._MSTRUCT_TFS:
            store, _ = tf_to_store[tf]
            bars = self._asc(store[pair])
            if len(bars) < 5:
                continue
            res = mstruct.classify(bars)
            sdir = mstruct.structure_direction(res)
            if sdir == direction:
                align.append(tf)
                weight += w
                if tf in ("W", "D"):
                    htf_dir = direction
                tier = "ITL" if direction > 0 else "ITH"
                if mstruct.last_intact(res, tier) is not None and not intact_tf:
                    intact_tf = tf
            if tf in ("60T", "15T") and mstruct.is_minor_sweep(res, direction):
                minor_sweep = True

        dxy_align = []
        dxy_minor_sweep = False
        for tf in self._DXY_MSTRUCT_TFS:
            dxy_bars = self._dxy_bars_for(dxy_tf_to_store[tf])
            if len(dxy_bars) < 5:
                continue
            dxy_res = mstruct.classify(dxy_bars)
            dxy_sdir = mstruct.structure_direction(dxy_res)
            if dxy_sdir == -direction:
                dxy_align.append(tf)
                if tf in ("W", "D") and not htf_dir:
                    htf_dir = direction
            if tf in ("240T", "60T") and mstruct.is_minor_sweep(dxy_res, -direction):
                dxy_minor_sweep = True
                minor_sweep = True

        points = 0
        if weight >= 1 or dxy_align:
            points += 1
        if htf_dir == direction:
            points += 1
        if minor_sweep:
            points += 1
        return {
            "points": points,
            "align_tfs": align,
            "htf_dir": htf_dir,
            "minor_sweep": minor_sweep,
            "ltf_intact_tf": intact_tf,
            "dxy_align": dxy_align,
            "dxy_minor_sweep": dxy_minor_sweep,
        }

    def _structure_stop(self, pair: str, direction: int, entry: float, pip: float) -> float | None:
        """Ep 12 Stage 3 — anchor the stop beyond the intact M1 INTERMEDIATE swing.

        The short-term swing (STL/STH) is what a Judas sweep takes. The intermediate
        swing (ITL/ITH) is the level that survives. Stop here = no premature exits on
        minor liquidity runs. Falls back to None when no intact intermediate swing is
        within the 10-pip universal cap (caller then uses _m1_structure_stop instead).
        """
        bars1m = self._asc(self.bars_1m[pair])
        if len(bars1m) < 5:
            return None
        bars = bars1m[-config.STRUCTURE_STOP_LOOKBACK:]
        res  = mstruct.classify(bars)
        buf  = config.M1_STOP_BUFFER_PIPS * pip
        min_dist = config.M1_STOP_MIN_PIPS * pip
        if direction > 0:
            itl = mstruct.last_intact(res, "ITL")
            if itl is None:
                return None
            stop = itl.price - buf
            if (entry - stop) < min_dist:
                stop = entry - min_dist
            return stop if stop < entry else None
        else:
            ith = mstruct.last_intact(res, "ITH")
            if ith is None:
                return None
            stop = ith.price + buf
            if (stop - entry) < min_dist:
                stop = entry + min_dist
            return stop if stop > entry else None

    # ──────────────────────────────────────────────────────────────────────────
    # Pattern detection helpers (ported from backtest.py)
    # ──────────────────────────────────────────────────────────────────────────

    def _get_limit_entry(self, bars5, bars15, bars1h, pair, direction, cur_price,
                         bars1m=None, for_pyramid=False):
        def _try(result, tag):
            if result is None:
                return None
            el, stop = result
            if direction > 0 and el >= cur_price:
                return None
            if direction < 0 and el <= cur_price:
                return None
            if tag in config.BLOCKED_ENTRY_PATTERNS:
                return None
            return el, stop, tag

        def _check_m1():
            if not bars1m:
                return None
            r = _try(self._find_fvg_entry(bars1m, pair, direction, lookback=30), "fvg_m1")
            if r: return r
            r = _try(self._find_ob_entry(bars1m, pair, direction), "ob_m1")
            if r: return r
            return _try(self._find_breaker_entry(bars1m, pair, direction), "breaker_m1")

        def _check_base():
            r = _try(self._find_fvg_entry(bars5, pair, direction, lookback=24), "fvg_m5")
            if r: return r
            r = _try(self._find_fvg_entry(bars15, pair, direction, lookback=8), "fvg_m15")
            if r: return r
            r = _try(self._find_fvg_entry(bars1h, pair, direction, lookback=4), "fvg_h1")
            if r: return r
            r = _try(self._find_ob_entry(bars5, pair, direction), "ob_m5")
            if r: return r
            r = _try(self._find_ob_entry(bars15, pair, direction), "ob_m15")
            if r: return r
            r = _try(self._find_breaker_entry(bars5, pair, direction), "breaker_m5")
            if r: return r
            r = _try(self._find_breaker_entry(bars15, pair, direction), "breaker_m15")
            if r: return r
            if bars1h:
                return _try(self._find_breaker_entry(bars1h, pair, direction), "breaker_h1")
            return None

        # Entries (initial AND pyramid) from M5/M15/H1 ONLY. M1 is not an entry
        # source — it is used solely for stop placement (_m1_structure_stop).
        result = _check_base()
        return result if result is not None else (None, None, None)

    def _m1_structure_stop(self, bars1m, direction, entry, pip):
        """Anchor the stop to the recent 1-minute swing extreme (Episode 12 STL/STH).

        LONG  → below the lowest M1 low of the move into entry, minus the buffer.
        SHORT → above the highest M1 high of the move, plus the buffer.
        Distance floored at M1_STOP_MIN_PIPS; the 10-pip cap bounds the wide side.
        Returns the stop price, or None if the extreme isn't on the correct side.
        """
        if not bars1m or len(bars1m) < 3:
            return None
        recent   = bars1m[-config.M1_STOP_LOOKBACK:]
        buf      = config.M1_STOP_BUFFER_PIPS * pip
        min_dist = config.M1_STOP_MIN_PIPS * pip
        if direction > 0:
            swing_low = min(b.Low for b in recent)
            stop = swing_low - buf
            if (entry - stop) < min_dist:
                stop = entry - min_dist
            return stop if stop < entry else None
        else:
            swing_high = max(b.High for b in recent)
            stop = swing_high + buf
            if (stop - entry) < min_dist:
                stop = entry + min_dist
            return stop if stop > entry else None

    def _find_fvg_entry(self, bars, pair, direction, lookback=24):
        pip_v   = pip_size(pair)
        min_sz  = config.FVG_MIN_SIZE_PIPS * pip_v
        n       = len(bars)
        start   = max(2, n - lookback)
        for i in range(n - 1, start - 1, -1):
            if i < 2:
                break
            c0, c1, c2 = bars[i - 2], bars[i - 1], bars[i]
            if direction > 0:
                gap = c2.Low - c0.High
                if gap < min_sz:
                    continue
                entry = c0.High
                stop  = c0.Low - pip_v
                mitigated = any(bars[j].Low <= c0.High for j in range(i + 1, n))
            else:
                gap = c0.Low - c2.High
                if gap < min_sz:
                    continue
                entry = c0.Low
                stop  = c0.High + pip_v
                mitigated = any(bars[j].High >= c0.Low for j in range(i + 1, n))
            if not mitigated:
                return entry, stop
        return None

    def _find_ob_entry(self, bars, pair, direction):
        obs = detect_order_blocks(bars)
        ob  = nearest_unmitigated_ob(obs, bars[-1].Close if bars else 0, direction)
        if ob is None:
            return None
        pip_v = pip_size(pair)
        if direction > 0:
            return ob.low, ob.low - pip_v
        else:
            return ob.high, ob.high + pip_v

    def _find_breaker_entry(self, bars, pair, direction):
        if not bars:
            return None
        zone = find_breaker_zone(bars, direction)
        if zone is None:
            return None
        pip_v = pip_size(pair)
        if direction > 0:
            return zone.low, zone.low - pip_v
        else:
            return zone.high, zone.high + pip_v

    # ──────────────────────────────────────────────────────────────────────────
    # Market profile helpers (live versions using cached opens)
    # ──────────────────────────────────────────────────────────────────────────

    def _profile_score_live(self, pair: str, direction: int, cur_price: float):
        d_op = self._daily_opens.get(pair)
        w_op = self._weekly_opens.get(pair)
        s_op = self._session_opens.get(pair)
        score = profile_score(cur_price, direction, d_op, w_op, s_op)
        return score, s_op

    def _get_weekly_amd_live(self, pair: str, bars1d: list):
        if len(bars1d) < 5:
            return None
        # Weekly AMD: detect from daily bars. We don't have a DatetimeIndex in QC
        # so we build a simple UTC-midnight based detection.
        # Use the detect_weekly_amd function with a synthetic timestamp sequence.
        try:
            import pandas as pd
            n = len(bars1d)
            # Build a DatetimeIndex from bar open times (QC QuoteBar has .Time)
            ts = pd.DatetimeIndex([
                pd.Timestamp(b.Time.year, b.Time.month, b.Time.day, tzinfo=_UTC)
                for b in bars1d
            ])
            from ict.market_profile import detect_weekly_amd
            return detect_weekly_amd(bars1d, ts, ts[-1])
        except Exception:
            return None

    # ──────────────────────────────────────────────────────────────────────────
    # Bias helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _sym_bias(self, sym, store) -> int:
        return htf_bias(self._asc(store[sym]))

    def _bias_stk(self, bars: list, lookback: int) -> int:
        return htf_bias(bars, lookback=lookback)

    def _dxy_bias_1h(self) -> int:
        rolls = {s: self._asc(self.bars_1h[s]) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        lb = config.SWING_LOOKBACK
        if n < lb + 2:
            return 0
        series = []
        for i in range(-n, 0):
            c = compute_dxy({s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS})
            o = compute_dxy({s: rolls[s][i].Open  for s in config.DXY_CONSTITUENTS})
            h, l = compute_dxy_range(
                {s: rolls[s][i].High for s in config.DXY_CONSTITUENTS},
                {s: rolls[s][i].Low  for s in config.DXY_CONSTITUENTS},
            )
            if None in (c, o, h, l):
                continue
            series.append(_SynBar(o, h, l, c))
        if len(series) < lb + 2:
            return 0
        return htf_bias(series)

    def _dxy_bias_15m(self) -> int:
        """Synthetic DXY M15 BOS bias (lookback = SWING_LOOKBACK_STH).

        Used by the breakout model's DXY confirmation leg. Mirrors the backtest's
        _dxy_bias("15T", lookback=SWING_LOOKBACK_STH): the synthetic DXY is on a
        ~100-point scale so forex-pip range detection can't apply — the M15
        structural bias is the scale-independent confirmation.
        """
        lb = config.SWING_LOOKBACK_STH
        rolls = {s: self._asc(self.bars_15m[s]) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        if n < lb + 2:
            return 0
        series = []
        for i in range(-n, 0):
            c = compute_dxy({s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS})
            o = compute_dxy({s: rolls[s][i].Open  for s in config.DXY_CONSTITUENTS})
            h, l = compute_dxy_range(
                {s: rolls[s][i].High for s in config.DXY_CONSTITUENTS},
                {s: rolls[s][i].Low  for s in config.DXY_CONSTITUENTS},
            )
            if None in (c, o, h, l):
                continue
            series.append(_SynBar(o, h, l, c))
        if len(series) < lb + 2:
            return 0
        return htf_bias(series, lookback=lb)

    def _intermarket_breakout(self) -> int:
        """Triple-confirmed intermarket breakout on M15 (live store version).

        A single-pair breakout from consolidation is usually a Judas fakeout; a
        genuine USD-driven expansion shows in all three legs at once:
          EURUSD HIGH + GBPUSD HIGH + DXY LOW  → +1 (USD weakness → look long)
          EURUSD LOW  + GBPUSD LOW  + DXY HIGH → -1 (USD strength → look short)
        Returns +1, -1, or 0. Mirrors backtest._intermarket_breakout.
        """
        if not config.BREAKOUT_MODEL_ENABLED:
            return 0
        eu = self._asc(self.bars_15m["EURUSD"])
        gu = self._asc(self.bars_15m["GBPUSD"])
        if not eu or not gu:
            return 0
        eu_brk = detect_breakout(eu, "EURUSD")
        gu_brk = detect_breakout(gu, "GBPUSD")
        if not (eu_brk and gu_brk):
            return 0
        eu_dir, gu_dir = eu_brk[1], gu_brk[1]
        dxy_dir = self._dxy_bias_15m()
        if eu_dir == +1 and gu_dir == +1 and dxy_dir == -1:
            return +1
        if eu_dir == -1 and gu_dir == -1 and dxy_dir == +1:
            return -1
        return 0

    # ──────────────────────────────────────────────────────────────────────────
    # Target finding
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _ithl_targets(bars, direction, price) -> list:
        """Unswept ITH (longs) / ITL (shorts) as primary liquidity draw targets.

        Price is drawn toward buy-side pools above unswept ITHs (longs) and
        sell-side pools below unswept ITLs (shorts). Bigger TF = stronger magnet.
        Vice versa: the intact ITL below entry is stop protection for longs;
        intact ITH above entry is stop protection for shorts (_structure_stop handles this).
        Returns (price, source_tag) tuples so confluence scoring counts ITH/ITL as
        distinct source families from plain swings.
        """
        if len(bars) < 5:
            return []
        res = mstruct.classify(bars)
        out = []
        if direction > 0:
            for s in res.get("ith", []):
                if not s.swept and s.price > price:
                    out.append((s.price, "ith_liquidity"))
        else:
            for s in res.get("itl", []):
                if not s.swept and s.price < price:
                    out.append((s.price, "itl_liquidity"))
        return out

    @staticmethod
    def _scan_htf_fvgs(bars, pair):
        """Scan bars for FVGs and mark mitigation (close-through, ICT Ep 9).

        Mirrors backtest._scan_htf_fvgs exactly.
        """
        start = max(2, len(bars) - config.HTF_FVG_SCAN_BARS)
        fvgs = []
        for i in range(start, len(bars)):
            fvg = detect_new_fvg(bars[: i + 1], pair)
            if fvg is not None:
                fvgs.append(fvg)
        for fvg in fvgs:
            for c in bars[fvg.bar_index + 1:]:
                if fvg.direction > 0 and c.Close <= fvg.bottom:
                    fvg.mitigated = True
                    break
                if fvg.direction < 0 and c.Close >= fvg.top:
                    fvg.mitigated = True
                    break
        return fvgs

    def _htf_fvg_conviction(self, pair, direction, cur_price):
        """P9 — HTF FVG 50% midpoint as draw-on-liquidity (live store version).

        Returns (points, tf_hit). Biggest TF first so the hit reflects the strongest
        draw. Used for the P9 sizing bump (breakout-anchored only).
        """
        pip_v = pip_size(pair)
        tol   = config.HTF_FVG_MID_TOLERANCE_PIPS * pip_v
        for tf, store in (("W", self.bars_1w), ("D", self.bars_1d), ("240T", self.bars_4h)):
            bars = self._asc(store[pair])
            if len(bars) < 3:
                continue
            for fvg in self._scan_htf_fvgs(bars, pair):
                if fvg.mitigated or fvg.direction != direction:
                    continue
                if abs(cur_price - fvg.mid) <= tol:
                    return 1, tf
        return 0, ""

    def _htf_crt_sweep(self, pair, direction, cur_price):
        """P19 — HTF CRT Turtle Soup sweep of prior H4/D range (live store version).

        A recent H4/D candle wicks beyond the prior 2-bar range extreme then closes
        back inside = the HTF Judas swing. Returns (points, tf_hit): D=2, H4=1.
        Mirrors backtest._htf_crt_sweep (max_bars=10 → last 10 stored bars).
        """
        if not config.CRT_SWEEP_ENABLED:
            return 0, ""
        pip_v = pip_size(pair)
        min_sweep = config.CRT_SWEEP_MIN_PIPS * pip_v
        for tf, store, points in (("D", self.bars_1d, 2), ("240T", self.bars_4h, 1)):
            bars = self._asc(store[pair])
            if len(bars) < 4:
                continue
            bars = bars[-10:]
            for i in range(len(bars) - 1, max(len(bars) - 3, 1), -1):
                sweep_bar = bars[i]
                ref_bars = bars[max(0, i - 2):i]
                if not ref_bars:
                    continue
                crt_high = max(b.High for b in ref_bars)
                crt_low  = min(b.Low  for b in ref_bars)
                if direction < 0:
                    if (sweep_bar.High >= crt_high + min_sweep
                            and sweep_bar.Close < crt_high
                            and cur_price < crt_high):
                        return points, tf
                else:
                    if (sweep_bar.Low <= crt_low - min_sweep
                            and sweep_bar.Close > crt_low
                            and cur_price > crt_low):
                        return points, tf
        return 0, ""

    @staticmethod
    def _confluence_score(candidates, target_price, tol):
        """Count distinct source families within `tol` price units of target_price."""
        seen = set()
        for price, src in candidates:
            if abs(price - target_price) <= tol:
                seen.add(src)
        return len(seen)

    def _min_pips_target(self):
        """Equity-scaled minimum target floor (mirrors backtest). OFF (default) →
        flat config.MIN_PIPS_TARGET. ON → small floor below the R3k multiplier
        threshold, large floor above. Account is ZAR so TotalPortfolioValue compares
        directly to DRAW_SIZE_MIN_EQUITY."""
        if not config.MIN_TARGET_SCALED:
            return config.MIN_PIPS_TARGET
        return (config.MIN_PIPS_TARGET_SMALL
                if self.Portfolio.TotalPortfolioValue < config.DRAW_SIZE_MIN_EQUITY
                else config.MIN_PIPS_TARGET_LARGE)

    def _find_target(self, pair, direction, cur_price):
        """Return (target_price, confluence_score) — mirrors backtest._find_target.

        Candidates are (price, source) tuples. The nearest-qualifying candidate is
        chosen (selection unchanged), then scored by how many distinct source families
        cluster within TARGET_CONFLUENCE_TOL_PIPS of it (P15/P18 sizing input).
        Returns (None, 0) when no candidate qualifies.
        """
        pip_v = pip_size(pair)
        candidates = []

        # Fibonacci extension from the initiating M15 OTE swing (100/127/162/200%).
        bars15 = self._asc(self.bars_15m[pair])
        swing = find_swing(bars15, direction, lookback=config.SWING_LOOKBACK)
        if swing is not None:
            fib_t = nearest_fib_target(
                swing[0], swing[1], direction, cur_price,
                min_distance=self._min_pips_target() * pip_v,
            )
            if fib_t is not None:
                candidates.append((fib_t, "fib_extension"))

        for store in (self.bars_4h, self.bars_1d, self.bars_1w):
            bars = self._asc(store[pair])
            if len(bars) < 5:
                continue
            candidates += self._targets_in_series(bars, pair, direction, cur_price)

        # PDH/PDL — primary buy/sell-side pools (last 3 completed daily candles).
        d_bars = self._asc(self.bars_1d[pair])
        if len(d_bars) >= 2:
            for db in d_bars[-4:-1]:
                candidates.append((db.High, "pdh_pdl"))
                candidates.append((db.Low,  "pdh_pdl"))
        # PWH/PWL — prior-week pools.
        w_bars = self._asc(self.bars_1w[pair])
        if len(w_bars) >= 2:
            candidates.append((w_bars[-2].High, "pwh_pwl"))
            candidates.append((w_bars[-2].Low,  "pwh_pwl"))

        # ITH/ITL liquidity draws from H4/D/W (P17) — full window (older majors matter).
        for store in (self.bars_4h, self.bars_1d, self.bars_1w):
            bars = self._asc(store[pair])
            candidates += self._ithl_targets(bars, direction, cur_price)

        candidates = [c for c in candidates if
                      (direction > 0 and c[0] > cur_price) or (direction < 0 and c[0] < cur_price)]
        if not candidates:
            return None, 0
        bars1h = self._asc(self.bars_1h[pair])
        dr = detect_dealing_range(bars1h, lookback=100)
        if dr is not None:
            filtered = [c for c in candidates if is_valid_target_zone(c[0], dr.high, dr.low, direction)]
            if filtered:
                candidates = filtered
        chosen = min(candidates, key=lambda x: abs(x[0] - cur_price))
        tol = config.TARGET_CONFLUENCE_TOL_PIPS * pip_v
        score = self._confluence_score(candidates, chosen[0], tol)
        return chosen[0], score

    @staticmethod
    def _targets_in_series(bars, pair, direction, price):
        """Liquidity-draw candidates as (price, source_tag) tuples.

        Mirrors backtest._targets_in_series exactly so the live confluence score
        (P15/P18 sizing) matches the backtest: fvg / ob / equal_hl / round_number /
        swing source families.
        """
        fvgs = []
        for i in range(2, len(bars)):
            g = detect_new_fvg(bars[:i+1], pair)
            if g is not None:
                fvgs.append(g)
        for g in fvgs:
            for c in bars[g.bar_index + 1:]:
                if g.direction > 0 and c.Low <= g.top:
                    g.mitigated = True; break
                if g.direction < 0 and c.High >= g.bottom:
                    g.mitigated = True; break
        out = []
        tgt = nearest_unmitigated(fvgs, price, direction)
        if tgt:
            out.append((tgt.mid, "fvg"))
        tgt_ob = nearest_unmitigated_ob(detect_order_blocks(bars), price, direction)
        if tgt_ob:
            out.append((tgt_ob.mid, "ob"))
        if direction > 0:
            out += [(h, "equal_hl") for h in find_equal_highs(bars, pair, lookback=200)]
        else:
            out += [(l, "equal_hl") for l in find_equal_lows(bars, pair, lookback=200)]
        # ICT Ep 17: round-number liquidity (x.x000/200/500/800 for 4-dec pairs).
        pip_v = pip_size(pair)
        base_pips = int(round(price / pip_v))
        base_round = (base_pips // 100) * 100
        for offset in range(-2, 6):
            for sub in (0, 20, 50, 80):
                level = (base_round + offset * 100 + sub) * pip_v
                if direction > 0 and level > price + pip_v:
                    out.append((level, "round_number"))
                elif direction < 0 and level < price - pip_v:
                    out.append((level, "round_number"))
        # Raw swing highs (BSL above) / lows (SSL below) as liquidity pools.
        n = len(bars)
        for i in range(1, n - 1):
            if direction > 0 and bars[i].High > bars[i-1].High and bars[i].High > bars[i+1].High:
                if bars[i].High > price:
                    out.append((bars[i].High, "swing"))
            elif direction < 0 and bars[i].Low < bars[i-1].Low and bars[i].Low < bars[i+1].Low:
                if bars[i].Low < price:
                    out.append((bars[i].Low, "swing"))
        return out

    # ──────────────────────────────────────────────────────────────────────────
    # Lot sizing
    # ──────────────────────────────────────────────────────────────────────────

    def _pyramid_lots(self):
        equity = self.Portfolio.TotalPortfolioValue
        for min_eq, lots in config.EQUITY_TIERS:
            if equity >= min_eq:
                return lots
        return config.EQUITY_TIERS[-1][1]

    # ──────────────────────────────────────────────────────────────────────────
    # Trade logging (ObjectStore JSON)
    # ──────────────────────────────────────────────────────────────────────────

    def _write_trade_log(self, record: dict):
        self._trade_buffer.append(record)
        # Flush every 10 records to avoid losing too much on restart
        if len(self._trade_buffer) >= 10:
            self._flush_trade_log()

    def _flush_trade_log(self):
        if not self._trade_buffer:
            return
        # Read existing log
        try:
            existing = self.ObjectStore.Read(self._trade_log_key) or ""
        except Exception:
            existing = ""
        new_lines = "\n".join(json.dumps(r, default=str) for r in self._trade_buffer)
        full = (existing + "\n" + new_lines).strip()
        try:
            self.ObjectStore.Save(self._trade_log_key, full)
        except Exception as exc:
            self.Debug(f"Trade log flush failed: {exc}")
        self._trade_buffer.clear()

    def OnEndOfAlgorithm(self):
        self._flush_trade_log()
        equity = self.Portfolio.TotalPortfolioValue
        self.Debug(f"Algorithm complete. Final equity: {equity:.2f}")

    # ──────────────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _asc(rw):
        """RollingWindow → ascending list (oldest first)."""
        out = list(rw)
        out.reverse()
        return out

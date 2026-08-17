"""Pandas-based backtester for the ICT intermarket strategy.

Fetches free 5-minute forex data from Yahoo Finance for the last ~60 days,
runs the strategy through the same `ict/` modules used by the QC version,
and reports trades + summary stats. No QuantConnect dependency.

Usage:  python backtest.py
"""

import itertools
import json
import os
import sys
from collections import namedtuple
from datetime import timedelta

import pandas as pd

import config
from ict.killzones import can_open_new_trade, current_killzone
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob, find_breaker_zone
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.bias import htf_bias
from ict import market_structure as mstruct
from ict.dxy_synthetic import compute_dxy, compute_dxy_range
from ict.amd import detect_consolidation, detect_manipulation, detect_amd_setup, detect_breakout
from ict.volume_modulator import get_volume_modifier
from ict.ote import in_ote, find_swing
from ict.liquidity_divergence import judas_sweep_divergence
from ict.fib_targets import nearest_fib_target
from ict.market_profile import (
    daily_open as mp_daily_open,
    weekly_open as mp_weekly_open,
    session_open as mp_session_open,
    nwog as mp_nwog,
    detect_weekly_amd,
    profile_score,
)
from ict.htf_draw import draw_cascade_score
from ict.dealing_range import (
    detect_dealing_range,
    is_valid_entry_zone,
    is_valid_target_zone,
    is_nfp_week_low_probability,
    is_post_fomc_low_probability,
)
from intermarket import (
    resolve as resolve_intermarket,
    resolve_pair_direction,
    resolve_gold_direction,
    resolve_index_direction,
)
from news_filter import NewsCalendar
from risk import position_size, pip_size
from trade_log import TradeLog


YF_TICKERS = {
    "GBPUSD": "GBPUSD=X",
    "EURUSD": "EURUSD=X",
    "EURGBP": "EURGBP=X",
    "USDJPY": "USDJPY=X",
    "USDCAD": "USDCAD=X",
    "USDSEK": "USDSEK=X",
    "USDCHF": "USDCHF=X",
    # NZD family — needed for the NZDUSD leg (DXY × AUDNZD cascade). Extra pairs
    # are harmless to the synthetic DXY (which uses only DXY_CONSTITUENTS).
    "NZDUSD": "NZDUSD=X",
    "AUDNZD": "AUDNZD=X",
    "AUDUSD": "AUDUSD=X",
}

Bar = namedtuple("Bar", "Open High Low Close")
SynBar = namedtuple("SynBar", "Open High Low Close")


def fetch_data(period="60d", interval="5m"):
    import yfinance as yf  # optional dep — only needed for the yfinance backtest path
    out = {}
    for name, ticker in YF_TICKERS.items():
        df = yf.download(ticker, period=period, interval=interval,
                         progress=False, auto_adjust=False)
        if df is None or df.empty:
            print(f"  WARN: no data for {name} ({ticker})")
            continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close"]].dropna()
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")
        out[name] = df
        print(f"  {name}: {len(df)} bars, {df.index.min()} -> {df.index.max()}")
    return out


def resample(df_5m, rule):
    return df_5m.resample(rule).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
    }).dropna()


def df_to_bars(df):
    return [Bar(r.Open, r.High, r.Low, r.Close) for r in df.itertuples(index=False)]


class Backtester:
    def __init__(self, data_5m):
        self.data_5m = data_5m
        self.tf_dfs = {}
        self.tf_bars = {}     # pre-built list[Bar] for fast slicing
        self.tf_index = {}    # pandas DatetimeIndex per (sym, tf) for searchsorted
        self.tf_pos = {}      # (sym, tf) -> dict[timestamp] -> position (for _bar_at)
        _tf_list = [("5T", None), ("15T", "15min"), ("60T", "60min"),
                    ("240T", "240min"), ("D", "1D"), ("W", "1W")]
        # MM cascade needs M30/M20/M10 (not in the default set). Built only when the
        # Market Maker model is on, so the default backtester is byte-identical.
        if config.MM_CONTINUATION_ENABLED:
            _tf_list += list(config.MM_EXTRA_TFS)
        for sym, df in data_5m.items():
            for tf_name, rule in _tf_list:
                d = df if rule is None else resample(df, rule)
                self.tf_dfs[(sym, tf_name)] = d
                self.tf_bars[(sym, tf_name)] = df_to_bars(d)
                self.tf_index[(sym, tf_name)] = d.index

        # P40: per-M5 tick counts for the conditional-volume modulator (optional).
        self._tickvol = self._load_tickvol() if config.USE_CONDITIONAL_VOLUME else {}

        self.equity = config.STARTING_CASH
        self.start_equity = self.equity
        self.withdrawn_total = 0.0      # cumulative profit banked (withdrawal model)
        self.withdrawal_count = 0
        self.withdrawal_events = []     # (timestamp, amount, keep_level_after)
        self._keep_level = config.WITHDRAW_KEEP   # ratchets up as profit is reinvested
        self._ceiling    = config.WITHDRAW_AT     # ceiling shifts up with the keep-level
        self._last_withdraw_date = None           # scheduled-withdrawal cadence tracker
        self._cur_loop_date = None                # run()-loop calendar-day tracker
        self._work_peak = self.equity   # peak of the WORKING balance (resets on withdrawal)
        self._max_work_dd = 0.0         # worst % drawdown seen on the working balance
        self.active = {}
        self._mm_day_dir = {}     # (pair, date) -> locked MM distribution direction
        self._mm_day_range = {}   # (pair, date) -> (dr_high, dr_low, equilibrium)
        self._mm_day_count = {}   # (pair, date) -> standalone MM entries opened today
        self.trades = []
        self.reject_log = []   # near-misses: setups that formed then hit a gate
        # Diagnostic counters: how many times each gate was reached / rejected.
        self.gate = {
            "checks": 0, "in_killzone": 0, "news_clear": 0,
            "nfp_fomc_ok": 0, "intermarket_signal": 0, "pair_matches": 0,
            "mss_h1_m15_m5_ok": 0,
            "daily_bias_ok": 0, "h1_bias_ok": 0, "h4_bias_ok": 0,
            "dealing_range_ok": 0, "consolidation_found": 0,
            "manipulation_correct_dir": 0,
            "m5_fvg_correct_dir": 0, "target_found": 0,
            "rr_ok": 0, "units_nonzero": 0, "limit_placed": 0, "entry_opened": 0,
            # pyramid counters (adds that fired vs blocked by the target-room gate)
            "pyramid_added": 0, "pyramid_blocked_min_target": 0,
            # protection counters
            "drawdown_halt": 0, "daily_loss_halt": 0, "consec_loss_pause": 0,
            # weekly/daily budget counters
            "weekly_cap": 0, "weekly_pair_cap": 0,
            "daily_cap": 0, "daily_pair_cap": 0,
            # market profile counters
            "weekly_amd_confirmed": 0, "session_handover_closed": 0,
            # HTF draw cascade counters (0-3 per trade)
            "htf_draw_full_cascade": 0, "htf_draw_partial": 0, "htf_draw_counter": 0,
            # HTF FVG 50% draw-on-liquidity conviction (P9)
            "htf_fvg_5050_hit": 0,
            # conviction signal counters
            "ote_zone": 0, "choch_confirmed": 0, "low_conviction": 0,
            "judas_divergence": 0, "ny_continuation": 0,
        }
        # Wipeout-prevention state
        self._peak_equity       = config.STARTING_CASH
        self._consec_losses     = 0
        self._day_open_eq       = {}   # date -> equity at start of that calendar day
        self._drawdown_halt_until = None  # date after which trading resumes
        # Market profile cache: (pair, date) -> profile dict (recomputed once per bar)
        self._mp_cache          = {}   # (pair, t) -> {"vwap", "vah", "val", "poc"}
        # Per-pair weekly AMD cache: updated each bar (daily resolution is enough)
        self._weekly_amd        = {}   # pair -> WeeklyAMD or None
        # HTF draw cascade cache: (pair, date) -> score; W/D/H4 draw doesn't change intraday
        self._draw_cache        = {}   # (pair, date) -> int
        # Weekly trade budget (3-of-5 pattern)
        self._week_total        = {}   # (iso_year, iso_week) -> int
        self._week_pair         = {}   # (iso_year, iso_week, pair) -> int
        self._day_total         = {}   # date -> int
        self._day_idx_total     = {}   # date -> int (separate index daily budget)
        self._day_pair          = {}   # (date, pair) -> int  — London session slot
        self._day_pair_ny       = {}   # (date, pair) -> int  — NY AM session slot
        self._day_pair_pm       = {}   # (date, pair) -> int  — NY PM session slot
        # Session-phase AMD cycle tracker: once a Judas sweep is detected for a pair
        # on a given NY date the flag stays True for the rest of that session so the
        # breakout_eligible gate knows whether the Judas already fired.
        self._judas_seen        = {}   # (pair, session_label, ny_date) -> bool  [London and NY each have independent AMD cycles]
        # P10: once a London-Open Judas reversal OPENS on a pair, flag it so the
        # same-pair NY-AM breakout that day can be sized down (it's the weaker echo).
        self._london_judas_open = {}   # (pair, ny_date) -> bool
        # P11: the day's London/DXY USD direction (DXY-wide). Set from the first
        # London-session position that opens. A NY-AM entry in this same direction is
        # a continuation of the day's move (handover consolidation → MSS → continue),
        # not a reversal — even when it "looks like a small Judas swing".
        self._london_dir = {}          # ny_date -> direction (+1/-1)

        self.news = NewsCalendar()
        for path in ("data/news_events.csv", "./data/news_events.csv"):
            try:
                with open(path, "r") as f:
                    n = self.news.load_csv(f.read())
                    print(f"  News CSV: {n} events loaded from {path}")
                    break
            except Exception:
                continue
        else:
            print("  News CSV: not found (skipping news filter)")

        self.log = TradeLog()

    def bars_up_to(self, sym, tf, t, max_bars=None):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return []
        pos = idx.searchsorted(t, side="right")
        if pos == 0:
            return []
        bars = self.tf_bars[(sym, tf)]
        if max_bars is not None:
            return bars[max(0, pos - max_bars):pos]
        return bars[:pos]

    def _bar_at(self, sym, tf, t):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return None
        try:
            pos = idx.get_loc(t)
        except KeyError:
            return None
        return self.tf_bars[(sym, tf)][pos]

    def run(self):
        if "GBPUSD" not in self.data_5m:
            raise SystemExit("GBPUSD data missing")
        timestamps = self.data_5m["GBPUSD"].index

        warmup_end = timestamps[0] + pd.Timedelta(days=5)
        total = len(timestamps)
        print(f"  Iterating {total} 5-min bars...")

        for i, t in enumerate(timestamps):
            for pair in config.PAIRS:
                self._update_orders(pair, t)
            if t < warmup_end:
                continue

            now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t

            # Scheduled income withdrawal — checked once per calendar day.
            if config.WITHDRAW_SCHEDULE and now.date() != self._cur_loop_date:
                if self._cur_loop_date is not None:
                    self._maybe_scheduled_withdraw(t)
                self._cur_loop_date = now.date()

            # Session handover runs at any EUR/GBP kill zone start.
            if can_open_new_trade(now):
                self._check_session_handover(t)

            for pair in config.PAIRS:
                if pair in self.active:
                    self._maybe_pyramid(pair, t)
                    self._mm_continuation(pair, t)
                elif can_open_new_trade(now, pair):
                    self._maybe_open(pair, t)
                    if pair not in self.active:   # base didn't open → standalone MM
                        self._mm_standalone(pair, t)

            if i % 1000 == 0 and i > 0:
                print(f"    bar {i}/{total} ({t}) - active={len(self.active)} "
                      f"trades={len(self.trades)} equity={self.equity:.0f}")

        # Close any remaining positions at last available 5m close.
        last_t = timestamps[-1]
        for pair in list(self.active.keys()):
            df = self.data_5m.get(pair)
            if df is None or df.empty:
                continue
            last_close = df.iloc[-1].Close
            self._force_close(pair, last_close, last_t, "end_of_data")

    def _update_orders(self, pair, t):
        bar = self._bar_at(pair, "5T", t)
        if bar is None:
            return

        # Position exits.
        if pair in self.active:
            st = self.active[pair]
            direction = st["direction"]
            target = st["target"]
            pip = pip_size(pair)

            # MFE (max favorable excursion) — analytics only, so the draw-ladder
            # study can ask "did price reach the 3-day / 30-day / 60-day pool?".
            _fav = bar.High if direction > 0 else bar.Low
            _mp = st.get("mfe_price")
            st["mfe_price"] = (_fav if _mp is None else
                               (max(_mp, _fav) if direction > 0 else min(_mp, _fav)))

            # Trail stop: move to BE at +TRAIL_BE_PIPS, lock +10 pips at +TRAIL_LOCK_PIPS.
            # Then (if enabled) trail behind the most recent confirmed M5 swing once
            # the trade clears STRUCTURE_TRAIL_ACTIVATE pips — the "trail off structure"
            # exit that lets winners run until an MSS breaks structure against them.
            # Load M5 bars for structure trail AND trail-at-TP ratchet.
            bars5_trail = (self.bars_up_to(pair, config.STRUCTURE_TRAIL_TF, t)
                           if (config.STRUCTURE_TRAIL or config.TRAIL_AT_TP) else None)
            for leg in st["legs"]:
                pips_profit = (bar.Close - leg["entry"]) * direction / pip
                if pips_profit >= config.TRAIL_LOCK_PIPS:
                    locked = leg["entry"] + 10 * pip * direction
                    if direction > 0:
                        leg["stop"] = max(leg["stop"], locked)
                    else:
                        leg["stop"] = min(leg["stop"], locked)
                elif pips_profit >= config.TRAIL_BE_PIPS:
                    if direction > 0:
                        leg["stop"] = max(leg["stop"], leg["entry"])
                    else:
                        leg["stop"] = min(leg["stop"], leg["entry"])

                # Milestone trailing: extends the TRAIL_LOCK step every
                # MILESTONE_TRAIL_STEP pips for long HTF-targeted trades.
                # At +40 pips → stop at entry+35; +60 → entry+55; +80 → entry+75…
                # Short trades (20-30 pip target) exit before any new milestone fires.
                if (config.MILESTONE_TRAIL_ENABLED
                        and pips_profit >= config.TRAIL_LOCK_PIPS + config.MILESTONE_TRAIL_STEP):
                    _step = config.MILESTONE_TRAIL_STEP
                    _buf  = config.MILESTONE_TRAIL_BUFFER
                    _milestone = int(pips_profit / _step) * _step
                    _lock_ms   = leg["entry"] + (_milestone - _buf) * pip * direction
                    if direction > 0:
                        leg["stop"] = max(leg["stop"], _lock_ms)
                    else:
                        leg["stop"] = min(leg["stop"], _lock_ms)

                # Structure trail: ratchet the stop to the latest M5 swing point.
                # Also runs when trail was engaged by TRAIL_AT_TP (leg["trail_engaged"]).
                _do_ratchet = (
                    (config.STRUCTURE_TRAIL and pips_profit >= config.STRUCTURE_TRAIL_ACTIVATE)
                    or (config.TRAIL_AT_TP and leg.get("trail_engaged"))
                )
                if _do_ratchet and bars5_trail:
                    s_stop = self._structure_trail_stop(bars5_trail, direction, pip)
                    if s_stop is not None:
                        if direction > 0 and s_stop > leg["stop"] and s_stop < bar.Close:
                            leg["stop"] = s_stop
                            leg["trail_engaged"] = True
                        elif direction < 0 and s_stop < leg["stop"] and s_stop > bar.Close:
                            leg["stop"] = s_stop
                            leg["trail_engaged"] = True

            for leg in list(st["legs"]):
                sl = leg["stop"]
                # Skip fixed TP when trail is engaged (either via STRUCTURE_TRAIL or TRAIL_AT_TP).
                let_run = leg.get("trail_engaged") and (
                    config.STRUCTURE_TRAIL_LET_RUN or config.TRAIL_AT_TP
                )
                if direction > 0:
                    sl_hit  = bar.Low <= sl
                    tp1_hit = (not leg.get("tp1_hit") and leg.get("tp1") is not None
                               and not sl_hit and bar.High >= leg["tp1"])
                    tp_hit  = (not let_run) and bar.High >= target
                else:
                    sl_hit  = bar.High >= sl
                    tp1_hit = (not leg.get("tp1_hit") and leg.get("tp1") is not None
                               and not sl_hit and bar.Low <= leg["tp1"])
                    tp_hit  = (not let_run) and bar.Low <= target
                if sl_hit:
                    self._exit_leg(pair, leg, sl, t, "stop")
                elif tp1_hit:
                    self._partial_exit_leg(pair, leg, leg["tp1"], t)
                    # If TP2 also hit on the same bar (big candle), close the runner
                    if pair in self.active:
                        if direction > 0 and (not let_run) and bar.High >= target:
                            self._exit_leg(pair, leg, target, t, "target")
                        elif direction < 0 and (not let_run) and bar.Low <= target:
                            self._exit_leg(pair, leg, target, t, "target")
                elif tp_hit:
                    if config.TRAIL_AT_TP:
                        # TP touched — find the M5 swing closest to TP (not nearest in
                        # time) that is above entry. Only engages when meaningful
                        # structure formed near the TP during the delivery phase.
                        trail_stop = (self._trail_stop_near_target(
                                          bars5_trail, direction, pip,
                                          leg["entry"], target)
                                      if bars5_trail else None)
                        if trail_stop is not None:
                            if direction > 0:
                                leg["stop"] = max(leg["stop"], trail_stop)
                            else:
                                leg["stop"] = min(leg["stop"], trail_stop)
                            leg["trail_engaged"] = True
                            # Do NOT exit — trail takes over from here
                        else:
                            # No qualifying swing (fast spike, no structure near TP)
                            self._exit_leg(pair, leg, target, t, "target")
                    else:
                        self._exit_leg(pair, leg, target, t, "target")
            if not self.active.get(pair, {}).get("legs"):
                self.active.pop(pair, None)


    def _exit_leg(self, pair, leg, exit_price, t, reason):
        st = self.active[pair]
        direction = st["direction"]
        # Apply exit spread friction (half-spread): you sell at bid for longs,
        # buy at ask for shorts — effective exit is worse than the mid price.
        # News trades: spread is still wide when the stop executes, so apply the
        # same NEWS_HIGH_SPREAD_PIPS used at entry (not the normal per-pair spread).
        _spread = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        if leg.get("entry_type", "").startswith("news"):
            _spread = max(_spread, config.NEWS_HIGH_SPREAD_PIPS)
        _exit_friction = (_spread / 2) * pip_size(pair)
        effective_exit = exit_price - direction * _exit_friction
        pnl_usd = (effective_exit - leg["entry"]) * leg["units"] * direction
        pnl_zar = pnl_usd * config.USD_ZAR
        self.equity += pnl_zar
        # Update peak equity and consecutive loss counter after every close.
        self._peak_equity = max(self._peak_equity, self.equity)
        self._track_working_dd()
        self._maybe_withdraw(t)         # bank profit at the ceiling (if enabled)
        if pnl_zar > 0:
            self._consec_losses = 0
        else:
            self._consec_losses += 1
        record = {
            "pair": pair, "leg_idx": leg["leg_idx"], "direction": direction,
            "entry": leg["entry"], "exit": effective_exit, "units": leg["units"],
            "stop": leg["stop"], "target": st["target"],
            "pnl": pnl_zar, "opened_at": leg["opened_at"], "closed_at": t,
            "reason": reason, "entry_type": leg.get("entry_type", "unknown"),
            "session_side": leg.get("session_side", "no_open"),
            "target_type": st.get("target_type", "unknown"),
            "draw_score": st.get("draw_score", 0),
            "im_scenario": st.get("im_scenario", "?"),
            "entry_model": st.get("entry_model", "judas"),
            "session_phase": st.get("session_phase", "unknown"),
            "profile": st.get("profile", "other"),
            "htf_fvg": st.get("htf_fvg", ""),
            "dxy_fvg_tf": st.get("dxy_fvg_tf", ""),
            "ny_cont": st.get("ny_cont", False),
            "target_confluence": st.get("target_confluence", 1),
            "mstruct_pts": st.get("mstruct_pts", 0),
            "mstruct_align": st.get("mstruct_align", ""),
            "mstruct_htf_dir": st.get("mstruct_htf_dir", 0),
            "mstruct_minor_sweep": st.get("mstruct_minor_sweep", False),
            "mstruct_intact_tf": st.get("mstruct_intact_tf", ""),
            "dxy_mstruct_align": st.get("dxy_mstruct_align", ""),
            "dxy_mstruct_sweep": st.get("dxy_mstruct_sweep", False),
            "crt_tf": st.get("crt_tf", ""),
            "nwog": st.get("nwog", ""),
            "smt_idx": st.get("smt_idx", False),
            "smt_dxy": st.get("smt_dxy", False),
            "target_escalated": st.get("target_escalated", False),
            "tp_runner": st.get("tp_runner", False),
            "tp1_price": st.get("tp1_price"),
            "soj_sweep": st.get("soj_sweep", False),
            "soj_type": st.get("soj_type", ""),
            "amd_range_pips": st.get("amd_range_pips"),
            "amd_range_bars": st.get("amd_range_bars"),
            "amd_touches_hi": st.get("amd_touches_hi"),
            "amd_touches_lo": st.get("amd_touches_lo"),
            "amd_sweep_side": st.get("amd_sweep_side", ""),
            "amd_sweep_depth": st.get("amd_sweep_depth"),
            "amd_sweep_aligned": st.get("amd_sweep_aligned"),
            "amd_accum_start": st.get("amd_accum_start"),
            "amd_accum_end": st.get("amd_accum_end"),
            "amd_sweep_time": st.get("amd_sweep_time"),
            "amd_sweep_time_m5": st.get("amd_sweep_time_m5"),
            "amd_swept_pdliq": st.get("amd_swept_pdliq"),
            "amd_entry_zone": st.get("amd_entry_zone", ""),
            "amd_liq_run": st.get("amd_liq_run", ""),
            "bond_confirm": st.get("bond_confirm", False),
            "htf_smt": st.get("htf_smt", False),
            "mm_adds": st.get("mm_adds", 0),
            "mfe_pips": round((st.get("mfe_price", leg["entry"]) - leg["entry"])
                              * direction / pip_size(pair), 1),
            "lad_sess": st.get("lad_sess"), "lad_d3": st.get("lad_d3"),
            "lad_wk": st.get("lad_wk"), "lad_d30": st.get("lad_d30"),
            "lad_d60": st.get("lad_d60"),
        }
        self.trades.append(record)
        self.log.write_trade(record, equity_after=self.equity)
        st["legs"].remove(leg)
        if not st["legs"]:
            self.active.pop(pair, None)
            self.log.delete_position(pair)
        else:
            self.log.upsert_position(pair, st)

    def _partial_exit_leg(self, pair, leg, exit_price, t):
        """Close the TP1 fraction of a leg; leave the remaining units running to TP2."""
        st        = self.active[pair]
        direction = st["direction"]
        _spread   = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        _friction = (_spread / 2) * pip_size(pair)
        eff_exit  = exit_price - direction * _friction

        units_tp1 = leg["_units_tp1"]
        pnl_usd   = (eff_exit - leg["entry"]) * units_tp1 * direction
        pnl_zar   = pnl_usd * config.USD_ZAR
        self.equity += pnl_zar
        self._peak_equity = max(self._peak_equity, self.equity)
        self._track_working_dd()
        self._maybe_withdraw(t)         # bank profit at the ceiling (if enabled)
        self._consec_losses = 0   # partial TP is a win

        record = {
            "pair": pair, "leg_idx": leg["leg_idx"], "direction": direction,
            "entry": leg["entry"], "exit": eff_exit, "units": units_tp1,
            "stop": leg["stop"], "target": st["target"],
            "pnl": pnl_zar, "opened_at": leg["opened_at"], "closed_at": t,
            "reason": "tp1_partial",
            "entry_type": leg.get("entry_type", "unknown"),
            "session_side": leg.get("session_side", "no_open"),
            "target_type": st.get("target_type", "unknown"),
            "draw_score": st.get("draw_score", 0),
            "im_scenario": st.get("im_scenario", "?"),
            "entry_model": st.get("entry_model", "judas"),
            "session_phase": st.get("session_phase", "unknown"),
            "profile": st.get("profile", "other"),
            "htf_fvg": st.get("htf_fvg", ""),
            "dxy_fvg_tf": st.get("dxy_fvg_tf", ""),
            "ny_cont": st.get("ny_cont", False),
            "target_confluence": st.get("target_confluence", 1),
            "mstruct_pts": st.get("mstruct_pts", 0),
            "mstruct_align": st.get("mstruct_align", ""),
            "mstruct_htf_dir": st.get("mstruct_htf_dir", 0),
            "mstruct_minor_sweep": st.get("mstruct_minor_sweep", False),
            "mstruct_intact_tf": st.get("mstruct_intact_tf", ""),
            "dxy_mstruct_align": st.get("dxy_mstruct_align", ""),
            "dxy_mstruct_sweep": st.get("dxy_mstruct_sweep", False),
            "crt_tf": st.get("crt_tf", ""),
            "nwog": st.get("nwog", ""),
            "smt_idx": st.get("smt_idx", False),
            "smt_dxy": st.get("smt_dxy", False),
            "target_escalated": st.get("target_escalated", False),
            "tp_runner": st.get("tp_runner", False),
            "tp1_price": st.get("tp1_price"),
            "soj_sweep": st.get("soj_sweep", False),
            "soj_type": st.get("soj_type", ""),
            "amd_range_pips": st.get("amd_range_pips"),
            "amd_range_bars": st.get("amd_range_bars"),
            "amd_touches_hi": st.get("amd_touches_hi"),
            "amd_touches_lo": st.get("amd_touches_lo"),
            "amd_sweep_side": st.get("amd_sweep_side", ""),
            "amd_sweep_depth": st.get("amd_sweep_depth"),
            "amd_sweep_aligned": st.get("amd_sweep_aligned"),
            "amd_accum_start": st.get("amd_accum_start"),
            "amd_accum_end": st.get("amd_accum_end"),
            "amd_sweep_time": st.get("amd_sweep_time"),
            "amd_sweep_time_m5": st.get("amd_sweep_time_m5"),
            "amd_swept_pdliq": st.get("amd_swept_pdliq"),
            "amd_entry_zone": st.get("amd_entry_zone", ""),
            "amd_liq_run": st.get("amd_liq_run", ""),
            "bond_confirm": st.get("bond_confirm", False),
            "htf_smt": st.get("htf_smt", False),
            "mm_adds": st.get("mm_adds", 0),
            "mfe_pips": round((st.get("mfe_price", leg["entry"]) - leg["entry"])
                              * direction / pip_size(pair), 1),
            "lad_sess": st.get("lad_sess"), "lad_d3": st.get("lad_d3"),
            "lad_wk": st.get("lad_wk"), "lad_d30": st.get("lad_d30"),
            "lad_d60": st.get("lad_d60"),
        }
        self.trades.append(record)
        self.log.write_trade(record, equity_after=self.equity)

        # Reduce to TP2 units and mark TP1 done
        leg["units"]    = leg["_units_tp2"]
        leg["tp1_hit"]  = True
        if config.SCALE_OUT_MOVE_BE or leg.get("runner_be_after_tp1"):
            if direction > 0:
                leg["stop"] = max(leg["stop"], leg["entry"])
            else:
                leg["stop"] = min(leg["stop"], leg["entry"])

    def _force_close(self, pair, price, t, reason):
        for leg in list(self.active[pair]["legs"]):
            self._exit_leg(pair, leg, price, t, reason)

    def _sym_bias(self, sym, tf, t, lookback: int = None):
        bars = self.bars_up_to(sym, tf, t)
        return htf_bias(bars, lookback=lookback)

    def _eurgbp_synthetic(self, t, lookback: int, threshold_pips: float) -> int:
        """Synthetic EURGBP bias from individual pair H1 momentum divergence.

        Compare pip change of EURUSD vs GBPUSD over `lookback` H1 bars.
        Positive divergence (EU rose more than GU) → EUR stronger → EURGBP +1.
        Negative divergence (GU rose more than EU) → GBP stronger → EURGBP -1.
        """
        eu = self.bars_up_to("EURUSD", "60T", t)
        gu = self.bars_up_to("GBPUSD", "60T", t)
        if min(len(eu), len(gu)) < lookback + 1:
            return 0
        eu_pips = (eu[-1].Close - eu[-lookback].Close) / 0.0001
        gu_pips = (gu[-1].Close - gu[-lookback].Close) / 0.0001
        divergence = eu_pips - gu_pips
        if divergence > threshold_pips:
            return +1   # EUR outperforming → synthetic EURGBP rising
        if divergence < -threshold_pips:
            return -1   # GBP outperforming → synthetic EURGBP falling
        return 0

    def _intermarket_breakout(self, t) -> int:
        """Triple-confirmed intermarket breakout on M15.

        A single-pair breakout from consolidation is usually a Judas fakeout. A
        genuine USD-driven expansion shows up in ALL THREE legs at once:

            EURUSD clears range HIGH + GBPUSD clears range HIGH + DXY clears LOW
              → USD weakness expansion → +1 (look long EURUSD/GBPUSD)
            EURUSD clears range LOW  + GBPUSD clears range LOW  + DXY clears HIGH
              → USD strength expansion → -1 (look short EURUSD/GBPUSD)

        Returns +1, -1, or 0 (no confirmed triple breakout).

        Multi-TF test history (all reverted — M15-only remains optimal):
        - v1/v2 (H1→M15 cascade, M15 params):       MaxDD -15.74%, R302M. ❌
        - v3 (D1→H4→H1→M15, M15 params):            MaxDD -18.89%, R390M. ❌
        - v4 (D1→H4→H1→M15, per-TF calibrated):     MaxDD -15.32%, R396M. ❌
        Root cause: cascade allows stale confirmations (EU confirmed on D1 hours ago,
        GU just now on M15). M15-only enforces strict simultaneity — all three must
        be showing the breakout right now on the same clock. Breakout count ballooned
        to 534–586 (vs ~130 M15-only) in every cascade variant.
        """
        if not config.BREAKOUT_MODEL_ENABLED:
            return 0

        eu = self.bars_up_to("EURUSD", "15T", t)
        gu = self.bars_up_to("GBPUSD", "15T", t)
        if not eu or not gu:
            return 0
        eu_brk = detect_breakout(eu, "EURUSD")
        gu_brk = detect_breakout(gu, "GBPUSD")
        if not (eu_brk and gu_brk):
            return 0
        eu_dir, gu_dir = eu_brk[1], gu_brk[1]
        dxy_dir = self._dxy_bias("15T", t, lookback=config.SWING_LOOKBACK_STH)
        if eu_dir == +1 and gu_dir == +1 and dxy_dir == -1:
            return +1
        if eu_dir == -1 and gu_dir == -1 and dxy_dir == +1:
            return -1
        return 0

    def _dxy_bias(self, tf, t, lookback: int = None):
        """Synthetic DXY BOS on the given timeframe. Robust to a constituent the
        broker doesn't carry (e.g. USDSEK on Exness): drops empty rolls so one
        unavailable constituent can't zero the series and flat-line the DXY gate."""
        rolls = {s: self.bars_up_to(s, tf, t) for s in config.DXY_CONSTITUENTS}
        rolls = {s: v for s, v in rolls.items() if v}      # drop unavailable
        lb = lookback if lookback is not None else config.SWING_LOOKBACK
        n = min((len(v) for v in rolls.values()), default=0)
        if n < lb + 2 or "EURUSD" not in rolls:
            return 0
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in rolls}
            high_px = {s: rolls[s][i].High for s in rolls}
            low_px = {s: rolls[s][i].Low for s in rolls}
            open_px = {s: rolls[s][i].Open for s in rolls}
            c = compute_dxy(close_px)
            o = compute_dxy(open_px)
            h, l = compute_dxy_range(high_px, low_px)
            if None in (c, o, h, l):
                continue
            series.append(SynBar(o, h, l, c))
        if len(series) < lb + 2:
            return 0
        return htf_bias(series, lookback=lb)

    def _dxy_bias_1h(self, t, lookback: int = None):
        return self._dxy_bias("60T", t, lookback=lookback)

    def _dxy_bars(self, tf, t):
        """Synthetic DXY bar series for the given timeframe (list of SynBar). Robust
        to an unavailable constituent (drops empty rolls) — same as _dxy_bias."""
        rolls = {s: self.bars_up_to(s, tf, t) for s in config.DXY_CONSTITUENTS}
        rolls = {s: v for s, v in rolls.items() if v}      # drop unavailable
        n = min((len(v) for v in rolls.values()), default=0)
        if n < 2 or "EURUSD" not in rolls:
            return []
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in rolls}
            high_px  = {s: rolls[s][i].High  for s in rolls}
            low_px   = {s: rolls[s][i].Low   for s in rolls}
            open_px  = {s: rolls[s][i].Open  for s in rolls}
            c = compute_dxy(close_px)
            o = compute_dxy(open_px)
            h, l = compute_dxy_range(high_px, low_px)
            if None in (c, o, h, l):
                continue
            series.append(SynBar(o, h, l, c))
        return series

    def _size_equity(self):
        """Equity used for POSITION SIZING. Under the withdrawal (income) model, cap at
        the working base (keep_level) so positions scale with WORKING capital — not the
        un-withdrawn profit sitting in the account. When the account is rarely flat,
        withdrawals fire seldom and raw equity compounds huge; sizing on that produces
        enormous positions that blow the account negative on a single loss. Capping at
        keep_level keeps the account small and un-blowuppable — the point of an income
        model. No-op when withdrawals are OFF (returns raw equity → byte-identical)."""
        if config.WITHDRAW_SCHEDULE or config.WITHDRAW_AT > 0:
            # Cap at the FIXED initial base (WITHDRAW_KEEP), NOT the growing keep_level:
            # the reinvest-30% compounds keep_level, and tying sizing to it re-created
            # the equity-proportional feedback that blows the account up. A fixed base
            # keeps positions small forever; the account climbs in BANKED profit, not
            # position size. Scales DOWN in a drawdown (min with live equity).
            base = config.WITHDRAW_KEEP or config.STARTING_CASH
            return max(0.0, min(self.equity, base))
        return self.equity

    def _pyramid_lots(self):
        """Return (leg1, leg2, leg3) lot sizes for the current equity tier. Uses
        _size_equity() so the tier reflects WORKING capital under the income model
        (byte-identical to raw equity when withdrawals are off). LOT_OVERRIDE>0 forces
        a fixed base lot past the tier (the max-risk-per-trade guard still applies)."""
        # drawdown de-risk: below the floor, cap the base lot (protective step-down)
        if config.DERISK_BELOW_ZAR > 0 and self._size_equity() < config.DERISK_BELOW_ZAR:
            dl = config.DERISK_LOT
            return (dl, dl, dl)
        if config.LOT_OVERRIDE > 0:
            lo = config.LOT_OVERRIDE
            return (lo, lo, lo)
        eq = self._size_equity()
        for min_eq, lots in config.EQUITY_TIERS:
            if eq >= min_eq:
                return lots
        return config.EQUITY_TIERS[-1][1]

    def _maybe_scheduled_withdraw(self, t):
        """Calendar-cadence income withdrawal. Frequency steps up as the working
        base grows: monthly while small, twice a month past WITHDRAW_BIWEEKLY_AT,
        weekly past WITHDRAW_WEEKLY_AT. Each due date banks WITHDRAW_FRACTION of the
        profit above the keep-level and reinvests the rest (base compounds, so the
        cadence can climb). Called once per calendar day from run()."""
        if not config.WITHDRAW_SCHEDULE:
            return
        if self.active:
            return   # only bank realized profit when FLAT (see _maybe_withdraw) —
                     # resetting equity under an open position sized on the larger
                     # pre-reset equity causes a negative blow-up when it closes.
        d = t.date() if hasattr(t, "date") else t
        if self._last_withdraw_date is None:
            self._last_withdraw_date = d
            return
        # R10k-band cadence: each additional band shortens the interval (more
        # frequent) — monthly at band 1, biweekly at band 2, ~10d at band 3,
        # floored at weekly. Amount grows too (fraction of a bigger base).
        band = max(1, int(self.equity // config.WITHDRAW_BAND))
        interval = max(config.WITHDRAW_WEEKLY_DAYS,
                       round(config.WITHDRAW_MONTHLY_DAYS / band))
        if (d - self._last_withdraw_date).days < interval:
            return
        self._last_withdraw_date = d
        if self.equity <= self._keep_level:
            return                              # no profit to draw this period
        excess   = self.equity - self._keep_level
        withdraw = excess * config.WITHDRAW_FRACTION
        reinvest = excess - withdraw
        self.withdrawn_total += withdraw
        self.withdrawal_count += 1
        self.withdrawal_events.append((t, withdraw, self._keep_level + reinvest))
        self._keep_level += reinvest            # compound the reinvested part
        self.equity = self._keep_level
        self._peak_equity = self.equity         # cash-out is not a drawdown
        self._work_peak = self.equity

    def _track_working_dd(self):
        """Track the worst % drawdown on the WORKING balance (the number you'd see
        in the real account each base->ceiling cycle). Called after every close,
        before any withdrawal; the peak resets on withdrawal so a cash-out is not
        counted as a drawdown."""
        self._work_peak = max(self._work_peak, self.equity)
        if self._work_peak > 0:
            d = (self._work_peak - self.equity) / self._work_peak * 100
            if d > self._max_work_dd:
                self._max_work_dd = d

    def _maybe_withdraw(self, t=None):
        """Profit withdrawal at the ceiling. Of the profit above the keep-level,
        WITHDRAW_FRACTION is banked (income) and the rest is REINVESTED — the
        keep-level and ceiling both ratchet up by the reinvested amount, so the
        working base compounds while you still draw income. FRACTION=1.0 reduces to
        the fixed-base model (bank all above keep). Keeps the account realistic (no
        runaway compounding). Peak-equity resets so a cash-out isn't seen as a loss;
        summarize() MaxDD is on the total-value curve (withdrawal-neutral)."""
        if config.WITHDRAW_SCHEDULE:
            return   # scheduled (calendar) mode owns withdrawals
        if config.WITHDRAW_AT <= 0:
            return
        if self.active:
            return   # only bank realized profit when FLAT — resetting equity while a
                     # position sized on the pre-reset (larger) equity is open makes its
                     # eventual loss dwarf the reset balance → negative blow-up.
        if self.equity >= self._ceiling and self.equity > self._keep_level:
            excess   = self.equity - self._keep_level
            withdraw = excess * config.WITHDRAW_FRACTION
            reinvest = excess - withdraw
            self.withdrawn_total += withdraw
            self.withdrawal_count += 1
            self.withdrawal_events.append((t, withdraw, self._keep_level + reinvest))
            self._keep_level += reinvest        # compound the reinvested part
            self._ceiling    += reinvest        # shift the band up with the base
            self.equity = self._keep_level
            self._peak_equity = self.equity     # cash-out is not a drawdown
            self._work_peak = self.equity       # new cycle starts from the keep level

    def _amd_max_range(self, pair, price=None):
        """AMD consolidation-range cap (in pips) for this pair. Indices are
        point-priced, so the FX 35-pip cap reads as 35 points and starves the
        index Judas path. For index pairs: a %-of-price cap (auto-scales US500 vs
        US100) if set, else a fixed-point cap, else the FX global."""
        if config.INDICES_ENABLED and pair in config.INDEX_PAIRS:
            if config.INDEX_AMD_MAX_RANGE_PCT > 0 and price:
                return (price * config.INDEX_AMD_MAX_RANGE_PCT / 100.0) / pip_size(pair)
            if config.INDEX_AMD_MAX_RANGE_PIPS > 0:
                return config.INDEX_AMD_MAX_RANGE_PIPS
        return config.AMD_MAX_RANGE_PIPS

    def _is_point_instrument(self, pair):
        """True for point-based (non-FX) instruments — gold and the US indices.
        These are dollar/point priced, so they use their own contract size,
        structural-only stops (no fixed-pip cap/news override), and pip units."""
        return ((config.GOLD_ENABLED and pair == config.GOLD_PAIR)
                or (config.INDICES_ENABLED and pair in config.INDEX_PAIRS))

    def _contract_units(self, pair):
        """Units per 1.0 lot for this symbol. Gold (100 oz) and the indices are
        ~1000x smaller than the FX 100k-unit lot AND move in dollars/points, so the
        min-lot floor must use their contract or the position is grossly oversized.
        FX pairs keep config.LOT_UNITS (byte-identical baseline)."""
        if config.GOLD_ENABLED and pair == config.GOLD_PAIR:
            return config.GOLD_LOT_UNITS
        if config.INDICES_ENABLED and pair in config.INDEX_PAIRS:
            return config.INDEX_LOT_UNITS
        return config.LOT_UNITS

    # ------------------------------------------------------------------
    # Market profile helpers
    # ------------------------------------------------------------------

    def _daily_open(self, pair: str, t) -> float | None:
        bars = self.tf_bars.get((pair, "60T"), [])
        ts   = self.tf_index.get((pair, "60T"))
        if ts is None or not bars:
            return None
        return mp_daily_open(bars, ts, t)

    def _weekly_open(self, pair: str, t) -> float | None:
        bars = self.tf_bars.get((pair, "D"), [])
        ts   = self.tf_index.get((pair, "D"))
        if ts is None or not bars:
            return None
        return mp_weekly_open(bars, ts, t)

    def _session_open(self, pair: str, sess_name: str, t) -> float | None:
        bars = self.tf_bars.get((pair, "5T"), [])
        ts   = self.tf_index.get((pair, "5T"))
        if ts is None or not bars:
            return None
        return mp_session_open(bars, ts, sess_name, t)

    def _nwog(self, pair: str, t):
        """New Week Opening Gap for this pair/week: (lo, hi, ce, gap_dir) or None."""
        bars = self.tf_bars.get((pair, "D"), [])
        ts   = self.tf_index.get((pair, "D"))
        if ts is None or not bars:
            return None
        return mp_nwog(bars, ts, t)

    def _index_smt(self, pair, direction, t):
        """Precise ICT SMT divergence for an index trade — TWO independent reads:
          1. index-vs-index: primary vs the sibling index and US30 (POSITIVE
             correlation — the classic ES/NQ/YM divergence).
          2. index-vs-dollar: primary vs DXY (INVERSE correlation — indices move
             opposite the dollar, so the dollar failing to confirm is divergence).
        Returns {points, idx_smt, dxy_smt}. Only meaningful for index pairs."""
        out = {"points": 0, "idx_smt": False, "dxy_smt": False}
        if not (config.INDICES_ENABLED and pair in config.INDEX_PAIRS):
            return out
        from ict.smt import smt_divergence, smt_divergence_fractal
        # Pick the detector: "fractal" = reactive fractal-swing alignment (fires at
        # the real pivot when fresh); "proxy" = block-half window (default).
        if config.SMT_MODE == "fractal":
            lb = config.SMT_FRACTAL_LOOKBACK
            _diverges = lambda p, r, inv: smt_divergence_fractal(
                p, r, direction, inverse=inv, lookback=lb,
                max_age=config.SMT_FRACTAL_MAX_AGE)
        else:
            lb = config.SMT_LOOKBACK
            _diverges = lambda p, r, inv: smt_divergence(
                p, r, direction, inverse=inv, lookback=lb)
        tf = config.SMT_TF
        prim = self.bars_up_to(pair, tf, t)
        if len(prim) < lb:
            return out
        # 1. index-vs-index (positive corr): any correlated index diverging.
        refs = [p for p in config.INDEX_PAIRS if p != pair] + [config.INDEX_REF]
        for rsym in refs:
            rb = self.bars_up_to(rsym, tf, t)
            if len(rb) >= lb and _diverges(prim, rb, False):
                out["idx_smt"] = True
                break
        # 2. index-vs-dollar (inverse corr).
        dxy_bars = self._dxy_bars(tf, t)
        if len(dxy_bars) >= lb and _diverges(prim, dxy_bars, True):
            out["dxy_smt"] = True
        out["points"] = (config.SMT_CONVICTION_PTS if out["idx_smt"] else 0) \
            + (config.SMT_CONVICTION_PTS if out["dxy_smt"] else 0)
        return out

    def _nwog_conviction(self, pair, direction, cur_price, t):
        """NWOG PD-array conviction (mirror of _htf_fvg_conviction).

        +NWOG_CONVICTION_PTS when price is sitting within NWOG_MID_TOLERANCE_PIPS
        of the gap's 50% (consequent encroachment) AND the gap polarity agrees
        with the trade (gap-up NWOG supports longs; gap-down supports shorts) —
        i.e. price is delivering into the weekend-gap equilibrium in our
        direction. Returns (points, tag) with tag "NWOG" when it fires."""
        if not config.NWOG_ENABLED:
            return 0, ""
        g = self._nwog(pair, t)
        if g is None:
            return 0, ""
        lo, hi, ce, gap_dir = g
        if gap_dir != direction:
            return 0, ""
        tol = config.NWOG_MID_TOLERANCE_PIPS * pip_size(pair)
        if abs(cur_price - ce) <= tol:
            return config.NWOG_CONVICTION_PTS, "NWOG"
        return 0, ""

    def _session_open_judas_sweep(self, pair: str, direction: int,
                                   session_open_price: float, t,
                                   daily_open_price: float | None = None) -> int:
        """P26: Session-open + daily-open pattern detection. Returns conviction points (0–2).

        Checks BOTH the session open (London 03:00 / NY 07:00 ET) and the daily open
        (00:00 UTC) as institutional AMD equilibrium references.

        For each reference price, two patterns are checked:

        Judas sweep (+1 per reference): price swept ≥ SWEEP_SOJ_MIN_PIPS through the
          reference in the manipulation direction then closed back on the distribution side.
          Long : any Low  < ref − 3 pips  AND  close > ref.
          Short: any High > ref + 3 pips  AND  close < ref.

        Pullback retest (+1 per reference): price first extended ≥ SOJ_EXTEND_MIN_PIPS
          in the trade direction from the reference, then pulled back to within
          SOJ_RETEST_TOL_PIPS of it.
          Long : any High > ref + 8 pips  AND  ref − 5 pips ≤ close ≤ ref + 5 pips.
          Short: any Low  < ref − 8 pips  AND  ref − 5 pips ≤ close ≤ ref + 5 pips.

        Points are capped at 1 per reference (either Judas or retest fires — both
        detecting on the same reference only counts once). Max total = 2 points
        (session open + daily open each contributing 1). The type stored in soj_type
        reflects the strongest signal across both references.
        """
        bars = self.bars_up_to(pair, "5T", t)
        if not bars or len(bars) < 3:
            return 0
        pip = 0.0001
        min_sweep  = config.SWEEP_SOJ_MIN_PIPS  * pip
        min_extend = config.SOJ_EXTEND_MIN_PIPS * pip
        retest_tol = config.SOJ_RETEST_TOL_PIPS * pip
        last = bars[-1]
        lookback = min(config.SOJ_LOOKBACK_BARS, len(bars) - 1)
        sess_bars = bars[-lookback:]
        points = 0

        def _check_ref(ref_price: float) -> bool:
            """Return True if Judas or pullback retest fires for this reference price."""
            if direction > 0:
                judas = (any(b.Low < ref_price - min_sweep for b in sess_bars)
                         and last.Close > ref_price)
                retest = (any(b.High > ref_price + min_extend for b in sess_bars)
                          and ref_price - retest_tol <= last.Close <= ref_price + retest_tol
                          and last.Close >= ref_price - pip)
            else:
                judas = (any(b.High > ref_price + min_sweep for b in sess_bars)
                         and last.Close < ref_price)
                retest = (any(b.Low < ref_price - min_extend for b in sess_bars)
                          and ref_price - retest_tol <= last.Close <= ref_price + retest_tol
                          and last.Close <= ref_price + pip)
            return judas or retest

        if _check_ref(session_open_price):
            points += 1
        if daily_open_price is not None and abs(daily_open_price - session_open_price) > 2 * pip:
            if _check_ref(daily_open_price):
                points += 1
        return points

    def _get_weekly_amd(self, pair: str, t) -> object | None:
        """Cached weekly AMD for this bar (recomputed at most once per bar per pair)."""
        bars = self.tf_bars.get((pair, "D"), [])
        ts   = self.tf_index.get((pair, "D"))
        if ts is None or not bars:
            self._weekly_amd[pair] = None
            return None
        self._weekly_amd[pair] = detect_weekly_amd(bars, ts, t)
        return self._weekly_amd[pair]

    def _market_profile(self, pair: str, t) -> dict | None:
        """Prior-day range structure: PDH, PDL, PDM, VAH, VAL.

        ICT uses PDH/PDL as the key premium/discount reference for the next day.
        Price below PDM = discount zone (buy bias); above PDM = premium (sell bias).
        VAH/VAL are the 85th/15th percentile of the prior day's typical price —
        the inner 70% zone where price spent most of the day.
        Cached per (pair, date) since prior-day values don't change intraday.
        """
        cache_key = (pair, t.date())
        cached = self._mp_cache.get(cache_key)
        if cached is not None:
            return cached

        df = self.tf_dfs.get((pair, "5T"))
        if df is None:
            self._mp_cache[cache_key] = None
            return None

        today_start    = t.replace(hour=0, minute=0, second=0, microsecond=0)
        prev_day_start = today_start - pd.Timedelta(days=1)
        prev_day_end   = today_start - pd.Timedelta(microseconds=1)
        try:
            prev_df = df.loc[prev_day_start:prev_day_end]
        except Exception:
            self._mp_cache[cache_key] = None
            return None

        if len(prev_df) < 50:
            self._mp_cache[cache_key] = None
            return None

        pdh = float(prev_df["High"].max())
        pdl = float(prev_df["Low"].min())
        pdm = (pdh + pdl) / 2.0
        typical = (prev_df["High"] + prev_df["Low"] + prev_df["Close"]) / 3
        vah = float(typical.quantile(0.85))
        val = float(typical.quantile(0.15))

        result = {"pdh": pdh, "pdl": pdl, "pdm": pdm, "vah": vah, "val": val}
        self._mp_cache[cache_key] = result
        return result

    def _classify_liq_run(self, swept_lvl, side, mp, pair, t, bars15, pip):
        """Which major liquidity pool the manipulation swept — the swept extreme is
        within 5 pips of it. Priority (most significant first): weekly PWH/PWL >
        daily PDH/PDL > engineered equal highs/lows > value-area VAH/VAL > none.
        Widens the PDH/PDL-only flag so we can rank which liquidity runs pay."""
        tol = 5 * pip

        def near(lvl):
            return abs(swept_lvl - lvl) <= tol

        w = self.bars_up_to(pair, "W", t)
        if len(w) >= 2:
            if side == "high" and near(w[-2].High):
                return "pwh"
            if side == "low" and near(w[-2].Low):
                return "pwl"
        if side == "high" and near(mp["pdh"]):
            return "pdh"
        if side == "low" and near(mp["pdl"]):
            return "pdl"
        if side == "high":
            if any(near(h) for h in find_equal_highs(bars15, pair)):
                return "eqh"
        elif any(near(l) for l in find_equal_lows(bars15, pair)):
            return "eql"
        if near(mp["vah"]):
            return "vah"
        if near(mp["val"]):
            return "val"
        return "none"

    def _prev_session_hl(self, pair, t, direction):
        """High (long) / low (short) of the PREVIOUS completed ET session block.
        Blocks are 8h: Asian 17:00-01:00, London 01:00-09:00, NY 09:00-17:00 ET.
        Analytics-only, no lookahead — only bars strictly before t are used."""
        df = self.tf_dfs.get((pair, "5T"))
        if df is None or len(df) == 0:
            return None
        ts = pd.Timestamp(t)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        cur = ts.tz_convert("America/New_York")
        day = cur.normalize()
        h = cur.hour
        if h >= 17:
            bs = day + pd.Timedelta(hours=17)
        elif h >= 9:
            bs = day + pd.Timedelta(hours=9)
        elif h >= 1:
            bs = day + pd.Timedelta(hours=1)
        else:
            bs = day - pd.Timedelta(hours=7)          # yesterday 17:00 ET
        ps, pe = bs - pd.Timedelta(hours=8), bs        # previous block window
        et_idx = df.index.tz_convert("America/New_York")
        mask = (et_idx >= ps) & (et_idx < pe) & (df.index < ts)
        seg = df[mask]
        if len(seg) == 0:
            return None
        return float(seg["High"].max()) if direction > 0 else float(seg["Low"].min())

    def _draw_ladder(self, pair, direction, price, t):
        """Distance (pips) to the nearest UNSWEPT draw ahead at each liquidity rung,
        in the trade direction — the ICT draw-on-liquidity ladder. None when the
        rung's level is behind price (already taken) or unavailable. Analytics-only."""
        pip = pip_size(pair)

        def ahead(level):
            if level is None:
                return None
            d = (level - price) * direction
            return round(d / pip, 1) if d > 0 else None

        def ext(bars):
            if not bars:
                return None
            return max(b.High for b in bars) if direction > 0 else min(b.Low for b in bars)

        d = self.bars_up_to(pair, "D", t)
        w = self.bars_up_to(pair, "W", t)
        wk_lvl = (w[-2].High if direction > 0 else w[-2].Low) if len(w) >= 2 else None
        return {
            "lad_sess": ahead(self._prev_session_hl(pair, t, direction)),
            "lad_d3":   ahead(ext(d[-3:]))  if len(d) >= 3  else None,
            "lad_wk":   ahead(wk_lvl),
            "lad_d30":  ahead(ext(d[-30:])) if len(d) >= 30 else None,
            "lad_d60":  ahead(ext(d[-60:])) if len(d) >= 60 else None,
        }

    def _min_pips_target(self):
        """Equity-scaled minimum target floor. Below the R3k multiplier threshold
        a smaller floor hits more often (compounding fuel for the small account);
        at/above it a larger floor gives higher PF + lower DD. When scaling is off
        (default) returns the flat config.MIN_PIPS_TARGET — byte-identical to shipped."""
        if not config.MIN_TARGET_SCALED:
            return config.MIN_PIPS_TARGET
        return (config.MIN_PIPS_TARGET_SMALL if self.equity < config.DRAW_SIZE_MIN_EQUITY
                else config.MIN_PIPS_TARGET_LARGE)

    def _log_reject(self, t, pair, direction, reason):
        """Record a would-be setup that formed (passed the earlier gates) but was
        blocked by a later gate — the 'trades that couldn't be taken'."""
        self.reject_log.append({"t": t, "pair": pair, "direction": direction,
                                "reason": reason})

    @staticmethod
    def _load_tickvol():
        """P40: load per-M5 tick counts from data/p39_agg/*_m5.csv, if present.
        Returns {pair: {bin_utc: ticks}} — empty if the aggregation isn't there."""
        import glob as _g
        import csv as _csv
        agg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "p39_agg")
        out = {}
        for p in _g.glob(os.path.join(agg, "*_m5.csv")):
            pair = os.path.basename(p).split("_")[0]
            d = out.setdefault(pair, {})
            try:
                with open(p) as f:
                    for r in _csv.DictReader(f):
                        d[int(r["bin_utc"])] = int(r["ticks"])
            except (OSError, ValueError, KeyError):
                continue
        return out

    def _entry_friction(self, pair, t):
        """Entry-bar tick friction = ticks in the entry M5 bin / mean of the prior
        20 bins. None when tick volume is unavailable for this pair/time."""
        tv = getattr(self, "_tickvol", None)
        s = tv.get(pair) if tv else None
        if not s:
            return None
        ts = int(pd.Timestamp(t).timestamp())
        eb = ts - ts % 300
        if eb not in s:
            return None
        prior = [s[eb - i * 300] for i in range(1, 21) if (eb - i * 300) in s]
        if len(prior) < 8:
            return None
        base = sum(prior) / len(prior)
        return (s[eb] / base) if base > 0 else None

    def _profile_score(self, pair: str, direction: int, cur_price: float, t):
        """Return (score, session_open_price).

        score: how many open levels (daily, weekly, session) agree with direction (0-3).
        session_open_price: the killzone open price (or None) — returned so callers can
        reuse it for conviction/analytics without a second mp_session_open call.
        """
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        import pytz
        ny = pytz.timezone("America/New_York")
        ny_dt = now.astimezone(ny)
        h = ny_dt.hour
        sess = "London Open" if 2 <= h < 5 else ("New York AM" if 7 <= h < 10 else None)
        d_op = self._daily_open(pair, t)
        w_op = self._weekly_open(pair, t)
        s_op = self._session_open(pair, sess, t) if sess else None
        return profile_score(cur_price, direction, d_op, w_op, s_op), s_op

    def _check_session_handover(self, t):
        """At kill zone open: close any position that is losing AND fights the weekly AMD.

        The weekly distribution run defines the multi-day directional bias. A
        position entered in a prior session that is now underwater AND against the
        confirmed weekly AMD should be closed rather than waiting for a 10-pip stop.
        The current session's entry logic will then open fresh in the correct direction.
        """
        if not config.SESSION_HANDOVER_CLOSE:
            return

        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        import pytz
        ny = pytz.timezone("America/New_York")
        ny_dt = now.astimezone(ny)
        h, m = ny_dt.hour, ny_dt.minute

        # Only fire at kill zone boundaries: exactly 02:00 or 07:00 ET (±5 min)
        is_kz_open = (h == 2 and m <= 5) or (h == 7 and m <= 5)
        if not is_kz_open:
            return

        for pair in list(self.active.keys()):
            if self._handover_exempt(pair):
                continue  # trader's /hold — let it run across the session boundary
            st = self.active[pair]
            wamd = self._get_weekly_amd(pair, t)
            if wamd is None:
                continue  # no confirmed weekly AMD — don't interfere
            if wamd.direction == st["direction"]:
                continue  # position agrees with weekly profile — leave it

            # Position is fighting the weekly AMD.
            # Get current price to determine if the position is losing.
            m5_bar = self._bar_at(pair, "5T", t)
            if m5_bar is None:
                continue
            cur_price = m5_bar.Close
            pip = pip_size(pair)
            first_entry = st["legs"][0]["entry"]
            pips_profit = (cur_price - first_entry) * st["direction"] / pip

            if pips_profit < 0:
                # Losing and fighting weekly AMD → close all legs at market.
                self._force_close(pair, cur_price, t, "session_handover")
                self.gate["session_handover_closed"] += 1

    def _choch_score(self, pair: str, direction: int, t) -> int:
        """Return 1 if a CHoCH (Change of Character) just fired on M15.

        CHoCH = the most recent swing BOS is OPPOSITE to the prior window's bias,
        confirming a reversal. This is the first BOS in the new direction after
        a sustained move in the opposite direction — the highest-conviction entry.
        """
        bars15 = self.bars_up_to(pair, "15T", t)
        lb = config.SWING_LOOKBACK_STH
        if len(bars15) < lb * 3 + 2:
            return 0
        prior_bias   = htf_bias(bars15[:-lb], lookback=lb)
        current_bias = htf_bias(bars15,       lookback=lb)
        if prior_bias == -direction and current_bias == direction:
            return 1
        return 0

    def _pair_has_mss(self, sym, t, direction):
        """Ep 12 STH tier: M15 or M5 BOS in `direction`. H1 excluded — daily M15
        liquidity sweeps are more frequent and the primary entry timeframe."""
        for tf in ("15T", "5T"):
            if self._sym_bias(sym, tf, t, lookback=config.SWING_LOOKBACK_STH) == direction:
                return True
        return False

    def _dxy_has_mss(self, t, direction):
        """Synthetic DXY M15/M5 BOS — same STH-tier focus as _pair_has_mss."""
        for tf in ("15T", "5T"):
            if self._dxy_bias(tf, t, lookback=config.SWING_LOOKBACK_STH) == direction:
                return True
        return False

    def _find_fvg_entry(self, bars, pair, direction, lookback=24):
        """Scan backwards for the nearest unmitigated FVG in `direction`.

        Entry  = fvg.top  (longs)  / fvg.bottom (shorts): where price touches to fill.
        Stop   = c0.Low   (longs)  / c0.High   (shorts): first candle's extreme (ICT rule).
        Returns (entry, stop) or None.
        """
        pip_v = pip_size(pair)
        min_sz = config.FVG_MIN_SIZE_PIPS * pip_v
        n = len(bars)
        start = max(2, n - lookback)
        for i in range(n - 1, start - 1, -1):
            if i < 2:
                break
            c0, _, c2 = bars[i - 2], bars[i - 1], bars[i]
            if direction > 0:
                if c2.Low > c0.High and (c2.Low - c0.High) >= min_sz:
                    # Unmitigated: no close below gap bottom (c0.High) after formation
                    if not any(bars[j].Close < c0.High for j in range(i + 1, n)):
                        entry, stop = c2.Low, c0.Low
                        if stop < entry:
                            return entry, stop
            else:
                if c2.High < c0.Low and (c0.Low - c2.High) >= min_sz:
                    if not any(bars[j].Close > c0.Low for j in range(i + 1, n)):
                        entry, stop = c2.High, c0.High
                        if stop > entry:
                            return entry, stop
        return None

    def _find_ob_entry(self, bars, pair, direction):
        """Find the nearest unmitigated OB body level for a limit-touch entry.

        Bullish OB: OB is below current price; entry at ob.body_top on retrace.
        Bearish OB: OB is above current price; entry at ob.body_bottom on retrace.
        Returns (entry, stop) or None.
        """
        obs = detect_order_blocks(bars, lookback=50)
        cur_price = bars[-1].Close
        pip = pip_size(pair)
        valid = []
        for ob in obs:
            if ob.mitigated or ob.direction != direction:
                continue
            if direction > 0 and ob.body_top < cur_price:
                entry, stop = ob.body_top, ob.bottom - pip
                if stop < entry:
                    valid.append((entry, stop))
            elif direction < 0 and ob.body_bottom > cur_price:
                entry, stop = ob.body_bottom, ob.top + pip
                if stop > entry:
                    valid.append((entry, stop))
        if not valid:
            return None
        return min(valid, key=lambda x: abs(x[0] - cur_price))

    def _find_breaker_entry(self, bars, pair, direction):
        """Return (entry, stop) if a breaker block is present, else None.

        Bullish breaker: old bearish OB broken upward; price pulls back into its
        body zone → entry at ob.body_bottom, stop one pip below ob.bottom.
        Bearish breaker: old bullish OB broken downward; price rallies into
        its body zone → entry at ob.body_top, stop one pip above ob.top.
        """
        cur_price = bars[-1].Close
        pip = pip_size(pair)
        ob = find_breaker_zone(bars, direction, cur_price, pip)
        if ob is None:
            return None
        if direction > 0:
            entry = ob.body_bottom
            stop  = ob.bottom - pip
        else:
            entry = ob.body_top
            stop  = ob.top + pip
        if direction > 0 and stop >= entry:
            return None
        if direction < 0 and stop <= entry:
            return None
        return entry, stop

    def _get_limit_entry(self, bars5, bars15, bars1h, pair, direction, cur_price,
                         bars1m=None, for_pyramid=False):
        """Return (pattern_level, stop, pattern_tag) for an ICT counter-trend entry.

        Confirms a valid pattern exists counter-trend to cur_price:
          LONG:  pattern_level < cur_price  (price still falling toward it)
          SHORT: pattern_level > cur_price  (price still rising toward it)

        pattern_level is discarded by the caller — market order fills at cur_price.
        stop is the pattern's invalidation level (OB/FVG boundary).

        for_pyramid=True: M1 patterns first (tightest current level for adds).
        for_pyramid=False: M1 patterns last (fallback; initial entries prefer HTF).

        Pattern functions are called LAZILY — stops at first valid match.
        """
        def _valid(result, tag):
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

        def _try(result, tag):
            """Return (el, stop, tag) if valid and counter-trend, else None."""
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
            r = _try(self._find_fvg_entry(bars5,  pair, direction, lookback=24), "fvg_m5");
            if r: return r
            r = _try(self._find_fvg_entry(bars15, pair, direction, lookback=8),  "fvg_m15");
            if r: return r
            r = _try(self._find_fvg_entry(bars1h, pair, direction, lookback=4),  "fvg_h1");
            if r: return r
            r = _try(self._find_ob_entry(bars5,   pair, direction),              "ob_m5");
            if r: return r
            r = _try(self._find_ob_entry(bars15,  pair, direction),              "ob_m15");
            if r: return r
            r = _try(self._find_breaker_entry(bars5,  pair, direction),          "breaker_m5")
            if r: return r
            r = _try(self._find_breaker_entry(bars15, pair, direction),          "breaker_m15")
            if r: return r
            if bars1h:
                return _try(self._find_breaker_entry(bars1h, pair, direction), "breaker_h1")
            return None

        # Entries (initial AND pyramid) come from M5/M15/H1 patterns ONLY. M1 is NOT
        # an entry source — it is used solely for stop placement (_m1_structure_stop).
        result = _check_base()
        return result if result is not None else (None, None, None)

    def _m1_structure_stop(self, bars1m, direction, entry, pip):
        """Anchor the stop to the recent 1-minute swing extreme (Episode 12 STL/STH).

        LONG  → below the lowest M1 low of the down-leg price just made (the STL),
                minus M1_STOP_BUFFER_PIPS.
        SHORT → above the highest M1 high of the up-leg (the STH), plus the buffer.

        On a counter-trend entry the relevant structural point is the extreme of
        the move into the entry — that is the short-term high/low a stop sits
        beyond. Distance is floored at M1_STOP_MIN_PIPS (avoid noise-tight stops);
        the caller's 10-pip cap bounds the wide side. Returns the stop price, or
        None if the extreme isn't on the correct side of entry.
        """
        if not bars1m or len(bars1m) < 3:
            return None
        recent  = bars1m[-config.M1_STOP_LOOKBACK:]
        buf     = config.M1_STOP_BUFFER_PIPS * pip
        min_dist = config.M1_STOP_MIN_PIPS * pip

        if direction > 0:
            swing_low = min(c.Low for c in recent)
            stop = swing_low - buf
            if (entry - stop) < min_dist:           # too tight → floor it
                stop = entry - min_dist
            return stop if stop < entry else None
        else:
            swing_high = max(c.High for c in recent)
            stop = swing_high + buf
            if (stop - entry) < min_dist:
                stop = entry + min_dist
            return stop if stop > entry else None

    def _structure_stop(self, pair, direction, entry, pip, t):
        """Ep 12 — anchor the stop beyond the intact INTERMEDIATE swing (ITL/ITH).

        The short-term swing (STL/STH) is precisely what a minor liquidity run
        sweeps, forming a new short-term extreme while leaving the intermediate
        and long-term structure intact (the double-sweep / Judas). A stop placed
        at the raw STL/STH is therefore frequently taken out on a continuation
        that was never actually invalidated. Anchoring one fractal tier up — at
        the most recent INTACT ITL (for longs) / ITH (for shorts) — keeps the
        stop beyond the sweep's reach.

        LONG  → stop below the intact M1 ITL, minus the buffer.
        SHORT → stop above the intact M1 ITH, plus the buffer.

        Returns the stop price, or None if no intact intermediate swing sits on
        the correct side of entry (caller then falls back to the STL/STH stop).
        The universal 10-pip cap downstream enforces the "if 10 pips permit"
        rule — a structural stop wider than the cap is pulled in to 10 pips.
        """
        # Point instruments read structure on a higher TF (M1 is noise at their scale).
        if config.INDICES_ENABLED and pair in config.INDEX_PAIRS:
            _sstf, _sslb = config.INDEX_STOP_TF, config.INDEX_STOP_LOOKBACK
        elif config.GOLD_ENABLED and pair == config.GOLD_PAIR:
            _sstf, _sslb = config.GOLD_STOP_TF, config.GOLD_STOP_LOOKBACK
        else:
            _sstf, _sslb = config.STRUCTURE_STOP_TF, config.STRUCTURE_STOP_LOOKBACK
        bars = self.bars_up_to(pair, _sstf, t, max_bars=_sslb)
        if len(bars) < 5:
            return None
        res = self._classify_cached(bars, pair, _sstf)
        buf = config.M1_STOP_BUFFER_PIPS * pip
        min_dist = config.M1_STOP_MIN_PIPS * pip
        if direction > 0:
            itl = mstruct.last_intact(res, "ITL")
            if itl is None:
                return None
            stop = itl.price - buf
            if (entry - stop) < min_dist:       # too tight → floor it
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

    def _structure_trail_stop(self, bars5, direction, pip):
        """Most recent CONFIRMED M5 swing point, for trailing the stop off structure.

        LONG  → the most recent confirmed swing low (a bar whose Low is below both
                neighbours), minus STRUCTURE_TRAIL_BUFFER. Price breaking below it
                is an MSS against the long → exit.
        SHORT → the most recent confirmed swing high, plus the buffer.

        A swing needs one bar on each side to confirm, so the last bar is never a
        swing. Returns the trail-stop price, or None if no confirmed swing exists
        in the lookback window.
        """
        if not bars5 or len(bars5) < 3:
            return None
        recent = bars5[-config.STRUCTURE_TRAIL_LOOKBACK:]
        buf    = config.STRUCTURE_TRAIL_BUFFER * pip
        # Scan from the most recent confirmable bar backwards (skip the last bar).
        for i in range(len(recent) - 2, 0, -1):
            c = recent[i]
            if direction > 0:
                if c.Low < recent[i - 1].Low and c.Low < recent[i + 1].Low:
                    return c.Low - buf
            else:
                if c.High > recent[i - 1].High and c.High > recent[i + 1].High:
                    return c.High + buf
        return None

    def _trail_stop_near_target(self, bars5, direction, pip, entry, target):
        """For TRAIL_AT_TP: find the M5 swing structurally closest to the TP.

        The user's intent is the M5 swing that formed NEAR the target during the
        delivery phase — not the most recent in time (which may be near entry on a
        fast Judas spike).  We collect ALL confirmed M5 swings that are:
          • above entry (longs) / below entry (shorts) → guaranteed-win stop
          • at least TRAIL_AT_TP_MIN_PIPS from target  → gives the runner room
        and return the one whose stop-level is CLOSEST to the target (highest STL
        for longs / lowest STH for shorts).  If no such swing exists → None, and
        the trade exits normally at the TP.
        """
        if not bars5 or len(bars5) < 3:
            return None
        buf     = config.STRUCTURE_TRAIL_BUFFER * pip
        min_gap = config.TRAIL_AT_TP_MIN_PIPS * pip
        recent  = bars5[-config.STRUCTURE_TRAIL_LOOKBACK:]
        best    = None
        for i in range(len(recent) - 2, 0, -1):
            c = recent[i]
            if direction > 0:
                if c.Low < recent[i - 1].Low and c.Low < recent[i + 1].Low:
                    candidate = c.Low - buf
                    # Must lock in a win (above entry) and leave room below TP
                    if candidate > entry and (target - candidate) >= min_gap:
                        if best is None or candidate > best:
                            best = candidate   # keep the highest (closest to TP)
            else:
                if c.High > recent[i - 1].High and c.High > recent[i + 1].High:
                    candidate = c.High + buf
                    if candidate < entry and (candidate - target) >= min_gap:
                        if best is None or candidate < best:
                            best = candidate   # keep the lowest (closest to TP)
        return best

    def _unswept_pdliq_target(self, pair, direction, price, t):
        """Draw-to-liquidity continuation (config.DRAW_CONT_ENABLED).

        Return the nearest UNSWEPT PDH/PDL in the trade direction that sits a NEAR
        distance ahead — within [MIN_PIPS_TARGET, DRAW_CONT_MAX_PIPS] — else None.
        For a long: an unswept prior-day HIGH above price (buy-side pool not yet
        taken). For a short: an unswept prior-day LOW below price. "Unswept" is read
        as 'the pool is still beyond current price in the draw direction' — price
        hasn't delivered to it yet. Near-only by design: a far pool is the NEXT
        cycle's draw and forcing trades to it wrecked MaxDD (HTF_TARGET_PREF revert).
        """
        d_bars = self.bars_up_to(pair, "D", t)
        if len(d_bars) < 2:
            return None
        pip_v = pip_size(pair)
        lo = config.MIN_PIPS_TARGET * pip_v
        hi = config.DRAW_CONT_MAX_PIPS * pip_v
        best = None
        for db in d_bars[-4:-1]:            # last 3 completed daily candles
            lvl = db.High if direction > 0 else db.Low
            dist = (lvl - price) if direction > 0 else (price - lvl)
            if lo <= dist <= hi:            # unswept (ahead) AND near (this cycle)
                if best is None or dist < best[1]:
                    best = (lvl, dist)
        return best[0] if best else None

    # P20: source families considered "premium" institutional draws.
    # When escalation is active, raw swing / round-number candidates are bypassed
    # in favour of these if any qualify above the RR floor.
    _PREMIUM_TARGET_TYPES = frozenset({
        "fib_extension", "fvg", "ob",
        "pdh_pdl", "pwh_pwl",
        "ith_liquidity", "itl_liquidity",
        "equal_hl",
    })

    def _find_target(self, pair, direction, t, price, stop=None, escalate=False, beyond=None):
        """Find the nearest target that satisfies the RR requirement.

        If `stop` is supplied, selects the nearest candidate where
        |target - price| >= |price - stop| * MIN_RR (RR-aware selection).
        Falls back to the plain-nearest candidate if nothing satisfies RR.

        If `escalate=True` (P20), prefers premium liquidity draws over raw
        swing / round-number targets when both are available above the RR floor.

        Timeframe search order: M15 (last 48 bars) → H1 (24 bars) → H4 → D → W.
        M15/H1 lookbacks are capped to avoid O(n²) scan cost.
        """
        # Each candidate is a (price, draw_type) tuple so the chosen target's
        # liquidity draw can be recorded on the trade for post-hoc analysis.
        candidates = []

        # Fibonacci extension targets from the initiating OTE swing (Ep. 12 / SD model).
        # These project the natural profit magnets at 100%, 127.2%, 161.8%, 200% of the swing.
        pip_v = pip_size(pair)
        bars15 = self.bars_up_to(pair, "15T", t)
        swing = find_swing(bars15, direction, lookback=config.SWING_LOOKBACK)
        if swing is not None:
            fib_t = nearest_fib_target(
                swing[0], swing[1], direction, price,
                min_distance=self._min_pips_target() * pip_v,
            )
            if fib_t is not None:
                candidates.append((fib_t, "fib_extension"))

        for tf, cap in [("15T", 48), ("60T", 24), ("240T", 60), ("D", 0), ("W", 0)]:
            bars = self.bars_up_to(pair, tf, t)
            if len(bars) < 5:
                continue
            bars_slice = bars[-cap:] if cap and len(bars) > cap else bars
            candidates += self._targets_in_series(bars_slice, pair, direction, price)

        # ICT: Previous Day High/Low (PDH/PDL) are the primary buy-side and sell-side
        # liquidity pools — explicitly added so they are always considered as targets
        # even when they don't qualify as local swing highs/lows.
        d_bars = self.bars_up_to(pair, "D", t)
        if len(d_bars) >= 2:
            for db in d_bars[-4:-1]:        # last 3 completed daily candles
                candidates.append((db.High, "pdh_pdl"))  # buy-side liquidity (BSL)
                candidates.append((db.Low, "pdh_pdl"))   # sell-side liquidity (SSL)
        # Previous Week High/Low (PWWH/PWWL) — higher-timeframe pools.
        w_bars = self.bars_up_to(pair, "W", t)
        if len(w_bars) >= 2:
            candidates.append((w_bars[-2].High, "pwh_pwl"))
            candidates.append((w_bars[-2].Low, "pwh_pwl"))

        # NWOG (New Week Opening Gap): the weekend gap's low, high and 50% (CE) are
        # HTF PD-array levels price is drawn to. Added as a distinct "nwog" source
        # family so an NWOG level clustering with a fib/FVG scores as multi-source
        # confluence (feeding the P18 score sizing), and can itself be the target.
        if config.NWOG_ENABLED:
            _ng = self._nwog(pair, t)
            if _ng is not None:
                _nlo, _nhi, _nce, _ = _ng
                candidates.append((_nlo, "nwog"))
                candidates.append((_nhi, "nwog"))
                candidates.append((_nce, "nwog"))

        # ICT: unswept ITH/ITL are primary institutional liquidity draws (P17). Bigger
        # TF = stronger magnet. config.ITHL_TARGET_TFS selects which timeframes contribute
        # ITH/ITL target candidates (empty = none); default is H4/D/W. The full history is
        # scanned — the valuable draws are OLDER major intermediate highs/lows, so capping
        # the lookback removes the edge (300-bar H4 ≈ 50 days lost most of it: R76M→R71M).
        # H4/D/W bar counts are small (~6k/1k/200 over 4yr) so full-history classify is
        # cheap. Do NOT add 15T/60T here without a cap — those series run to ~100k bars and
        # uncapped mstruct.classify (O(n)) dominates runtime; they also hurt PnL (-R10M).
        _ithl_cap = config.ITHL_TARGET_MAX_BARS or None
        for _itf in config.ITHL_TARGET_TFS:
            _ibars = self.bars_up_to(pair, _itf, t, max_bars=_ithl_cap)
            if len(_ibars) < 5:
                continue
            candidates += self._ithl_targets(_ibars, direction, price, pair, _itf)

        _floor = beyond if beyond is not None else price
        if direction > 0:
            candidates = [c for c in candidates if c[0] > _floor]
        else:
            candidates = [c for c in candidates if c[0] < _floor]
        if not candidates:
            return None
        # Prefer targets in the correct dealing range zone (premium/discount).
        bars1h = self.bars_up_to(pair, "60T", t)
        dr = detect_dealing_range(bars1h, lookback=100)
        if dr is not None:
            filtered = [c for c in candidates
                        if is_valid_target_zone(c[0], dr.high, dr.low, direction)]
            if filtered:
                candidates = filtered
        # Prefer the nearest target satisfying both MIN_RR and MIN_PIPS_TARGET.
        _min_tgt = self._min_pips_target()
        if stop is not None:
            min_reward = max(abs(price - stop) * config.MIN_RR,
                             _min_tgt * pip_v)
        else:
            min_reward = _min_tgt * pip_v
        rr_ok = [c for c in candidates if abs(c[0] - price) >= min_reward]
        # P20: when high-conviction signals fire, prefer premium liquidity draws
        # (ITH/ITL, PDH/PDL, FVG, OB, fib) over raw swing / round-number targets.
        # Only applies when a premium candidate clears the RR floor — never skips
        # the trade entirely (falls back to full rr_ok if no premium qualifies).
        _used_escalation = False
        if escalate and config.TARGET_ESCALATE_ENABLED and rr_ok:
            _premium_ok = [c for c in rr_ok if c[1] in self._PREMIUM_TARGET_TYPES]
            if _premium_ok:
                rr_ok = _premium_ok
                _used_escalation = True
        # P23: prefer HTF institutional draws over fib/FVG projections when one is
        # available within HTF_TARGET_PREF_PIPS.  ITH/ITL/PDH/PDL/PWH/PWL are resting
        # liquidity pools — the actual institutional destination.  Fib extensions are
        # projected levels; they lose the selection when a real liquidity pool exists.
        _htf_draw_types = {"ith_liquidity", "itl_liquidity", "pdh_pdl", "pwh_pwl"}
        if config.HTF_TARGET_PREF_PIPS > 0 and rr_ok:
            _htf_pref_dist = config.HTF_TARGET_PREF_PIPS * pip_v
            _htf_ok = [c for c in rr_ok
                       if c[1] in _htf_draw_types
                       and abs(c[0] - price) <= _htf_pref_dist]
            if _htf_ok:
                rr_ok = _htf_ok   # narrow to HTF draws; fib/FVG become fallback

        # Keep the original selection: nearest target that clears MIN_RR (fewest
        # path changes). Confluence is an analytics signal, not a selection criterion.
        if rr_ok:
            chosen = min(rr_ok, key=lambda x: abs(x[0] - price))
        else:
            chosen = min(candidates, key=lambda x: abs(x[0] - price))
        # Score the chosen target: how many distinct source families cluster within
        # tolerance of this price? Higher score → stronger institutional draw here.
        tol = config.TARGET_CONFLUENCE_TOL_PIPS * pip_v
        score = self._confluence_score(candidates, chosen[0], tol)
        return chosen[0], chosen[1], score, _used_escalation

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
            out.append((tgt_fvg.mid, "fvg"))
        tgt_ob = nearest_unmitigated_ob(detect_order_blocks(bars), price, direction)
        if tgt_ob is not None:
            out.append((tgt_ob.mid, "ob"))
        if direction > 0:
            out += [(h, "equal_hl") for h in find_equal_highs(bars, pair, lookback=200)]
        else:
            out += [(l, "equal_hl") for l in find_equal_lows(bars, pair, lookback=200)]
        # ICT Ep 17: round-number liquidity levels (x.x000/200/500/800 for 4-dec pairs)
        # are always present above and below price — use as fallback targets.
        pip_v = pip_size(pair)
        base_pips = int(round(price / pip_v))
        base_round = (base_pips // 100) * 100
        for offset in range(-2, 6):
            for sub in (0, 20, 50, 80):
                level_pips = base_round + offset * 100 + sub
                level = level_pips * pip_v
                if direction > 0 and level > price + pip_v:
                    out.append((level, "round_number"))
                elif direction < 0 and level < price - pip_v:
                    out.append((level, "round_number"))
        # ICT: raw swing highs (BSL) above price and swing lows (SSL) below price
        # are liquidity pools that price gravitates toward.
        n = len(bars)
        for i in range(1, n - 1):
            if direction > 0 and bars[i].High > bars[i - 1].High and bars[i].High > bars[i + 1].High:
                if bars[i].High > price:
                    out.append((bars[i].High, "swing"))
            elif direction < 0 and bars[i].Low < bars[i - 1].Low and bars[i].Low < bars[i + 1].Low:
                if bars[i].Low < price:
                    out.append((bars[i].Low, "swing"))
        return out

    @staticmethod
    def _confluence_score(candidates, target_price, tol):
        """Count distinct source families within `tol` price units of target_price."""
        seen = set()
        for price, src in candidates:
            if abs(price - target_price) <= tol:
                seen.add(src)
        return len(seen)

    def _ithl_targets(self, bars, direction, price, pair: str = "", tf: str = ""):
        """Unswept ITH (longs) / ITL (shorts) as primary liquidity draw candidates.

        ICT: price is drawn toward resting buy-side liquidity ABOVE unswept intermediate
        highs (ITHs) for longs, and sell-side liquidity BELOW unswept intermediate lows
        (ITLs) for shorts. The fractal tier confirms institutional order flow stopped
        there — these are stronger magnets than plain swing highs/lows.

        Vice versa for protection: the same ITL levels below entry are where stops
        belong for longs (price must break the ITL to invalidate the setup), and ITH
        levels above entry are the stop reference for shorts. The structural stop
        (_structure_stop) already anchors to the most recent intact M1 ITL/ITH.

        Returns (price, source_tag) tuples — source families "ith_liquidity" /
        "itl_liquidity" are distinct from "swing" so the confluence scorer counts
        them separately.
        """
        if len(bars) < 5:
            return []
        res = (self._classify_cached(bars, pair, tf)
               if pair and tf else mstruct.classify(bars))
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
        """Scan bars for FVGs and mark mitigation (close-through, ICT Ep 9)."""
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

    def _htf_fvg_conviction(self, pair, direction, cur_price, t):
        """P9 — HTF FVG 50% midpoint as draw-on-liquidity conviction.

        Unmitigated H4/D1/W1 FVGs are the bigger-timeframe draw on liquidity that
        continuation moves deliver into. Price entering an HTF FVG typically
        consolidates at ~50% (the gap's equilibrium) before continuing — that 50%
        zone is the natural HTF Accumulation anchor for the next AMD cycle.

        When current price sits within HTF_FVG_MID_TOLERANCE_PIPS of an unmitigated
        HTF FVG midpoint whose direction matches the trade, the AMD consolidation
        has formed at the natural HTF delivery zone (not random) → +1 conviction.

        Returns (points, timeframe_hit) where timeframe_hit is "" on no hit.
        Highest timeframe wins ties — W draw > D draw > H4 draw.
        """
        pip_v = pip_size(pair)
        tol   = config.HTF_FVG_MID_TOLERANCE_PIPS * pip_v
        # Scan biggest TF first so the reported hit reflects the strongest draw.
        for tf in ("W", "D", "240T"):
            bars = self.bars_up_to(pair, tf, t)
            if bars is None or len(bars) < 3:
                continue
            for fvg in self._scan_htf_fvgs(bars, pair):
                if fvg.mitigated or fvg.direction != direction:
                    continue
                if abs(cur_price - fvg.mid) <= tol:
                    return 1, tf
        return 0, ""

    def _htf_fvg_opposing(self, pair, direction, cur_price, t):
        """Reversal filter: detect unmitigated HTF FVGs in the opposing direction.

        When a REVERSAL trade would fade a move, it may be fighting an unmitigated
        HTF draw. Example: going SHORT after a Judas sweep, but an unmitigated
        BULLISH H4 FVG sits above price — the HTF draw is UP, so the reversal is
        premature; price will likely first deliver into the FVG before reversing.

        Returns True if such a blocking opposing FVG exists on any HTF.
        The check is intentionally direction-agnostic: an opposing FVG that price
        has already passed through (already inside or beyond) is ignored — only
        FVGs that are still "in the path" count.
        """
        pip_v = pip_size(pair)
        opp = -direction   # direction we'd be fighting
        for tf in ("W", "D", "240T"):
            bars = self.bars_up_to(pair, tf, t)
            if bars is None or len(bars) < 3:
                continue
            for fvg in self._scan_htf_fvgs(bars, pair):
                if fvg.mitigated or fvg.direction != opp:
                    continue
                # The FVG is "in the path" when price must travel through it to
                # reach the reversal target.  For a SHORT reversal, a bullish FVG
                # above price means price would have to rally into it before the
                # short target is reached (it represents an unfilled draw UP).
                # For a LONG reversal, a bearish FVG below price works the same way.
                max_dist = config.HTF_FVG_OPPOSING_MAX_PIPS * pip_v
                if opp > 0 and fvg.bottom > cur_price:   # bullish FVG above → blocks short
                    if fvg.bottom - cur_price <= max_dist:
                        return True
                if opp < 0 and fvg.top < cur_price:      # bearish FVG below → blocks long
                    if cur_price - fvg.top <= max_dist:
                        return True
        return False

    def _dxy_htf_context(self, trade_direction, t):
        """P13 — DXY's own HTF FVG as a 'room to run' signal.

        DXY underlies all three traded pairs (EURUSD/GBPUSD/NZDUSD move inverse to DXY).
        When DXY is sitting at the midpoint of an unmitigated W/D/H4 FVG in its own
        direction, the dollar has a clear HTF delivery draw ahead — the move has room.
        Same concept as P9 (pair FVG draw) but applied directly to the dollar index.

        trade_direction: +1 = long pair (DXY needs to fall), -1 = short pair (DXY rises).
        Returns (score, tf_hit): +1 when DXY has clear HTF room, 0 otherwise.
        """
        dxy_direction = -trade_direction   # DXY moves inverse to EUR/GBP/NZD pairs
        dxy_pip = 0.001                    # DXY ~100 scale; pip = 0.001 points
        tol = config.DXY_FVG_MID_TOLERANCE_PIPS * dxy_pip
        for tf in ("W", "D", "240T"):
            bars = self._dxy_bars(tf, t)
            if not bars or len(bars) < 3:
                continue
            fvgs = self._scan_htf_fvgs(bars, "UDXUSD")
            cur = bars[-1].Close
            for fvg in fvgs:
                if fvg.mitigated or fvg.direction != dxy_direction:
                    continue
                if abs(cur - fvg.mid) <= tol:
                    return 1, tf
        return 0, ""

    def _load_bond_bias(self):
        """Lazy-load data/bond_bias.json -> {date_str: +1/-1/0} (DGS10 structure).

        Cached on the instance; a missing/malformed file yields an empty map (the
        lever simply never fires). Written by
        `scripts/bonds_analysis.py --emit-bias`. Only called when
        config.BONDS_BIAS_ENABLED, so the default path never touches disk.
        """
        cache = getattr(self, "_bond_bias_cache", None)
        if cache is not None:
            return cache
        cache = {}
        try:
            with open(config.BONDS_BIAS_FILE) as f:
                data = json.load(f)
            cache = {k: int(v) for k, v in data.get("DGS10", {}).items()}
        except (OSError, ValueError, TypeError):
            cache = {}
        self._bond_bias_cache = cache
        return cache

    def _htf_crt_sweep(self, pair, direction, cur_price, t):
        """P19 — HTF CRT Turtle Soup: sweep of prior H4/D candle range extreme.

        ICT CRT (Candlestick Range Theory): the High and Low of a completed HTF
        candle define CRT H / CRT L — the institutional delivery range. A Turtle
        Soup = price wicks BEYOND CRT H (for shorts) or below CRT L (for longs)
        on a WICK, then CLOSES BACK INSIDE. This is the HTF Judas swing —
        manipulation on the bigger timeframe confirms the reversal is real.

        When detected within the last 2–3 completed bars in agreement with the
        trade direction → award conviction points.

        Returns (score, tf_hit): Daily sweep = 2 pts, H4 sweep = 1 pt.
        """
        if not config.CRT_SWEEP_ENABLED:
            return 0, ""
        pip_v = pip_size(pair)
        min_sweep = config.CRT_SWEEP_MIN_PIPS * pip_v

        for tf, points in [("D", 2), ("240T", 1)]:
            bars = self.bars_up_to(pair, tf, t, max_bars=10)
            if len(bars) < 4:
                continue
            # Check last 2 completed bars (bars[-1] is the bar that just closed)
            for i in range(len(bars) - 1, max(len(bars) - 3, 1), -1):
                sweep_bar = bars[i]
                # CRT range = the 2 bars immediately before the sweep bar
                ref_bars = bars[max(0, i - 2):i]
                if not ref_bars:
                    continue
                crt_high = max(b.High for b in ref_bars)
                crt_low  = min(b.Low  for b in ref_bars)

                if direction < 0:
                    # SHORT: wick above CRT H, close back inside, price still below CRT H
                    if (sweep_bar.High >= crt_high + min_sweep
                            and sweep_bar.Close < crt_high
                            and cur_price < crt_high):
                        return points, tf
                else:
                    # LONG: wick below CRT L, close back inside, price still above CRT L
                    if (sweep_bar.Low <= crt_low - min_sweep
                            and sweep_bar.Close > crt_low
                            and cur_price > crt_low):
                        return points, tf
        return 0, ""

    def _classify_cached(self, bars, pair: str, tf: str) -> dict:
        """Return mstruct.classify(bars).

        NOTE: this was previously a memoised cache keyed by (pair, tf, len(bars)),
        but Bar is a namedtuple("Open High Low Close") with no timestamp — the
        intended bars[-1].name key always raised AttributeError and fell back to
        len(bars), which saturates at the max_bars cap (300/90). The key became
        constant for the whole run, so the cache returned the FIRST classification
        forever, freezing _structure_stop and _structure_conviction at early-2022
        structure and silently degrading PF 5.20→4.19 / MaxDD -12.95→-13.89.

        The real performance fix is the max_bars cap at every call site (classify
        is O(n) on ≤300 bars, called ~1.7k times over 4yr) — no cache is needed.
        Direct passthrough is provably correct; the method is retained as a thin
        wrapper so call sites stay unchanged.
        """
        _empty = {k: [] for k in ("sth", "stl", "ith", "itl", "lth", "ltl")}
        if not bars or len(bars) < 3:
            return _empty
        return mstruct.classify(bars)

    # Timeframes scanned for market-structure conviction (Ep 12), HTF → LTF.
    # M5 (5T) is excluded per the trader's spec — too noisy for tier classification;
    # M1 (1T) is used only for stop anchoring, not structural read. Weighting is
    # hierarchical: the bigger the timeframe agreeing, the stronger the draw.
    _MSTRUCT_TFS = (
        ("W",    3),   # weekly structure — the macro draw, highest weight
        ("D",    2),   # daily structure
        ("240T", 1),   # H4 structure
        ("60T",  1),   # H1 structure — session bias tier
        ("15T",  1),   # M15 structure — entry tier
    )
    # DXY structure is read at H1 and above — M15 is too noisy for the dollar index.
    # No weighting needed: DXY agreement is binary (aligned / not aligned).
    _DXY_MSTRUCT_TFS = ("W", "D", "240T", "60T")

    def _structure_conviction(self, pair, direction, t):
        """Ep 12 — couple the fractal LTH/ITH/STH read with the draw cascade.

        Scans the TRADED PAIR and DXY independently:
        - Pair structure: does this pair's own swing hierarchy agree with direction?
        - DXY structure: is the dollar's fractal hierarchy confirming USD strength/weakness?
          DXY up (higher ITLs) = USD strong = pairs fall → agrees when direction == -1.
          DXY down (lower ITHs) = USD weak = pairs rise → agrees when direction == +1.
          DXY is the PRIMARY driver — its alignment is the most important structural read.

        Minor-sweep detection: when a short-term swing was taken (Judas) but the
        intermediate swing in the trade direction is still INTACT, the move is a
        minor liquidity run confirming the trend continues.

        Returns a dict:
          points          — conviction to add
          align_tfs       — pair TFs whose structure agrees with direction
          htf_dir         — daily/weekly structural direction (+1/-1/0)
          minor_sweep     — True if a Judas continuation is confirmed (pair or DXY)
          ltf_intact_tf   — highest TF with an intact intermediate level supporting trade
          dxy_align       — DXY TFs whose structure agrees with trade direction
          dxy_minor_sweep — True if DXY itself shows a Judas confirmation
        """
        align = []
        weight = 0
        htf_dir = 0
        minor_sweep = False
        intact_tf = ""

        # ── Pair structure ────────────────────────────────────────────────────
        for tf, w in self._MSTRUCT_TFS:
            bars = self.bars_up_to(pair, tf, t, max_bars=300)
            if len(bars) < 5:
                continue
            res = self._classify_cached(bars, pair, tf)
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

        # ── DXY structure (primary USD driver) ───────────────────────────────
        # DXY rising  → USD strong → pairs fall  → agrees with direction == -1
        # DXY falling → USD weak   → pairs rise  → agrees with direction == +1
        # "DXY agrees" ≡ structure_direction(dxy) == -direction
        dxy_align = []
        dxy_minor_sweep = False
        for tf in self._DXY_MSTRUCT_TFS:
            dxy_bars = self.bars_up_to("UDXUSD", tf, t, max_bars=300)
            if len(dxy_bars) < 5:
                continue
            dxy_res = self._classify_cached(dxy_bars, "UDXUSD", tf)
            dxy_sdir = mstruct.structure_direction(dxy_res)
            if dxy_sdir == -direction:
                dxy_align.append(tf)
                # DXY W/D agreement is as strong as the pair's — update htf_dir
                if tf in ("W", "D") and not htf_dir:
                    htf_dir = direction
            # DXY Judas: short-term sweep against the trade direction, but DXY's
            # intermediate swing in the trade-supporting direction is still intact.
            if tf in ("240T", "60T") and mstruct.is_minor_sweep(dxy_res, -direction):
                dxy_minor_sweep = True
                minor_sweep = True

        # Conviction: +1 when pair structure has any HTF agreement,
        # +1 when W/D (pair or DXY) confirms, +1 for minor-sweep continuation.
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

    def _structure_entry_confirmed(self, pair, direction, t):
        """Optional Ep-12 entry trigger — 'enter on the LTF reversal swing'.

        After the HTF read + MSS confirm the bias, require a freshly-confirmed
        lower-TF fractal swing in the trade direction:
          LONG  -> a confirmed, still-intact Short-Term LOW  (STL)
          SHORT -> a confirmed, still-intact Short-Term HIGH (STH)
        'Confirmed' = the swing's right-side (3rd) bar has printed (age >= 1);
        'fresh'     = it formed within STRUCTURE_ENTRY_MAX_AGE bars;
        'intact'    = not yet swept (the reversal is holding).
        Gated by STRUCTURE_ENTRY_ENABLED; a pure no-op (never called) when off.
        """
        bars = self.bars_up_to(pair, config.STRUCTURE_ENTRY_TF, t,
                               max_bars=config.STRUCTURE_ENTRY_LOOKBACK)
        if len(bars) < 5:
            return False
        res = mstruct.classify(bars)
        swings = res.get("stl" if direction > 0 else "sth", [])
        if not swings:
            return False
        last = swings[-1]
        age = (len(bars) - 1) - last.bar_index   # completed bars to the swing's right
        if age < 1 or age > config.STRUCTURE_ENTRY_MAX_AGE:
            return False
        return not last.swept

    def _direction_allowed(self, pair, direction, t):
        """Hook for the live semi-auto layer to veto a trade direction.

        Default (backtest): always allow — a pure no-op so backtest numbers are
        byte-identical. LiveTrader overrides it to apply the trader's Telegram
        direction filter + full-manual-AMD levels gate.
        """
        return True

    def _handover_exempt(self, pair):
        """Hook: True = keep this pair's trade open across the session handover
        (the trader's /hold instruction). Default (backtest): never exempt — a
        pure no-op so backtest numbers are byte-identical. LiveTrader overrides."""
        return False

    def _maybe_open(self, pair, t):
        g = self.gate
        g["checks"] += 1
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if not can_open_new_trade(now, pair):
            return
        g["in_killzone"] += 1

        # ── Wipeout-prevention checks ──────────────────────────────────────
        day_key = now.date()
        # Reset daily equity snapshot and consecutive loss counter each new day.
        if day_key not in self._day_open_eq:
            self._day_open_eq[day_key] = self.equity
            self._consec_losses = 0

        # 1. Peak drawdown halt: pause trading for DRAWDOWN_PAUSE_DAYS after >20% DD.
        if self._drawdown_halt_until is not None:
            if day_key < self._drawdown_halt_until:
                g["drawdown_halt"] += 1
                return
            # Pause expired → reset peak to current equity so DD is measured from here
            self._peak_equity = self.equity
            self._drawdown_halt_until = None
        if self._peak_equity > 0:
            if self.equity < config.GROWTH_PHASE_EQUITY:
                # Growth phase: use hard ZAR floor instead of %-from-peak.
                # The % breaker is too tight at R500 — a 2-trade losing run
                # already exceeds -15%. Floor fires only at half starting capital.
                breached = self.equity <= config.GROWTH_PHASE_FLOOR_ZAR
            else:
                breached = (
                    (self._peak_equity - self.equity) / self._peak_equity * 100
                    >= config.MAX_DRAWDOWN_HALT_PCT
                )
            if breached:
                from datetime import timedelta
                self._drawdown_halt_until = day_key + timedelta(days=config.DRAWDOWN_PAUSE_DAYS)
                g["drawdown_halt"] += 1
                return

        # 2. Daily loss cap: sit out rest of day after losing >6% of day-open equity.
        day_open = self._day_open_eq[day_key]
        if day_open > 0 and (day_open - self.equity) / day_open * 100 >= config.MAX_DAILY_LOSS_PCT:
            g["daily_loss_halt"] += 1
            return

        # 3. Consecutive loss pause: sit out rest of day after N straight losses.
        if self._consec_losses >= config.MAX_CONSECUTIVE_LOSSES:
            g["consec_loss_pause"] += 1
            return
        # ────────────────────────────────────────────────────────────────────

        # News gate:
        #   Critical (CPI/NFP/FOMC) → block. 20-40+ pip Judas spike blows any tight stop.
        #   Medium                  → block. Spread risk without directional catalyst.
        #   High (BOE/ECB/other)    → allow with 10-pip stop + widened news spread.
        news_impact = self.news.nearest_impact(now)
        if news_impact in ("Medium", "Critical"):
            return
        g["news_clear"] += 1

        if is_nfp_week_low_probability(now, self.news.is_nfp_week(now)):
            return
        if is_post_fomc_low_probability(now, self.news.fomc_whipsaw_date):
            return
        g["nfp_fomc_ok"] += 1

        # Detect NY AM session early — needed for session-specific budget + threshold.
        import pytz as _pytz
        _ny_tz = _pytz.timezone("America/New_York")
        _ny_dt = now.astimezone(_ny_tz)
        _is_ny     = (7 <= _ny_dt.hour < 10)
        _is_london = (2 <= _ny_dt.hour < 5)
        _is_pm     = config.NY_PM_ENABLED and (13 <= _ny_dt.hour < 16)
        # Each session evaluates price independently (clean profile handover):
        # London, NY AM, and NY PM each track their own AMD cycle.
        if _is_london:
            _session_label = "london"
        elif _is_ny:
            _session_label = "ny"
        elif _is_pm:
            _session_label = "ny_pm"
        else:
            _session_label = "other"

        # ── Weekly / daily trade budget ───────────────────────────────────────
        iso = day_key.isocalendar()
        week_key   = (iso[0], iso[1])
        week_total = self._week_total.get(week_key, 0)
        week_pair   = self._week_pair.get((week_key[0], week_key[1], pair), 0)
        day_total   = self._day_total.get(day_key, 0)
        day_pair    = self._day_pair.get((day_key, pair), 0)
        day_pair_ny = self._day_pair_ny.get((day_key, pair), 0)
        day_pair_pm = self._day_pair_pm.get((day_key, pair), 0)

        if week_pair >= config.MAX_PAIR_TRADES_PER_WEEK:
            g["weekly_pair_cap"] += 1
            return
        # Indices get their OWN daily budget (when configured) so they don't compete
        # with the currencies for the basket-wide MAX_TRADES_PER_DAY slots. FX path
        # is unchanged (byte-identical) when INDEX_MAX_TRADES_PER_DAY=0 or off.
        _idx_budget = (config.INDICES_ENABLED and pair in config.INDEX_PAIRS
                       and config.INDEX_MAX_TRADES_PER_DAY > 0)
        if _idx_budget:
            if self._day_idx_total.get(day_key, 0) >= config.INDEX_MAX_TRADES_PER_DAY:
                g["daily_cap"] += 1
                return
        elif day_total >= config.MAX_TRADES_PER_DAY:
            g["daily_cap"] += 1
            return
        # Each session has its own per-pair slot so sessions don't block each other.
        if _is_ny:
            if day_pair_ny >= config.MAX_PAIR_TRADES_PER_DAY_NY:
                g["daily_pair_cap"] += 1
                return
        elif _is_pm:
            if day_pair_pm >= config.MAX_PAIR_TRADES_PER_DAY_PM:
                g["daily_pair_cap"] += 1
                return
        else:
            if day_pair >= config.MAX_PAIR_TRADES_PER_DAY:
                g["daily_pair_cap"] += 1
                return
        # ─────────────────────────────────────────────────────────────────────

        # PM precision gate: afternoon session only fires on the exact confluence
        # described by the user — London+NY AM still within internal range, with a
        # HTF draw (FVG) still in play and a news catalyst to deliver the final leg.
        # Without all three, PM is position-squaring noise (IS PF 1.64, MaxDD -17.66%).
        #   1. EURUSD only — GBPUSD PM is PF 0.69, a proven loser (GBP liquidity
        #      dries up after London close; cable tracks equities, not FX flow).
        #   2. High-impact news only — the catalyst that forces price to deliver
        #      into the HTF target. Without it, PM moves are random squaring.
        #   3. HTF FVG conviction (checked below after _htf_fvg_pts is computed).
        if _is_pm:
            if pair != "EURUSD":
                return
            if news_impact != "High":
                return
        g["pm_gate_pair_news"] = g.get("pm_gate_pair_news", 0) + (1 if _is_pm else 0)

        # Intermarket: DXY gives USD direction.
        # EUR/GBP family (unchanged): EURGBP selects EURUSD vs GBPUSD.
        # NZDUSD family (independent): AUDNZD selects NZD as preferred vs AUD; DXY confirms direction.
        dxy_bias = self._dxy_bias("60T", t, lookback=config.SWING_LOOKBACK_STH)
        if dxy_bias == 0:
            return   # DXY flat → no USD bias → hard gate for all pairs

        _im_scenario = "?"
        if pair in ("EURUSD", "GBPUSD"):
            eurgbp_bias = self._sym_bias(config.REF_EURGBP, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            # Escalation cascade for EURGBP when H1 cross is flat:
            #   Level 1: H1 EURGBP (direct)
            #   Level 2: H4 EURGBP (when H1 flat) — unlocks GBPUSD, reclassifies scenario
            #   Level 3: individual pair bias (when H4 also flat) — synthetic from EU vs GU momentum
            # If all three are flat → keep eurgbp_bias=0 and trade EURUSD only (3a/3b).
            _h4_escalated = False
            _ip_escalated = False
            if eurgbp_bias == 0:
                eurgbp_h4 = self._sym_bias(config.REF_EURGBP, "240T", t,
                                           lookback=config.SWING_LOOKBACK_STH)
                if eurgbp_h4 != 0:
                    eurgbp_bias   = eurgbp_h4
                    _h4_escalated = True
            if eurgbp_bias == 0:
                eurgbp_ip = self._eurgbp_synthetic(
                    t,
                    config.EURGBP_SYNTHETIC_LOOKBACK,
                    config.EURGBP_SYNTHETIC_THRESHOLD_PIPS,
                )
                if eurgbp_ip != 0:
                    eurgbp_bias  = eurgbp_ip
                    _ip_escalated = True
            direction, im_score = resolve_pair_direction(
                dxy_bias, eurgbp_bias, pair, "EURUSD"
            )
            if direction is None:
                return
            if im_score < 0.75:
                return
            # When cross is flat at all three levels, GBPUSD has no selection signal.
            if eurgbp_bias == 0 and pair == "GBPUSD":
                return
            mss_sym1, mss_sym2 = "EURUSD", "GBPUSD"
            # ICT intermarket cheat sheet scenario classification.
            # _h4 = H1 flat, H4 used; _ip = H1+H4 both flat, individual pair momentum used.
            _scenario_map = {
                (+1, +1): "1a", (+1, -1): "1b",
                (-1, +1): "2a", (-1, -1): "2b",
                (+1,  0): "3a", (-1,  0): "3b",
            }
            _base = _scenario_map.get((dxy_bias, eurgbp_bias), "?")
            if _h4_escalated:
                _im_scenario = _base + "_h4"
            elif _ip_escalated:
                _im_scenario = _base + "_ip"
            else:
                _im_scenario = _base

        elif config.GOLD_ENABLED and pair == config.GOLD_PAIR:
            # Gold (XAUUSD) — DXY + silver + AUDUSD 2-of-3 breadth gate.
            # Gold is inverse to the dollar; silver (XAGUSD) and AUDUSD are
            # positive confirmers. DXY is the hard gate (already checked non-zero
            # above); at least one of silver/AUD must also confirm, and silver
            # diverging suppresses (see intermarket.resolve_gold_direction).
            silver_bias = self._sym_bias(config.GOLD_REF_SILVER, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            aud_bias    = self._sym_bias(config.GOLD_REF_AUD, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            direction, im_score = resolve_gold_direction(dxy_bias, silver_bias, aud_bias)
            if direction is None:
                return
            if im_score < config.GOLD_MIN_IMSCORE:
                return   # default 1.0 → require DXY + silver + AUD all to agree
            # MSS breadth for gold: its own structure + silver, DXY inverse.
            mss_sym1, mss_sym2 = config.GOLD_PAIR, config.GOLD_REF_SILVER
            _im_scenario = "G-long" if direction > 0 else "G-short"

        elif config.INDICES_ENABLED and pair in config.INDEX_PAIRS:
            sibling = next((p for p in config.INDEX_PAIRS if p != pair), None)
            _inp = getattr(self, "inputs", None)
            if config.INDEX_SEMI_AUTO_ONLY and _inp is not None:
                # SEMI-AUTO (live): the trader supplies the direction via /bias; the
                # auto gate does NOT open indices. No bias set -> index doesn't trade.
                _b = _inp.bias(pair)
                if _b not in ("long", "short"):
                    return
                direction = 1 if _b == "long" else -1
                im_score = 1.0
                _im_scenario = "IDX-man"
            else:
                # AUTO gate (backtest / auto mode): DXY (inverse) + sibling + US30
                # breadth; sibling divergence suppresses (SMT), US30 confirms.
                sib_bias = (self._sym_bias(sibling, "60T", t,
                                           lookback=config.SWING_LOOKBACK_STH)
                            if sibling else 0)
                ref_bias = self._sym_bias(config.INDEX_REF, "60T", t,
                                          lookback=config.SWING_LOOKBACK_STH)
                direction, im_score = resolve_index_direction(dxy_bias, sib_bias, ref_bias)
                if direction is None:
                    return
                if im_score < config.INDEX_MIN_IMSCORE:
                    return
                _im_scenario = "IDX-long" if direction > 0 else "IDX-short"
            # MSS breadth: this index + its sibling, DXY inverse (algo still needs its setup).
            mss_sym1, mss_sym2 = pair, (sibling or config.INDEX_REF)

        else:   # NZDUSD — DXY + AUDNZD cross (independent of EUR/GBP family)
            audnzd_bias = self._sym_bias(config.REF_AUDNZD, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            # H4 AUDNZD escalation: same logic as EURGBP cascade.
            # When H1 AUDNZD is flat, check H4. If H4 shows NZD stronger
            # (audnzd_bias → -1), NZDUSD still scores 1.0 and is allowed.
            # If H4 shows AUD stronger, NZDUSD scores 0.5 → still blocked below.
            _nzd_h4_escalated = False
            if audnzd_bias == 0:
                audnzd_h4 = self._sym_bias(config.REF_AUDNZD, "240T", t,
                                           lookback=config.SWING_LOOKBACK_STH)
                if audnzd_h4 != 0:
                    audnzd_bias       = audnzd_h4
                    _nzd_h4_escalated = True
            # NZDUSD is the non-primary pair; AUDNZD picks NZD vs AUD.
            # im_score 1.0: AUDNZD confirms NZD is the extreme (NZDUSD preferred).
            # im_score 0.5: AUDNZD says AUD is extreme → AUDUSD preferred (not traded, skip).
            # im_score 0.75: AUDNZD neutral → no cross signal, don't default to NZDUSD.
            direction, im_score = resolve_pair_direction(
                dxy_bias, audnzd_bias, "NZDUSD", "AUDUSD"
            )
            if direction is None:
                return
            if im_score < 1.0:
                return   # only trade when AUDNZD explicitly confirms NZDUSD
            mss_sym1, mss_sym2 = "NZDUSD", "AUDUSD"
            _base = "N-long" if dxy_bias == -1 else "N-short"
            _im_scenario = (_base + "_h4") if _nzd_h4_escalated else _base

        g["intermarket_signal"] += 1
        g["pair_matches"] += 1

        # Intermarket breakout: triple-confirmed continuation (EURUSD + GBPUSD + DXY
        # all clear their M15 ranges in agreement). When it fires in the trade
        # direction the setup is a continuation/expansion, not a reversal — it gets
        # its own entry_model tag, extra conviction, and an exemption from the
        # inverted-draw 0/3 hard gate below (which is reversal logic that would
        # otherwise block every continuation trade).
        _brk_dir = self._intermarket_breakout(t)
        _is_breakout = (_brk_dir != 0 and _brk_dir == direction)
        # The triple-confirmed breakout is a EURUSD+GBPUSD+DXY model — it has no
        # meaning for gold or the indices, so never let it tag/exempt those trades.
        if self._is_point_instrument(pair):
            _is_breakout = False
        if _is_breakout:
            g["breakout_confirmed"] = g.get("breakout_confirmed", 0) + 1

        # Semi-auto manual override (live only; no-op in backtest). Vetoes the
        # trade when it fights the trader's Telegram direction filter or the
        # full-manual-AMD levels gate (sweep-one-side / target-the-other). Placed
        # here — before MSS/budget — so a vetoed setup consumes no daily slot.
        if not self._direction_allowed(pair, direction, t):
            self._log_reject(t, pair, direction, "semi-auto: direction/levels gate")
            return

        # P11: NY-AM continuation of the day's London/DXY direction. London sets the
        # day's USD direction (DXY-wide); into NY price consolidates over the handover
        # then shifts structure (MSS) and continues the SAME way. Such a trade runs
        # WITH the daily draw — it only "looks like" a reversal (micro-Judas) but is a
        # continuation, so the inverted-draw 0/3 reversal gate would wrongly kill it.
        # ANALYTICS-ONLY for now: tagged + counted, no gate/size change yet.
        _is_ny_cont = (_is_ny and not _is_breakout
                       and self._london_dir.get(_ny_dt.date(), 0) == direction)

        # MSS: 2-of-3 using both pairs in the family + DXY inverse.
        sym1_mss  = self._pair_has_mss(mss_sym1, t, direction)
        sym2_mss  = self._pair_has_mss(mss_sym2, t, direction)
        dxy_mss   = self._dxy_has_mss(t, -direction)
        mss_count = sym1_mss + sym2_mss + dxy_mss
        if mss_count < 2:
            self._log_reject(t, pair, direction, f"no MSS ({mss_count}/3 structure shift, need 2)")
            return   # Need at least 2-of-3 MSS
        g["mss_h1_m15_m5_ok"] += 1

        # Optional Ep-12 structure entry trigger (default OFF -> no-op). Require a
        # freshly-confirmed LTF reversal swing (STL for longs / STH for shorts) —
        # "enter on the swing formation, the moment its 3rd bar prints".
        if config.STRUCTURE_ENTRY_ENABLED and not self._structure_entry_confirmed(pair, direction, t):
            g["structure_entry_blocked"] = g.get("structure_entry_blocked", 0) + 1
            self._log_reject(t, pair, direction, "no confirmed LTF reversal swing (structure entry)")
            return

        # Dealing range: informational only (DR over-rejects in trending markets).
        bars1h = self.bars_up_to(pair, "60T", t)
        if not bars1h:
            return
        dr = detect_dealing_range(bars1h, lookback=100)
        cur_price = bars1h[-1].Close
        dr_aligned = (dr is None) or is_valid_entry_zone(cur_price, dr.high, dr.low, direction)
        g["dealing_range_ok"] += 1 if dr_aligned else 0

        g["daily_bias_ok"] += 1
        g["h1_bias_ok"] += 1
        g["h4_bias_ok"] += 1

        # ── Conviction scoring ────────────────────────────────────────────────
        # Sum points from all confirming signals. Score → max pyramid legs:
        #   0-2 pts  → 1 leg only (entry only, no pyramid adds)
        #   3-4 pts  → 2 legs  (one add)
        #   5+ pts   → 3 legs  (full pyramid)
        conviction = 0

        # Intermarket quality (0-2)
        if im_score >= 1.0:   conviction += 2    # preferred pair per cross
        elif im_score >= 0.75: conviction += 1   # cross neutral or DXY-only

        # MSS quality (0-2)
        conviction += min(mss_count, 2)

        # Weekly AMD confirmed in same direction (0-2)
        wamd = self._get_weekly_amd(pair, t)
        weekly_amd_dir = wamd.direction if wamd is not None else 0
        if wamd is not None and wamd.direction == direction:
            conviction += 2
            g["weekly_amd_confirmed"] += 1

        # HTF Draw on Liquidity cascade: W → D → H4 (0-3)
        # The single most important directional factor — where is price magnetically
        # drawn on the higher timeframes?  Each TF that agrees with trade direction
        # adds +1.  Counter-draw trades earn 0 here (heavy disadvantage, no hard gate).
        # Cached per (pair, date): W/D/H4 draw doesn't change within a trading day.
        pip_v = pip_size(pair)
        _draw_key = (pair, day_key)
        if _draw_key not in self._draw_cache:
            bars_w  = self.bars_up_to(pair, "W",    t)
            bars_d  = self.bars_up_to(pair, "D",    t)
            bars_h4 = self.bars_up_to(pair, "240T", t)
            self._draw_cache[_draw_key] = (
                draw_cascade_score(bars_w, bars_d, bars_h4, pair, direction, pip_v),
                direction,
            )
        _cached_draw, _cached_dir = self._draw_cache[_draw_key]
        # Cache stores the draw score for the FIRST direction seen that day.
        # If current direction flipped intraday, recompute fresh.
        if _cached_dir != direction:
            bars_w  = self.bars_up_to(pair, "W",    t)
            bars_d  = self.bars_up_to(pair, "D",    t)
            bars_h4 = self.bars_up_to(pair, "240T", t)
            _cached_draw = draw_cascade_score(bars_w, bars_d, bars_h4, pair, direction, pip_v)
            self._draw_cache[_draw_key] = (_cached_draw, direction)
        _draw_score = _cached_draw

        # SOJ early check: compute session open before the conviction block so
        # _soj_pts_early is available for the full conviction block below.
        # The session open and direction match what _profile_score would compute.
        # Also compute daily open early for the P26 dual-reference check.
        _sess_name_early = "London Open" if _is_london else ("New York AM" if _is_ny else None)
        _session_open_early = self._session_open(pair, _sess_name_early, t) if _sess_name_early else None
        _daily_open_early = self._daily_open(pair, t)
        _soj_pts_early = 0
        if config.SOJ_SWEEP_ENABLED and _session_open_early is not None:
            _soj_pts_early = self._session_open_judas_sweep(
                pair, direction, _session_open_early, t,
                daily_open_price=_daily_open_early)

        # Draw-to-liquidity continuation (config.DRAW_CONT_ENABLED): is there an
        # unswept PDH/PDL a near distance ahead in the trade direction? If so this
        # trade can run WITH the draw toward that pool — a continuation, not a
        # reversal — and is a candidate for the 0/3 gate exemption below.
        _is_draw_cont = False
        if (config.DRAW_CONT_ENABLED and _draw_score == 0 and not _is_breakout
                and self._unswept_pdliq_target(pair, direction, cur_price, t) is not None):
            _is_draw_cont = True

        if _draw_score == 0 and not _is_breakout:
            if _is_ny_cont and config.NY_CONTINUATION_GATE_EXEMPT:
                # Exempt: this runs WITH the daily draw (continuation of London's
                # move), not a fresh reversal — the 0/3 rule is reversal logic.
                g["ny_continuation_exempt"] = g.get("ny_continuation_exempt", 0) + 1
            elif _is_draw_cont:
                # Exempt: continuation toward an unswept near PDH/PDL pool. Runs WITH
                # the draw (scores 0 on the inverted reversal cascade by design), MSS
                # 2-of-3 already confirmed the structure. Earns breakout-style credit.
                g["draw_cont_confirmed"] = g.get("draw_cont_confirmed", 0) + 1
            else:
                if _is_ny_cont:
                    # Measure how many NY-AM continuations the reversal gate kills.
                    g["ny_continuation_gated"] = g.get("ny_continuation_gated", 0) + 1
                g["htf_draw_counter"] += 1
                self._log_reject(t, pair, direction, "no HTF draw (0/3 cascade, not a breakout)")
                return   # hard gate: no HTF draw alignment → skip (reversal logic).
            # Breakout continuations are exempt: a strong continuation move runs
            # WITH the HTF, which scores low on the inverted draw cascade by design.
        # 2a variants gated entirely — move too extended by the time synthetic confirms.
        # 2a_h4: H1 flat but H4 EURGBP confirms EUR>GBP (PF 0.01, WR 25%). Gate.
        # 2a_ip: H1+H4 both flat, synthetic momentum fires — even more extended. Gate.
        if _im_scenario in ("2a_h4", "2a_ip"):
            self._log_reject(t, pair, direction, f"{_im_scenario} scenario gated (PF≤0.01)")
            return
        if _im_scenario in ("2a", "2a_h4", "2a_ip") and _draw_score == 3:
            self._log_reject(t, pair, direction, "2a at 3/3 draw (over-extended)")
            return
        # 2a London = price entering London already deep into a EURUSD rally (PF 0.84).
        if _im_scenario in ("2a", "2a_h4", "2a_ip") and _is_london:
            self._log_reject(t, pair, direction, "2a in London (chasing the spike)")
            return
        # N-long_h4: H1 AUDNZD flat, H4 confirms NZD strong → NZDUSD long.
        # WR 0% in both IS (2022-23) and OOS (2024-25). Clear loser — gate entirely.
        if _im_scenario == "N-long_h4":
            return
        conviction += _draw_score
        if _draw_score == 3:
            g["htf_draw_full_cascade"] += 1
        elif _draw_score > 0:
            g["htf_draw_partial"] += 1
        # Breakout continuations earn conviction from the triple-confirmation instead
        # of the (low/zero) inverted-draw score — the intermarket agreement IS the edge.
        if _is_breakout:
            conviction += config.BREAKOUT_CONVICTION
        # Draw-continuation earns the same continuation credit — the unswept near
        # pool is the draw the move is delivering into (replaces the 0 draw score).
        if _is_draw_cont:
            conviction += config.BREAKOUT_CONVICTION

        # Open-level profile score: daily/weekly/session opens agreeing (0-1).
        # _session_open is returned from the same call so we don't duplicate mp_session_open.
        p_score, _session_open = self._profile_score(pair, direction, cur_price, t)
        conviction += min(p_score, 1)

        # AMD on M15 (0-1): Asia/London consolidation + manipulation sweep
        bars15 = self.bars_up_to(pair, "15T", t)
        _amd_price = bars15[-1].Close if bars15 else None
        amd = detect_amd_setup(bars15, pair,
                               max_range_pips=self._amd_max_range(pair, _amd_price))
        amd_score = 0
        # AMD analytics: accumulation shape + stop-run (manipulation) depth per trade.
        _amd_range_pips = _amd_range_bars = None
        _amd_touches_hi = _amd_touches_lo = None
        _amd_sweep_side = ""
        _amd_sweep_depth = None
        _amd_sweep_aligned = None
        _amd_accum_start = _amd_accum_end = _amd_sweep_time = None
        _amd_sweep_time_m5 = None
        _amd_swept_pdliq = None
        _amd_entry_zone = ""
        _amd_liq_run = ""
        if amd is not None:
            rng, sweep_dir = amd
            g["consolidation_found"] += 1
            _amd_pip = pip_size(pair)
            _amd_range_pips = round(rng.width / _amd_pip, 1)
            _amd_range_bars = rng.length_bars
            _amd_touches_hi = rng.touches_high
            _amd_touches_lo = rng.touches_low
            _amd_sweep_aligned = (sweep_dir == direction)
            _post = bars15[rng.end_idx:]
            if sweep_dir > 0:          # low extreme swept (bullish manipulation)
                _amd_sweep_side = "low"
                _amd_sweep_depth = (round((rng.low - min(c.Low for c in _post)) / _amd_pip, 1)
                                    if _post else 0.0)
            else:                      # high extreme swept (bearish manipulation)
                _amd_sweep_side = "high"
                _amd_sweep_depth = (round((max(c.High for c in _post) - rng.high) / _amd_pip, 1)
                                    if _post else 0.0)
            # Phase timestamps (backtest only) for the tick-volume study: map the
            # M15 bar indices to UTC via tf_index. Guarded — live has no tf_index.
            _m15_idx = getattr(self, "tf_index", {}).get((pair, "15T"))
            if _m15_idx is not None and rng.end_idx <= len(bars15):
                try:
                    _amd_accum_start = str(_m15_idx[rng.start_idx])
                    _amd_accum_end   = str(_m15_idx[rng.end_idx - 1])
                    if _post:
                        _sw_off = (min(range(len(_post)), key=lambda i: _post[i].Low)
                                   if sweep_dir > 0 else
                                   max(range(len(_post)), key=lambda i: _post[i].High))
                        _amd_sweep_time = str(_m15_idx[rng.end_idx + _sw_off])
                        # Option B: pin the sweep to M5 resolution — the M5 bar
                        # inside the M15 sweep bar that actually made the extreme.
                        _m5_idx = getattr(self, "tf_index", {}).get((pair, "5T"))
                        _m5_bars = getattr(self, "tf_bars", {}).get((pair, "5T"))
                        if _m5_idx is not None and _m5_bars is not None:
                            _sw_ts = pd.Timestamp(_amd_sweep_time)
                            _lo = _m5_idx.searchsorted(_sw_ts, side="left")
                            _hi = _m5_idx.searchsorted(
                                _sw_ts + pd.Timedelta(minutes=15), side="left")
                            if _hi > _lo:
                                _seg = _m5_bars[_lo:_hi]
                                _k = (min(range(len(_seg)), key=lambda i: _seg[i].Low)
                                      if sweep_dir > 0 else
                                      max(range(len(_seg)), key=lambda i: _seg[i].High))
                                _amd_sweep_time_m5 = str(_m5_idx[_lo + _k])
                except (IndexError, KeyError):
                    pass
            if sweep_dir == direction:
                amd_score = 1
                conviction += 1
                g["manipulation_correct_dir"] += 1
            # Judas detected — mark it sticky for this session's profile only.
            # Key is session-specific so London's Judas doesn't bleed into NY.
            _judas_key = (pair, _session_label, _ny_dt.date())
            self._judas_seen[_judas_key] = True

        # PDH/PDL context (option B): did the manipulation run previous-day
        # liquidity, and is the entry in premium or discount vs the prior-day mid?
        _mp = self._market_profile(pair, t)
        if _mp:
            _amd_entry_zone = "premium" if cur_price > _mp["pdm"] else "discount"
            if amd is not None:
                _tol = 5 * _amd_pip
                _swept_lvl = rng.low if sweep_dir > 0 else rng.high
                _amd_swept_pdliq = (abs(_swept_lvl - _mp["pdh"]) <= _tol or
                                    abs(_swept_lvl - _mp["pdl"]) <= _tol)
                _amd_liq_run = self._classify_liq_run(
                    _swept_lvl, _amd_sweep_side, _mp, pair, t, bars15, _amd_pip)

        # P26 — Session-open + daily-open pattern (Judas sweep / pullback retest):
        # Session open (03:00 London / 07:00 NY ET) and daily open (00:00 UTC) are
        # both AMD equilibrium references. +1 per reference that confirms a Judas
        # or pullback. Max +2 (both references active), min +1 (one reference).
        # Reuse early-computed values (before the draw gate, same logic).
        _soj_pts = _soj_pts_early
        _soj_type = ""
        if _soj_pts:
            conviction += _soj_pts
            if _soj_pts >= 2:
                # Both session open and daily open confirmed the pattern.
                g["soj_judas"] = g.get("soj_judas", 0) + 1
                _soj_type = "dual"
            else:
                # Single reference (session open or daily open) confirmed.
                g["soj_retest"] = g.get("soj_retest", 0) + 1
                _soj_type = "single"
            g["soj_sweep"] = g.get("soj_sweep", 0) + 1
            _judas_key = (pair, _session_label, _ny_dt.date())
            self._judas_seen[_judas_key] = True
        _soj_sweep = _soj_pts > 0

        # HTF FVG 50% draw (P9): price consolidating at the equilibrium of an
        # unmitigated H4/D1/W1 FVG aligned with the trade. These gaps are the
        # bigger-timeframe draw on liquidity continuation moves deliver into —
        # the AMD cycle forming here is anchored to a real HTF delivery zone. +1.
        _htf_fvg_pts, _htf_fvg_tf = self._htf_fvg_conviction(pair, direction, cur_price, t)
        if _htf_fvg_pts:
            conviction += _htf_fvg_pts
            g["htf_fvg_5050_hit"] += 1
        # PM gate condition 3 (reserved): HTF FVG active = external draw still in play.
        # Tested triple gate (EURUSD + High news + HTF FVG) and 2-condition (EURUSD +
        # High news): both produced 0 trades in 4yr. High-impact news during 13:30-16:00
        # ET never co-occurs with a passing DXY/conviction check in this dataset.
        # Gate left as analytics comment — do not enable without new data evidence.
        # if _is_pm and not _htf_fvg_pts:
        #     return

        # DXY level context (P13): DXY's own W/D/H4 FVG in its direction means the
        # dollar itself has an undelivered HTF draw — the move has structural room.
        # When DXY is sitting at the 50% of its own gap, every correlated pair benefits.
        _dxy_fvg_pts, _dxy_fvg_tf = self._dxy_htf_context(direction, t)
        if _dxy_fvg_pts:
            conviction += _dxy_fvg_pts
            g["dxy_fvg_room"] = g.get("dxy_fvg_room", 0) + 1

        # CRT Turtle Soup (P19): HTF Judas sweep of the prior H4/D candle range.
        # A wick beyond CRT H/L that closes back inside = manipulation on the bigger
        # TF — the same Judas logic that drives our M15 entry, one tier higher.
        # D1 sweep = +2 conviction, H4 sweep = +1 conviction (analytics-first).
        _crt_pts, _crt_tf = self._htf_crt_sweep(pair, direction, cur_price, t)
        if _crt_pts:
            conviction += _crt_pts
            g["crt_turtle_soup"] = g.get("crt_turtle_soup", 0) + 1

        # Bonds/yields dollar-bias (OFF by default). A short on any X/USD pair is a
        # bet on dollar STRENGTH (+1); a long is dollar WEAKNESS (-1). When yields'
        # own daily structure agrees with that dollar direction, the rates market
        # confirms the trade — the sizing lever below acts on it. File is only read
        # when enabled, so this is byte-identical when off.
        _bond_confirm = False
        if config.BONDS_BIAS_ENABLED:
            _dollar_dir = -direction
            _yld_dir = self._load_bond_bias().get(str(now.date()))
            _bond_confirm = (_yld_dir is not None and _yld_dir != 0
                             and _yld_dir == _dollar_dir)
            if _bond_confirm:
                g["bond_confirm"] = g.get("bond_confirm", 0) + 1

        # H1 EURUSD↔GBPUSD SMT at the reversal — the divergence that starts the
        # Market Maker distribution (one pair sweeps, the other fails to confirm).
        # Only computed when the MM model is active, so the default path is untouched
        # (cost-free) and its results stay byte-identical.
        _htf_smt = False
        if config.MM_CONTINUATION_ENABLED or config.MM_HTF_SMT_REQUIRED:
            _htf_smt = self._htf_pair_smt(pair, direction, t)
            if _htf_smt:
                g["htf_smt"] = g.get("htf_smt", 0) + 1

        # NWOG (New Week Opening Gap): price delivering into the weekend gap's 50%
        # (consequent encroachment) aligned with the trade. The NWOG is an ICT HTF
        # PD array / draw on liquidity — a gap-up week supports longs, gap-down
        # supports shorts. +NWOG_CONVICTION_PTS, and (below) NWOG bounds/CE are
        # added as confluence + target candidates via _find_target.
        _nwog_pts, _nwog_tf = self._nwog_conviction(pair, direction, cur_price, t)
        if _nwog_pts:
            conviction += _nwog_pts
            g["nwog_ce_hit"] = g.get("nwog_ce_hit", 0) + 1

        # Precise ICT SMT (index pairs): index-vs-index (positive) + index-vs-dollar
        # (inverse) divergence at the swept level. Adds conviction; if
        # INDEX_SMT_REQUIRED, an index entry must show at least one SMT confirmation.
        _smt = self._index_smt(pair, direction, t)
        if _smt["points"]:
            conviction += _smt["points"]
            if _smt["idx_smt"]:
                g["smt_index"] = g.get("smt_index", 0) + 1
            if _smt["dxy_smt"]:
                g["smt_dollar"] = g.get("smt_dollar", 0) + 1
        if (config.INDEX_SMT_REQUIRED and config.INDICES_ENABLED
                and pair in config.INDEX_PAIRS
                and not (_smt["idx_smt"] or _smt["dxy_smt"])):
            self._log_reject(t, pair, direction, "index SMT not confirmed")
            return

        # Ep 12 market structure: fractal LTH/ITH/STH read across W→M15, coupled
        # with the inverted draw cascade. Higher-TF intermediate structure agreeing
        # with the trade = a bigger draw on liquidity in our favour → more conviction.
        # The minor-sweep flag identifies Judas continuations (STH/STL swept but the
        # ITH/ITL still intact = trend continues). Analytics columns recorded below.
        _ms = self._structure_conviction(pair, direction, t)
        if _ms["points"]:
            conviction += _ms["points"]
            g["mstruct_align"] = g.get("mstruct_align", 0) + 1
        if _ms["minor_sweep"]:
            g["mstruct_minor_sweep"] = g.get("mstruct_minor_sweep", 0) + 1

        # ── Session-phase AMD cycle tracking ──────────────────────────────────
        # ICT price delivery:  Asian accumulation → London Judas (manipulation)
        #                       → Distribution / breakout continuation.
        # If the Judas window closes with no sweep, the fallback entry is the
        # triple-confirmed breakout continuation using the bigger-TF draw.
        # Phases are keyed by (pair, NY date) so each trading day starts fresh.
        # Session profiles are independent: each session tracks its own AMD cycle.
        # London profile: london_watch → london_judas (sweep seen) / london_breakout (no sweep)
        # NY profile:     ny_judas (own sweep seen) / ny_extend (no own sweep — handover continuation)
        _judas_key   = (pair, _session_label, _ny_dt.date())
        _judas_fired = self._judas_seen.get(_judas_key, False)
        _ny_hhmm     = _ny_dt.hour * 100 + _ny_dt.minute

        if _is_ny:
            _session_phase = "ny_judas" if _judas_fired else "ny_extend"
        elif _is_pm:
            # PM: position squaring / mean-reversion flow (Tier 2 banks + funds).
            # If PM has its own Judas sweep the reversal is valid; otherwise it's squaring.
            _session_phase = "pm_reversal" if _judas_fired else "pm_squaring"
        elif _is_london:
            if _judas_fired:
                _session_phase = "london_judas"
            elif _ny_hhmm < 330:
                _session_phase = "london_watch"    # prime Judas sweep window (03:00–03:30)
            else:
                _session_phase = "london_breakout" # fallback continuation (03:30–05:00)
        else:
            _session_phase = "accumulation"        # Asian session — entries blocked by KZ

        # Session phase is tracked for analytics but NOT used as a hard gate.
        # breakout_eligible (PF 0.13) and ny_extend (PF 0.16) have negative arithmetic
        # P&L in isolation, but their wins cluster at high-equity periods where the
        # compounding path dependency means removing them cuts final equity by ~R31M.
        # In a compounding strategy, TWRR contribution > arithmetic P&L — these phases stay open.
        g[f"phase_{_session_phase}"] = g.get(f"phase_{_session_phase}", 0) + 1

        # P9 reversal filter: skip Judas reversals that fade INTO an unmitigated HTF FVG
        # in the opposing direction. An undelivered HTF gap above price (for a short) or
        # below price (for a long) is a draw that must be filled before the reversal can
        # work — the market will run to it first, stopping out the early fade.
        # Breakout continuations are exempt: they run WITH the HTF draw, not against it.
        if config.HTF_FVG_REVERSAL_FILTER and not _is_breakout:
            if self._htf_fvg_opposing(pair, direction, cur_price, t):
                g["htf_fvg_reversal_blocked"] = g.get("htf_fvg_reversal_blocked", 0) + 1
                return

        # M1 fractal structure is captured via _get_limit_entry (fvg_m1/ob_m1/
        # breaker_m1) — same AMD concept at execution speed without the O(n³)
        # consolidation scan cost that would stall the main loop.

        # OTE zone: bonus conviction when price is in 62-79% retrace (M15 or H1 swing).
        # OTE defines profit POTENTIAL (Fib extension targets), not an entry filter.
        ote_hit = (
            in_ote(cur_price, bars15, direction,
                   lookback=config.SWING_LOOKBACK, pip_tol=3 * pip_v)
            or in_ote(cur_price, bars1h, direction,
                      lookback=config.SWING_LOOKBACK // 2, pip_tol=3 * pip_v)
        )
        if ote_hit:
            conviction += 1
            g["ote_zone"] += 1

        # CHoCH: bias on the PRIOR window was OPPOSITE, confirming reversal (0-1)
        choch = self._choch_score(pair, direction, t)
        if choch:
            conviction += 1
            g["choch_confirmed"] += 1

        # ── Game-theory bonuses ──────────────────────────────────────────────
        # 1. Retail-pool sweep: equal highs/lows actually swept in last 20 bars.
        #    Requires price to have PIERCED the level (stop-hunt) then recovered —
        #    not just "equal lows exist and price is above them" (too loose).
        eq_lows  = find_equal_lows(bars15,  pair)
        eq_highs = find_equal_highs(bars15, pair)
        recent15 = bars15[-20:] if len(bars15) >= 20 else bars15
        if direction > 0 and eq_lows:
            level = eq_lows[-1]
            swept  = any(b.Low < level for b in recent15)
            recovered = cur_price > level
            if swept and recovered:
                conviction += 1
                g["gt_pool_sweep"] = g.get("gt_pool_sweep", 0) + 1
        elif direction < 0 and eq_highs:
            level = eq_highs[-1]
            swept  = any(b.High > level for b in recent15)
            recovered = cur_price < level
            if swept and recovered:
                conviction += 1
                g["gt_pool_sweep"] = g.get("gt_pool_sweep", 0) + 1

        # 2. Strong displacement wick: last M5 bar's wick ≥ 60% of bar range.
        #    Aggressive institutional delivery bar — confirms the directional push.
        _bars5_gt = self.bars_up_to(pair, "5T", t)
        if _bars5_gt:
            lb = _bars5_gt[-1]
            bar_range = lb.High - lb.Low
            if bar_range > 0:
                if direction > 0:
                    lower_wick = lb.Close - lb.Low
                    if lower_wick / bar_range >= 0.60:
                        conviction += 1
                        g["gt_disp_wick"] = g.get("gt_disp_wick", 0) + 1
                else:
                    upper_wick = lb.High - lb.Close
                    if upper_wick / bar_range >= 0.60:
                        conviction += 1
                        g["gt_disp_wick"] = g.get("gt_disp_wick", 0) + 1

        # 3. ICT macro window: entry fires inside a known high-probability delivery
        #    window (London 02:33–03:00, 10am macro 09:50–10:10, 1pm macro 12:50–13:10,
        #    NY close macro 15:15–15:45 — all New York time).
        ny_hour   = (t.hour - 5) % 24   # UTC-5 approx (EST)
        ny_minute = t.minute
        ny_hhmm   = ny_hour * 100 + ny_minute
        _macro_windows = [(233, 300), (950, 1010), (1250, 1310), (1515, 1545)]
        if any(lo <= ny_hhmm <= hi for lo, hi in _macro_windows):
            conviction += 1
            g["gt_macro_window"] = g.get("gt_macro_window", 0) + 1

        # 4. Judas reversal: NY AM session is reversing London's first-hour direction.
        #    Strongest game-theory setup — NY is the smart-money correction of London manipulation.
        kz = current_killzone(t, pair)
        if kz and "New York" in kz and len(bars1h) >= 3:
            london_dir = 1 if bars1h[-2].Close > bars1h[-3].Close else -1
            if london_dir != direction:
                conviction += 1
                g["gt_judas_reversal"] = g.get("gt_judas_reversal", 0) + 1

        # 4c. NY continuation: NY AM is extending London's direction (momentum run).
        #     Not a reversal — price is running WITH London, usually a news-driven
        #     distribution move toward the weekly target.
        if _is_ny and len(bars1h) >= 3:
            _london_dir = 1 if bars1h[-2].Close > bars1h[-3].Close else -1
            if _london_dir == direction:
                conviction += 1
                g["ny_continuation"] += 1

        # 4b. Intermarket Judas-sweep divergence: DXY sweeps a liquidity level and
        #     one of EURUSD/GBPUSD fails to follow. The failing pair held its ground
        #     against the manipulation — when DXY reverses it delivers the strongest
        #     move. Only credit when the divergence names THIS pair in THIS direction.
        dxy15 = self._dxy_bars("15T", t)
        eu15  = self.bars_up_to("EURUSD", "15T", t)
        gu15  = self.bars_up_to("GBPUSD", "15T", t)
        if dxy15 and eu15 and gu15:
            div = judas_sweep_divergence(dxy15, eu15, gu15)
            if div is not None and div[0] == pair and div[1] == direction:
                conviction += 1
                g["judas_divergence"] += 1

        # 5. Market Profile — prior-day discount/premium bonus.
        #    Long below PDM = entering in discount; short above PDM = premium (+1).
        #    Deep extreme (within 20% of PDH-PDL range) adds another +1.
        mp = self._market_profile(pair, t)
        if mp:
            _mp_price = _bars5_gt[-1].Close if _bars5_gt else cur_price
            pdm, pdh, pdl = mp["pdm"], mp["pdh"], mp["pdl"]
            pd_range = pdh - pdl

            if (direction > 0 and _mp_price < pdm) or (direction < 0 and _mp_price > pdm):
                conviction += 1
                g["gt_mp_discount"] = g.get("gt_mp_discount", 0) + 1

            if pd_range > 0:
                if (direction > 0 and _mp_price <= pdl + pd_range * 0.20) or \
                   (direction < 0 and _mp_price >= pdh - pd_range * 0.20):
                    conviction += 1
                    g["gt_mp_extreme"] = g.get("gt_mp_extreme", 0) + 1
        # ─────────────────────────────────────────────────────────────────────

        min_conv = config.MIN_CONVICTION_NY if _is_ny else config.MIN_CONVICTION
        if conviction < min_conv:
            g["low_conviction"] += 1
            return

        # Max legs this trade may pyramid to based on conviction
        if conviction <= 2:
            max_legs = 1
        elif conviction <= 4:
            max_legs = 2
        else:
            max_legs = config.MAX_LEGS
        # ─────────────────────────────────────────────────────────────────────

        bars5 = self.bars_up_to(pair, "5T", t)
        if not bars5:
            return
        cur_price = bars5[-1].Close

        # Judas-swing confirmation: price below open for longs / above for shorts (+1).
        # _session_open was already computed inside _profile_score above.
        if _session_open is not None:
            if (direction > 0 and cur_price < _session_open) or (direction < 0 and cur_price > _session_open):
                conviction += 1
                if conviction > 4:
                    max_legs = config.MAX_LEGS
                elif conviction > 2:
                    max_legs = max(max_legs, 2)

        # Pattern detection with counter-trend confirmation.
        # _get_limit_entry finds the nearest valid pattern level that price is
        # still moving TOWARD (direction > 0 → level below price; direction < 0
        # → level above price).  We use that level only for the STOP placement;
        # the actual fill is a market order at cur_price (bar close).
        bars1m = self.bars_up_to(pair, "1T", t, max_bars=120)
        _level, stop, pattern_tag = self._get_limit_entry(
            bars5, bars15, bars1h, pair, direction, cur_price, bars1m=bars1m
        )
        if pattern_tag is None:
            return
        # In scenario 2a, entering on an H1 FVG means EURUSD has already moved
        # 60-100 pips into the confirmed rally before the entry triggers (WR 14.3%).
        # Only M5/M15 precision entries are valid in 2a — the move is too mature for H1.
        if _im_scenario in ("2a", "2a_h4", "2a_ip") and pattern_tag == "fvg_h1":
            return
        g["m5_fvg_correct_dir"] += 1

        pip = pip_size(pair)
        # Simulate spread + slippage: worsen entry price by (half-spread + slippage).
        # During high-impact news the broker widens the spread; model that realistically.
        _spread = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        if news_impact == "High":
            _spread = max(_spread, config.NEWS_HIGH_SPREAD_PIPS)
        _friction = (_spread / 2 + config.SLIPPAGE_PIPS) * pip
        entry = cur_price + direction * _friction   # market order fill with friction

        # Stop placement: anchor to M1 market structure (Episode 12 STL/STH). The
        # entry pattern came from M5/M15/H1; the STOP comes from the nearest 1-minute
        # swing, which keeps it naturally tight. Fall back to the pattern stop if no
        # valid M1 swing is found.
        # Stage 3 (toggle): prefer the intact INTERMEDIATE swing (ITL/ITH) so the
        # stop survives a minor short-term sweep; fall back to the STL/STH stop.
        _stop_reason = "pattern (FVG/OB boundary)"   # default: pattern-invalidation stop
        _struct_stop = None
        if config.STRUCTURE_STOP_ENABLED:
            _struct_stop = self._structure_stop(pair, direction, entry, pip, t)
        if _struct_stop is not None:
            stop = _struct_stop
            _stop_reason = "structural swing (intact ITL/ITH)"
            g["structure_stop_used"] = g.get("structure_stop_used", 0) + 1
        else:
            _m1_stop = self._m1_structure_stop(bars1m, direction, entry, pip)
            if _m1_stop is not None:
                stop = _m1_stop
                _stop_reason = "M1 swing"
                g["m1_stop_used"] = g.get("m1_stop_used", 0) + 1

        # Point instruments (gold, indices): stop is placed PURELY by structure — no
        # fixed-pip news override and no universal cap (both are FX conventions; a
        # ~$10 fixed stop is far too tight for a dollar/point-priced instrument and
        # would over-size the position). Risk-based sizing scales the position down
        # for the wider structural stop.
        _is_gold = self._is_point_instrument(pair)

        # High-impact news nearby: override to fixed 10-pip stop (protects against
        # spread widening while still trading the news catalyst). Not for point instruments.
        if news_impact == "High" and not _is_gold:
            stop = entry - config.FIXED_STOP_PIPS * pip if direction > 0 \
                   else entry + config.FIXED_STOP_PIPS * pip
            _stop_reason = "fixed 10-pip (high-impact news)"

        # Universal stop cap: never risk more than FIXED_STOP_PIPS on any trade.
        # The structural stop can sit 30–50 pips away, which at the broker min-lot
        # floor produces 10%+ single-trade losses at small equity. Measure the cap
        # from the spread-adjusted `entry` (the real fill) so the 10-pip buffer is
        # true adverse room, not eaten by the spread. Tighter structural stops are
        # left as-is; only stops wider than the cap are pulled in. SKIPPED for gold.
        if not _is_gold:
            _max_stop = config.FIXED_STOP_PIPS * pip
            if abs(entry - stop) > _max_stop:
                stop = entry - _max_stop if direction > 0 else entry + _max_stop
                g["stop_capped_10pip"] = g.get("stop_capped_10pip", 0) + 1

        # P20: escalate to premium liquidity draws when high-conviction signals fire.
        # CRT-D/W (HTF Judas on Daily/Weekly), draw≥2 (2+ HTF levels agree), or
        # mstruct_minor_sweep (M15 Judas sweep with ITH/ITL still intact) each trigger.
        _escalate_tgt = (
            config.TARGET_ESCALATE_ENABLED and (
                _crt_tf in ("D", "W") or
                _draw_score >= config.TARGET_ESCALATE_MIN_DRAW or
                _ms.get("minor_sweep", False)
            )
        )
        _tgt = self._find_target(pair, direction, t, entry, stop=stop, escalate=_escalate_tgt)
        if _tgt is None:
            return
        target, target_type, _target_score, _tgt_escalated = _tgt
        g["target_found"] += 1
        # Target confluence conviction: ≥3 independent source families agreeing on
        # the TP area adds +1 conviction; ≥4 adds +2 (max +2 from this signal).
        # Scores 1-2 are analytics-only — backtest shows PF<1 at those tiers.
        if _target_score >= 4:
            conviction += 2
        elif _target_score >= 3:
            conviction += 1
        # Re-evaluate max_legs to incorporate the confluence conviction bump.
        # (max_legs was set before _find_target; this upgrades borderline trades.)
        if conviction > 4:
            max_legs = config.MAX_LEGS
        elif conviction > 2:
            max_legs = max(max_legs, 2)

        reward_pips = abs(target - entry) / pip
        if reward_pips < self._min_pips_target():
            self.gate["entry_blocked_min_target"] = self.gate.get("entry_blocked_min_target", 0) + 1
            self._log_reject(t, pair, direction,
                             f"target only {reward_pips:.0f} pips (< {self._min_pips_target()} floor)")
            return
        g["rr_ok"] += 1

        # ZAR equity → USD for position sizing; floor at leg-1 lot for current tier.
        equity_usd = self._size_equity() / config.USD_ZAR
        risk_units = int(position_size(equity_usd, entry, stop, pair))
        tier_lots  = self._pyramid_lots()
        min_units  = int(tier_lots[0] * self._contract_units(pair))
        # Point instruments can trade at a fraction of FX size (GOLD_SIZE_MULT /
        # INDEX_SIZE_MULT) to cap drawdown contribution — the edge can be real but
        # cluster DD. Applied to both the risk-based size and the floor so they can
        # size below the FX min-lot.
        _pt_mult = 1.0
        if config.GOLD_ENABLED and pair == config.GOLD_PAIR:
            _pt_mult = config.GOLD_SIZE_MULT
        elif config.INDICES_ENABLED and pair in config.INDEX_PAIRS:
            _pt_mult = config.INDEX_SIZE_MULT
        if _pt_mult != 1.0:
            risk_units = int(risk_units * _pt_mult)
            min_units  = max(1, int(min_units * _pt_mult))
        units = max(risk_units, min_units)
        # Draw-weighted sizing: scale up the highest-edge setups (3/3 cascade, PF 6.17)
        # so they carry more capital. Applied to the risk-based size, then floored at
        # the min lot so a multiplier never sizes below a tradeable position. Only
        # engages above DRAW_SIZE_MIN_EQUITY — the fragile early account trades flat.
        _draw_mult = config.DRAW_SIZE_MULT.get(_draw_score, 1.0)
        if _draw_mult != 1.0 and self.equity >= config.DRAW_SIZE_MIN_EQUITY:
            units = max(int(units * _draw_mult), min_units)
        # P9 sizing boost: breakout/continuation anchored at HTF FVG 50% midpoint.
        # The FVG is the HTF draw on liquidity — the AMD cycle forming exactly at the
        # gap's equilibrium is the highest-conviction continuation setup. Scale up,
        # same equity floor as the draw-cascade multiplier.
        if _is_breakout and _htf_fvg_pts and self.equity >= config.DRAW_SIZE_MIN_EQUITY:
            units = max(int(units * config.HTF_FVG_BREAKOUT_MULT), min_units)
            g["htf_fvg_breakout_sized"] = g.get("htf_fvg_breakout_sized", 0) + 1
        # Target confluence sizing: when the chosen TP has score≥3 (fib + ITH/ITL +
        # FVG/OB all pointing at the same price), multiple institutional frameworks
        # agree this is the draw — scale up. Same equity floor as draw-cascade.
        if (_target_score >= config.TARGET_SCORE_MULT_THRESHOLD
                and self.equity >= config.DRAW_SIZE_MIN_EQUITY):
            units = max(int(units * config.TARGET_SCORE_MULT), min_units)
            g["target_score_sized"] = g.get("target_score_sized", 0) + 1
        # P19 CRT sizing boost: H4 Turtle Soup is the HTF Judas swing — the bigger-TF
        # manipulation phase already fired in our direction. It's the highest-WR
        # HTF-timing bucket (WR 50.4%), so scale it up like the P9/P18 buckets. Gated
        # to the H4 sweep only (CRT_SWEEP_MULT_TF); same equity floor as draw-cascade.
        if (_crt_tf == config.CRT_SWEEP_MULT_TF and config.CRT_SWEEP_MULT != 1.0
                and self.equity >= config.DRAW_SIZE_MIN_EQUITY):
            units = max(int(units * config.CRT_SWEEP_MULT), min_units)
            g["crt_sweep_sized"] = g.get("crt_sweep_sized", 0) + 1
        # PDH/PDL-sweep sizing lever: when the manipulation ran previous-day
        # liquidity (sweep within ~5 pips of PDH/PDL), the AMD raid hit a genuine
        # resting-liquidity pool — the setup-quality bucket that held WR 55%/53%
        # above the ~45% baseline in BOTH years (AMD tick-vol study §9). Price-
        # based (no tick data) so it applies across all pairs/years. Same 1.25×
        # magnitude and R3k floor as P18/P19. Default off (mult=1.0) until the
        # full-backtest IS/OOS + MaxDD validation passes.
        if (config.PDLIQ_SWEEP_MULT != 1.0 and _amd_swept_pdliq
                and self.equity >= config.DRAW_SIZE_MIN_EQUITY):
            units = max(int(units * config.PDLIQ_SWEEP_MULT), min_units)
            g["pdliq_sweep_sized"] = g.get("pdliq_sweep_sized", 0) + 1
        # Bonds/yields sizing lever: yields' daily structure confirms the trade's
        # dollar direction (rates lead the dollar). Same 1.25× magnitude + R3k floor
        # as the P18/P19/P41 buckets. Default off (mult=1.0) until run_bonds.sh is
        # GREEN and run_bonds_validation.sh passes the full + IS/OOS gate.
        if (config.BONDS_SIZE_MULT != 1.0 and _bond_confirm
                and self.equity >= config.DRAW_SIZE_MIN_EQUITY):
            units = max(int(units * config.BONDS_SIZE_MULT), min_units)
            g["bond_bias_sized"] = g.get("bond_bias_sized", 0) + 1
        # Entry-type tag (computed here so the P40 modulator below can read it;
        # also reused at fill time). news upgrade may already have set max_legs.
        base_type  = "amd" if amd_score else "mss"
        entry_tag  = "news" if news_impact == "High" else base_type
        entry_type = f"{entry_tag}_{pattern_tag}"
        # P40 conditional-volume modulator: high-vol FVG entries lose more (size
        # down) / high-vol OB entries win more (size up). Only fires where tick
        # data exists (EU/GU 2022+2024); neutral (1.0) otherwise. No equity floor —
        # it's a quality read, not a compounding-only lever. Validation-gated.
        if config.USE_CONDITIONAL_VOLUME:
            _vmod = get_volume_modifier(entry_type, self._entry_friction(pair, t))
            if _vmod != 1.0:
                units = max(int(units * _vmod), min_units)
                g["vol_mod_applied"] = g.get("vol_mod_applied", 0) + 1
        # P10 London-Judas priority (REVERTED — downsize multiplier defaults to 1.0,
        # so this is a no-op + analytics counter). Hypothesis was that a NY-AM breakout
        # on a pair whose London Judas already fired today is the weaker echo and should
        # be sized down. Backtest disproved it (lost R5.84M / 4yr, no MaxDD benefit —
        # the echoes still compound). Counter retained to measure how often the
        # same-day London-Judas → NY-breakout echo occurs.
        if (_is_breakout and _is_ny
                and self._london_judas_open.get((pair, _ny_dt.date()), False)):
            if config.LONDON_JUDAS_NY_BREAKOUT_DOWNSIZE != 1.0:
                units = max(int(units * config.LONDON_JUDAS_NY_BREAKOUT_DOWNSIZE), min_units)
            g["london_judas_ny_echo"] = g.get("london_judas_ny_echo", 0) + 1
        if units == 0:
            return
        g["units_nonzero"] += 1

        # Max-risk-per-trade guard: when the min-lot floor forces a position whose
        # stop would cost more than MAX_RISK_PER_TRADE_PCT of equity, the account is
        # too small to trade this stop width safely — skip it. Prevents the 10%+
        # single-trade losses that build the early-account drawdown.
        _risk_cap = self.equity * (config.MAX_RISK_PER_TRADE_PCT / 100.0)
        trade_risk_zar = units * abs(entry - stop) * config.USD_ZAR
        if trade_risk_zar > _risk_cap:
            if config.RISK_CAP_HALVE:
                # size DOWN (halve to the broker min) so the setup is TAKEN, not skipped
                _floor = max(1, int(config.MIN_LOT_SIZE * self._contract_units(pair)))
                while units > _floor and units * abs(entry - stop) * config.USD_ZAR > _risk_cap:
                    units = max(_floor, units // 2)
                trade_risk_zar = units * abs(entry - stop) * config.USD_ZAR
                g["risk_cap_halved"] = g.get("risk_cap_halved", 0) + 1
            else:
                g["risk_cap_skip"] = g.get("risk_cap_skip", 0) + 1
                self._log_reject(t, pair, direction, "risk > max-per-trade cap (stop too wide for equity)")
                return
        g["risk_cap_ok"] = g.get("risk_cap_ok", 0) + 1

        # High-impact news = distribution catalyst: upgrade to full pyramid regardless
        # of conviction score.  News drives speed, direction, and strength — this is
        # the highest-probability setup for reaching target fast.
        if news_impact == "High":
            max_legs = config.MAX_LEGS

        # Market order: fill immediately at current bar close. (entry_type computed
        # above, before the P40 sizing block.)
        # Session-open side analytics tag (reuse _session_open computed above).
        if _session_open is None:
            _so_side = "no_open"
        elif (direction > 0 and cur_price < _session_open) or (direction < 0 and cur_price > _session_open):
            _so_side = "judas"
        else:
            _so_side = "momentum"
        _pip_sz      = pip_size(pair)
        _tgt_pips    = abs(target - entry) / _pip_sz

        # TP Runner: partial exit AT the original institutional draw (TP1), stop
        # moved to break-even, remainder runs to the next premium structural draw
        # (TP2) found at least TP_RUNNER_MIN_PIPS beyond TP1.  Mutually exclusive
        # with SCALE_OUT_ENABLED.
        _runner_tp2 = None
        if config.TP_RUNNER_ENABLED and not config.SCALE_OUT_ENABLED:
            _tp2_beyond = target + config.TP_RUNNER_MIN_PIPS * _pip_sz * direction
            _tp2_res    = self._find_target(pair, direction, t, entry, stop=stop,
                                             escalate=True, beyond=_tp2_beyond)
            if _tp2_res is not None:
                _runner_tp2 = _tp2_res[0]
        _runner_applies = _runner_tp2 is not None
        _r_units_1   = int(units * config.TP_RUNNER_RATIO) if _runner_applies else 0
        _r_units_2   = units - _r_units_1
        _runner_applies = _runner_applies and _r_units_1 > 0

        _so_applies  = (config.SCALE_OUT_ENABLED and not _runner_applies and
                        _tgt_pips >= config.SCALE_OUT_MIN_TARGET_PIPS)
        _units_tp1   = int(units * config.SCALE_OUT_RATIO) if _so_applies else 0
        _units_tp2   = units - _units_tp1
        _so_applies  = _so_applies and _units_tp1 > 0

        _active_target = _runner_tp2 if _runner_applies else target
        leg = {
            "entry": entry, "stop": stop, "units": units,
            "leg_idx": 1, "opened_at": t, "entry_type": entry_type,
            "session_side": _so_side,
            "tp1":       (target if _runner_applies else
                          (entry + config.SCALE_OUT_PIPS * _pip_sz * direction)
                          if _so_applies else None),
            "tp1_hit":   not (_runner_applies or _so_applies),
            "_units_tp1": (_r_units_1 if _runner_applies else _units_tp1),
            "_units_tp2": (_r_units_2 if _runner_applies else _units_tp2),
            "runner_be_after_tp1": _runner_applies,
        }
        _ladder = self._draw_ladder(pair, direction, cur_price, t)
        self.gate["entry_opened"] = self.gate.get("entry_opened", 0) + 1
        self.active[pair] = {
            "direction": direction,
            "mfe_price": entry,
            "lad_sess": _ladder["lad_sess"],
            "lad_d3":   _ladder["lad_d3"],
            "lad_wk":   _ladder["lad_wk"],
            "lad_d30":  _ladder["lad_d30"],
            "lad_d60":  _ladder["lad_d60"],
            "target": _active_target,
            "tp1_price": target if _runner_applies else None,
            "tp_runner": _runner_applies,
            "target_type": target_type,
            "stop_reason": _stop_reason,
            "legs": [leg],
            "weekly_amd_dir": weekly_amd_dir,
            "profile_score": p_score,
            "max_legs": max_legs,
            "draw_score": _draw_score,
            "im_scenario": _im_scenario,
            "entry_model": ("breakout" if _is_breakout else
                            "draw_cont" if _is_draw_cont else "judas"),
            "session_phase": _session_phase,
            "profile": _session_label,
            "htf_fvg": _htf_fvg_tf,
            "dxy_fvg_tf": _dxy_fvg_tf,
            "ny_cont": _is_ny_cont,
            "target_confluence": _target_score,
            "mstruct_pts": _ms["points"],
            "mstruct_align": "|".join(_ms["align_tfs"]),
            "mstruct_htf_dir": _ms["htf_dir"],
            "mstruct_minor_sweep": _ms["minor_sweep"],
            "mstruct_intact_tf": _ms["ltf_intact_tf"],
            "dxy_mstruct_align": "|".join(_ms["dxy_align"]),
            "dxy_mstruct_sweep": _ms["dxy_minor_sweep"],
            "crt_tf": _crt_tf,
            "nwog": _nwog_tf,
            "smt_idx": _smt["idx_smt"],
            "smt_dxy": _smt["dxy_smt"],
            "target_escalated": _tgt_escalated,
            "soj_sweep": _soj_sweep,
            "soj_type": _soj_type,
            "amd_range_pips": _amd_range_pips,
            "amd_range_bars": _amd_range_bars,
            "amd_touches_hi": _amd_touches_hi,
            "amd_touches_lo": _amd_touches_lo,
            "amd_sweep_side": _amd_sweep_side,
            "amd_sweep_depth": _amd_sweep_depth,
            "amd_sweep_aligned": _amd_sweep_aligned,
            "amd_accum_start": _amd_accum_start,
            "amd_accum_end": _amd_accum_end,
            "amd_sweep_time": _amd_sweep_time,
            "amd_sweep_time_m5": _amd_sweep_time_m5,
            "amd_swept_pdliq": _amd_swept_pdliq,
            "amd_entry_zone": _amd_entry_zone,
            "amd_liq_run": _amd_liq_run,
            "bond_confirm": _bond_confirm,
            "htf_smt": _htf_smt,
        }
        # P10: record a London-Open Judas opening so the same-day NY breakout echo
        # can be sized down. Only Judas (not breakout) reversals in London qualify.
        if not _is_breakout and _is_london:
            self._london_judas_open[(pair, _ny_dt.date())] = True
        # P11: record the day's London/DXY direction from the first London position
        # so NY-AM continuations in the same direction can be recognised.
        if _is_london and _ny_dt.date() not in self._london_dir:
            self._london_dir[_ny_dt.date()] = direction
        self._week_total[week_key]                        = week_total + 1
        self._week_pair[(week_key[0], week_key[1], pair)] = week_pair + 1
        # Indices with their own budget increment the index counter only, so they
        # don't consume the currencies' basket-wide daily slots.
        if (config.INDICES_ENABLED and pair in config.INDEX_PAIRS
                and config.INDEX_MAX_TRADES_PER_DAY > 0):
            self._day_idx_total[day_key] = self._day_idx_total.get(day_key, 0) + 1
        else:
            self._day_total[day_key]                      = day_total + 1
        if _is_ny:
            self._day_pair_ny[(day_key, pair)] = day_pair_ny + 1
        elif _is_pm:
            self._day_pair_pm[(day_key, pair)] = day_pair_pm + 1
        else:
            self._day_pair[(day_key, pair)]    = day_pair + 1

    def _htf_pair_smt(self, pair, direction, t, tfs=None):
        """H1 EURUSD↔GBPUSD SMT divergence in the trade direction.

        The two pairs are positively correlated (both X/USD). SMT = one sweeps a
        directional extreme the other FAILS to confirm — the reversal tell that
        starts the Market Maker distribution. Only meaningful for EUR/GBP; returns
        False for NZDUSD (no correlated partner in the book).

        `tfs` overrides the cascade — the refined standalone passes MM_SMT_HTF_TFS
        (H1/H4/D only) so the SMT read is on the BIGGER timeframe, not M5/M1 noise.
        """
        partner = {"EURUSD": "GBPUSD", "GBPUSD": "EURUSD"}.get(pair)
        if partner is None:
            return False
        from ict.smt import smt_divergence
        lb = config.MM_HTF_SMT_LOOKBACK
        # Walk the SMT cascade; fire if divergence shows on ANY rung.
        # direction is the TRADE direction (short = -1). smt_divergence's `direction`
        # is the sweep direction: a short fades a buy-side sweep (higher high) = -1.
        # positive correlation → inverse=False. Either pair may be the primary.
        for tf in (tfs if tfs is not None else config.MM_SMT_TFS):
            p = self.bars_up_to(pair, tf, t, max_bars=lb + 5)
            r = self.bars_up_to(partner, tf, t, max_bars=lb + 5)
            if len(p) < lb or len(r) < lb:
                continue
            if (smt_divergence(p, r, direction, inverse=False, lookback=lb) or
                    smt_divergence(r, p, direction, inverse=False, lookback=lb)):
                return True
        return False

    def _mm_structure_confirm(self, pair, direction, ifvg_tf, t):
        """Fresh, still-intact retracement swing in the trade direction, hunted on
        the TF(s) PROPORTIONAL to the IFVG timeframe (MM_SWING_TF_MAP): a W1/D1 gap's
        swing forms on H4/H1, an H1 gap's on M30/M15, etc. — never on M1 for an HTF
        gap. (Short → a rolled-over swing HIGH still holding; long → a swing LOW.)
        M1 is reserved for the entry/stop, not this structure read."""
        swing_tfs = config.MM_SWING_TF_MAP.get(ifvg_tf, ("1T",))
        for tf in swing_tfs:
            bars = self.bars_up_to(pair, tf, t, max_bars=120)
            if len(bars) < 5:
                continue
            res = mstruct.classify(bars)
            swings = res.get("stl" if direction > 0 else "sth", [])
            if not swings:
                continue
            last = swings[-1]
            age = (len(bars) - 1) - last.bar_index
            if age < 1 or age > config.MM_STRUCTURE_MAX_AGE:
                continue
            if not last.swept:
                return True
        return False

    def _mm_ifvg_zone(self, pair, direction, cur_price, t):
        """The inversion FVG price is currently retraced INTO, found by cascading
        the TF ladder HIGHEST→lowest and taking the FIRST TF that has one.

        The full-body-close inversion of a TF's FVG box is judged on THAT TF and the
        next-lower TF in the cascade (the trader's rule). For a short we want a
        SUPPLY inversion (idir -1) price pulled UP into; long → demand (+1).
        Returns (tf_label, lo, hi) or None.
        """
        from ict.ifvg import _fvgs, latest_inversion
        cap = config.MM_IFVG_SCAN_BARS
        cascade = config.MM_IFVG_TFS
        for i, tf in enumerate(cascade):
            bars = self.bars_up_to(pair, tf, t, max_bars=cap)
            if len(bars) < 3:
                continue
            boxes = _fvgs(bars)
            if not boxes:
                continue
            lower = (self.bars_up_to(pair, cascade[i + 1], t, max_bars=cap)
                     if i + 1 < len(cascade) else [])
            for (bi, lo, hi) in reversed(boxes):      # most recent box first
                if not (lo <= cur_price <= hi):       # must be retraced into it
                    continue
                idir = latest_inversion(bars[bi:], lo, hi)    # judged on this TF…
                if idir == 0 and lower:
                    idir = latest_inversion(lower, lo, hi)    # …and the next lower
                if idir == direction:
                    return (tf, lo, hi)
            # no valid inverted+retraced IFVG on this TF → keep cascading down until
            # one materialises (the highest TF that actually "identified" an IFVG).
        return None

    def _mm_entry_pattern(self, pair, direction, zone, cur_price, t):
        """Entry PD array for the MM add, on M5 first then M1 (MM_ENTRY_TFS).

        The entry TRIGGER is a normal FVG / OB / breaker on the small TF — the same
        PD arrays the base strategy enters on. Where a NORMAL FVG OVERLAPS the IFVG
        zone, that normal FVG is the entry (the trader's rule: IFVG is the zone
        context, the overlapping normal FVG is the precise trigger). OB/breaker are
        the fallback when no overlapping FVG exists. Returns (entry_level, stop, tag,
        tf) or None. The entry_level is the PD-array price (a limit into the
        retracement), which the caller fills as a limit — this is the precision fix:
        entering AT the FVG (tight true stop) instead of at market with a wide cap.
        Only levels on the retracement side of cur_price qualify (a genuine limit).
        """
        _, zlo, zhi = zone
        _lbl = {"15T": "m15", "5T": "m5", "1T": "m1"}
        _lb = {"15T": 8, "5T": 24, "1T": 30}

        def _ok(r):
            # the PD array must sit INSIDE the IFVG gap AND be a retracement limit
            # (short: at/above price; long: at/below). Entries live inside the gap.
            if r is None:
                return False
            el = r[0]
            if not (zlo <= el <= zhi):
                return False
            return (el >= cur_price) if direction < 0 else (el <= cur_price)

        for etf in config.MM_ENTRY_TFS:              # ("15T", "5T", "1T")
            bars = self.bars_up_to(pair, etf, t,
                                   max_bars=(120 if etf == "1T" else None))
            if not bars:
                continue
            lbl = _lbl.get(etf, etf)
            fvg = self._find_fvg_entry(bars, pair, direction, lookback=_lb.get(etf, 24))
            # a NORMAL FVG inside the IFVG is the preferred trigger; OB / breaker
            # inside the gap are the fallback (all must be inside the gap).
            if _ok(fvg):
                return (fvg[0], fvg[1], f"fvg_{lbl}", etf)
            for r, tag in ((self._find_ob_entry(bars, pair, direction), f"ob_{lbl}"),
                           (self._find_breaker_entry(bars, pair, direction), f"breaker_{lbl}")):
                if _ok(r):
                    return (r[0], r[1], tag, etf)
        return None

    def _mm_internal_amd(self, pair, direction, zone, t):
        """The INTERNAL mini-AMD inside the IFVG (the trader's core model): on M5 then
        M1, an internal short-term extreme AGAINST the trade was SWEPT and price closed
        back on our side — the internal manipulation. Returns the stop level just beyond
        that swept extreme (tight + survivable), or None if the manipulation hasn't
        happened yet. Short → an internal high wicked + closed back below → stop above
        it; long → mirror."""
        _, zlo, zhi = zone
        pip = pip_size(pair)
        buf = config.MM_STOP_BUF_PIPS * pip
        for tf in ("5T", "1T"):
            bars = self.bars_up_to(pair, tf, t, max_bars=60)
            if len(bars) < 5:
                continue
            res = mstruct.classify(bars)
            swings = res.get("sth" if direction < 0 else "stl", [])
            cur = bars[-1].Close
            for sw in reversed(swings):               # most recent internal extreme
                if not (zlo - buf <= sw.price <= zhi + buf):
                    continue                          # must be inside/at the gap
                if not sw.swept:
                    continue                          # the extreme must have been TAKEN
                if direction < 0 and cur < sw.price:  # swept a high, closed back below
                    return sw.price + buf
                if direction > 0 and cur > sw.price:  # swept a low, closed back above
                    return sw.price - buf
        return None

    def _mm_structural_stop(self, zone, direction, entry, pip, t=None, pair=None):
        """Stop for an MM entry. Prefers the INTERNAL mini-AMD stop (just beyond the
        swept internal extreme — tight + survivable). Falls back to the gap EDGE only
        for narrow gaps; a WIDE (>MM_WIDE_GAP_PIPS) gap with no internal manipulation
        is too risky (edge stop blew MaxDD to -38%) → returns None so the caller skips.
        Clamped to MM_MAX_STOP_PIPS."""
        _, zlo, zhi = zone
        buf = config.MM_STOP_BUF_PIPS * pip
        gap_pips = (zhi - zlo) / pip
        internal = None
        if t is not None and pair is not None:
            internal = self._mm_internal_amd(pair, direction, zone, t)
        if internal is not None and (internal - entry) * direction < 0:
            stop = internal
        elif config.MM_REQUIRE_INTERNAL_AMD and gap_pips > config.MM_WIDE_GAP_PIPS:
            return None                               # wide gap, no manip → skip
        else:
            stop = (zhi + buf) if direction < 0 else (zlo - buf)   # gap-edge fallback
            if (stop - entry) * direction >= 0:
                stop = entry - config.MM_STOP_BUF_PIPS * pip * direction
        cap = config.MM_MAX_STOP_PIPS * pip
        if abs(entry - stop) > cap:
            stop = entry - cap * direction
        return stop

    def _opposing_liquidity(self, pair, direction, price, t):
        """Nearest UNSWEPT opposing-liquidity pool (ITH/ITL on H4/D/W) beyond the
        current price in the trade direction — the far draw the distribution leg
        delivers to. Returns a price or None."""
        pip = pip_size(pair)
        floor = self._min_pips_target() * pip
        best = None
        for tf in config.MM_TARGET_TFS:
            try:
                bars = self.bars_up_to(pair, tf, t,
                                       max_bars=(config.ITHL_TARGET_MAX_BARS or None))
                for cand in self._ithl_targets(bars, direction, price, pair, tf):
                    lvl = cand[0]
                    if (lvl - price) * direction >= floor:
                        if best is None or (lvl - price) * direction > (best - price) * direction:
                            best = lvl      # the FURTHEST qualifying pool = opposing end
            except Exception:
                continue
        return best

    def _session_label(self, t):
        """'london' / 'ny' / 'ny_pm' / 'other' from the ET hour (shared helper)."""
        import pytz as _pytz
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        h = now.astimezone(_pytz.timezone("America/New_York")).hour
        if 2 <= h < 5:
            return "london"
        if 7 <= h < 10:
            return "ny"
        if config.NY_PM_ENABLED and 13 <= h < 16:
            return "ny_pm"
        return "other"

    def _mm_day_model(self, pair, t):
        """The day's MM direction from the EXTERNAL/INTERNAL liquidity model.

        The dealing range (ict.dealing_range) is bounded by the two swept liquidity
        extremes = EXTERNAL range liquidity (ERL). When price takes out ONE external
        side (sweeps the DR high or low) and closes back inside, that is the Judas:
        it reverses to deliver toward INTERNAL liquidity (IRL — an FVG / the opposite
        half). So:
          sweep DR HIGH (external BSL) + close back below → distribute DOWN → +? no,
            direction -1 (sell in premium, draw = internal/discount).
          sweep DR LOW  (external SSL) + close back above → distribute UP → +1.
        The external extremes are the SWEEP; the DRAW is INTERNAL (handled in the
        target selection). Locked per (pair, date); the range is cached for targeting.
        """
        from ict.dealing_range import detect_dealing_range
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        key = (pair, now.date())
        if key in self._mm_day_dir:
            return self._mm_day_dir[key]
        pip = pip_size(pair)
        buf = config.MM_SWEEP_MIN_PIPS * pip
        dr = detect_dealing_range(
            self.bars_up_to(pair, "60T", t, max_bars=150), lookback=100)
        if dr is None or dr.width <= 0:
            return 0
        bars = self.bars_up_to(pair, "5T", t, max_bars=config.MM_SWEEP_LOOKBACK)
        if not bars:
            return 0
        hi = max(b.High for b in bars)
        lo = min(b.Low for b in bars)
        cur = bars[-1].Close
        d = 0
        if hi > dr.high + buf and cur < dr.high:      # external BSL swept, closed back
            d = -1                                    # → distribute DOWN to internal
        elif lo < dr.low - buf and cur > dr.low:      # external SSL swept, closed back
            d = +1                                    # → distribute UP to internal
        if d != 0:
            self._mm_day_dir[key] = d
            self._mm_day_range[(pair, now.date())] = (dr.high, dr.low, dr.equilibrium)
        return d

    def _mm_mss_confirm(self, pair, direction, t):
        """Market-structure shift on MM_MSS_TF (M5) in the trade direction — the
        confirmation the chart examples show BEFORE the IFVG re-entries. The reversal
        is only tradeable once the opposing short-term swing is BROKEN: for a short a
        recent short-term LOW is taken out (a lower low = downside MSS); for a long a
        recent short-term HIGH is taken out (higher high). Distinct from
        _mm_structure_confirm, which finds the swing to enter AT — this proves the
        reversal actually happened. Returns True when the shift is confirmed."""
        bars = self.bars_up_to(pair, config.MM_MSS_TF, t, max_bars=config.MM_MSS_LOOKBACK)
        if len(bars) < 6:
            return False
        res = mstruct.classify(bars)
        # short → the opposing tier is the short-term LOW (STL); long → STH.
        swings = res.get("stl" if direction < 0 else "sth", [])
        if not swings:
            return False
        last = swings[-1]
        age = (len(bars) - 1) - last.bar_index
        # a fresh, already-swept opposing swing = structure just shifted our way.
        return bool(last.swept) and age <= config.MM_MSS_LOOKBACK

    def _mm_open_position(self, pair, direction, entry, stop, target, target_type,
                          tag, units, t):
        """Open a standalone MM position (mirrors the base open's essential fields;
        analytics fields default via .get in consumers)."""
        leg = {"entry": entry, "stop": stop, "units": units, "leg_idx": 1,
               "opened_at": t, "entry_type": tag, "tp1": None, "tp1_hit": True,
               "_units_tp1": 0, "_units_tp2": units, "runner_be_after_tp1": False}
        self.active[pair] = {
            "direction": direction, "mfe_price": entry, "target": target,
            "target_type": target_type, "legs": [leg],
            "max_legs": config.MAX_LEGS, "draw_score": 0,
            "entry_model": "mm_standalone", "profile": self._session_label(t),
            "htf_smt": self._htf_pair_smt(pair, direction, t), "mm_adds": 0,
            "stop_reason": "mm_pd_array",
        }
        self.gate["mm_std_opened"] = self.gate.get("mm_std_opened", 0) + 1

    def _mm_standalone(self, pair, t):
        """Open the MM model as its OWN trade on the day's Judas sweep + IFVG retrace,
        independent of the base strategy. Default OFF (no-op when disabled)."""
        if not config.MM_STANDALONE_ENABLED or pair in self.active:
            return
        g = self.gate
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if not can_open_new_trade(now, pair):
            return
        if self.news.nearest_impact(now) in ("Medium", "Critical"):
            return
        # Circuit breakers — READ-ONLY (state is maintained by _maybe_open, which runs
        # first in the loop, and the close path). The standalone entries were bypassing
        # these, firing straight through drawdowns that halt the base strategy — a
        # major driver of the -23.9% MaxDD.
        _dk = now.date()
        if self._drawdown_halt_until is not None and _dk < self._drawdown_halt_until:
            g["mm_std_dd_halt"] = g.get("mm_std_dd_halt", 0) + 1
            return
        _day_open = self._day_open_eq.get(_dk)
        if _day_open and (_day_open - self.equity) / _day_open * 100 >= config.MAX_DAILY_LOSS_PCT:
            g["mm_std_daily_halt"] = g.get("mm_std_daily_halt", 0) + 1
            return
        if self._consec_losses >= config.MAX_CONSECUTIVE_LOSSES:
            g["mm_std_consec_halt"] = g.get("mm_std_consec_halt", 0) + 1
            return
        daykey = (pair, now.date())
        # De-correlate: block if a same-direction standalone is already open on any
        # pair (EU/GU/NZD are all dollar bets — don't stack the same USD risk).
        if config.MM_STANDALONE_ONE_PER_DIR:
            _dm = self._mm_day_model(pair, t)
            if _dm != 0 and any(
                    op.get("entry_model") == "mm_standalone" and op["direction"] == _dm
                    for op in self.active.values()):
                g["mm_std_corr_block"] = g.get("mm_std_corr_block", 0) + 1
                return
        if self._mm_day_count.get(daykey, 0) >= config.MM_STANDALONE_MAX_PER_DAY:
            return
        d = self._mm_day_model(pair, t)
        if d == 0:
            g["mm_std_no_sweep"] = g.get("mm_std_no_sweep", 0) + 1
            return
        bars5 = self.bars_up_to(pair, "5T", t)
        if not bars5:
            return
        cur_price = bars5[-1].Close
        pip = pip_size(pair)
        # entry must be in the correct half — sell in PREMIUM (after sweeping the DR
        # high), buy in DISCOUNT (after sweeping the DR low). Smart money sells the
        # premium, buys the discount.
        _dr = self._mm_day_range.get(daykey)
        if _dr is not None:
            from ict.dealing_range import is_valid_entry_zone
            if not is_valid_entry_zone(cur_price, _dr[0], _dr[1], d):
                g["mm_std_wrong_half"] = g.get("mm_std_wrong_half", 0) + 1
                return
        zone = self._mm_ifvg_zone(pair, d, cur_price, t)
        if zone is None:
            g["mm_std_no_ifvg"] = g.get("mm_std_no_ifvg", 0) + 1
            return
        if not self._mm_structure_confirm(pair, d, zone[0], t):
            g["mm_std_no_structure"] = g.get("mm_std_no_structure", 0) + 1
            return
        # WR filter 1 — MSS confirmation on M5 (structure shifted before we enter).
        if config.MM_REQUIRE_MSS and not self._mm_mss_confirm(pair, d, t):
            g["mm_std_no_mss"] = g.get("mm_std_no_mss", 0) + 1
            return
        # WR filter 2 — H1 EU/GU SMT on the BIGGER timeframe (H1/H4/D only). The
        # standalone requirement is independent of the continuation-add flag.
        if ((config.MM_STANDALONE_REQUIRE_SMT or config.MM_HTF_SMT_REQUIRED)
                and not self._htf_pair_smt(pair, d, t, tfs=config.MM_SMT_HTF_TFS)):
            g["mm_std_no_smt"] = g.get("mm_std_no_smt", 0) + 1
            return
        pat = self._mm_entry_pattern(pair, d, zone, cur_price, t)
        if pat is None:
            g["mm_std_no_entry"] = g.get("mm_std_no_entry", 0) + 1
            return
        el, pat_stop, pat_tag, entry_tf = pat
        bar = bars5[-1]
        if (d < 0 and bar.High < el) or (d > 0 and bar.Low > el):
            g["mm_std_not_filled"] = g.get("mm_std_not_filled", 0) + 1
            return
        _spread_p = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        _fric = (_spread_p / 2 + config.SLIPPAGE_PIPS) * pip
        entry = el + d * _fric
        stop = self._mm_structural_stop(zone, d, entry, pip, t=t, pair=pair)
        if stop is None:                             # wide gap, no internal manip → skip
            g["mm_std_wide_gap"] = g.get("mm_std_wide_gap", 0) + 1
            return
        # DRAW = INTERNAL liquidity (the point of the ERL/IRL model): after the
        # external sweep + reversal, price delivers back INTO the range. Target the
        # nearest qualifying draw, but clamp so it never overshoots the OPPOSITE
        # external extreme — an over-far external target is the repeatedly-failed
        # config. The dealing-range equilibrium is the internal-liquidity anchor.
        dr = self._mm_day_range.get(daykey)
        if config.MM_STANDALONE_TARGET_OPPOSING:      # kept for A/B; the wrong model
            target = self._opposing_liquidity(pair, d, entry, t)
            target_type = "opposing_external"
        else:
            target = target_type = None
            # Session draw map: prefer the previous session block's opposing pool
            # (London→Asia H/L, NY→London H/L) as the distribution's draw.
            if config.MM_SESSION_DRAW:
                sd = self._prev_session_hl(pair, t, d)
                if sd is not None and (sd - entry) * d >= self._min_pips_target() * pip:
                    if dr is None or not ((d < 0 and sd < dr[1]) or (d > 0 and sd > dr[0])):
                        target, target_type = sd, "session_draw"
            if target is None:
                _tgt = self._find_target(pair, d, t, entry, stop=stop)
                if _tgt is None:
                    g["mm_std_no_target"] = g.get("mm_std_no_target", 0) + 1
                    return
                target, target_type = _tgt[0], _tgt[1]
                if dr is not None and target is not None:
                    dr_hi, dr_lo, dr_eq = dr
                    overshoot = (d < 0 and target < dr_lo) or (d > 0 and target > dr_hi)
                    if overshoot:                      # don't reach past external → use eq
                        target, target_type = dr_eq, "range_equilibrium"
        if target is None or abs(target - entry) / pip < self._min_pips_target():
            g["mm_std_no_target"] = g.get("mm_std_no_target", 0) + 1
            return
        equity_usd = self._size_equity() / config.USD_ZAR
        units = int(position_size(equity_usd, entry, stop, pair))
        if config.MM_STANDALONE_SIZE_MULT != 1.0:
            units = int(units * config.MM_STANDALONE_SIZE_MULT)
        min_units = int(self._pyramid_lots()[0] * self._contract_units(pair))
        units = max(units, min_units)
        self._mm_open_position(pair, d, entry, stop, target, target_type,
                               f"mmstd_{pat_tag}_ifvg{zone[0]}", units, t)
        self._mm_day_count[daykey] = self._mm_day_count.get(daykey, 0) + 1

    def _mm_continuation(self, pair, t):
        """Market Maker distribution add: re-enter on an IFVG retrace toward the
        opposing liquidity pool. Fires only on an already-open position (the Judas
        reversal defines the model direction). Default OFF — a no-op when
        config.MM_CONTINUATION_ENABLED is false, so backtest numbers are identical.
        """
        if not config.MM_CONTINUATION_ENABLED:
            return
        st = self.active.get(pair)
        if st is None:
            return
        g = self.gate
        g["mm_checks"] = g.get("mm_checks", 0) + 1
        d = st["direction"]
        max_legs = st.get("max_legs", config.MAX_LEGS)
        if len(st["legs"]) >= max_legs:
            return
        # Cap MM re-entry adds per position (0 = unlimited) — limits loss-clustering.
        if config.MM_MAX_ADDS and st.get("mm_adds", 0) >= config.MM_MAX_ADDS:
            g["mm_blocked_max_adds"] = g.get("mm_blocked_max_adds", 0) + 1
            return
        # Require HTF draw alignment (winner study: draw_score=0 adds were 3% WR).
        if st.get("draw_score", 0) < config.MM_MIN_DRAW_SCORE:
            g["mm_blocked_draw"] = g.get("mm_blocked_draw", 0) + 1
            return
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if not can_open_new_trade(now, pair):
            return
        if self.news.nearest_impact(now) in ("Medium", "Critical"):
            return

        bars5 = self.bars_up_to(pair, "5T", t)
        if not bars5:
            return
        cur_price = bars5[-1].Close
        pip = pip_size(pair)

        # position must be in profit (distribution underway) before an add
        u = sum(l["units"] for l in st["legs"]) or 1
        avg = sum(l["entry"] * l["units"] for l in st["legs"]) / u
        if (cur_price - avg) * d / pip < config.MM_MIN_FAVOUR_PIPS:
            g["mm_blocked_favour"] = g.get("mm_blocked_favour", 0) + 1
            return

        # (1) retrace: price inside the highest-TF inverted FVG in the trade direction
        zone = self._mm_ifvg_zone(pair, d, cur_price, t)
        if zone is None:
            g["mm_blocked_no_ifvg"] = g.get("mm_blocked_no_ifvg", 0) + 1
            return
        ifvg_tf = zone[0]
        # (2) reversal: fresh retracement swing on the TF(s) PROPORTIONAL to the IFVG
        # timeframe (W1/D1 gap → H4/H1 swing) — never M1 for an HTF gap.
        if not self._mm_structure_confirm(pair, d, ifvg_tf, t):
            g["mm_blocked_no_structure"] = g.get("mm_blocked_no_structure", 0) + 1
            return
        # (3) optional HTF EU/GU SMT confirmation of the reversal
        if config.MM_HTF_SMT_REQUIRED and not self._htf_pair_smt(pair, d, t):
            g["mm_blocked_no_smt"] = g.get("mm_blocked_no_smt", 0) + 1
            return

        # optional: escalate the position target to the opposing liquidity pool so
        # the trade rides the full distribution (isolated behind its own flag).
        if config.MM_TARGET_OPPOSING:
            opp = self._opposing_liquidity(pair, d, cur_price, t)
            if opp is not None and (opp - st["target"]) * d > 0:
                st["target"] = opp
                g["mm_target_escalated"] = g.get("mm_target_escalated", 0) + 1

        # (4) entry TRIGGER: an M5 FVG/OB/breaker (drop to M1 if M5 has none), with a
        # normal FVG overlapping the IFVG preferred. Small TF = precision + risk only.
        pat = self._mm_entry_pattern(pair, d, zone, cur_price, t)
        if pat is None:
            g["mm_blocked_no_entry"] = g.get("mm_blocked_no_entry", 0) + 1
            return
        el, pat_stop, pat_tag, entry_tf = pat
        # LIMIT fill at the PD-array level (precision fix): the current M5 bar must
        # have TRADED to the level (no lookahead), then we fill AT it — tight true
        # stop instead of a wide market+cap. If price hasn't reached it, retry next bar.
        _bar = bars5[-1]
        if (d < 0 and _bar.High < el) or (d > 0 and _bar.Low > el):
            g["mm_blocked_not_filled"] = g.get("mm_blocked_not_filled", 0) + 1
            return
        _spread_p = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        _fric = (_spread_p / 2 + config.SLIPPAGE_PIPS) * pip
        entry = el + d * _fric                       # fill at the FVG level
        stop = self._mm_structural_stop(zone, d, entry, pip, t=t, pair=pair)
        if stop is None:                             # wide gap, no internal manip → skip
            g["mm_blocked_wide_gap"] = g.get("mm_blocked_wide_gap", 0) + 1
            return
        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < self._min_pips_target():
            g["mm_blocked_min_target"] = g.get("mm_blocked_min_target", 0) + 1
            return

        tier_lots = self._pyramid_lots()
        lot_idx = min(len(st["legs"]), len(tier_lots) - 1)
        units = max(int(tier_lots[lot_idx] * self._contract_units(pair)),
                    int(tier_lots[-1] * self._contract_units(pair)))
        st["legs"][-1]["stop"] = st["legs"][-1]["entry"]   # prior leg → breakeven
        st["legs"].append({
            "entry": entry, "stop": stop, "units": units,
            "leg_idx": len(st["legs"]) + 1, "opened_at": t,
            "entry_type": f"mm_{pat_tag}_ifvg{zone[0]}",
            "tp1": None, "tp1_hit": True, "_units_tp1": 0, "_units_tp2": units,
            "runner_be_after_tp1": False,
        })
        st["mm_adds"] = st.get("mm_adds", 0) + 1
        g["mm_added"] = g.get("mm_added", 0) + 1

    def _maybe_pyramid(self, pair, t):
        """Add a new leg to a winning position at market price with fixed stop.

        Intermarket signal is used as a score to scale the pyramid lot size:
          - Signal still agrees with trade direction → full pyramid lot
          - Signal neutral (DXY or EURGBP flat)    → half lot (cautious add)
          - Signal disagrees                        → skip pyramid entirely
        """
        st = self.active[pair]
        max_legs = st.get("max_legs", config.MAX_LEGS)
        if len(st["legs"]) >= max_legs:
            return
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        # Block pyramids during Critical (CPI/NFP/FOMC) and Medium events.
        pyr_news_impact = self.news.nearest_impact(now)
        if pyr_news_impact in ("Medium", "Critical"):
            return
        # Only pyramid inside the correct kill zone for this pair.
        if not can_open_new_trade(now, pair):
            return

        # Intermarket score for this pyramid leg.
        dxy_bias = self._dxy_bias("60T", t, lookback=config.SWING_LOOKBACK_STH)
        if pair in ("EURUSD", "GBPUSD"):
            eurgbp_bias = self._sym_bias(config.REF_EURGBP, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            dir_check, im_score = resolve_pair_direction(
                dxy_bias, eurgbp_bias, pair, "EURUSD"
            )
            if dir_check is None:
                im_score = 0.5
            elif dir_check != st["direction"]:
                return
        else:   # NZDUSD — DXY + AUDNZD (independent of EUR/GBP)
            audnzd_bias = self._sym_bias(config.REF_AUDNZD, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            if audnzd_bias == 0:
                audnzd_h4 = self._sym_bias(config.REF_AUDNZD, "240T", t,
                                           lookback=config.SWING_LOOKBACK_STH)
                if audnzd_h4 != 0:
                    audnzd_bias = audnzd_h4
            dir_check, im_score = resolve_pair_direction(
                dxy_bias, audnzd_bias, "NZDUSD", "AUDUSD"
            )
            if dir_check is None:
                im_score = 0.5
            elif dir_check != st["direction"]:
                return

        # Only allow pyramids with full intermarket conviction (im_score = 1.0).
        # Exception: if the parent trade had a 3/3 HTF draw cascade, the draw itself
        # is the higher-level confirmation — allow adds even when EURGBP is temporarily
        # flat (im_score = 0.75), as long as DXY still agrees and cross hasn't reversed.
        # Weekly AMD upgrade: if the confirmed weekly distribution direction agrees
        # with this position, upgrade im_score to 1.0 (full lots) even when the
        # H1 intermarket is temporarily neutral.  The weekly profile is the higher-
        # timeframe authority — if the Judas swing already fired, price SHOULD
        # distribute toward PWWH/PWWL for the rest of the week.
        if config.WEEKLY_AMD_FULL_PYRAMID:
            wamd_dir = st.get("weekly_amd_dir", 0)
            if wamd_dir == st["direction"]:
                im_score = 1.0      # weekly AMD confirms — full pyramid lots

        if im_score < 1.0:
            _draw_unlock = (st.get("draw_score", 0) >= config.PYRAMID_DRAW_UNLOCK_MIN
                            and im_score >= 0.75)
            if not _draw_unlock:
                self.gate["pyramid_blocked_low_im"] = self.gate.get("pyramid_blocked_low_im", 0) + 1
                return

        # Block neutral-conviction pyramid adds (im_score=0.5 = no clear signal).
        # Backtest: pyramid_im0.5 → 0W/5L across 4 years. No edge without a clear bias.
        if config.BLOCK_NEUTRAL_PYRAMID and im_score == 0.5:
            return

        bars5 = self.bars_up_to(pair, "5T", t)
        if not bars5:
            return
        cur_price = bars5[-1].Close
        pip = pip_size(pair)

        # Weekly AMD hard gate: skip pyramid unless weekly distribution already fired
        # in the same direction as the trade. Controlled by PYRAMID_REQUIRE_WEEKLY_AMD.
        if config.PYRAMID_REQUIRE_WEEKLY_AMD:
            if st.get("weekly_amd_dir", 0) != st["direction"]:
                return

        # Must be at least PYRAMID_MIN_FAVOUR_PIPS in favour of the last leg before adding.
        last_entry = st["legs"][-1]["entry"]
        favour_pips = (cur_price - last_entry) * st["direction"] / pip
        if favour_pips < config.PYRAMID_MIN_FAVOUR_PIPS:
            self.gate["pyramid_blocked_favour"] = self.gate.get("pyramid_blocked_favour", 0) + 1
            return

        # Entry pattern from M5/M15/H1 (same as normal entries); the stop is then
        # re-anchored to M1 structure below via _m1_structure_stop.
        bars15 = self.bars_up_to(pair, "15T", t)
        bars1h = self.bars_up_to(pair, "60T", t)
        bars1m = self.bars_up_to(pair, "1T", t, max_bars=120)
        _level, stop, pyr_pattern = self._get_limit_entry(
            bars5, bars15, bars1h, pair, st["direction"], cur_price,
            bars1m=bars1m, for_pyramid=False,
        )
        if pyr_pattern is None:
            self.gate["pyramid_blocked_no_pattern"] = self.gate.get("pyramid_blocked_no_pattern", 0) + 1
            return

        # Apply entry friction to pyramid fills too (widen for news, same as initial entries).
        _spread_p = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        if pyr_news_impact == "High":
            _spread_p = max(_spread_p, config.NEWS_HIGH_SPREAD_PIPS)
        _fric_p = (_spread_p / 2 + config.SLIPPAGE_PIPS) * pip
        entry = cur_price + st["direction"] * _fric_p

        # Anchor the pyramid stop to M1 market structure too (same as initial entries).
        _m1_stop = self._m1_structure_stop(bars1m, st["direction"], entry, pip)
        if _m1_stop is not None:
            stop = _m1_stop

        # High-impact news nearby: fixed 10-pip stop (spread protection).
        if pyr_news_impact == "High":
            stop = entry - config.FIXED_STOP_PIPS * pip if st["direction"] > 0 \
                   else entry + config.FIXED_STOP_PIPS * pip

        # Universal stop cap: never risk more than FIXED_STOP_PIPS on a pyramid leg.
        _max_stop = config.FIXED_STOP_PIPS * pip
        if abs(entry - stop) > _max_stop:
            stop = entry - _max_stop if st["direction"] > 0 else entry + _max_stop

        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < self._min_pips_target():
            self.gate["pyramid_blocked_min_target"] = self.gate.get("pyramid_blocked_min_target", 0) + 1
            return

        # High-impact news = distribution catalyst: upgrade to full lots.
        if pyr_news_impact == "High":
            im_score = 1.0

        # Lot size: growing pyramid schedule for current tier, scaled by intermarket score.
        tier_lots  = self._pyramid_lots()
        leg_num    = len(st["legs"]) + 1
        lot_idx    = min(leg_num - 1, len(tier_lots) - 1)
        base_units = int(tier_lots[lot_idx] * self._contract_units(pair))
        units = max(int(base_units * im_score),
                    int(tier_lots[-1] * self._contract_units(pair)))

        # Promote prior leg stop to breakeven before adding new leg.
        prior = st["legs"][-1]
        prior["stop"] = prior["entry"]

        wamd_tag     = "wamd" if st.get("weekly_amd_dir") == st["direction"] else "im"
        news_tag     = "news" if pyr_news_impact == "High" else ""
        _pip_sz      = pip_size(pair)
        _tgt_pips    = abs(st["target"] - entry) / _pip_sz
        # Pyramid legs when TP_RUNNER is active: no tp1 partial — they target TP2 directly.
        _so_applies  = (config.SCALE_OUT_ENABLED and not config.TP_RUNNER_ENABLED and
                        _tgt_pips >= config.SCALE_OUT_MIN_TARGET_PIPS)
        _units_tp1   = int(units * config.SCALE_OUT_RATIO) if _so_applies else 0
        _units_tp2   = units - _units_tp1
        _so_applies  = _so_applies and _units_tp1 > 0
        leg = {
            "entry": entry, "stop": stop, "units": units,
            "leg_idx": len(st["legs"]) + 1, "opened_at": t,
            "entry_type": f"pyramid_{wamd_tag}{news_tag}{im_score:.1f}_{pyr_pattern}",
            "tp1":       (entry + config.SCALE_OUT_PIPS * _pip_sz * st["direction"])
                         if _so_applies else None,
            "tp1_hit":   not _so_applies,
            "_units_tp1": _units_tp1,
            "_units_tp2": _units_tp2,
            "runner_be_after_tp1": False,
        }
        st["legs"].append(leg)
        self.gate["pyramid_added"] = self.gate.get("pyramid_added", 0) + 1


def summarize(bt):
    ccy = getattr(config, "ACCOUNT_CURRENCY", "USD")
    n = len(bt.trades)
    if n == 0:
        return {
            "trades": 0,
            f"starting_equity_{ccy}": bt.start_equity,
            f"ending_equity_{ccy}": round(bt.equity, 2),
            f"pnl_{ccy}": round(bt.equity - bt.start_equity, 2),
        }
    df = pd.DataFrame(bt.trades)
    wins = df[df.pnl > 0]
    losses = df[df.pnl <= 0]
    win_rate = len(wins) / n * 100
    gp = wins.pnl.sum()
    gl = -losses.pnl.sum()
    pf = gp / gl if gl > 0 else float("inf")
    # eq = start + cumulative P&L = the TOTAL-value curve (working balance + all
    # profit withdrawn), so MaxDD here is withdrawal-neutral by construction.
    eq = bt.start_equity + df.pnl.cumsum()
    rmax = eq.cummax()
    dd = ((eq - rmax) / rmax * 100).min() if len(eq) else 0
    withdrawn = getattr(bt, "withdrawn_total", 0.0)
    total_value = bt.equity + withdrawn        # working balance + banked profit
    out = {
        "trades": n,
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": "inf" if pf == float("inf") else round(pf, 2),
        f"starting_equity_{ccy}": bt.start_equity,
        f"ending_equity_{ccy}": round(total_value, 2),   # total value (incl. withdrawn)
        f"pnl_{ccy}": round(total_value - bt.start_equity, 2),
        "pnl_pct": round((total_value - bt.start_equity) / bt.start_equity * 100, 2),
        "max_drawdown_pct": round(dd, 2),
        f"avg_win_{ccy}": round(wins.pnl.mean() if len(wins) else 0, 2),
        f"avg_loss_{ccy}": round(losses.pnl.mean() if len(losses) else 0, 2),
    }
    if withdrawn > 0 or config.WITHDRAW_AT > 0:
        out[f"withdrawn_total_{ccy}"] = round(withdrawn, 2)
        out["withdrawal_count"] = getattr(bt, "withdrawal_count", 0)
        out[f"working_balance_{ccy}"] = round(bt.equity, 2)
        # The realistic per-cycle drawdown seen in the actual account (peak resets
        # each base->ceiling cycle; cash-outs excluded).
        out["working_max_drawdown_pct"] = round(getattr(bt, "_max_work_dd", 0.0), 2)
    return out


def main():
    print("Fetching 60d of 5-min forex data from yfinance...")
    data = fetch_data()
    if "GBPUSD" not in data or "EURUSD" not in data:
        print("ERROR: primary pairs missing")
        sys.exit(1)

    print("\nRunning backtest...")
    bt = Backtester(data)
    bt.run()

    print("\n=== Gate funnel (how many times each filter let entries through) ===")
    for k, v in bt.gate.items():
        print(f"  {k:30s} {v}")

    print("\n=== Results ===")
    for k, v in summarize(bt).items():
        print(f"  {k:20s} {v}")

    if bt.trades:
        print("\n=== Trades ===")
        df = pd.DataFrame(bt.trades)
        cols = ["opened_at", "closed_at", "pair", "direction", "leg_idx",
                "entry", "exit", "units", "pnl", "reason"]
        # Show all trades (likely few given strict AMD gating).
        print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()

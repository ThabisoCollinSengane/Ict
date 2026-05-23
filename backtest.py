"""Pandas-based backtester — ICT rewrite (NYO-SMT, AMD, fake-run sweep,
hierarchical liquidity targets, D1/W1 FVGs, M15/H4 breakers, ICT macros).

Plan: /root/.claude/plans/here-is-my-strategy-elegant-squid.md

Usage: python backtest.py
"""

import os
import sys
from collections import namedtuple

import pandas as pd

try:
    import yfinance as yf
except ImportError:
    yf = None

CSV_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "yf")

import config
from ict.bias import htf_bias
from ict.dxy_synthetic import compute_dxy, compute_dxy_range
from ict.fvg import enumerate_fvgs, first_fvg_after, detect_new_fvg
from ict.order_block import detect_order_blocks
from ict.breaker import detect_breakers
from ict.killzones import (
    in_used_killzone, minutes_into_killzone, can_enter_new_pipeline,
)
from ict.structure import directional_pull, bias_holds_on_tf, classify_intermediates, last_unmitigated
from ict.mss import mss_direction, structural_direction
from ict.levels import build_day_levels
from ict.cls_cycles import cbdr_hl, cycle_phases, in_macro_window
from ict.liquidity_zones import collect_zones, most_recent_tap
from ict.liquidity_run import validate as validate_sweep, confirm_tf_for
from ict.smt import confirm as smt_confirm
from ict.target import pick as pick_target, pick_dol, candidates as target_candidates
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.swings import find_swings
from ict.game_theory import score_setup, passes as gt_passes
from ict.context import time_in_zone_pre_event, dwell_at_level
from ict.volatility import realized_vol, range_expansion, vol_regime
from ict.amd import classify_phase as classify_amd_phase
from ict.risk_overlay import RiskOverlay
from ict.intermarket import resolve as resolve_intermarket
from ict.entry import build as build_entry
from news_filter import NewsCalendar
from risk import (
    position_size, pip_size, adjust_exit,
)


YF_TICKERS = {
    "GBPUSD": "GBPUSD=X",
    "EURUSD": "EURUSD=X",
    "EURGBP": "EURGBP=X",
    "USDJPY": "USDJPY=X",
    "USDCAD": "USDCAD=X",
    "USDSEK": "USDSEK=X",
    "USDCHF": "USDCHF=X",
    # Real US Dollar Index (HistData ticker UDXUSD, remapped to "DXY"
    # on import). Optional — when present we use it as the DXY series
    # directly instead of computing synthetic DXY from constituents.
    "DXY":    None,
}

Bar = namedtuple("Bar", "Open High Low Close")
SynBar = namedtuple("SynBar", "Open High Low Close")


def _load_csv_cache(name, interval):
    """Read a pre-cached CSV for `name` at `interval` (e.g. '5m') if present.

    Expected path: data/yf/{NAME}_{interval}.csv with a DatetimeIndex and
    Open/High/Low/Close columns. Returns None if the file is missing.
    """
    path = os.path.join(CSV_CACHE_DIR, f"{name}_{interval}.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")
    return df


def fetch_data(period="60d", interval="5m"):
    """Return {symbol: DataFrame[Open, High, Low, Close, (Volume)]} at M5.

    Resolution order (per symbol):
      1. data.loader.get_bars (M1 store -> resample, OR yf CSV fallback)
      2. live yfinance download if loader returns None and yfinance is installed

    Volume column is preserved if present (Dukascopy tick-count); absent for
    yfinance bars.
    """
    from data import loader
    out = {}
    for name, ticker in YF_TICKERS.items():
        df = loader.get_bars(name, tf="5T")
        source = loader.source_for(name)
        if df is None or df.empty:
            if ticker is None or yf is None:
                # ticker=None means "store-only" (e.g. DXY). Skip silently
                # if no store data; the caller is expected to handle absence.
                if df is None:
                    print(f"  INFO: no data for {name} (store empty, no yfinance fallback)")
                continue
            df = yf.download(ticker, period=period, interval=interval,
                             progress=False, auto_adjust=False)
            source = "yf_live"
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
        print(f"  {name} [{source}]: {len(df)} bars, {df.index.min()} -> {df.index.max()}")
    return out


def resample(df_5m, rule):
    return df_5m.resample(rule).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
    }).dropna()


def df_to_bars(df):
    return [Bar(r.Open, r.High, r.Low, r.Close) for r in df.itertuples(index=False)]


# Direction: which pair OTHERS sit on the opposite side of NYO.
OTHER = {"EURUSD": "GBPUSD", "GBPUSD": "EURUSD"}


class Backtester:
    def __init__(self, data_5m):
        self.data_5m = data_5m
        self.tf_dfs = {}
        self.tf_bars = {}
        self.tf_index = {}
        for sym, df in data_5m.items():
            for tf_name, rule in [("5T", None), ("15T", "15min"), ("60T", "60min"),
                                  ("240T", "240min"), ("D", "1D"), ("W", "1W")]:
                d = df if rule is None else resample(df, rule)
                self.tf_dfs[(sym, tf_name)] = d
                self.tf_bars[(sym, tf_name)] = df_to_bars(d)
                self.tf_index[(sym, tf_name)] = d.index

        self.equity = config.STARTING_CASH
        self.start_equity = self.equity
        self.active = {}
        self.pending = {}
        self.trades = []
        self.risk = RiskOverlay(start_equity=self.equity, equity=self.equity)
        # Per-session entry tracking: only one INITIAL entry per pair per
        # killzone per UTC date. Pyramid adds do NOT consume this slot.
        self.session_entries = {}    # (date, kz_name, pair) -> int
        # Whether the London->NY handoff reversal has been processed today.
        self.session_handoff_done = {}    # (date, pair) -> bool
        self.gate = {
            "checks": 0,
            "killzone+first_hour": 0,
            "news_clear": 0,
            "intermarket": 0,
            "pair_match": 0,
            "bias_cascade_d1_supports": 0,
            "bias_cascade_d1_neutral": 0,
            "bias_cascade_d1_against": 0,
            "bias_cascade_h4_supports": 0,
            "bias_cascade_h4_neutral": 0,
            "bias_cascade_h4_against": 0,
            "bias_cascade_h1_supports": 0,
            "bias_cascade_h1_neutral": 0,
            "bias_cascade_h1_against": 0,
            "bias_cascade_m15_supports": 0,
            "bias_cascade_m15_neutral": 0,
            "bias_cascade_m15_against": 0,
            "htf_zone_tap": 0,
            "kz_swing_identified": 0,
            "retail_pool_swept": 0,
            "sweep_validated": 0,
            "smt_confirmed": 0,
            "m5_fvg_trigger": 0,
            "target_found": 0,
            "game_theory_pass": 0,
            "rr_ok": 0,
            "limit_placed": 0,
        }

        self._levels_cache = {}
        self._cbdr_cache = {}
        self._london_first_hour_cache = {}

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

    # -- data slicing ---------------------------------------------------------

    def bars_up_to(self, sym, tf, t):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return []
        pos = idx.searchsorted(t, side="right")
        return self.tf_bars[(sym, tf)][:pos] if pos else []

    def _bar_at(self, sym, tf, t):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return None
        try:
            pos = idx.get_loc(t)
        except KeyError:
            return None
        return self.tf_bars[(sym, tf)][pos]

    def _bars_by_tf(self, sym, t) -> dict:
        return {tf: self.bars_up_to(sym, tf, t)
                for tf in ("5T", "15T", "60T", "240T", "D", "W")}

    # -- caches: levels, CBDR, London first-hour direction -------------------

    def _day_levels(self, sym, t):
        key = (sym, pd.Timestamp(t).tz_convert("America/New_York").normalize())
        if key not in self._levels_cache:
            self._levels_cache[key] = build_day_levels(self.data_5m[sym], t)
        return self._levels_cache[key]

    def _cbdr(self, sym, t):
        key = (sym, pd.Timestamp(t).tz_convert("America/New_York").normalize())
        if key not in self._cbdr_cache:
            self._cbdr_cache[key] = cbdr_hl(self.data_5m[sym], t)
        return self._cbdr_cache[key]

    def _killzone_open_swings(self, sym, t):
        """At the most recent killzone-open prior to `t`, snapshot the
        CLOSEST M15 swing high (above the killzone-open price) and CLOSEST
        M15 swing low (below it). Those are the immediate liquidity targets
        the manipulation leg is most likely to hunt during this killzone.
        Returns (closest_high_price | None, closest_low_price | None).
        """
        now_ny = pd.Timestamp(t).tz_convert("America/New_York")
        today_ny = now_ny.normalize()
        kz_starts_ny = []
        for _, s, _ in config.KZ_USED:
            h, m = (int(x) for x in s.split(":"))
            start_ny = today_ny.replace(hour=h, minute=m)
            if start_ny <= now_ny:
                kz_starts_ny.append(start_ny)
        if not kz_starts_ny:
            return None, None
        kz_open_ny = max(kz_starts_ny)
        kz_open_utc = kz_open_ny.tz_convert("UTC")

        bars_at_open = self.bars_up_to(sym, "15T", kz_open_utc)
        if len(bars_at_open) < 10:
            return None, None
        price_at_open = bars_at_open[-1].Close
        swings = find_swings(bars_at_open[-120:])
        highs_above = [s.price for s in swings if s.kind == +1 and s.price > price_at_open]
        lows_below = [s.price for s in swings if s.kind == -1 and s.price < price_at_open]
        closest_high = min(highs_above) if highs_above else None
        closest_low = max(lows_below) if lows_below else None
        return closest_high, closest_low

    def _london_first_hour_dir(self, sym, t):
        """Direction of the London 02:00-03:00 NY hour. +1 if close > open, -1 if <."""
        day = pd.Timestamp(t).tz_convert("America/New_York").normalize()
        key = (sym, day)
        if key in self._london_first_hour_cache:
            return self._london_first_hour_cache[key]
        s = day.replace(hour=2).tz_convert("UTC")
        e = day.replace(hour=3).tz_convert("UTC")
        df = self.data_5m[sym]
        sl = df.loc[(df.index >= s) & (df.index < e)]
        if sl.empty:
            res = None
        else:
            res = +1 if sl.iloc[-1].Close > sl.iloc[0].Open else -1
        self._london_first_hour_cache[key] = res
        return res

    # -- biases --------------------------------------------------------------

    def _dxy_bias_1h(self, t):
        # Prefer the real DXY series if we have it loaded; the synthetic
        # constituent rebuild was a workaround for not having an index feed.
        real = self.bars_up_to("DXY", "60T", t) if ("DXY", "60T") in self.tf_bars else None
        if real and len(real) >= config.SWING_LOOKBACK + 2:
            return htf_bias(real)

        rolls = {s: self.bars_up_to(s, "60T", t) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        if n < config.SWING_LOOKBACK + 2:
            return 0
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS}
            high_px = {s: rolls[s][i].High for s in config.DXY_CONSTITUENTS}
            low_px = {s: rolls[s][i].Low for s in config.DXY_CONSTITUENTS}
            open_px = {s: rolls[s][i].Open for s in config.DXY_CONSTITUENTS}
            c = compute_dxy(close_px); o = compute_dxy(open_px)
            h, l = compute_dxy_range(high_px, low_px)
            if None in (c, o, h, l):
                continue
            series.append(SynBar(o, h, l, c))
        if len(series) < config.SWING_LOOKBACK + 2:
            return 0
        return htf_bias(series)

    # -- run loop ------------------------------------------------------------

    def run(self):
        if "GBPUSD" not in self.data_5m:
            raise SystemExit("GBPUSD data missing")
        timestamps = self.data_5m["GBPUSD"].index
        warmup_end = timestamps[0] + pd.Timedelta(days=7)
        total = len(timestamps)
        print(f"  Iterating {total} 5-min bars...")

        for i, t in enumerate(timestamps):
            for pair in config.PAIRS:
                self._update_orders(pair, t)
            if t < warmup_end:
                continue

            now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            in_kz = in_used_killzone(now)

            # London -> NY handoff: at the start of NY-AM, if any open
            # position's direction conflicts with the current D1 directional
            # pull, exit it so the NY pipeline can re-enter on the new side.
            if in_kz == "NY AM":
                self._maybe_session_handoff(t, now)

            for pair in config.PAIRS:
                if pair in self.active:
                    self._maybe_pyramid(pair, t)
                elif in_kz and pair not in self.pending:
                    self._maybe_open(pair, t)

            if i % 1000 == 0 and i > 0:
                print(f"    bar {i}/{total} ({t}) active={len(self.active)} "
                      f"pending={len(self.pending)} trades={len(self.trades)} "
                      f"equity={self.equity:.0f}")

        last_t = timestamps[-1]
        for pair in list(self.active.keys()):
            last_close = self.data_5m[pair].iloc[-1].Close
            self._force_close(pair, last_close, last_t, "end_of_data")

    # -- fills + exits -------------------------------------------------------

    def _update_orders(self, pair, t):
        bar = self._bar_at(pair, "5T", t)
        if bar is None:
            return
        if pair in self.active:
            st = self.active[pair]
            direction = st["direction"]
            target = st["target"]
            tp_was_hit_this_bar = False
            for leg in list(st["legs"]):
                sl = leg["stop"]
                if direction > 0:
                    sl_hit = bar.Low <= sl
                    tp_hit = bar.High >= target
                else:
                    sl_hit = bar.High >= sl
                    tp_hit = bar.Low <= target
                if sl_hit:
                    self._exit_leg(pair, leg, sl, t, "stop")
                elif tp_hit:
                    if not st.get("tp1_hit", False):
                        # FIRST leg only on TP1; runners stay open.
                        if leg is st["legs"][0]:
                            self._exit_leg(pair, leg, target, t, "target_tp1_scale")
                            tp_was_hit_this_bar = True
                        # Other legs at TP1: leave them, runner extension below.
                    else:
                        # Runner target hit -> close.
                        self._exit_leg(pair, leg, target, t, "target_runner")
            if tp_was_hit_this_bar and self.active.get(pair, {}).get("legs"):
                self._extend_runners(pair, t, target)
            if not self.active.get(pair, {}).get("legs"):
                self.active.pop(pair, None)

        if pair in self.pending:
            pe = self.pending[pair]
            entry = pe["entry_price"]
            direction = pe["direction"]
            filled = (direction > 0 and bar.Low <= entry) or \
                     (direction < 0 and bar.High >= entry)
            age_min = (t - pe["placed_at"]).total_seconds() / 60.0
            if filled:
                self._fill_entry(pair, t)
            elif age_min > 60:        # cancel limit if unfilled after 1h
                idx = pe.get("_setup_log_idx")
                if idx is not None and hasattr(self, "_setup_log"):
                    # Record price excursion during the limit's life.
                    direction = pe["direction"]
                    entry = pe["entry_price"]
                    placed_at = pe["placed_at"]
                    bars = self.tf_dfs[(pair, "5T")]
                    # Fill check starts on the bar AFTER placement (the order
                    # didn't exist during _update_orders on placed_at itself).
                    mask = (bars.index > placed_at) & (bars.index <= t)
                    window = bars[mask]
                    if not window.empty:
                        if direction > 0:
                            best_offset_pips = (window.Low.min() - entry) / pip_size(pair)
                        else:
                            best_offset_pips = (entry - window.High.max()) / pip_size(pair)
                    else:
                        best_offset_pips = float("nan")
                    self._setup_log[idx].update({
                        "outcome": "expired",
                        "best_offset_pips": round(best_offset_pips, 1) if best_offset_pips == best_offset_pips else None,
                    })
                self.pending.pop(pair, None)

    def _fill_entry(self, pair, t):
        pe = self.pending.pop(pair)
        leg = {"entry": pe["entry_price"], "stop": pe["stop"],
               "units": pe["units"], "leg_idx": pe["leg_idx"], "opened_at": t,
               "risk_pct": pe.get("risk_pct", config.RISK_PER_TRADE_PCT)}
        leg_id = f"{pair}-{pe['leg_idx']}-{int(t.timestamp())}"
        leg["leg_id"] = leg_id
        self.risk.note_entry(leg_id, pair, pe["direction"], leg["risk_pct"])
        if pair not in self.active:
            self.active[pair] = {
                "direction": pe["direction"], "target": pe["target"],
                "original_target": pe["target"],
                "legs": [leg], "opened_at": t, "tp1_hit": False,
            }
            # Initial entry: consume the per-session entry slot.
            now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            kz_name = in_used_killzone(now)
            if kz_name:
                key = (now.date(), kz_name, pair)
                self.session_entries[key] = self.session_entries.get(key, 0) + 1
        else:
            prior = self.active[pair]["legs"][-1]
            prior["stop"] = prior["entry"]   # BE on add
            self.active[pair]["legs"].append(leg)

    def _exit_leg(self, pair, leg, exit_price, t, reason):
        st = self.active[pair]
        direction = st["direction"]
        # Apply exit-side spread + slippage.
        exit_adj = adjust_exit(exit_price, direction, pair)
        pnl = (exit_adj - leg["entry"]) * leg["units"] * direction
        self.equity += pnl
        if "leg_id" in leg:
            self.risk.note_exit(leg["leg_id"])
        self.trades.append({
            "pair": pair, "leg_idx": leg["leg_idx"], "direction": direction,
            "entry": leg["entry"], "exit": exit_adj, "units": leg["units"],
            "pnl": pnl, "opened_at": leg["opened_at"], "closed_at": t,
            "reason": reason,
        })
        st["legs"].remove(leg)
        if not st["legs"]:
            self.active.pop(pair, None)

    def _force_close(self, pair, price, t, reason):
        for leg in list(self.active[pair]["legs"]):
            self._exit_leg(pair, leg, price, t, reason)

    def _extend_runners(self, pair, t, tp1_price):
        """Called once when TP1 is hit and at least one runner leg survives.
        Tighten runner stops to the nearest M15 ITH/ITL behind price, and set
        the new target to the next HTF DOL beyond TP1. If no further DOL is
        available (we're against the HTF draw), close all runners.
        """
        st = self.active[pair]
        st["tp1_hit"] = True
        direction = st["direction"]
        cur_price = tp1_price   # we just hit it

        # New target = next HTF DOL beyond current price.
        levels = self._day_levels(pair, t)
        cbdr_h, cbdr_l = self._cbdr(pair, t)
        htf_for_dol = {
            "D":    self.bars_up_to(pair, "D", t),
            "240T": self.bars_up_to(pair, "240T", t),
            "60T":  self.bars_up_to(pair, "60T", t),
            "15T":  self.bars_up_to(pair, "15T", t),
        }
        new_target = pick_dol(
            pair, htf_for_dol, levels, cbdr_h, cbdr_l, direction, cur_price,
            risk_pips=None, min_rr=None,
        ) if levels is not None else None
        # Validate the new target is meaningfully beyond TP1.
        pip = pip_size(pair)
        min_extension_pips = 5
        if (new_target is None
                or (direction > 0 and new_target.price <= cur_price + min_extension_pips * pip)
                or (direction < 0 and new_target.price >= cur_price - min_extension_pips * pip)):
            # No HTF DOL beyond -> we're against the bigger draw. Exit runners.
            self._force_close(pair, cur_price, t, "runner_no_htf_dol")
            return

        # Tighten runner stops to the nearest unmitigated M15 ITH/ITL
        # behind price (ITH for longs' runners = above, but wait we want stop
        # BEHIND for runners; for shorts the stop is ABOVE so we want the
        # nearest unmitigated ITH above current; for longs we want the
        # nearest unmitigated ITL below).
        bars_15 = self.bars_up_to(pair, "15T", t)
        new_stop = None
        if bars_15:
            ints = classify_intermediates(bars_15)
            if direction > 0:
                # Long runners: stop below at nearest unmitigated ITL.
                itl_candidates = [i for i in ints if i.kind == -1
                                  and not i.mitigated and i.price < cur_price]
                if itl_candidates:
                    new_stop = max(c.price for c in itl_candidates)
            else:
                ith_candidates = [i for i in ints if i.kind == +1
                                  and not i.mitigated and i.price > cur_price]
                if ith_candidates:
                    new_stop = min(c.price for c in ith_candidates)

        # Update target on the position and stops on remaining legs.
        st["target"] = new_target.price
        if new_stop is not None:
            for leg in st["legs"]:
                if direction > 0:
                    leg["stop"] = max(leg["stop"], new_stop)
                else:
                    leg["stop"] = min(leg["stop"], new_stop)

    def _maybe_session_handoff(self, t, now):
        """At NY-AM open, close any open position whose direction conflicts
        with the current D1 directional pull. The NY pipeline can then re-enter
        on the new side as its own per-session trade.
        """
        for pair in list(self.active.keys()):
            key = (now.date(), pair)
            if self.session_handoff_done.get(key):
                continue
            d1_bars = self.bars_up_to(pair, "D", t)
            if not d1_bars:
                continue
            d1_dir = directional_pull(d1_bars)
            if d1_dir == 0:
                self.session_handoff_done[key] = True
                continue
            pos_dir = self.active[pair]["direction"]
            if pos_dir != d1_dir:
                bar = self._bar_at(pair, "5T", t)
                if bar is not None:
                    self._force_close(pair, bar.Close, t, "session_handoff_reversal")
            self.session_handoff_done[key] = True

    # -- new entry pipeline --------------------------------------------------

    def _maybe_open(self, pair, t):
        g = self.gate
        g["checks"] += 1
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t

        if not can_enter_new_pipeline(now):
            return
        g["killzone+first_hour"] += 1
        if config.NEWS_HARD_BLOCK_ENABLED and self.news.is_blocked(now):
            return
        g["news_clear"] += 1

        # Per-session entry cap: only one INITIAL entry per pair per killzone.
        kz_name = in_used_killzone(now)
        session_key = (now.date(), kz_name, pair) if kz_name else None
        if session_key and self.session_entries.get(session_key, 0) >= 1:
            g.setdefault("session_entry_cap", 0)
            g["session_entry_cap"] += 1
            return

        # Intermarket pair selection.
        dxy_b = self._dxy_bias_1h(t)
        eurgbp_b = htf_bias(self.bars_up_to(config.REF_EURGBP, "60T", t))
        sig = resolve_intermarket(dxy_b, eurgbp_b)
        if sig is None:
            return
        g["intermarket"] += 1
        if sig.pair != pair:
            return
        g["pair_match"] += 1
        direction = sig.direction

        # Fractal bias cascade: D1 -> H4 -> H1 -> M15. Tri-state per TF
        # ("supports" / "against" / "neutral"). Strict TFs reject only on
        # EXPLICIT against; neutral (no structural read on that TF) falls
        # through. This is what lets the algo trade when a higher TF is
        # quiet enough not to have formed unmitigated ITH/ITL yet — common
        # on D1 with only ~40 days of history.
        bars_5_pre = self.bars_up_to(pair, "5T", t)
        if not bars_5_pre:
            return
        cur_price_cascade = bars_5_pre[-1].Close

        d1_bars = self.bars_up_to(pair, "D", t)
        d1_pull = directional_pull(d1_bars)
        if d1_pull == direction:
            g["bias_cascade_d1_supports"] += 1
        elif d1_pull == -direction:
            g["bias_cascade_d1_against"] += 1
            if "D" in config.BIAS_CASCADE_STRICT_TFS:
                return
        else:
            g["bias_cascade_d1_neutral"] += 1

        cascade_pass = True
        for tf, key_root in (("240T", "bias_cascade_h4"),
                             ("60T",  "bias_cascade_h1"),
                             ("15T",  "bias_cascade_m15")):
            tf_bars_now = self.bars_up_to(pair, tf, t)
            state = bias_holds_on_tf(tf_bars_now, direction, cur_price_cascade)
            if state is True:
                g[f"{key_root}_supports"] += 1
            elif state is False:
                g[f"{key_root}_against"] += 1
                if tf in config.BIAS_CASCADE_STRICT_TFS:
                    cascade_pass = False
                    break
            else:
                g[f"{key_root}_neutral"] += 1
        if not cascade_pass:
            return

        # HTF liquidity zone tap.
        tf_bars = self._bars_by_tf(pair, t)
        zones = collect_zones(tf_bars, direction)
        bars_5 = tf_bars["5T"]
        if not bars_5:
            return
        cur_price = bars_5[-1].Close
        # Tap = any of the last ~30 min of M5 wicks entered an unmitigated zone.
        zone = most_recent_tap(zones, bars_5[-6:])
        if zone is None:
            return
        g["htf_zone_tap"] += 1

        # What level got swept? Take the nearest recognized retail pool that
        # the most recent extreme on M15 went beyond.
        levels = self._day_levels(pair, t)
        cbdr_h, cbdr_l = self._cbdr(pair, t)
        if levels is None:
            return
        bars_15 = tf_bars["15T"]
        if len(bars_15) < 4:
            return
        recent_15 = bars_15[-8:]   # ~2h of manipulation
        if direction > 0:
            sweep_extreme = min(b.Low for b in recent_15)
        else:
            sweep_extreme = max(b.High for b in recent_15)

        # PRIMARY swept-level source: closest M15 swing extreme as of the
        # most recent killzone-open. That's the visible liquidity the
        # manipulation leg is most likely to hunt.
        kz_high, kz_low = self._killzone_open_swings(pair, t)
        kz_target = kz_low if direction > 0 else kz_high
        if kz_target is not None:
            g["kz_swing_identified"] += 1

        swept_name = None
        swept_price = None

        # Was the killzone-open swing actually swept?
        if kz_target is not None:
            if direction > 0 and sweep_extreme < kz_target <= cur_price:
                swept_name, swept_price = "KZSwingLow", kz_target
            elif direction < 0 and sweep_extreme > kz_target >= cur_price:
                swept_name, swept_price = "KZSwingHigh", kz_target

        # Secondary: any other recognized retail pool in the M15 sweep range.
        if swept_name is None:
            equal_highs = find_equal_highs(bars_15, pair, lookback=120)
            equal_lows = find_equal_lows(bars_15, pair, lookback=120)
            m15_swings = find_swings(bars_15[-120:])
            recent_swing_highs = [s.price for s in m15_swings if s.kind == +1]
            recent_swing_lows = [s.price for s in m15_swings if s.kind == -1]
            if direction > 0:
                cands = target_candidates(levels, cbdr_h, cbdr_l, direction=-1)
                cands += [("EqualLows", p) for p in equal_lows]
                cands += [("M15SwingLow", p) for p in recent_swing_lows]
                swept = [(n, px) for n, px in cands if sweep_extreme < px <= cur_price]
            else:
                cands = target_candidates(levels, cbdr_h, cbdr_l, direction=+1)
                cands += [("EqualHighs", p) for p in equal_highs]
                cands += [("M15SwingHigh", p) for p in recent_swing_highs]
                swept = [(n, px) for n, px in cands if sweep_extreme > px >= cur_price]
            if swept:
                if direction > 0:
                    swept_name, swept_price = min(swept, key=lambda x: x[1])
                else:
                    swept_name, swept_price = max(swept, key=lambda x: x[1])

        # Tertiary: D1/W1 zone tap counts as institutional liquidity itself.
        # Use the OUTER boundary (the edge price crossed first to enter the
        # zone) as the swept level — that's what gets "swept" semantically.
        if swept_name is None and zone.tf in ("D", "W"):
            swept_name = f"{zone.tf}{zone.kind.upper()}"
            swept_price = zone.top if direction > 0 else zone.bottom

        if swept_name is None:
            return
        g["retail_pool_swept"] += 1

        # Sweep validation: M5 wick (High/Low) pierces, M15 confirm by Close.
        # KZ manipulation can take up to ~3h, so pierce window = 36 M5 bars.
        sweep = validate_sweep(
            entry_tf_bars=bars_5,
            confirm_tf_bars=bars_15,
            entry_tf="5T", symbol=pair,
            swept_level=swept_price, direction=direction,
            pierce_lookback=36,
        )
        if not sweep.valid:
            return
        g["sweep_validated"] += 1

        # SMT vs NYO on both pairs — confluence, NOT a hard gate.
        # config.SMT_REQUIRED=True restores the legacy block-on-no-divergence
        # behaviour. Default is False: SMT contributes to the game-theory
        # score; setups can still fire without it.
        other = OTHER[pair]
        other_levels = self._day_levels(other, t)
        other_bars_5 = self.bars_up_to(other, "5T", t)
        smt = None
        if other_levels is not None and other_bars_5:
            smt = smt_confirm(
                traded_symbol=pair, traded_price=cur_price, traded_nyo=levels.nyo,
                other_symbol=other, other_price=other_bars_5[-1].Close,
                other_nyo=other_levels.nyo, direction=direction,
            )
        if config.SMT_REQUIRED and smt is None:
            return
        if smt is not None:
            g["smt_confirmed"] += 1
        else:
            g.setdefault("smt_absent", 0)
            g["smt_absent"] += 1

        # MSS-2-of-3 — primary directional gate. At least 2 of
        # {EURUSD, GBPUSD, DXY} M15 must show a market-structure shift
        # in the trade direction. DXY's MSS is inverted because DXY up
        # = USD strong = EUR/GBP pairs down.
        mss_hits = 0
        for sym in ("EURUSD", "GBPUSD"):
            sb = self.bars_up_to(sym, "15T", t)
            if sb and mss_direction(sb) == direction:
                mss_hits += 1
        dxy_bars_15 = self.bars_up_to("DXY", "15T", t)
        if dxy_bars_15 and mss_direction(dxy_bars_15) == -direction:
            mss_hits += 1
        if mss_hits < 2:
            g.setdefault("mss_2_of_3_fail", 0)
            g["mss_2_of_3_fail"] += 1
            return
        g.setdefault("mss_2_of_3_pass", 0)
        g["mss_2_of_3_pass"] += 1

        # Trigger search: any unmitigated in-direction zone inside the
        # killzone, in operator-priority order: M5 FVG -> M5 OB -> M5
        # breaker -> M15 breaker. The user-spec rule is "look for entries
        # starting from the smaller timeframes."
        mins_in = minutes_into_killzone(now) or 0
        kz_open_bar_idx = len(bars_5) - (mins_in // 5)

        trigger = None         # the zone object
        trigger_kind = None    # "fvg" / "ob" / "breaker"
        trigger_tf = None      # "5T" / "15T"
        c0_for_stop = None     # M5 bar reference for fallback stop logic

        fvg = first_fvg_after(bars_5, pair, kz_open_bar_idx, direction)
        if fvg is not None:
            trigger, trigger_kind, trigger_tf = fvg, "fvg", "5T"
            trigger_idx = fvg.bar_index
            c0_for_stop = bars_5[max(0, fvg.bar_index - 1)]
        else:
            obs = detect_order_blocks(bars_5)
            for ob in obs:
                if (ob.direction == direction and not ob.mitigated
                        and ob.bar_index >= kz_open_bar_idx):
                    trigger, trigger_kind, trigger_tf = ob, "ob", "5T"
                    trigger_idx = ob.bar_index
                    break
        if trigger is None:
            for tf in ("5T", "15T"):
                tf_bars = self.bars_up_to(pair, tf, t)
                if not tf_bars:
                    continue
                brks = detect_breakers(tf_bars)
                # Filter to in-direction, unmitigated, recent (last ~12 bars on M5
                # is ~1h; on M15 it's ~3h — both within a killzone's reach).
                recent_cut = len(tf_bars) - (12 if tf == "5T" else 8)
                for br in brks:
                    if (br.direction == direction and not br.mitigated
                            and br.flipped_index >= recent_cut):
                        trigger, trigger_kind, trigger_tf = br, "breaker", tf
                        trigger_idx = br.flipped_index
                        break
                if trigger is not None:
                    break
        if trigger is None:
            return
        g["m5_fvg_trigger"] += 1
        g.setdefault(f"trigger_{trigger_kind}_{trigger_tf}", 0)
        g[f"trigger_{trigger_kind}_{trigger_tf}"] += 1

        # Near edge of the trigger zone: the side price reaches first
        # when retesting. Same convention for FVG, OB, Breaker — they
        # all expose top/bottom on the same dataclass shape.
        near_edge = trigger.top if direction > 0 else trigger.bottom

        # Stop: nearest M5 swing high/low BEYOND the near edge, with M15
        # swing as a tighter alternative if M5 is too wide. User spec:
        # "my stops are always based on m5 and M15 timeframe."
        pip_p = pip_size(pair)
        swings_5 = find_swings(bars_5)
        bars_15 = self.bars_up_to(pair, "15T", t)
        swings_15 = find_swings(bars_15) if bars_15 else []

        def _structural_stop(target_swings, edge):
            if direction < 0:
                cands = [s.price for s in target_swings if s.kind == +1 and s.price > edge]
                return (min(cands) + pip_p) if cands else None
            cands = [s.price for s in target_swings if s.kind == -1 and s.price < edge]
            return (max(cands) - pip_p) if cands else None

        stop_m5 = _structural_stop(swings_5, near_edge)
        stop_m15 = _structural_stop(swings_15, near_edge)
        # Prefer the tighter (closer to entry) of the two — that's the
        # smallest risk; the M5 swing usually wins unless price has been
        # tightly coiling and the M15 swing is closer.
        candidates = [s for s in (stop_m5, stop_m15) if s is not None]
        if not candidates:
            # Last-resort fallback so a trigger without nearby swings still
            # gets a structural stop, even if wider than ideal.
            if c0_for_stop is not None:
                stop_raw = (c0_for_stop.Low - pip_p) if direction > 0 else (c0_for_stop.High + pip_p)
            else:
                stop_raw = (trigger.bottom - pip_p) if direction > 0 else (trigger.top + pip_p)
        else:
            if direction < 0:
                stop_raw = min(candidates)
            else:
                stop_raw = max(candidates)

        # Risk sanity check: a swing-based stop > 30 pips is a sign that
        # the M5/M15 structure is too thin nearby; in that case skip the
        # setup rather than overrisk.
        if abs(near_edge - stop_raw) / pip_p > config.MAX_STRUCTURAL_STOP_PIPS:
            g.setdefault("stop_too_wide", 0)
            g["stop_too_wide"] += 1
            return

        # Target — prefer the highest-TF pool that gives acceptable RR.
        # We can pre-compute risk from the swept-price stop to feed the
        # picker; this lets it prefer PWH/PDH over LondonHigh when the
        # nearest pool gives sub-1.5R but the next pool up is reachable.
        pip_p = pip_size(pair)
        raw_entry_preview = near_edge
        est_stop = stop_raw
        est_risk_pips = abs(raw_entry_preview - est_stop) / pip_p
        # Structural DOL — anchored to most recent unmitigated HTF ITH/ITL
        # with rank-based pool list (PWH/PDH/session/CBDR) as fallback.
        htf_for_dol = {
            "D":    self.bars_up_to(pair, "D", t),
            "240T": self.bars_up_to(pair, "240T", t),
            "60T":  self.bars_up_to(pair, "60T", t),
            "15T":  self.bars_up_to(pair, "15T", t),
        }
        target = pick_dol(
            pair, htf_for_dol, levels, cbdr_h, cbdr_l, direction, cur_price,
            risk_pips=est_risk_pips, min_rr=config.MIN_RR,
        )
        if target is None:
            return
        g["target_found"] += 1

        # --- Continuous context features (new scoring) ---
        # Consolidation before the trigger: how many of the K bars before
        # the trigger formed had ranges overlapping the trigger zone.
        pre = bars_5[:trigger_idx] if trigger_idx > 0 else []
        consolidation = time_in_zone_pre_event(
            pre, trigger.top, trigger.bottom, config.GT_CONSOLIDATION_LOOKBACK_BARS,
        )

        # Dwell at swept level pre-sweep: how many recent M5 bars touched
        # the level within tolerance.
        dwell = dwell_at_level(
            bars_5, swept_price, 2 * pip_p, config.GT_DWELL_LOOKBACK_BARS,
        )

        # Displacement strength of the trigger candle. For FVGs and OBs the
        # candle range vs trailing median is meaningful; for breakers we use
        # the bar at flipped_index. trigger_idx already abstracts the index.
        disp_strength = None
        if 0 <= trigger_idx < len(bars_5) and trigger_idx >= config.GT_DISPLACEMENT_LOOKBACK_BARS:
            window = bars_5[trigger_idx - config.GT_DISPLACEMENT_LOOKBACK_BARS:trigger_idx]
            ranges = sorted([b.High - b.Low for b in window])
            if ranges:
                med = ranges[len(ranges) // 2]
                if med > 0:
                    mid_bar = bars_5[trigger_idx]
                    disp_strength = (mid_bar.High - mid_bar.Low) / med

        # Range expansion at the most recent M5 bar (the entry bar).
        rng_exp = range_expansion(bars_5, config.GT_DISPLACEMENT_LOOKBACK_BARS)

        # Vol regime: build a short history of realized-vol values and
        # classify the latest one.
        rv_hist = []
        window = config.GT_REALIZED_VOL_WINDOW
        history = config.GT_REALIZED_VOL_HISTORY
        for end in range(max(window + 1, len(bars_5) - history), len(bars_5) + 1):
            rv_hist.append(realized_vol(bars_5[:end], window))
        regime = vol_regime(rv_hist) if rv_hist else "NORMAL"

        # News proximity (replaces the old hard block).
        prox_min, prox_impact = self.news.proximity_minutes(now)

        # AMD phase on the setup TF (M15) — gates the consolidation bonus so
        # we don't reward dwell that happened mid-distribution (which is
        # institutional unloading, not accumulation).
        bars_15 = self.bars_up_to(pair, "15T", t)
        amd_label, _, _ = classify_amd_phase(bars_15, pair) if bars_15 else ("NONE", None, None)

        # Record audit fields on the trigger if it's an FVG. OB / Breaker
        # dataclasses don't have these fields - we just skip the recording.
        if trigger_kind == "fvg":
            fvg.displacement_strength = disp_strength
            fvg.time_in_zone_pre_formation = consolidation
            fvg.range_expansion = rng_exp
            fvg.news_proximity_minutes = prox_min
            fvg.news_impact = prox_impact
            fvg.formed_in_macro_window = in_macro_window(now)

        # Game-theory score.
        phases = cycle_phases(now)
        session_phase = "ny_am" if "ny_am" in phases else ("london" if "london" in phases else "other")
        london_dir = self._london_first_hour_dir(pair, t)
        score = score_setup(
            swept_level_name=swept_name,
            sweep_strong=sweep.strong,
            htf_zone_kind=zone.kind, htf_zone_tf=zone.tf,
            timestamp=t,
            london_first_hour_dir=london_dir,
            trade_direction=direction,
            session_phase=session_phase,
            consolidation_score=consolidation,
            amd_phase=amd_label,
            dwell_count=dwell,
            displacement_strength=disp_strength,
            range_expansion_ratio=rng_exp,
            vol_regime_label=regime,
            news_proximity_minutes=prox_min,
            news_impact=prox_impact,
            smt_confirmed=(smt is not None),
        )
        if not gt_passes(score):
            return
        g["game_theory_pass"] += 1

        # Build entry signal (applies spread+slippage to entry).
        signal = build_entry(
            pair=pair, direction=direction, trigger_fvg=trigger,
            swept_price=swept_price, target=target,
            confluence_score=score.total,
            swept_level_name=swept_name,
            htf_zone_kind=zone.kind, htf_zone_tf=zone.tf,
            raw_entry_override=near_edge,
            stop_override=stop_raw,
        )
        if signal is None:
            # Diagnostic: show why RR was rejected so we can tune floors.
            from risk import pip_size as _pip
            pip = _pip(pair)
            raw_entry = near_edge
            est_stop = stop_raw
            est_risk = abs(raw_entry - est_stop) / pip
            est_reward = abs(target.price - raw_entry) / pip
            est_rr = est_reward / est_risk if est_risk > 0 else 0.0
            if not hasattr(self, "_rr_misses"):
                self._rr_misses = []
            self._rr_misses.append({
                "t": t, "pair": pair, "dir": direction,
                "swept": swept_name, "target": target.name,
                "risk_p": round(est_risk, 1), "reward_p": round(est_reward, 1),
                "rr": round(est_rr, 2),
            })
            return
        g["rr_ok"] += 1

        # Risk overlay: portfolio-level vetoes + correlation-aware sizing.
        self.risk.update_equity(self.equity, now)
        leg_risk_pct = config.RISK_PER_TRADE_PCT * config.PYRAMID_LEG_RISK_FRAC[0]
        allowed, reason, size_mult = self.risk.can_enter(pair, direction, leg_risk_pct)
        if not allowed:
            g.setdefault(f"risk_veto_{reason}", 0)
            g[f"risk_veto_{reason}"] += 1
            return

        units = int(position_size(self.equity, signal.entry, signal.stop, pair)
                    * config.PYRAMID_LEG_RISK_FRAC[0]
                    * size_mult)
        if units == 0:
            return

        # Entry price: limit at FVG mid (signal.entry) OR market at current
        # M5 Close (with spread/slippage already applied via signal-side
        # adjust_entry below). Market mode bypasses the FVG-mid passive
        # limit which often goes unfilled in fast markets.
        if config.ENTRY_MODE == "market":
            from risk import adjust_entry as _adj_entry
            cur_bar = self._bar_at(pair, "5T", t)
            mkt_entry_raw = cur_bar.Close if cur_bar is not None else signal.entry
            entry_price = _adj_entry(mkt_entry_raw, direction, pair)
            # Recompute units against the actual entry (sizing is risk-based).
            units = int(position_size(self.equity, entry_price, signal.stop, pair)
                        * config.PYRAMID_LEG_RISK_FRAC[0]
                        * size_mult)
            if units == 0:
                return
        else:
            entry_price = signal.entry

        # Diagnostic: per-setup detail so we can see what happens to each entry.
        if not hasattr(self, "_setup_log"):
            self._setup_log = []
        self._setup_log.append({
            "t": t, "pair": pair, "direction": direction,
            "entry": entry_price, "stop": signal.stop, "target": signal.target.price,
            "risk_pips": round(signal.risk_pips, 1),
            "reward_pips": round(signal.reward_pips, 1),
            "rr": round(signal.rr, 2), "score": round(score.total, 2),
            "swept": swept_name, "zone": f"{zone.kind}/{zone.tf}",
            "trigger": f"{trigger_kind}/{trigger_tf}",
            "target_name": signal.target.name,
            "mss_hits": mss_hits,
            "outcome": "placed",
        })
        self.pending[pair] = {
            "entry_price": entry_price, "stop": signal.stop, "target": signal.target.price,
            "direction": direction, "units": units, "leg_idx": 1,
            "risk_pct": leg_risk_pct * size_mult,
            "_setup_log_idx": len(self._setup_log) - 1,
            "placed_at": t,
            "meta": {
                "score": signal.confluence_score, "swept": swept_name,
                "zone": f"{zone.kind}/{zone.tf}", "rr": round(signal.rr, 2),
                "target": target.name,
            },
        }
        g["limit_placed"] += 1
        # Market mode: fill immediately on the same bar.
        if config.ENTRY_MODE == "market":
            self._fill_entry(pair, t)
            self._setup_log[-1]["outcome"] = "market_filled"

    def _maybe_pyramid(self, pair, t):
        st = self.active[pair]
        if len(st["legs"]) >= config.MAX_LEGS:
            return
        if pair in self.pending:
            return
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if config.NEWS_HARD_BLOCK_ENABLED and self.news.is_blocked(now):
            return
        if not in_used_killzone(now):
            return

        bars5 = self.bars_up_to(pair, "5T", t)
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != st["direction"]:
            return

        pip = pip_size(pair)
        last_entry = st["legs"][-1]["entry"]
        cur_price = bars5[-1].Close
        favour_pips = (cur_price - last_entry) * st["direction"] / pip
        if favour_pips < config.PYRAMID_MIN_FAVOUR_PIPS:
            return

        from risk import adjust_entry as _adj
        leg_idx = len(st["legs"]) + 1
        entry = _adj(fvg.mid, st["direction"], pair)
        stop = st["legs"][-1]["entry"]
        if abs(entry - stop) <= 0:
            return
        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return

        risk_frac = config.PYRAMID_LEG_RISK_FRAC[min(leg_idx - 1, len(config.PYRAMID_LEG_RISK_FRAC) - 1)]

        # Risk overlay gates pyramids too — same daily cap, same group budget.
        self.risk.update_equity(self.equity, t.to_pydatetime() if hasattr(t, "to_pydatetime") else t)
        leg_risk_pct = config.RISK_PER_TRADE_PCT * risk_frac
        allowed, reason, size_mult = self.risk.can_enter(pair, st["direction"], leg_risk_pct)
        if not allowed:
            return

        units = int(position_size(self.equity, entry, stop, pair) * risk_frac * size_mult)
        if units == 0:
            return

        self.pending[pair] = {
            "entry_price": entry, "stop": stop, "target": st["target"],
            "direction": st["direction"], "units": units,
            "leg_idx": leg_idx, "placed_at": t,
            "risk_pct": leg_risk_pct * size_mult,
            "meta": {"add": True},
        }


def summarize(bt):
    n = len(bt.trades)
    if n == 0:
        return {
            "trades": 0,
            "starting_equity": bt.start_equity,
            "ending_equity": round(bt.equity, 2),
            "pnl": round(bt.equity - bt.start_equity, 2),
        }
    df = pd.DataFrame(bt.trades)
    wins = df[df.pnl > 0]
    losses = df[df.pnl <= 0]
    win_rate = len(wins) / n * 100
    gp = wins.pnl.sum(); gl = -losses.pnl.sum()
    pf = gp / gl if gl > 0 else float("inf")
    eq = bt.start_equity + df.pnl.cumsum()
    rmax = eq.cummax()
    dd = ((eq - rmax) / rmax * 100).min() if len(eq) else 0
    return {
        "trades": n,
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": "inf" if pf == float("inf") else round(pf, 2),
        "starting_equity": bt.start_equity,
        "ending_equity": round(bt.equity, 2),
        "pnl": round(bt.equity - bt.start_equity, 2),
        "pnl_pct": round((bt.equity - bt.start_equity) / bt.start_equity * 100, 2),
        "max_drawdown_pct": round(dd, 2),
        "avg_win": round(wins.pnl.mean() if len(wins) else 0, 2),
        "avg_loss": round(losses.pnl.mean() if len(losses) else 0, 2),
    }


def calibration_report(bt):
    """Trade-frequency vs the operator-target of 2 trades/day (London + NY)
    on 3-5 tradable days/week. Counts initial entries only (pyramid adds
    don't count as new positions).
    """
    if not bt.trades:
        return {"initial_entries": 0, "trades_per_day": 0.0,
                "tradable_days": 0, "weeks_covered": 0}
    df = pd.DataFrame(bt.trades)
    df["opened_at"] = pd.to_datetime(df["opened_at"], utc=True)
    df["date"] = df.opened_at.dt.date
    # Initial entries = leg_idx 1.
    initial = df[df.leg_idx == 1]
    by_day = initial.groupby("date").size()
    by_week = initial.groupby(initial.opened_at.dt.isocalendar().week).size()
    tradable_days = (by_day > 0).sum()
    span_days = (df.opened_at.max() - df.opened_at.min()).days or 1
    return {
        "initial_entries": int(len(initial)),
        "pyramid_adds": int(len(df) - len(initial)),
        "trades_per_day": round(len(initial) / max(span_days, 1), 2),
        "tradable_days": int(tradable_days),
        "calendar_days": int(span_days),
        "target_per_day": 2,
        "target_tradable_days_per_5_weekday_week": "3-5",
        "by_week_initial_entries": by_week.to_dict() if not by_week.empty else {},
    }


def main():
    print("Fetching 60d of 5-min forex data from yfinance...")
    data = fetch_data()
    if "GBPUSD" not in data or "EURUSD" not in data:
        print("ERROR: primary pairs missing")
        sys.exit(1)

    print("\nRunning backtest...")
    bt = Backtester(data)
    bt.run()

    print("\n=== Gate funnel (how many bars survive each filter) ===")
    for k, v in bt.gate.items():
        print(f"  {k:24s} {v}")

    misses = getattr(bt, "_rr_misses", [])
    if misses:
        print(f"\n=== RR-rejected setups ({len(misses)}) ===")
        for m in misses:
            print(f"  {m['t']} {m['pair']} dir={m['dir']:+d} "
                  f"swept={m['swept']} -> target={m['target']} "
                  f"risk={m['risk_p']}p reward={m['reward_p']}p rr={m['rr']}")

    print("\n=== Results ===")
    for k, v in summarize(bt).items():
        print(f"  {k:20s} {v}")

    setup_log = getattr(bt, "_setup_log", [])
    if setup_log:
        print(f"\n=== Setup detail ({len(setup_log)} limits placed) ===")
        for s in setup_log:
            best = s.get("best_offset_pips")
            best_s = f" best_offset_pips={best}" if best is not None else ""
            print(f"  {s['t']} {s['pair']:6s} dir={s['direction']:+d} "
                  f"entry={s['entry']:.5f} stop={s['stop']:.5f} "
                  f"target={s['target']:.5f} ({s.get('target_name','')})")
            print(f"     risk={s.get('risk_pips','?')}p reward={s.get('reward_pips','?')}p "
                  f"rr={s['rr']} score={s['score']} mss={s.get('mss_hits','?')}/3 "
                  f"trigger={s.get('trigger','?')} swept={s['swept']} zone={s['zone']} "
                  f"outcome={s['outcome']}{best_s}")

    print("\n=== Calibration (vs 2 trades/day, 3-5 tradable days/week) ===")
    for k, v in calibration_report(bt).items():
        print(f"  {k:32s} {v}")

    if bt.trades:
        print("\n=== Trades ===")
        df = pd.DataFrame(bt.trades)
        cols = ["opened_at", "closed_at", "pair", "direction", "leg_idx",
                "entry", "exit", "units", "pnl", "reason"]
        print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()

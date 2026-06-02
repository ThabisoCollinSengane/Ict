"""Pandas-based backtester for the ICT intermarket strategy.

Fetches free 5-minute forex data from Yahoo Finance for the last ~60 days,
runs the strategy through the same `ict/` modules used by the QC version,
and reports trades + summary stats. No QuantConnect dependency.

Usage:  python backtest.py
"""

import itertools
import sys
from collections import namedtuple
from datetime import timedelta

import pandas as pd
import yfinance as yf

import config
from ict.killzones import can_open_new_trade, current_killzone
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob, find_breaker_zone
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.bias import htf_bias
from ict.dxy_synthetic import compute_dxy, compute_dxy_range
from ict.amd import detect_consolidation, detect_manipulation, detect_amd_setup
from ict.ote import in_ote, find_swing
from ict.liquidity_divergence import judas_sweep_divergence
from ict.fib_targets import nearest_fib_target
from ict.market_profile import (
    daily_open as mp_daily_open,
    weekly_open as mp_weekly_open,
    session_open as mp_session_open,
    detect_weekly_amd,
    profile_score,
)
from ict.dealing_range import (
    detect_dealing_range,
    is_valid_entry_zone,
    is_valid_target_zone,
    is_nfp_week_low_probability,
    is_post_fomc_low_probability,
)
from intermarket import resolve as resolve_intermarket, resolve_pair_direction
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
}

Bar = namedtuple("Bar", "Open High Low Close")
SynBar = namedtuple("SynBar", "Open High Low Close")


def fetch_data(period="60d", interval="5m"):
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
        self.trades = []
        # Diagnostic counters: how many times each gate was reached / rejected.
        self.gate = {
            "checks": 0, "in_killzone": 0, "news_clear": 0,
            "nfp_fomc_ok": 0, "intermarket_signal": 0, "pair_matches": 0,
            "mss_h1_m15_m5_ok": 0,
            "daily_bias_ok": 0, "h1_bias_ok": 0, "h4_bias_ok": 0,
            "dealing_range_ok": 0, "consolidation_found": 0,
            "manipulation_correct_dir": 0,
            "m5_fvg_correct_dir": 0, "target_found": 0,
            "rr_ok": 0, "units_nonzero": 0, "limit_placed": 0,
            # protection counters
            "drawdown_halt": 0, "daily_loss_halt": 0, "consec_loss_pause": 0,
            # weekly/daily budget counters
            "weekly_cap": 0, "weekly_pair_cap": 0,
            "daily_cap": 0, "daily_pair_cap": 0,
            # market profile counters
            "weekly_amd_confirmed": 0, "session_handover_closed": 0,
            # conviction signal counters
            "ote_zone": 0, "choch_confirmed": 0, "low_conviction": 0,
            "judas_divergence": 0,
        }
        # Wipeout-prevention state
        self._peak_equity       = config.STARTING_CASH
        self._consec_losses     = 0
        self._day_open_eq       = {}   # date -> equity at start of that calendar day
        self._drawdown_halt_until = None  # date after which trading resumes
        # Per-pair weekly AMD cache: updated each bar (daily resolution is enough)
        self._weekly_amd        = {}   # pair -> WeeklyAMD or None
        # Weekly trade budget (3-of-5 pattern)
        self._week_total        = {}   # (iso_year, iso_week) -> int
        self._week_pair         = {}   # (iso_year, iso_week, pair) -> int
        self._day_total         = {}   # date -> int
        self._day_pair          = {}   # (date, pair) -> int

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

            # Session handover runs at any EUR/GBP kill zone start.
            if can_open_new_trade(now):
                self._check_session_handover(t)

            for pair in config.PAIRS:
                if pair in self.active:
                    self._maybe_pyramid(pair, t)
                elif can_open_new_trade(now, pair):
                    self._maybe_open(pair, t)

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

            # Trail stop: move to BE at +TRAIL_BE_PIPS, lock +10 pips at +TRAIL_LOCK_PIPS.
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

            for leg in list(st["legs"]):
                sl = leg["stop"]
                if direction > 0:
                    sl_hit = bar.Low <= sl
                    tp_hit = bar.High >= target
                else:
                    sl_hit = bar.High >= sl
                    tp_hit = bar.Low <= target
                if sl_hit:                       # worst-case: SL first
                    self._exit_leg(pair, leg, sl, t, "stop")
                elif tp_hit:
                    self._exit_leg(pair, leg, target, t, "target")
            if not self.active.get(pair, {}).get("legs"):
                self.active.pop(pair, None)


    def _exit_leg(self, pair, leg, exit_price, t, reason):
        st = self.active[pair]
        direction = st["direction"]
        # Apply exit spread friction (half-spread): you sell at bid for longs,
        # buy at ask for shorts — effective exit is worse than the mid price.
        _spread = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        _exit_friction = (_spread / 2) * pip_size(pair)
        effective_exit = exit_price - direction * _exit_friction
        pnl_usd = (effective_exit - leg["entry"]) * leg["units"] * direction
        pnl_zar = pnl_usd * config.USD_ZAR
        self.equity += pnl_zar
        # Update peak equity and consecutive loss counter after every close.
        self._peak_equity = max(self._peak_equity, self.equity)
        if pnl_zar > 0:
            self._consec_losses = 0
        else:
            self._consec_losses += 1
        record = {
            "pair": pair, "leg_idx": leg["leg_idx"], "direction": direction,
            "entry": leg["entry"], "exit": effective_exit, "units": leg["units"],
            "pnl": pnl_zar, "opened_at": leg["opened_at"], "closed_at": t,
            "reason": reason, "entry_type": leg.get("entry_type", "unknown"),
            "session_side": leg.get("session_side", "no_open"),
        }
        self.trades.append(record)
        self.log.write_trade(record, equity_after=self.equity)
        st["legs"].remove(leg)
        if not st["legs"]:
            self.active.pop(pair, None)
            self.log.delete_position(pair)
        else:
            self.log.upsert_position(pair, st)

    def _force_close(self, pair, price, t, reason):
        for leg in list(self.active[pair]["legs"]):
            self._exit_leg(pair, leg, price, t, reason)

    def _sym_bias(self, sym, tf, t, lookback: int = None):
        bars = self.bars_up_to(sym, tf, t)
        return htf_bias(bars, lookback=lookback)

    def _dxy_bias(self, tf, t, lookback: int = None):
        """Synthetic DXY BOS on the given timeframe."""
        rolls = {s: self.bars_up_to(s, tf, t) for s in config.DXY_CONSTITUENTS}
        lb = lookback if lookback is not None else config.SWING_LOOKBACK
        n = min((len(v) for v in rolls.values()), default=0)
        if n < lb + 2:
            return 0
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS}
            high_px = {s: rolls[s][i].High for s in config.DXY_CONSTITUENTS}
            low_px = {s: rolls[s][i].Low for s in config.DXY_CONSTITUENTS}
            open_px = {s: rolls[s][i].Open for s in config.DXY_CONSTITUENTS}
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
        """Synthetic DXY bar series for the given timeframe (list of SynBar)."""
        rolls = {s: self.bars_up_to(s, tf, t) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        if n < 2:
            return []
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS}
            high_px  = {s: rolls[s][i].High  for s in config.DXY_CONSTITUENTS}
            low_px   = {s: rolls[s][i].Low   for s in config.DXY_CONSTITUENTS}
            open_px  = {s: rolls[s][i].Open  for s in config.DXY_CONSTITUENTS}
            c = compute_dxy(close_px)
            o = compute_dxy(open_px)
            h, l = compute_dxy_range(high_px, low_px)
            if None in (c, o, h, l):
                continue
            series.append(SynBar(o, h, l, c))
        return series

    def _pyramid_lots(self):
        """Return (leg1, leg2, leg3) lot sizes for the current equity tier."""
        for min_eq, lots in config.EQUITY_TIERS:
            if self.equity >= min_eq:
                return lots
        return config.EQUITY_TIERS[-1][1]

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

    def _get_weekly_amd(self, pair: str, t) -> object | None:
        """Cached weekly AMD for this bar (recomputed at most once per bar per pair)."""
        bars = self.tf_bars.get((pair, "D"), [])
        ts   = self.tf_index.get((pair, "D"))
        if ts is None or not bars:
            self._weekly_amd[pair] = None
            return None
        self._weekly_amd[pair] = detect_weekly_amd(bars, ts, t)
        return self._weekly_amd[pair]

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

        # M1 first for pyramids (tightest current level); last for initial entries.
        result = (_check_m1() or _check_base()) if for_pyramid else (_check_base() or _check_m1())
        return result if result is not None else (None, None, None)

    def _find_target(self, pair, direction, t, price, stop=None):
        """Find the nearest target that satisfies the RR requirement.

        If `stop` is supplied, selects the nearest candidate where
        |target - price| >= |price - stop| * MIN_RR (RR-aware selection).
        Falls back to the plain-nearest candidate if nothing satisfies RR.

        Timeframe search order: M15 (last 48 bars) → H1 (24 bars) → H4 → D → W.
        M15/H1 lookbacks are capped to avoid O(n²) scan cost.
        """
        candidates = []

        # Fibonacci extension targets from the initiating OTE swing (Ep. 12 / SD model).
        # These project the natural profit magnets at 100%, 127.2%, 161.8%, 200% of the swing.
        pip_v = pip_size(pair)
        bars15 = self.bars_up_to(pair, "15T", t)
        swing = find_swing(bars15, direction, lookback=config.SWING_LOOKBACK)
        if swing is not None:
            fib_t = nearest_fib_target(
                swing[0], swing[1], direction, price,
                min_distance=config.MIN_PIPS_TARGET * pip_v,
            )
            if fib_t is not None:
                candidates.append(fib_t)

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
                candidates.append(db.High)  # buy-side liquidity (BSL)
                candidates.append(db.Low)   # sell-side liquidity (SSL)
        # Previous Week High/Low (PWWH/PWWL) — higher-timeframe pools.
        w_bars = self.bars_up_to(pair, "W", t)
        if len(w_bars) >= 2:
            candidates.append(w_bars[-2].High)
            candidates.append(w_bars[-2].Low)

        if direction > 0:
            candidates = [c for c in candidates if c > price]
        else:
            candidates = [c for c in candidates if c < price]
        if not candidates:
            return None
        # Prefer targets in the correct dealing range zone (premium/discount).
        bars1h = self.bars_up_to(pair, "60T", t)
        dr = detect_dealing_range(bars1h, lookback=100)
        if dr is not None:
            filtered = [c for c in candidates
                        if is_valid_target_zone(c, dr.high, dr.low, direction)]
            if filtered:
                candidates = filtered
        # Prefer the nearest target satisfying both MIN_RR and MIN_PIPS_TARGET.
        if stop is not None:
            min_reward = max(abs(price - stop) * config.MIN_RR,
                             config.MIN_PIPS_TARGET * pip_v)
        else:
            min_reward = config.MIN_PIPS_TARGET * pip_v
        rr_ok = [c for c in candidates if abs(c - price) >= min_reward]
        if rr_ok:
            return min(rr_ok, key=lambda x: abs(x - price))
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
                    out.append(level)
                elif direction < 0 and level < price - pip_v:
                    out.append(level)
        # ICT: raw swing highs (BSL) above price and swing lows (SSL) below price
        # are liquidity pools that price gravitates toward.
        n = len(bars)
        for i in range(1, n - 1):
            if direction > 0 and bars[i].High > bars[i - 1].High and bars[i].High > bars[i + 1].High:
                if bars[i].High > price:
                    out.append(bars[i].High)
            elif direction < 0 and bars[i].Low < bars[i - 1].Low and bars[i].Low < bars[i + 1].Low:
                if bars[i].Low < price:
                    out.append(bars[i].Low)
        return out

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
            dd_pct = (self._peak_equity - self.equity) / self._peak_equity * 100
            if dd_pct >= config.MAX_DRAWDOWN_HALT_PCT:
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

        # News gate: Medium impact → block (spread risk, no directional catalyst).
        # High impact → allow but override stop to fixed 10-pip (spread protection).
        # News is often the CATALYST that drives price to target faster.
        news_impact = self.news.nearest_impact(now)
        if news_impact == "Medium":
            return
        g["news_clear"] += 1

        if is_nfp_week_low_probability(now, self.news.is_nfp_week(now)):
            return
        if is_post_fomc_low_probability(now, self.news.fomc_whipsaw_date):
            return
        g["nfp_fomc_ok"] += 1

        # ── Weekly / daily trade budget ───────────────────────────────────────
        iso = day_key.isocalendar()
        week_key   = (iso[0], iso[1])
        week_total = self._week_total.get(week_key, 0)
        week_pair  = self._week_pair.get((week_key[0], week_key[1], pair), 0)
        day_total  = self._day_total.get(day_key, 0)
        day_pair   = self._day_pair.get((day_key, pair), 0)

        if week_pair >= config.MAX_PAIR_TRADES_PER_WEEK:
            g["weekly_pair_cap"] += 1
            return
        if day_total >= config.MAX_TRADES_PER_DAY:
            g["daily_cap"] += 1
            return
        if day_pair >= config.MAX_PAIR_TRADES_PER_DAY:
            g["daily_pair_cap"] += 1
            return
        # ─────────────────────────────────────────────────────────────────────

        # Intermarket: DXY gives USD direction.
        # EUR/GBP family (unchanged): EURGBP selects EURUSD vs GBPUSD.
        # NZDUSD family (independent): AUDNZD selects NZD as preferred vs AUD; DXY confirms direction.
        dxy_bias = self._dxy_bias("60T", t, lookback=config.SWING_LOOKBACK_STH)
        if dxy_bias == 0:
            return   # DXY flat → no USD bias → hard gate for all pairs

        if pair in ("EURUSD", "GBPUSD"):
            # Original EUR/GBP logic — unchanged.
            eurgbp_bias = self._sym_bias(config.REF_EURGBP, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
            direction, im_score = resolve_pair_direction(
                dxy_bias, eurgbp_bias, pair, "EURUSD"
            )
            if direction is None:
                return
            if im_score < 0.75:
                return
            if eurgbp_bias == 0 and pair == "GBPUSD":
                return
            mss_sym1, mss_sym2 = "EURUSD", "GBPUSD"

        else:   # NZDUSD — DXY + AUDNZD cross (independent of EUR/GBP family)
            audnzd_bias = self._sym_bias(config.REF_AUDNZD, "60T", t,
                                         lookback=config.SWING_LOOKBACK_STH)
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

        g["intermarket_signal"] += 1
        g["pair_matches"] += 1

        # MSS: 2-of-3 using both pairs in the family + DXY inverse.
        sym1_mss  = self._pair_has_mss(mss_sym1, t, direction)
        sym2_mss  = self._pair_has_mss(mss_sym2, t, direction)
        dxy_mss   = self._dxy_has_mss(t, -direction)
        mss_count = sym1_mss + sym2_mss + dxy_mss
        if mss_count < 2:
            return   # Need at least 2-of-3 MSS
        g["mss_h1_m15_m5_ok"] += 1

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

        # Open-level profile score: daily/weekly/session opens agreeing (0-1).
        # _session_open is returned from the same call so we don't duplicate mp_session_open.
        p_score, _session_open = self._profile_score(pair, direction, cur_price, t)
        conviction += min(p_score, 1)

        # AMD on M15 (0-1): Asia/London consolidation + manipulation sweep
        bars15 = self.bars_up_to(pair, "15T", t)
        amd = detect_amd_setup(bars15, pair)
        amd_score = 0
        if amd is not None:
            rng, sweep_dir = amd
            g["consolidation_found"] += 1
            if sweep_dir == direction:
                amd_score = 1
                conviction += 1
                g["manipulation_correct_dir"] += 1

        # M1 fractal structure is captured via _get_limit_entry (fvg_m1/ob_m1/
        # breaker_m1) — same AMD concept at execution speed without the O(n³)
        # consolidation scan cost that would stall the main loop.

        # OTE zone: bonus conviction when price is in 62-79% retrace (M15 or H1 swing).
        # OTE defines profit POTENTIAL (Fib extension targets), not an entry filter.
        pip_v = pip_size(pair)
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
        # 1. Retail-pool sweep: equal highs/lows swept just before our entry.
        #    Price hunted obvious liquidity → smart money distributed → ideal entry.
        eq_lows  = find_equal_lows(bars15,  config.EQ_HIGH_LOW_TOLERANCE_PIPS * pip_v)
        eq_highs = find_equal_highs(bars15, config.EQ_HIGH_LOW_TOLERANCE_PIPS * pip_v)
        if direction > 0 and eq_lows  and cur_price > eq_lows[-1]:
            conviction += 1
            g["gt_pool_sweep"] = g.get("gt_pool_sweep", 0) + 1
        elif direction < 0 and eq_highs and cur_price < eq_highs[-1]:
            conviction += 1
            g["gt_pool_sweep"] = g.get("gt_pool_sweep", 0) + 1

        # 2. Strong displacement wick: last M5 bar's wick ≥ 60% of bar range.
        #    Aggressive institutional delivery bar — confirms the directional push.
        if bars5:
            lb = bars5[-1]
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
        if kz and "New York" in kz:
            london_bars = [b for b in bars1h if hasattr(b, 'Close')]
            if len(bars1h) >= 3:
                london_dir = 1 if bars1h[-2].Close > bars1h[-3].Close else -1
                if london_dir != direction:
                    conviction += 1
                    g["gt_judas_reversal"] = g.get("gt_judas_reversal", 0) + 1
        # ─────────────────────────────────────────────────────────────────────

        min_conv = config.MIN_CONVICTION
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
        g["m5_fvg_correct_dir"] += 1

        pip = pip_size(pair)
        # Simulate spread + slippage: worsen entry price by (half-spread + slippage).
        _spread = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        _friction = (_spread / 2 + config.SLIPPAGE_PIPS) * pip
        entry = cur_price + direction * _friction   # market order fill with friction

        # High-impact news nearby: override to fixed 10-pip stop (protects against
        # spread widening while still trading the news catalyst).
        if news_impact == "High":
            stop = entry - config.FIXED_STOP_PIPS * pip if direction > 0 \
                   else entry + config.FIXED_STOP_PIPS * pip

        target = self._find_target(pair, direction, t, entry, stop=stop)
        if target is None:
            return
        g["target_found"] += 1

        reward_pips = abs(target - entry) / pip
        if reward_pips < config.MIN_ENTRY_PIPS_TARGET:
            return
        g["rr_ok"] += 1

        # ZAR equity → USD for position sizing; floor at leg-1 lot for current tier.
        equity_usd = self.equity / config.USD_ZAR
        risk_units = int(position_size(equity_usd, entry, stop, pair))
        tier_lots  = self._pyramid_lots()
        min_units  = int(tier_lots[0] * config.LOT_UNITS)
        units = max(risk_units, min_units)
        if units == 0:
            return
        g["units_nonzero"] += 1

        # High-impact news = distribution catalyst: upgrade to full pyramid regardless
        # of conviction score.  News drives speed, direction, and strength — this is
        # the highest-probability setup for reaching target fast.
        if news_impact == "High":
            max_legs = config.MAX_LEGS

        # Market order: fill immediately at current bar close.
        base_type  = "amd" if amd_score else "mss"
        entry_tag  = "news" if news_impact == "High" else base_type
        entry_type = f"{entry_tag}_{pattern_tag}"
        # Session-open side analytics tag (reuse _session_open computed above).
        if _session_open is None:
            _so_side = "no_open"
        elif (direction > 0 and cur_price < _session_open) or (direction < 0 and cur_price > _session_open):
            _so_side = "judas"
        else:
            _so_side = "momentum"
        leg = {
            "entry": entry, "stop": stop, "units": units,
            "leg_idx": 1, "opened_at": t, "entry_type": entry_type,
            "session_side": _so_side,
        }
        self.active[pair] = {
            "direction": direction,
            "target": target,
            "legs": [leg],
            "weekly_amd_dir": weekly_amd_dir,
            "profile_score": p_score,
            "max_legs": max_legs,
        }
        self._week_total[week_key]                        = week_total + 1
        self._week_pair[(week_key[0], week_key[1], pair)] = week_pair + 1
        self._day_total[day_key]                          = day_total + 1
        self._day_pair[(day_key, pair)]                   = day_pair + 1

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
        # Medium impact: block pyramid. High impact: allow with fixed stop below.
        pyr_news_impact = self.news.nearest_impact(now)
        if pyr_news_impact == "Medium":
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
            dir_check, im_score = resolve_pair_direction(
                dxy_bias, audnzd_bias, "NZDUSD", "AUDUSD"
            )
            if dir_check is None:
                im_score = 0.5
            elif dir_check != st["direction"]:
                return

        # Weekly AMD override: if the confirmed weekly distribution direction
        # agrees with this position, upgrade im_score to 1.0 (full lots) even
        # when the intermarket is neutral. The weekly profile is the higher-
        # timeframe authority — if the Judas swing already fired, the market
        # SHOULD distribute toward PWWH/PWWL for the rest of the week.
        if config.WEEKLY_AMD_FULL_PYRAMID:
            wamd_dir = st.get("weekly_amd_dir", 0)
            if wamd_dir == st["direction"]:
                im_score = 1.0      # weekly AMD confirms — full pyramid lots

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
            return

        # FVG, OB, or Breaker across M1→H1 confirms a pullback to a live pattern.
        # M1 is checked first for pyramid adds — it shows the tightest, most current
        # level and confirms the fractal structure is still intact at execution speed.
        bars15 = self.bars_up_to(pair, "15T", t)
        bars1h = self.bars_up_to(pair, "60T", t)
        bars1m = self.bars_up_to(pair, "1T", t, max_bars=120)
        _level, stop, pyr_pattern = self._get_limit_entry(
            bars5, bars15, bars1h, pair, st["direction"], cur_price,
            bars1m=bars1m, for_pyramid=True,
        )
        if pyr_pattern is None:
            return

        # Apply entry friction to pyramid fills too.
        _spread_p = config.PAIR_SPREAD_PIPS.get(pair, config.PAIR_SPREAD_PIPS["default"])
        _fric_p = (_spread_p / 2 + config.SLIPPAGE_PIPS) * pip
        entry = cur_price + st["direction"] * _fric_p
        # High-impact news nearby: fixed 10-pip stop (spread protection).
        if pyr_news_impact == "High":
            stop = entry - config.FIXED_STOP_PIPS * pip if st["direction"] > 0 \
                   else entry + config.FIXED_STOP_PIPS * pip

        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return

        # High-impact news = distribution catalyst: upgrade to full lots.
        if pyr_news_impact == "High":
            im_score = 1.0

        # Lot size: growing pyramid schedule for current tier, scaled by intermarket score.
        tier_lots  = self._pyramid_lots()
        leg_num    = len(st["legs"]) + 1
        lot_idx    = min(leg_num - 1, len(tier_lots) - 1)
        base_units = int(tier_lots[lot_idx] * config.LOT_UNITS)
        units = max(int(base_units * im_score), int(tier_lots[-1] * config.LOT_UNITS))

        # Promote prior leg stop to breakeven before adding new leg.
        prior = st["legs"][-1]
        prior["stop"] = prior["entry"]

        wamd_tag = "wamd" if st.get("weekly_amd_dir") == st["direction"] else "im"
        news_tag = "news" if pyr_news_impact == "High" else ""
        leg = {
            "entry": entry, "stop": stop, "units": units,
            "leg_idx": len(st["legs"]) + 1, "opened_at": t,
            "entry_type": f"pyramid_{wamd_tag}{news_tag}{im_score:.1f}_{pyr_pattern}",
        }
        st["legs"].append(leg)


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
    eq = bt.start_equity + df.pnl.cumsum()
    rmax = eq.cummax()
    dd = ((eq - rmax) / rmax * 100).min() if len(eq) else 0
    return {
        "trades": n,
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": "inf" if pf == float("inf") else round(pf, 2),
        f"starting_equity_{ccy}": bt.start_equity,
        f"ending_equity_{ccy}": round(bt.equity, 2),
        f"pnl_{ccy}": round(bt.equity - bt.start_equity, 2),
        "pnl_pct": round((bt.equity - bt.start_equity) / bt.start_equity * 100, 2),
        "max_drawdown_pct": round(dd, 2),
        f"avg_win_{ccy}": round(wins.pnl.mean() if len(wins) else 0, 2),
        f"avg_loss_{ccy}": round(losses.pnl.mean() if len(losses) else 0, 2),
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

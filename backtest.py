"""Pandas-based backtester for the ICT intermarket strategy.

Fetches free 5-minute forex data from Yahoo Finance for the last ~60 days,
runs the strategy through the same `ict/` modules used by the QC version,
and reports trades + summary stats. No QuantConnect dependency.

Usage:  python backtest.py
"""

import sys
from collections import namedtuple
from datetime import timedelta

import pandas as pd
import yfinance as yf

import config
from ict.killzones import can_open_new_trade, current_killzone
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
from risk import position_size, pip_size


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
        self.pending = {}
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
        }

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

    def bars_up_to(self, sym, tf, t):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return []
        pos = idx.searchsorted(t, side="right")
        if pos == 0:
            return []
        return self.tf_bars[(sym, tf)][:pos]

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

            # Cheap killzone gate: skip heavy entry logic if not in any killzone.
            now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            in_kz = can_open_new_trade(now)
            for pair in config.PAIRS:
                if pair in self.active:
                    self._maybe_pyramid(pair, t)
                elif in_kz and pair not in self.pending:
                    self._maybe_open(pair, t)

            if i % 1000 == 0 and i > 0:
                print(f"    bar {i}/{total} ({t}) - active={len(self.active)} "
                      f"pending={len(self.pending)} trades={len(self.trades)} "
                      f"equity={self.equity:.0f}")

        # Close any remaining positions at last available 5m close.
        last_t = timestamps[-1]
        for pair in list(self.active.keys()):
            last_close = self.data_5m[pair].iloc[-1].Close
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

        # Pending limit entry fills.
        if pair in self.pending:
            pe = self.pending[pair]
            entry = pe["entry_price"]
            direction = pe["direction"]
            filled = (direction > 0 and bar.Low <= entry) or \
                     (direction < 0 and bar.High >= entry)
            now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            in_kz = current_killzone(now) is not None
            if filled and in_kz:
                # Only fill if we are still inside a kill zone — no off-hours entries.
                self._fill_entry(pair, t)
            elif not in_kz:
                # Kill zone ended before the limit filled — cancel immediately.
                self.pending.pop(pair, None)
            elif (t - pe["placed_at"]).total_seconds() / 60.0 > 90:
                self.pending.pop(pair, None)

    def _fill_entry(self, pair, t):
        pe = self.pending.pop(pair)
        leg = {
            "entry": pe["entry_price"], "stop": pe["stop"],
            "units": pe["units"], "leg_idx": pe["leg_idx"], "opened_at": t,
            "entry_type": pe.get("entry_type", "unknown"),
        }
        if pair not in self.active:
            self.active[pair] = {
                "direction": pe["direction"],
                "target": pe["target"],
                "legs": [leg],
            }
        else:
            # Pyramid: promote prior leg to BE.
            prior = self.active[pair]["legs"][-1]
            prior["stop"] = prior["entry"]
            self.active[pair]["legs"].append(leg)

    def _exit_leg(self, pair, leg, exit_price, t, reason):
        st = self.active[pair]
        direction = st["direction"]
        pnl_usd = (exit_price - leg["entry"]) * leg["units"] * direction
        pnl_zar = pnl_usd * config.USD_ZAR
        self.equity += pnl_zar
        self.trades.append({
            "pair": pair, "leg_idx": leg["leg_idx"], "direction": direction,
            "entry": leg["entry"], "exit": exit_price, "units": leg["units"],
            "pnl": pnl_zar, "opened_at": leg["opened_at"], "closed_at": t,
            "reason": reason, "entry_type": leg.get("entry_type", "unknown"),
        })
        st["legs"].remove(leg)
        if not st["legs"]:
            self.active.pop(pair, None)

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

    def _find_target(self, pair, direction, t, price):
        candidates = []
        for tf in ("240T", "D", "W"):
            bars = self.bars_up_to(pair, tf, t)
            if len(bars) < 5:
                continue
            tgts = self._targets_in_series(bars, pair, direction, price)
            candidates += tgts
        if direction > 0:
            candidates = [c for c in candidates if c > price]
        else:
            candidates = [c for c in candidates if c < price]
        if not candidates:
            return None
        # Prefer targets in the correct dealing range zone (premium for buys, discount
        # for sells); fall back to unfiltered if no filtered target exists.
        bars1h = self.bars_up_to(pair, "60T", t)
        dr = detect_dealing_range(bars1h, lookback=100)
        if dr is not None:
            filtered = [c for c in candidates
                        if is_valid_target_zone(c, dr.high, dr.low, direction)]
            if filtered:
                candidates = filtered
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
        if not can_open_new_trade(now):
            return
        g["in_killzone"] += 1
        if self.news.is_blocked(now):
            return
        g["news_clear"] += 1

        if is_nfp_week_low_probability(now, self.news.is_nfp_week(now)):
            return
        if is_post_fomc_low_probability(now, self.news.fomc_whipsaw_date):
            return
        g["nfp_fomc_ok"] += 1

        # Intermarket: H1 DXY + H1 EURGBP → macro pair/direction signal.
        # EURGBP is strength/weakness reference only — never used for MSS.
        dxy_bias    = self._dxy_bias("60T", t, lookback=config.SWING_LOOKBACK_STH)
        eurgbp_bias = self._sym_bias(config.REF_EURGBP, "60T", t,
                                      lookback=config.SWING_LOOKBACK_STH)
        signal = resolve_intermarket(dxy_bias, eurgbp_bias)
        if signal is None:
            return
        g["intermarket_signal"] += 1
        if signal.pair != pair:
            return
        g["pair_matches"] += 1

        # MSS: 2-of-3 (EURUSD, GBPUSD, DXY) must show M15/M5 BOS.
        # DXY is inverse — bearish DXY confirms a bullish EUR/GBP signal.
        eurusd_mss = self._pair_has_mss("EURUSD", t, signal.direction)
        gbpusd_mss = self._pair_has_mss("GBPUSD", t, signal.direction)
        dxy_mss    = self._dxy_has_mss(t, -signal.direction)
        if (eurusd_mss + gbpusd_mss + dxy_mss) < 2:
            return
        g["mss_h1_m15_m5_ok"] += 1

        # Dealing range: used for target filtering in _find_target (is_valid_target_zone).
        # As an entry gate it over-rejects in trending markets, so only record alignment
        # here without hard-blocking — the DR's main role is directing where targets sit.
        bars1h = self.bars_up_to(pair, "60T", t)
        if not bars1h:
            return
        dr = detect_dealing_range(bars1h, lookback=100)
        cur_price = bars1h[-1].Close
        dr_aligned = (dr is None) or is_valid_entry_zone(cur_price, dr.high, dr.low, signal.direction)
        g["dealing_range_ok"] += 1 if dr_aligned else 0  # informational only

        g["daily_bias_ok"] += 1
        g["h1_bias_ok"] += 1
        g["h4_bias_ok"] += 1

        # AMD filter on M15: Asia range → manipulation sweep in signal direction.
        bars15 = self.bars_up_to(pair, "15T", t)
        amd = detect_amd_setup(bars15, pair)
        if amd is None:
            return
        rng, sweep_dir = amd
        g["consolidation_found"] += 1
        if sweep_dir != signal.direction:
            return
        g["manipulation_correct_dir"] += 1

        bars5 = self.bars_up_to(pair, "5T", t)
        if not bars5:
            return
        cur_price = bars5[-1].Close

        # Collect limit-entry candidates: FVG on M5/M15/H1, OB on M5/M15.
        # Entry is placed at the pattern level; fill occurs when price touches it.
        candidates = []  # (entry, stop, entry_type)

        r = self._find_fvg_entry(bars5, pair, signal.direction, lookback=24)
        if r:
            candidates.append((*r, "fvg_m5"))

        r = self._find_fvg_entry(bars15, pair, signal.direction, lookback=8)
        if r:
            candidates.append((*r, "fvg_m15"))

        r = self._find_fvg_entry(bars1h, pair, signal.direction, lookback=4)
        if r:
            candidates.append((*r, "fvg_h1"))

        r = self._find_ob_entry(bars5, pair, signal.direction)
        if r:
            candidates.append((*r, "ob_m5"))

        r = self._find_ob_entry(bars15, pair, signal.direction)
        if r:
            candidates.append((*r, "ob_m15"))

        if not candidates:
            return
        g["m5_fvg_correct_dir"] += 1

        # Keep only candidates on the correct retrace side (below price for longs,
        # above price for shorts) and pick the one nearest to current price.
        if signal.direction > 0:
            valid_cands = [(e, s, et) for e, s, et in candidates if e <= cur_price]
        else:
            valid_cands = [(e, s, et) for e, s, et in candidates if e >= cur_price]
        if not valid_cands:
            return

        entry, stop, entry_type = min(valid_cands, key=lambda x: abs(x[0] - cur_price))

        target = self._find_target(pair, signal.direction, t, entry)
        if target is None:
            return
        g["target_found"] += 1

        pip = pip_size(pair)
        if signal.direction > 0 and stop >= entry:
            return
        if signal.direction < 0 and stop <= entry:
            return
        risk_pips   = abs(entry - stop) / pip
        reward_pips = abs(target - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return
        if risk_pips <= 0 or (reward_pips / risk_pips) < config.MIN_RR:
            return
        g["rr_ok"] += 1

        # ZAR equity → USD for position sizing; enforce standard-account minimum lot.
        equity_usd = self.equity / config.USD_ZAR
        risk_units = int(position_size(equity_usd, entry, stop, pair))
        min_units  = int(config.MIN_LOT_SIZE * config.LOT_UNITS)
        units = max(risk_units, min_units)
        if units == 0:
            return
        g["units_nonzero"] += 1

        self.pending[pair] = {
            "entry_price": entry, "stop": stop, "target": target,
            "direction": signal.direction, "units": units,
            "leg_idx": 1, "placed_at": t, "entry_type": entry_type,
        }
        g["limit_placed"] += 1

    def _maybe_pyramid(self, pair, t):
        """Add a new leg to a winning position.

        Each pyramid leg gets its own FVG/OB stop (ICT c0 extreme) rather than
        using the previous leg's entry as stop — that can be 50-80 pips wide and
        turns pyramid legs into outsized losing trades.
        """
        st = self.active[pair]
        if len(st["legs"]) >= config.MAX_LEGS:
            return
        if pair in self.pending:
            return
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if self.news.is_blocked(now):
            return

        bars5 = self.bars_up_to(pair, "5T", t)
        if not bars5:
            return
        cur_price = bars5[-1].Close
        pip = pip_size(pair)

        # Must be at least 10 pips in favour of the last leg before adding.
        last_entry = st["legs"][-1]["entry"]
        favour_pips = (cur_price - last_entry) * st["direction"] / pip
        if favour_pips < 10:
            return

        # Find a fresh FVG or OB entry with its own tight stop.
        bars15 = self.bars_up_to(pair, "15T", t)
        result = (
            self._find_fvg_entry(bars5, pair, st["direction"], lookback=12)
            or self._find_fvg_entry(bars15, pair, st["direction"], lookback=4)
            or self._find_ob_entry(bars5, pair, st["direction"])
        )
        if result is None:
            return
        entry, stop = result

        # Entry must be on the correct retrace side.
        if st["direction"] > 0 and entry > cur_price:
            return
        if st["direction"] < 0 and entry < cur_price:
            return
        if st["direction"] > 0 and stop >= entry:
            return
        if st["direction"] < 0 and stop <= entry:
            return

        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return

        # Pyramid lot: always minimum lot — tight, controlled add.
        units = int(config.MIN_LOT_SIZE * config.LOT_UNITS)

        self.pending[pair] = {
            "entry_price": entry, "stop": stop, "target": st["target"],
            "direction": st["direction"], "units": units,
            "leg_idx": len(st["legs"]) + 1, "placed_at": t,
            "entry_type": "pyramid",
        }


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

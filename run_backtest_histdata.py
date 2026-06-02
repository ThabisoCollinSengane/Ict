"""Backtest using real HistData.com 1-minute OHLC data.

Data files required in data/histdata/:
  GBPUSD_2025.csv, EURUSD_2025.csv, EURGBP_2025.csv, UDXUSD_2025.csv

HistData format:  YYYYMMDD HHMMSS;Open;High;Low;Close;Volume
Timezone:         US Eastern Standard Time (fixed UTC-5, no DST shift)

Uses the actual DXY index (UDXUSD) directly for DXY bias instead of the
6-constituent synthetic formula, since we have real index data.
"""

import os
import sys
from collections import namedtuple

import pandas as pd

import config
from ict.bias import htf_bias
from ict.amd import detect_consolidation, detect_manipulation
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.killzones import can_open_new_trade
from ict.dealing_range import (
    detect_dealing_range, is_valid_entry_zone, is_valid_target_zone,
    is_nfp_week_low_probability, is_post_fomc_low_probability,
)
from intermarket import resolve as resolve_intermarket
from news_filter import NewsCalendar
from risk import position_size, pip_size
import backtest as bt_module   # reuse summarize()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "histdata")

# HistData uses fixed Eastern Standard Time (UTC-5).  Add 5 h to get UTC.
_EST_OFFSET = pd.Timedelta(hours=5)

Bar = namedtuple("Bar", "Open High Low Close")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_m1(filepath: str) -> pd.DataFrame:
    """Load HistData ASCII M1 CSV and convert timestamps to UTC."""
    df = pd.read_csv(
        filepath, sep=";", header=None,
        names=["dt", "Open", "High", "Low", "Close", "Volume"],
        dtype={"Open": float, "High": float, "Low": float, "Close": float},
    )
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S") + _EST_OFFSET
    df = df.set_index("dt")[["Open", "High", "Low", "Close"]]
    df.index = df.index.tz_localize("UTC")
    return df


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return df.resample(rule).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    ).dropna()


def df_to_bars(df: pd.DataFrame) -> list[Bar]:
    return [Bar(r.Open, r.High, r.Low, r.Close) for r in df.itertuples(index=False)]


# ---------------------------------------------------------------------------
# Backtester subclass — swaps in real DXY for synthetic
# ---------------------------------------------------------------------------

class HistdataBacktester(bt_module.Backtester):
    """Identical to Backtester but uses real UDXUSD for DXY bias."""

    def __init__(self, data_5m: dict, dxy_5m: pd.DataFrame, data_m1: dict | None = None):
        super().__init__(data_5m)
        # Register raw M1 bars for tradeable pairs (fractal pattern detection on M1).
        if data_m1:
            for sym, df in data_m1.items():
                self.tf_dfs[(sym, "1T")]   = df
                self.tf_bars[(sym, "1T")]  = df_to_bars(df)
                self.tf_index[(sym, "1T")] = df.index
        # Register UDXUSD at all needed timeframes.
        for tf_name, rule in [
            ("5T", None), ("15T", "15min"), ("60T", "60min"),
            ("240T", "240min"), ("D", "1D"),
        ]:
            d = dxy_5m if rule is None else _resample(dxy_5m, rule)
            self.tf_dfs[("UDXUSD", tf_name)] = d
            self.tf_bars[("UDXUSD", tf_name)] = df_to_bars(d)
            self.tf_index[("UDXUSD", tf_name)] = d.index

    def _dxy_bias(self, tf, t, lookback=None) -> int:
        """Use real UDXUSD at any timeframe instead of ICE-formula synthetic DXY."""
        bars = self.bars_up_to("UDXUSD", tf, t)
        lb = lookback if lookback is not None else config.SWING_LOOKBACK
        return htf_bias(bars, lookback=lb)

    def _dxy_bias_1h(self, t, lookback=None) -> int:
        return self._dxy_bias("60T", t, lookback=lookback)

    def _dxy_bars(self, tf, t):
        """Use real UDXUSD bars for Judas divergence (matches _dxy_bias override)."""
        return self.bars_up_to("UDXUSD", tf, t)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("ICT Intermarket Backtest — HistData.com M1 data (2022–2025)")
    print("=" * 60)

    years = ["2022", "2023", "2024", "2025"]
    # Core pairs required for the EUR/GBP family. AUD/NZD pairs are optional —
    # the backtest runs without them and gains those trades when data is added.
    core_syms     = ["GBPUSD", "EURUSD", "EURGBP", "UDXUSD"]
    optional_syms = ["AUDUSD", "NZDUSD", "AUDNZD"]

    # Abort only if core pairs are completely absent for recent years.
    core_missing = [
        os.path.join(DATA_DIR, f"{s}_{yr}.csv")
        for s in core_syms for yr in years
        if not os.path.exists(os.path.join(DATA_DIR, f"{s}_{yr}.csv"))
        and yr in ("2024", "2025")
    ]
    if core_missing:
        for p in core_missing:
            print(f"ERROR: missing {p}")
        sys.exit(1)

    # Filter to years where all core pairs are present.
    years = [yr for yr in years
             if all(os.path.exists(os.path.join(DATA_DIR, f"{s}_{yr}.csv"))
                    for s in core_syms)]
    if not years:
        print("ERROR: no complete years found for core pairs")
        sys.exit(1)

    # Determine which optional pairs have complete coverage for the same years.
    available_optional = [
        s for s in optional_syms
        if all(os.path.exists(os.path.join(DATA_DIR, f"{s}_{yr}.csv")) for yr in years)
    ]
    if available_optional:
        print(f"  Optional pairs available: {', '.join(available_optional)}")
    else:
        print("  Optional pairs (AUDUSD/NZDUSD/AUDNZD): not yet downloaded — "
              "download from HistData.com to enable AUD/NZD trades")

    syms = core_syms + available_optional

    print(f"\nLoading and resampling to 5-minute bars ({' + '.join(years)})...")
    data_5m = {}
    data_m1 = {}   # raw 1-minute bars for tradeable pairs (M1 pattern detection)
    dxy_5m = None
    _tradeable = set(config.PAIRS)  # GBPUSD, EURUSD, NZDUSD
    for sym in syms:
        frames = []
        for yr in years:
            path = os.path.join(DATA_DIR, f"{sym}_{yr}.csv")
            frames.append(load_m1(path))
        m1 = pd.concat(frames).sort_index()
        m1 = m1[~m1.index.duplicated(keep='first')]
        m5 = _resample(m1, "5min")
        print(f"  {sym}: {len(m1):>7,} M1 → {len(m5):>6,} M5 bars  "
              f"{m5.index[0].date()} – {m5.index[-1].date()}  "
              f"close {m5['Close'].iloc[-1]:.5f}")
        if sym == "UDXUSD":
            dxy_5m = m5
        else:
            data_5m[sym] = m5
            # M1 registration disabled: df_to_bars on 1.4M rows is too slow at startup.
            # M1 patterns in _get_limit_entry silently skip when bars1m=[].
            # Re-enable when M1 bar access is refactored to lazy/on-demand loading.
            # if sym in _tradeable: data_m1[sym] = m1

    print("\nRunning backtest...")
    backtester = HistdataBacktester(data_5m, dxy_5m, data_m1)
    backtester.run()

    print("\n=== Gate funnel (entries passing each filter) ===")
    max_v = max(backtester.gate.values()) or 1
    for k, v in backtester.gate.items():
        bar_width = min(v * 40 // max(max_v, 1), 40)
        bar = "█" * bar_width
        print(f"  {k:32s} {v:6d}  {bar}")

    print("\n=== Results ===")
    results = bt_module.summarize(backtester)
    for k, v in results.items():
        print(f"  {k:25s} {v}")

    if backtester.trades:
        df = pd.DataFrame(backtester.trades)
        print(f"\n=== Trade log ({len(backtester.trades)} trades) ===")
        cols = ["opened_at", "closed_at", "pair", "direction",
                "leg_idx", "entry", "exit", "units", "pnl", "reason",
                "session_side", "entry_type"]
        pd.set_option("display.max_rows", None)
        pd.set_option("display.width", 200)
        print(df[cols].to_string(index=False))

        print("\n=== Per-pair P&L (ZAR) ===")
        for pair, grp in df.groupby("pair"):
            w = (grp.pnl > 0).sum()
            print(f"  {pair}: {len(grp)} trades  "
                  f"wins={w}  losses={len(grp)-w}  "
                  f"P&L=R{grp.pnl.sum():.2f}")

        print("\n=== Per-year breakdown ===")
        print(f"  {'Year':<6} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'P&L ZAR':>12} {'MaxDD%':>8}")
        print("  " + "-" * 50)
        df["year"] = df["opened_at"].dt.year
        for yr, grp in df.groupby("year"):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            eq_yr = grp.pnl.cumsum()
            rmax = eq_yr.cummax()
            dd = ((eq_yr - rmax) / (rmax + 500) * 100).min() if len(eq_yr) else 0
            print(f"  {yr:<6} {len(grp):>7} {w:>5} {wr:>5.1f}% {grp.pnl.sum():>12.2f} {dd:>7.1f}%")

        print("\n=== Per-pair × year ===")
        print(f"  {'Pair':<8} {'Year':<6} {'Trades':>7} {'Wins':>5} {'WR%':>6}")
        print("  " + "-" * 35)
        for (pair, yr), grp in df.groupby(["pair", "year"]):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            print(f"  {pair:<8} {yr:<6} {len(grp):>7} {w:>5} {wr:>5.1f}%")

        print("\n=== Entry-type breakdown ===")
        print(f"  {'Entry type':<20} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'Avg P&L':>10}")
        print("  " + "-" * 50)
        for etype, grp in df.groupby("entry_type"):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            print(f"  {etype:<20} {len(grp):>7} {w:>5} {wr:>5.1f}% {grp.pnl.mean():>10.2f}")

        print("\n=== Session-open side breakdown (above/below open) ===")
        print(f"  {'Category':<12} {'Trades':>7} {'Wins':>5} {'Losses':>7} {'WR%':>6} "
              f"{'P&L ZAR':>12} {'Avg P&L':>10}")
        print("  " + "-" * 65)
        for side in ["judas", "momentum", "no_open"]:
            g = df[df.session_side == side]
            if len(g) == 0:
                continue
            wins = (g.pnl > 0).sum()
            losses = len(g) - wins
            wr = 100 * wins / len(g)
            pnl = g.pnl.sum()
            avg = g.pnl.mean()
            label = {"judas": "below open", "momentum": "above open",
                     "no_open": "no session"}[side]
            print(f"  {label:<12} {len(g):>7} {wins:>5} {losses:>7} {wr:>5.1f}% "
                  f"{pnl:>11.2f} {avg:>10.2f}")
    else:
        print("\nNo trades generated.")
        print("Check the gate funnel to see which filter is the bottleneck.")


if __name__ == "__main__":
    main()

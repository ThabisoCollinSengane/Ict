"""Backtest using real HistData.com 1-minute OHLC data.

Data files required in data/histdata/:
  GBPUSD_2025.csv, EURUSD_2025.csv, EURGBP_2025.csv, UDXUSD_2025.csv

HistData format:  YYYYMMDD HHMMSS;Open;High;Low;Close;Volume
Timezone:         US Eastern Standard Time (fixed UTC-5, no DST shift)

Uses the actual DXY index (UDXUSD) directly for DXY bias instead of the
6-constituent synthetic formula, since we have real index data.
"""

import argparse
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
    parser = argparse.ArgumentParser(description="ICT Intermarket Backtest")
    parser.add_argument(
        "--years", nargs="+", default=["2022", "2023", "2024", "2025"],
        metavar="YYYY",
        help="Which years to include (default: all four)",
    )
    args = parser.parse_args()
    requested_years = args.years

    label = "–".join([requested_years[0], requested_years[-1]])
    print("=" * 60)
    print(f"ICT Intermarket Backtest — HistData.com M1 data ({label})")
    print("=" * 60)

    years = requested_years
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
            # M1 bars registered for tradeable pairs — used for stop placement
            # (_m1_structure_stop anchors the stop to the nearest M1 swing).
            if sym in _tradeable:
                data_m1[sym] = m1

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
        # Drawdown must be measured on the running account equity (carried across
        # years), not a per-year cumsum reset to 0 over a fixed R500 base — the
        # latter divides a within-year dip by ~R500 even after the account has
        # grown to six figures, producing impossible <-100% readings.
        df_sorted = df.sort_values("opened_at")
        equity = config.STARTING_CASH + df_sorted.pnl.cumsum()
        peak = equity.cummax()
        df_sorted = df_sorted.assign(_dd=(equity - peak) / peak * 100)
        for yr, grp in df_sorted.groupby("year"):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            dd = grp["_dd"].min() if len(grp) else 0
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

        if "draw_score" in df.columns:
            print("\n=== HTF Draw cascade (W→D→H4 agreement) — all trades ===")
            print("  draw_score = how many of Weekly/Daily/H4 agreed with trade direction")
            print(f"  {'Draw score':<12} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>12} {'Avg P&L':>10} {'PF':>6}")
            print("  " + "-" * 62)
            for score in sorted(df["draw_score"].unique()):
                grp = df[df["draw_score"] == score]
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gross_win = grp.loc[grp.pnl > 0, "pnl"].sum()
                gross_loss = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
                label = f"{int(score)}/3"
                print(f"  {label:<12} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>12.2f} {grp.pnl.mean():>10.2f} {pf:>6.2f}")

        if "target_type" in df.columns:
            print("\n=== Draw on liquidity (target type) — all trades ===")
            print(f"  {'Draw on liquidity':<18} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>12} {'Avg P&L':>10}")
            print("  " + "-" * 62)
            for ttype, grp in df.groupby("target_type"):
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                print(f"  {ttype:<18} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>12.2f} {grp.pnl.mean():>10.2f}")

            wins_df = df[df.pnl > 0]
            print("\n=== Winning trades only — by draw on liquidity ===")
            print(f"  {'Draw on liquidity':<18} {'Wins':>5} {'% of wins':>10} {'P&L ZAR':>12}")
            print("  " + "-" * 48)
            total_wins = len(wins_df)
            for ttype, grp in wins_df.groupby("target_type"):
                pct = 100 * len(grp) / total_wins if total_wins else 0
                print(f"  {ttype:<18} {len(grp):>5} {pct:>9.1f}% {grp.pnl.sum():>12.2f}")

            # --- Pyramids: draw on liquidity by leg type (initial vs pyramid add) ---
            if "leg_idx" in df.columns:
                df["leg_kind"] = df["leg_idx"].apply(
                    lambda i: "initial (L1)" if i == 1 else "pyramid (L2+)")
                print("\n=== Draw on liquidity — initial vs pyramid legs (winners) ===")
                print(f"  {'Leg':<14} {'Draw on liquidity':<18} {'Wins':>5} {'WR%':>6} {'P&L ZAR':>12}")
                print("  " + "-" * 60)
                for legk in ["initial (L1)", "pyramid (L2+)"]:
                    sub_all = df[df.leg_kind == legk]
                    for ttype, grp in sub_all[sub_all.pnl > 0].groupby("target_type"):
                        all_grp = sub_all[sub_all.target_type == ttype]
                        wr = 100 * len(grp) / len(all_grp) if len(all_grp) else 0
                        print(f"  {legk:<14} {ttype:<18} {len(grp):>5} {wr:>5.1f}% {grp.pnl.sum():>12.2f}")

            # --- Sessions: which killzone the winning draws were hit in ---
            def _killzone(ts):
                # opened_at is tz-aware UTC; killzones defined in NY time.
                ny = ts.tz_convert("America/New_York")
                h = ny.hour
                if 2 <= h < 5:
                    return "London Open"
                if 7 <= h < 10:
                    return "New York AM"
                if 20 <= h or h < 2:
                    return "Asian"
                return "Other"
            try:
                wins_df = wins_df.copy()
                wins_df["session"] = wins_df["opened_at"].apply(_killzone)
                print("\n=== Winning trades — by session × draw on liquidity ===")
                print(f"  {'Session':<13} {'Draw on liquidity':<18} {'Wins':>5} {'P&L ZAR':>12}")
                print("  " + "-" * 52)
                for sess, sgrp in wins_df.groupby("session"):
                    for ttype, grp in sgrp.groupby("target_type"):
                        print(f"  {sess:<13} {ttype:<18} {len(grp):>5} {grp.pnl.sum():>12.2f}")
                print("\n=== Winning trades — totals by session ===")
                print(f"  {'Session':<13} {'Wins':>5} {'% of wins':>10} {'P&L ZAR':>12}")
                print("  " + "-" * 44)
                for sess, sgrp in wins_df.groupby("session"):
                    pct = 100 * len(sgrp) / total_wins if total_wins else 0
                    print(f"  {sess:<13} {len(sgrp):>5} {pct:>9.1f}% {sgrp.pnl.sum():>12.2f}")
            except Exception as e:
                print(f"  (session breakdown skipped: {e})")

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

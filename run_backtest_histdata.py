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

    def __init__(self, data_5m: dict, dxy_5m: pd.DataFrame):
        super().__init__(data_5m)
        # Register UDXUSD at all needed timeframes.
        for tf_name, rule in [
            ("5T", None), ("15T", "15min"), ("60T", "60min"),
            ("240T", "240min"), ("D", "1D"),
        ]:
            d = dxy_5m if rule is None else _resample(dxy_5m, rule)
            self.tf_dfs[("UDXUSD", tf_name)] = d
            self.tf_bars[("UDXUSD", tf_name)] = df_to_bars(d)
            self.tf_index[("UDXUSD", tf_name)] = d.index

    def _dxy_bias_1h(self, t) -> int:
        """Use real UDXUSD 1H bars directly instead of ICE-formula synthetic DXY."""
        bars = self.bars_up_to("UDXUSD", "60T", t)
        return htf_bias(bars)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("ICT Intermarket Backtest — HistData.com M1 data (2024–2025)")
    print("=" * 60)

    years = ["2024", "2025"]
    syms = ["GBPUSD", "EURUSD", "EURGBP", "UDXUSD"]
    for sym in syms:
        for yr in years:
            path = os.path.join(DATA_DIR, f"{sym}_{yr}.csv")
            if not os.path.exists(path):
                print(f"ERROR: missing {path}")
                sys.exit(1)

    print("\nLoading and resampling to 5-minute bars (2024 + 2025)...")
    data_5m = {}
    dxy_5m = None
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

    print("\nRunning backtest...")
    backtester = HistdataBacktester(data_5m, dxy_5m)
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
                "leg_idx", "entry", "exit", "units", "pnl", "reason"]
        pd.set_option("display.max_rows", None)
        pd.set_option("display.width", 180)
        print(df[cols].to_string(index=False))

        print("\n=== Per-pair P&L ===")
        for pair, grp in df.groupby("pair"):
            w = (grp.pnl > 0).sum()
            print(f"  {pair}: {len(grp)} trades  "
                  f"wins={w}  losses={len(grp)-w}  "
                  f"P&L={grp.pnl.sum():.2f}")
    else:
        print("\nNo trades generated.")
        print("Check the gate funnel to see which filter is the bottleneck.")


if __name__ == "__main__":
    main()

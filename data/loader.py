"""Single read interface for all backtest / live data.

`get_bars(symbol, tf)` returns a DataFrame[Open, High, Low, Close, Volume]
indexed by UTC datetime, for any timeframe the strategy needs.

Resolution order:

  1. Canonical M1 store (data/store/{symbol}_M1.csv.gz). Resample to `tf`.
     This is the preferred path — Dukascopy minute bars + tick volume.
  2. Legacy M5 CSV cache (data/yf/{symbol}_5m.csv). yfinance, no Volume.
     Works for any tf >= 5T.
  3. None — caller decides whether to skip or hit yfinance live.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from data import store

REPO = Path(__file__).resolve().parent.parent

# Pandas resample aliases that match the rest of the codebase.
TF_TO_PANDAS_RULE = {
    "1T":   "1min",
    "5T":   "5min",
    "15T":  "15min",
    "60T":  "60min",
    "240T": "240min",
    "D":    "1D",
    "W":    "1W",
}


def _resample(m1: pd.DataFrame, tf: str) -> pd.DataFrame:
    if tf == "1T":
        return m1
    rule = TF_TO_PANDAS_RULE.get(tf)
    if rule is None:
        raise ValueError(f"unknown timeframe {tf!r}")
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    if "Volume" in m1.columns:
        agg["Volume"] = "sum"
    return m1.resample(rule).agg(agg).dropna(subset=["Open", "High", "Low", "Close"])


def _legacy_yf_5m(symbol: str) -> pd.DataFrame | None:
    p = REPO / "data" / "yf" / f"{symbol}_5m.csv"
    if not p.exists():
        return None
    df = pd.read_csv(p, index_col=0, parse_dates=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].dropna()
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")
    df["Volume"] = float("nan")
    return df


def get_bars(symbol: str, tf: str = "5T") -> pd.DataFrame | None:
    """Return OHLCV bars for `symbol` at `tf`. None if no source available."""
    m1 = store.read_m1(symbol)
    if m1 is not None and not m1.empty:
        return _resample(m1, tf)

    # Legacy fallback: yfinance M5 CSVs. Can only serve tf >= 5T.
    legacy = _legacy_yf_5m(symbol)
    if legacy is None:
        return None
    if tf == "1T":
        # Cannot upsample M5 to M1; signal absence so caller can degrade.
        return None
    if tf == "5T":
        return legacy
    return _resample(legacy, tf)


def source_for(symbol: str) -> str:
    """Diagnostic: which path will get_bars use? 'm1_store', 'yf_csv', or 'none'."""
    if store.has_m1(symbol):
        return "m1_store"
    if (REPO / "data" / "yf" / f"{symbol}_5m.csv").exists():
        return "yf_csv"
    return "none"

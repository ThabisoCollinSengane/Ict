"""Canonical M1 OHLCV+V store.

Stores per-symbol minute bars as gzip-compressed CSV under
data/store/{symbol}_M1.csv.gz. Schema:

    Datetime (UTC, ISO8601) | Open | High | Low | Close | Volume

Volume is tick-count (Dukascopy convention for forex — there's no
centralised exchange-volume in FX).

Designed so a future swap to parquet is one line: read_m1 / write_m1
abstract the format. Callers should never read these files directly.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

STORE_DIR = Path(__file__).resolve().parent / "store"
STORE_DIR.mkdir(parents=True, exist_ok=True)


def m1_path(symbol: str) -> Path:
    return STORE_DIR / f"{symbol}_M1.csv.gz"


def has_m1(symbol: str) -> bool:
    return m1_path(symbol).exists()


def read_m1(symbol: str) -> pd.DataFrame | None:
    p = m1_path(symbol)
    if not p.exists():
        return None
    df = pd.read_csv(p, index_col=0, parse_dates=True, compression="gzip")
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC")
    else:
        df.index = df.index.tz_convert("UTC")
    cols = [c for c in ("Open", "High", "Low", "Close", "Volume") if c in df.columns]
    return df[cols].dropna(subset=["Open", "High", "Low", "Close"])


def write_m1(symbol: str, df: pd.DataFrame) -> None:
    p = m1_path(symbol)
    out = df.copy()
    if out.index.tz is None:
        out.index = out.index.tz_localize("UTC")
    else:
        out.index = out.index.tz_convert("UTC")
    # Stable column order; ensure Volume present (NaN if missing).
    if "Volume" not in out.columns:
        out["Volume"] = float("nan")
    out = out[["Open", "High", "Low", "Close", "Volume"]]
    out.to_csv(p, compression="gzip")

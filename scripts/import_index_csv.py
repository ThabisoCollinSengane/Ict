#!/usr/bin/env python3
"""Convert a downloaded M1 OHLC CSV (Dukascopy / generic) into the HistData ASCII
format the backtest loader expects, split per year, written to data/histdata/.

    python scripts/import_index_csv.py SOURCE.csv --symbol US30 [--tz UTC]

Output: data/histdata/US30_2022.csv, US30_2023.csv, ...  in
    YYYYMMDD HHMMSS;Open;High;Low;Close;0         (Eastern time, fixed UTC-5)
which is exactly what run_backtest_histdata.load_m1 reads (it re-adds 5h to get
UTC). Source timestamps are treated as --tz (default UTC) and shifted to fixed
UTC-5 — the same fixed-EST convention HistData uses (no DST), so index bars line
up with the FX/DXY bars already in data/histdata/.

Where to get Dow (US30) M1 history for free (HistData has no Dow):
  * Dukascopy — full 2022-2025 M1. Easiest via dukascopy-node:
        npx dukascopy-node -i usa30idxusd -from 2022-01-01 -to 2025-12-31 \
            -t m1 -f csv -v true
    then:  python scripts/import_index_csv.py usa30idxusd-*.csv --symbol US30
  * Or the VM's own MT5 US30 symbol — see scripts/export_mt5_history.py (limited
    history depth, but zero setup since MT5 is already on the VM).

Column detection is tolerant: the datetime is the first column (or a column named
time/date/timestamp/gmt time); OHLC are matched case-insensitively.
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "histdata")
_EST = pd.Timedelta(hours=5)   # fixed UTC-5, matches HistData/load_m1


def _find_col(cols, *names):
    low = {c.lower().strip(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    for want in names:
        for lc, orig in low.items():
            if want in lc:
                return orig
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="source CSV (Dukascopy / generic OHLC)")
    ap.add_argument("--symbol", required=True, help="output symbol name, e.g. US30")
    ap.add_argument("--tz", default="UTC",
                    help="source timezone (default UTC; use ET-5 sources as-is with --tz Etc/GMT+5)")
    ap.add_argument("--sep", default=None, help="force delimiter (auto by default)")
    args = ap.parse_args()

    if not os.path.exists(args.source):
        sys.exit(f"source not found: {args.source}")

    df = pd.read_csv(args.source, sep=args.sep, engine="python")
    dt_col = _find_col(df.columns, "gmt time", "timestamp", "time", "date", "datetime") \
        or df.columns[0]
    o = _find_col(df.columns, "open"); h = _find_col(df.columns, "high")
    l = _find_col(df.columns, "low");  c = _find_col(df.columns, "close")
    if not all([o, h, l, c]):
        sys.exit(f"could not find OHLC columns in {list(df.columns)}")

    # Parse datetime: numeric = epoch ms/s; else let pandas infer (ISO, dd.mm.yyyy…).
    s = df[dt_col]
    if pd.api.types.is_numeric_dtype(s):
        unit = "ms" if s.iloc[0] > 1e11 else "s"
        idx = pd.to_datetime(s, unit=unit, utc=True)
    else:
        idx = pd.to_datetime(s, utc=(args.tz.upper() == "UTC"),
                             dayfirst=("." in str(s.iloc[0])), errors="coerce")
        if idx.dt.tz is None:
            idx = idx.dt.tz_localize(args.tz).dt.tz_convert("UTC")
    # Use .values so the OHLC align POSITIONALLY with idx (not by the source's
    # integer index, which would reindex everything to NaN against a datetime index).
    out = pd.DataFrame({
        "Open": pd.to_numeric(df[o], errors="coerce").values,
        "High": pd.to_numeric(df[h], errors="coerce").values,
        "Low":  pd.to_numeric(df[l], errors="coerce").values,
        "Close": pd.to_numeric(df[c], errors="coerce").values,
    }, index=pd.DatetimeIndex(idx)).dropna()
    out = out[~out.index.duplicated(keep="first")].sort_index()
    span0, span1 = out.index[0].date(), out.index[-1].date()
    # UTC -> fixed ET (UTC-5) INDEX for the on-disk file (load_m1 re-adds 5h).
    out.index = out.index.tz_convert("UTC").tz_localize(None) - _EST

    os.makedirs(DATA_DIR, exist_ok=True)
    total = 0
    for year, grp in out.groupby(out.index.year):
        lines = [
            f"{ts.strftime('%Y%m%d %H%M%S')};{r.Open:.2f};{r.High:.2f};"
            f"{r.Low:.2f};{r.Close:.2f};0"
            for ts, r in grp.iterrows()
        ]
        path = os.path.join(DATA_DIR, f"{args.symbol}_{year}.csv")
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  wrote {path}  ({len(lines):,} M1 bars)")
        total += len(lines)
    print(f"done — {total:,} bars for {args.symbol} across {span0}..{span1}")


if __name__ == "__main__":
    main()

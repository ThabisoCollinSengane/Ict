#!/usr/bin/env python3
"""Compute seasonal tendencies (monthly + day-of-week lean) per pair from the
prepared HistData daily history -> data/seasonal_bias.json (advisory lean read).

    python scripts/build_seasonal.py [--pairs EURUSD GBPUSD NZDUSD]
    python scripts/build_seasonal.py --selftest      # math check, no data/network

Uses whatever years exist in data/histdata/ (PAIR_YYYY.csv M1 -> daily). MORE
history = more robust; drop 15-20yr Dukascopy daily CSVs in (via
scripts/import_index_csv.py) for a real sample. FX seasonality is WEAK, so each
bucket is GRADED (noise/mild/moderate/strong) from sample size + how far the
up-rate is from a coin-flip — the read shows the grade so it's never over-trusted.
Advisory only; nothing here touches the auto engine.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ensure the repo root is importable (run_backtest_histdata lives there). When
# invoked as `python scripts/build_seasonal.py`, Python only puts scripts/ on the
# path, so the root import fails without this.
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
DATA_DIR = os.path.join(_ROOT, "data", "histdata")
OUT = os.path.join(_ROOT, "data", "seasonal_bias.json")


def _grade(n: int, up_rate: float, kind: str) -> str:
    """Strength label from sample size + up-rate deviation from 0.5 (coin-flip).
    Monthly buckets have few samples (years) so need a bigger edge; day-of-week
    buckets have many (days) but the daily effect is tiny, so a smaller bar."""
    dev = abs(up_rate - 0.5)
    if kind == "month":
        if n < 8 or dev < 0.12:
            return "noise"
        if dev >= 0.25:
            return "strong"
        if dev >= 0.18:
            return "moderate"
        return "mild"
    # day-of-week
    if n < 150 or dev < 0.04:
        return "noise"
    if dev >= 0.10:
        return "moderate"
    return "mild"


def _bucket(returns_pct: pd.Series, keys, key_of, kind: str) -> dict:
    out = {}
    for k in keys:
        vals = returns_pct[key_of == k]
        if len(vals) == 0:
            continue
        avg = float(vals.mean())
        up = float((vals > 0).mean())
        n = int(len(vals))
        out[str(k)] = {"avg_pct": round(avg, 4), "up_rate": round(up, 3),
                       "n": n, "grade": _grade(n, up, kind)}
    return out


def seasonal_from_daily(d: pd.DataFrame) -> dict:
    """d: daily OHLC with a DatetimeIndex. Returns {month:{...}, dow:{...}}."""
    # monthly close-to-close % return, averaged by calendar month
    m = d["Close"].resample("MS").last()
    mret = m.pct_change().dropna() * 100.0
    month = _bucket(mret, range(1, 13), mret.index.month, "month")
    # daily % return, averaged by weekday (Mon..Fri)
    dret = d["Close"].pct_change().dropna() * 100.0
    dret = dret[dret.index.dayofweek < 5]
    dow = _bucket(dret, range(5), dret.index.dayofweek, "dow")
    return {"month": month, "dow": dow, "n_years": int(round(len(mret) / 12))}


def _load_daily(pair: str, src_dir: str = DATA_DIR):
    try:
        from run_backtest_histdata import load_m1
    except Exception as exc:
        sys.exit(f"cannot import load_m1: {exc}")
    frames = []
    for f in sorted(glob.glob(os.path.join(src_dir, f"{pair}_*.csv"))):
        try:
            frames.append(load_m1(f))
        except Exception:
            pass
    if not frames:
        return None
    m1 = pd.concat(frames).sort_index()
    m1 = m1[~m1.index.duplicated(keep="first")]
    return m1.resample("1D").agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}).dropna()


def _selftest():
    # synthetic daily series with a strong "up in month 1" seasonal
    idx = pd.date_range("2003-01-01", "2025-12-31", freq="D")
    base = pd.Series(100.0, index=idx)
    # add +0.1%/day drift in January across all years, flat otherwise
    ret = pd.Series(0.0, index=idx)
    ret[idx.month == 1] = 0.001
    price = base * (1 + ret).cumprod()
    d = pd.DataFrame({"Open": price, "High": price, "Low": price, "Close": price})
    s = seasonal_from_daily(d)
    jan = s["month"]["1"]
    assert jan["avg_pct"] > 0 and jan["up_rate"] > 0.6, jan
    assert jan["grade"] in ("moderate", "strong"), jan
    print(f"selftest OK — Jan seasonal detected: {jan}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="+",
                    default=["EURUSD", "GBPUSD", "NZDUSD", "EURGBP"])
    ap.add_argument("--src-dir", default=DATA_DIR,
                    help="where the daily CSVs live (default data/histdata; use the "
                         "seasonal folder so long-history daily data is kept separate "
                         "from the M1 backtest data)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    out = {"_meta": {"pairs": {}}}
    for p in args.pairs:
        d = _load_daily(p, args.src_dir)
        if d is None or len(d) < 60:
            print(f"  {p}: no/insufficient data — skipped")
            continue
        out[p] = seasonal_from_daily(d)
        yrs = out[p]["n_years"]
        out["_meta"]["pairs"][p] = {"n_years": yrs,
                                    "span": f"{d.index[0].date()}..{d.index[-1].date()}"}
        note = "" if yrs >= 10 else "  (LOW SAMPLE - mostly 'noise' grades until you add long history)"
        print(f"  {p}: {yrs} yrs {d.index[0].date()}..{d.index[-1].date()}{note}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

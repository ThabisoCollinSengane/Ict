#!/usr/bin/env python3
"""Fetch daily US Treasury constant-maturity yields from FRED (stdlib only).

FRED serves every series as a plain CSV with no API key:

    https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10&cosd=2020-01-01&coed=2025-12-31

Columns are `DATE,<ID>` (older exports use `observation_date,<ID>`); non-trading
days carry a "." placeholder. We keep the raw rows verbatim under data/bonds_src/
so the analysis step owns all cleaning (forward-fill / drop) — the fetcher only
downloads and never interprets the values.

Series (the rates side of the intermarket model — yields lead the dollar):
    DGS2   2-year   — Fed-policy anchor (most sensitive to rate expectations)
    DGS5   5-year   — belly
    DGS10  10-year  — growth / inflation expectations
    T10Y2Y 2s10s spread — regime read (optional, off by default)

Run:
    python scripts/fetch_fred.py --start 2020-01-01 --end 2025-12-31
    python scripts/fetch_fred.py --series DGS2 DGS5 DGS10 --dest data/bonds_src
    python scripts/fetch_fred.py --selftest        # parse-only, no network
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(_ROOT, "data", "bonds_src")
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv"
DEFAULT_SERIES = ("DGS2", "DGS5", "DGS10")
_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def parse_fred_csv(text: str, series_id: str):
    """Parse a FRED CSV body into a list of (date_str, value_or_None).

    Handles both the `DATE,<id>` and `observation_date,<id>` header variants and
    treats "." (FRED's non-trading-day marker) and blanks as missing (None).
    Rows that don't parse are skipped rather than raising — a partial series is
    still useful and the analysis step reports coverage.
    """
    rows = []
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return rows
    start = 1 if lines[0].lower().startswith(("date", "observation_date")) else 0
    for ln in lines[start:]:
        parts = ln.split(",")
        if len(parts) < 2:
            continue
        date_s = parts[0].strip()
        raw = parts[1].strip()
        val = None
        if raw not in (".", "", "NA", "null"):
            try:
                val = float(raw)
            except ValueError:
                val = None
        rows.append((date_s, val))
    return rows


def _fetch(series_id: str, start: str, end: str, timeout: int = 60) -> str:
    url = f"{FRED}?id={series_id}&cosd={start}&coed={end}"
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed host)
        return resp.read().decode("utf-8", "replace")


def _write(series_id: str, rows, dest: str) -> str:
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, f"{series_id}.csv")
    with open(path, "w") as f:
        f.write(f"DATE,{series_id}\n")
        for date_s, val in rows:
            f.write(f"{date_s},{'.' if val is None else val}\n")
    return path


def fetch_all(series, start, end, dest):
    ok, failed = [], []
    for sid in series:
        try:
            text = _fetch(sid, start, end)
            rows = parse_fred_csv(text, sid)
            good = [r for r in rows if r[1] is not None]
            if not good:
                failed.append((sid, "no numeric observations returned"))
                continue
            path = _write(sid, rows, dest)
            span = f"{good[0][0]}..{good[-1][0]}"
            print(f"  {sid}: {len(good)} obs {span} -> {os.path.relpath(path, _ROOT)}")
            ok.append(sid)
        except Exception as exc:  # network / proxy / parse — report, keep going
            failed.append((sid, str(exc)))
            print(f"  {sid}: FAILED — {exc}")
    return ok, failed


def _selftest():
    sample = ("DATE,DGS10\n"
              "2022-01-03,1.63\n"
              "2022-01-04,1.66\n"
              "2022-01-17,.\n"          # holiday marker
              "2022-01-18,1.87\n"
              "bad,row,extra\n")        # malformed -> value None, not a crash
    rows = parse_fred_csv(sample, "DGS10")
    assert rows[0] == ("2022-01-03", 1.63), rows[0]
    assert rows[2][1] is None, rows[2]           # "." -> missing
    assert rows[3] == ("2022-01-18", 1.87), rows[3]
    # observation_date header variant
    alt = parse_fred_csv("observation_date,DGS2\n2024-06-03,4.88\n", "DGS2")
    assert alt == [("2024-06-03", 4.88)], alt
    # empty body
    assert parse_fred_csv("", "DGS2") == []
    print("selftest OK — FRED CSV parse (holidays, header variants, malformed rows)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", nargs="+", default=list(DEFAULT_SERIES))
    ap.add_argument("--start", default="2020-01-01")
    ap.add_argument("--end", default="2025-12-31")
    ap.add_argument("--dest", default=DEST)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    print(f"=== FRED fetch {a.start}..{a.end} -> {os.path.relpath(a.dest, _ROOT)} ===")
    ok, failed = fetch_all(a.series, a.start, a.end, a.dest)
    if not ok:
        print("ERROR: no series fetched. If the proxy blocks fred.stlouisfed.org, "
              "download the CSVs manually (fredgraph.csv?id=DGS10) into "
              f"{os.path.relpath(a.dest, _ROOT)}/ and re-run the analysis.")
        return 1
    if failed:
        print(f"  ({len(failed)} series failed: {', '.join(s for s, _ in failed)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

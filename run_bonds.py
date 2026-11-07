#!/usr/bin/env python3
"""Bonds/yields × dollar — daily-bias measurement. Pure Python, no bash.

    python run_bonds.py

Fetches US Treasury yields (DGS2/5/10) from FRED, runs the analysis over whatever
pair M1 is already in data/histdata (the same data your backtest uses), writes
data/bonds_report.md + data/bond_bias.json, and prints the GREEN/YELLOW/RED
verdict. Measurement only — nothing ships to the engine. Only a GREEN warrants
run_bonds_validation.py.

Options (all optional):
    --horizon-days 3   forward window for the reversal test
    --lookback 20      SMT lookback in daily bars
    --skip-fetch       don't hit FRED (use CSVs already in data/bonds_src/)
"""
from __future__ import annotations

import argparse
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon-days", type=int, default=3)
    ap.add_argument("--lookback", type=int, default=20)
    ap.add_argument("--skip-fetch", action="store_true")
    a = ap.parse_args()

    import fetch_fred
    import bonds_analysis as ba

    if not a.skip_fetch:
        print("=== fetching US Treasury yields from FRED (DGS2/DGS5/DGS10) ===")
        ok, failed = fetch_fred.fetch_all(fetch_fred.DEFAULT_SERIES,
                                          "2020-01-01", "2025-12-31",
                                          fetch_fred.DEST)
        if not ok:
            print("  ⚠️ FRED fetch failed (proxy/network). Drop DGS2.csv / DGS5.csv "
                  "/ DGS10.csv into data/bonds_src/ manually, then re-run with "
                  "--skip-fetch.")
    else:
        print("=== --skip-fetch: using existing data/bonds_src/ CSVs ===")

    print("=== bonds analysis + emit data/bond_bias.json ===")
    result = ba.analyse(a.horizon_days, a.lookback)
    lines, verdict = result if isinstance(result, tuple) else (result, "?")
    text = "\n".join(lines) + "\n"
    with open(ba.REPORT, "w") as f:
        f.write(text)
    print(text)
    ba.write_bond_bias(a.horizon_days, a.lookback)
    print(f"\n[report → {os.path.relpath(ba.REPORT, _ROOT)}]  verdict = {verdict}")
    print("Paste data/bonds_report.md back to Claude, or commit+push it however you "
          "normally push (this script does not touch git).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

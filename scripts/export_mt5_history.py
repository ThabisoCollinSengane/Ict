#!/usr/bin/env python3
"""Export M1 history from the VM's running MetaTrader 5 terminal into the HistData
ASCII format the backtest expects (data/histdata/{SYMBOL}_{YEAR}.csv).

Run this ON THE VM (MT5 must be open and logged in — the algo already uses it):
    python scripts/export_mt5_history.py --symbols US30 US500 US100 --years 2022 2023 2024 2025
    python scripts/export_mt5_history.py --symbols US30            # just Dow

Zero setup — US30 is already a symbol on your broker's MT5. The ONE caveat is
history depth: most brokers keep only ~1-2 years of M1, so 2022/2023 may come back
short or empty (the script reports the actual range it got per symbol/year). For a
guaranteed full 2022-2025 history use Dukascopy + scripts/import_index_csv.py
instead. Output timestamps are written in fixed ET (UTC-5) to match load_m1.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone

try:
    import MetaTrader5 as mt5
except Exception:
    sys.exit("MetaTrader5 not importable — run this on the VM inside the live venv.")

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "histdata")
_EST = pd.Timedelta(hours=5)


def _resolve_symbol(sym: str) -> str | None:
    """Match the requested name to a broker symbol (handles US30 vs US30.cash etc.)."""
    if mt5.symbol_info(sym) is not None:
        return sym
    want = sym.upper().replace(".", "").replace("_", "")
    for s in (mt5.symbols_get() or []):
        norm = s.name.upper().replace(".", "").replace("_", "")
        if norm == want or norm.startswith(want):
            return s.name
    return None


def export(sym: str, years: list[int]) -> None:
    resolved = _resolve_symbol(sym)
    if resolved is None:
        print(f"  {sym}: NOT found on this broker — check Market Watch")
        return
    if not mt5.symbol_select(resolved, True):
        print(f"  {sym}: could not select {resolved}")
        return
    os.makedirs(DATA_DIR, exist_ok=True)
    for yr in years:
        start = datetime(yr, 1, 1, tzinfo=timezone.utc)
        end   = datetime(yr + 1, 1, 1, tzinfo=timezone.utc)
        rates = mt5.copy_rates_range(resolved, mt5.TIMEFRAME_M1, start, end)
        if rates is None or len(rates) == 0:
            print(f"  {sym} {yr}: no data (history depth?) — {mt5.last_error()}")
            continue
        df = pd.DataFrame(rates)
        # MT5 'time' is broker-server time in epoch seconds. Treat as UTC for a
        # 24/5 CFD (server tz varies by broker; DXY/FX bars use fixed UTC-5 on
        # disk, so we write ET = UTC-5 here for alignment — adjust if your broker
        # server offset differs materially).
        idx = pd.to_datetime(df["time"], unit="s", utc=True)
        et = idx.dt.tz_convert("UTC").dt.tz_localize(None) - _EST
        lines = [
            f"{ts.strftime('%Y%m%d %H%M%S')};{o:.2f};{h:.2f};{lo:.2f};{c:.2f};0"
            for ts, o, h, lo, c in zip(et, df["open"], df["high"], df["low"], df["close"])
        ]
        path = os.path.join(DATA_DIR, f"{sym}_{yr}.csv")
        with open(path, "w") as f:
            f.write("\n".join(lines) + "\n")
        print(f"  {sym} {yr}: {len(lines):,} M1 bars  "
              f"{et.iloc[0].date()}..{et.iloc[-1].date()}  -> {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", nargs="+", default=["US30"])
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2023, 2024, 2025])
    args = ap.parse_args()
    if not mt5.initialize():
        sys.exit(f"MT5 initialize() failed: {mt5.last_error()} — is the terminal open?")
    try:
        for s in args.symbols:
            export(s, args.years)
    finally:
        mt5.shutdown()


if __name__ == "__main__":
    main()

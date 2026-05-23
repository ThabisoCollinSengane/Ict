"""Import HistData.com free M1 forex ASCII zips into data/store/.

Input: any number of HistData zip files at data/raw/*.zip (or as
arguments). Each contains one CSV / TXT named
``DAT_ASCII_{SYMBOL}_M1_{YYYYMM}.csv`` with semicolon-delimited rows:

    YYYYMMDD HHMMSS;Open;High;Low;Close;Volume

HistData's published timestamps are EST WITHOUT daylight savings (a
constant UTC-5 offset). We shift by +5h to produce true UTC and write
one merged M1 dataset per symbol via ``data.store.write_m1``. Existing
store data for the same symbol is merged (overlapping minutes prefer
the newest file).

HistData provides no volume for forex (column is always 0); we leave it
as 0 in the store so the column exists for schema consistency with
Dukascopy imports. Downstream scoring that uses Volume should treat
0/NaN as "missing" rather than "no activity".

Special case: ``UDXUSD`` (US Dollar Index) is remapped to ``DXY`` in
the store, since downstream code refers to the index by that name.

Usage:
    python scripts/import_histdata.py             # processes data/raw/*.zip
    python scripts/import_histdata.py path/*.zip  # processes specific files
"""

from __future__ import annotations

import argparse
import io
import re
import sys
import zipfile
from datetime import timedelta
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from data import store  # noqa: E402

RAW_DIR = REPO / "data" / "raw"

# Filename pattern inside the ZIP: DAT_ASCII_{SYMBOL}_M1_{YYYYMM}.{csv|txt}
_FNAME_RE = re.compile(r"DAT_ASCII_([A-Z]{6})_M1_(\d{6})\.(?:csv|txt)$")

# Remap special HistData instrument codes to our internal symbols.
SYMBOL_REMAP = {"UDXUSD": "DXY"}


def _parse_one(zpath: Path) -> tuple[str, pd.DataFrame] | None:
    with zipfile.ZipFile(zpath) as zf:
        members = [n for n in zf.namelist() if _FNAME_RE.search(n)]
        if not members:
            print(f"  ! {zpath.name}: no matching CSV/TXT inside")
            return None
        # Prefer the .csv; fall back to .txt (HistData ships both, same content).
        members.sort(key=lambda n: 0 if n.endswith(".csv") else 1)
        member = members[0]
        m = _FNAME_RE.search(member)
        if not m:
            return None
        raw_symbol, yyyymm = m.group(1), m.group(2)
        symbol = SYMBOL_REMAP.get(raw_symbol, raw_symbol)
        with zf.open(member) as f:
            df = pd.read_csv(
                f, sep=";", header=None,
                names=["dt_est", "Open", "High", "Low", "Close", "Volume"],
                dtype={"dt_est": str, "Open": float, "High": float,
                       "Low": float, "Close": float, "Volume": float},
            )
    # Parse "YYYYMMDD HHMMSS" as EST (fixed UTC-5, no DST per HistData spec).
    dt = pd.to_datetime(df["dt_est"], format="%Y%m%d %H%M%S")
    utc = (dt + timedelta(hours=5)).dt.tz_localize("UTC")
    df = df.drop(columns=["dt_est"]).set_index(utc)
    df.index.name = "Datetime"
    return symbol, df.sort_index()


def import_all(zips: list[Path]) -> dict[str, pd.DataFrame]:
    per_symbol: dict[str, list[pd.DataFrame]] = {}
    for z in sorted(zips):
        parsed = _parse_one(z)
        if not parsed:
            continue
        sym, df = parsed
        per_symbol.setdefault(sym, []).append(df)
        print(f"  {z.name}: {sym} {len(df)} rows "
              f"{df.index.min().isoformat()} -> {df.index.max().isoformat()}")
    return {s: pd.concat(parts).sort_index() for s, parts in per_symbol.items()}


def merge_into_store(symbol: str, new_df: pd.DataFrame) -> int:
    existing = store.read_m1(symbol)
    if existing is None or existing.empty:
        merged = new_df
    else:
        # Existing wins on conflict only if newer file isn't present — but in
        # practice rows are minute-stamped, so concat + drop_duplicates(last)
        # keeps the freshly imported row whenever both exist.
        merged = pd.concat([existing, new_df])
        merged = merged[~merged.index.duplicated(keep="last")].sort_index()
    store.write_m1(symbol, merged)
    return len(merged)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("zips", nargs="*", help="zip files (defaults to data/raw/*.zip)")
    args = parser.parse_args()

    zips = [Path(z) for z in args.zips] if args.zips else sorted(RAW_DIR.glob("*.zip"))
    if not zips:
        print(f"No zips to process (looked in {RAW_DIR}).")
        return

    print(f"Processing {len(zips)} HistData zip(s)...")
    per_symbol = import_all(zips)

    for sym, df in per_symbol.items():
        total = merge_into_store(sym, df)
        print(f"  STORE {sym}: {total} M1 bars total ({store.m1_path(sym).name})")


if __name__ == "__main__":
    main()

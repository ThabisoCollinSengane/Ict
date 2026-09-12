#!/usr/bin/env python3
"""Prepare HistData.com M1 downloads for the ICT backtester.

Unzips HistData ASCII / MT M1 archives, normalises every file to the
semicolon-delimited *generic ASCII* format that the backtester's `load_m1()`
reads, dedupes duplicate downloads, and writes `SYMBOL_YYYY_MM.csv` into
`data/histdata/`.

Why this exists
---------------
HistData serves most forex pairs as **Generic ASCII** M1:

    20260102 170000;1.10512;1.10530;1.10498;1.10515;0     (semicolon-delimited)

…but the Dollar Index (UDXUSD) is only offered in **MetaTrader (MT)** format:

    2026.01.02,17:00,99.123,99.130,99.120,99.125,45        (comma, dotted date)

`load_m1()` only understands the first shape, so the MT files must be converted
before a run or the DXY gate can't parse them. This script auto-detects the
format per file and normalises both to the ASCII shape.

Usage
-----
    python scripts/prepare_histdata.py <source_dir> [--dest data/histdata] [--force]

`<source_dir>` is a folder of HistData zips (e.g. the "2026" folder you
downloaded from Drive). Filenames look like:

    HISTDATA_COM_ASCII_EURUSD_M1202601.zip
    HISTDATA_COM_ASCII_EURUSD_M1202601 (1).zip    # duplicate download → skipped
    HISTDATA_COM_MT_UDXUSD_M1202601.zip           # MT format → auto-converted

Then run:

    python run_backtest_histdata.py --years 2026
    # or, for the meaningful continuous compounding path:
    python run_backtest_histdata.py --years 2022 2023 2024 2025 2026
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile

# HISTDATA M1 zips come two ways:
#   monthly: HISTDATA_COM_<ASCII|MT>_<SYMBOL>_M1<YYYY><MM>[ (n)].zip
#   annual:  HISTDATA_COM_<ASCII|MT>_<SYMBOL>_M1<YYYY>[ (n)].zip
# The month group is optional; absent → a full-year file (SYMBOL_YYYY.csv).
_NAME_RE = re.compile(
    r"HISTDATA_COM_(?:ASCII|MT)_([A-Z]{6})_M1(\d{4})(\d{2})?", re.IGNORECASE
)

# Core pairs the backtester needs; used only for the coverage report at the end.
_CORE = ("EURUSD", "GBPUSD", "EURGBP", "UDXUSD")


def _normalize_line(line: str) -> str | None:
    """Return a `YYYYMMDD HHMMSS;O;H;L;C;V` line, or None if unparseable.

    Handles three inputs:
      1. Generic ASCII : `YYYYMMDD HHMMSS;O;H;L;C;V`            → passed through
      2. MT (2 fields) : `YYYY.MM.DD,HH:MM,O,H,L,C,V`          → converted
      3. MT (1 field)  : `YYYY.MM.DD HH:MM,O,H,L,C,V`          → converted
    """
    line = line.strip()
    if not line:
        return None

    # --- already generic ASCII (semicolon) ---------------------------------
    if ";" in line:
        parts = line.split(";")
        # sanity: dt field must be `YYYYMMDD HHMMSS`
        if len(parts) >= 5 and re.fullmatch(r"\d{8} \d{6}", parts[0]):
            return line
        return None

    # --- MetaTrader (comma-delimited, dotted date) -------------------------
    parts = line.split(",")

    def _fmt(date_raw: str, time_raw: str, ohlcv: list[str]) -> str | None:
        date = date_raw.replace(".", "").replace("-", "")
        time = time_raw.replace(":", "")
        if len(time) == 4:          # HHMM → HHMMSS
            time += "00"
        if not re.fullmatch(r"\d{8}", date) or not re.fullmatch(r"\d{6}", time):
            return None
        if len(ohlcv) < 4:
            return None
        o, h, l, c = ohlcv[0], ohlcv[1], ohlcv[2], ohlcv[3]
        vol = ohlcv[4] if len(ohlcv) > 4 else "0"
        return f"{date} {time};{o};{h};{l};{c};{vol}"

    # shape 2: date, time, O, H, L, C[, V]
    if len(parts) >= 6 and ":" in parts[1] and " " not in parts[0]:
        return _fmt(parts[0], parts[1], parts[2:])
    # shape 3: "date time", O, H, L, C[, V]
    if len(parts) >= 5 and " " in parts[0]:
        d, _, t = parts[0].partition(" ")
        return _fmt(d, t, parts[1:])
    return None


def _extract_csv_text(zip_path: str) -> str | None:
    """Return the text of the first .csv member inside `zip_path`, or None."""
    try:
        with zipfile.ZipFile(zip_path) as zf:
            csv_members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csv_members:
                return None
            with zf.open(csv_members[0]) as f:
                return f.read().decode("utf-8", errors="replace")
    except (zipfile.BadZipFile, OSError) as exc:
        print(f"  ! cannot read {os.path.basename(zip_path)}: {exc}")
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Prepare HistData M1 zips for the backtester")
    ap.add_argument("source_dir", help="Folder containing the HistData .zip downloads")
    ap.add_argument(
        "--dest",
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "histdata"),
        help="Output directory (default: <repo>/data/histdata)",
    )
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing SYMBOL_YYYY_MM.csv outputs")
    args = ap.parse_args()

    if not os.path.isdir(args.source_dir):
        print(f"ERROR: source dir not found: {args.source_dir}")
        return 1
    os.makedirs(args.dest, exist_ok=True)

    zips = sorted(f for f in os.listdir(args.source_dir) if f.lower().endswith(".zip"))
    if not zips:
        print(f"ERROR: no .zip files in {args.source_dir}")
        return 1

    print(f"Source : {args.source_dir}")
    print(f"Dest   : {args.dest}")
    print(f"Found  : {len(zips)} zip(s)\n")

    seen: dict[tuple[str, str, str], str] = {}   # (sym, yyyy, mm) → source file used
    coverage: dict[str, set[str]] = {}           # sym → {"YYYY-MM", …}
    written = skipped_dupe = failed = 0

    for name in zips:
        m = _NAME_RE.search(name)
        if not m:
            print(f"  ? skip (unrecognised name): {name}")
            continue
        sym, yyyy, mm = m.group(1).upper(), m.group(2), (m.group(3) or "")
        key = (sym, yyyy, mm)
        label = f"{yyyy}-{mm}" if mm else yyyy          # "2026-01" or "2022"

        if key in seen:
            skipped_dupe += 1
            print(f"  = dupe  {sym} {label}  ({name}) — already have {seen[key]}")
            continue

        out_name = f"{sym}_{yyyy}_{mm}.csv" if mm else f"{sym}_{yyyy}.csv"
        out_path = os.path.join(args.dest, out_name)
        if os.path.exists(out_path) and not args.force:
            seen[key] = name
            coverage.setdefault(sym, set()).add(label)
            print(f"  · exists {out_name} (use --force to overwrite)")
            continue

        text = _extract_csv_text(os.path.join(args.source_dir, name))
        if text is None:
            failed += 1
            continue

        out_lines, bad = [], 0
        for raw in text.splitlines():
            norm = _normalize_line(raw)
            if norm is None:
                bad += 1
            else:
                out_lines.append(norm)

        if not out_lines:
            print(f"  ! {name}: no parseable rows (skipped)")
            failed += 1
            continue

        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out_lines) + "\n")

        seen[key] = name
        coverage.setdefault(sym, set()).add(label)
        written += 1
        warn = f"  ({bad} rows unparseable)" if bad else ""
        print(f"  + {out_name}  {len(out_lines):>6} rows{warn}")

    # ── Summary + coverage report ──────────────────────────────────────────
    print(f"\nDone: {written} written, {skipped_dupe} duplicates skipped, {failed} failed.")
    if coverage:
        print("\nCoverage:")
        for sym in sorted(coverage):
            months = sorted(coverage[sym])
            tag = "" if sym in _CORE else "  (optional)"
            print(f"  {sym:<8} {len(months):>2} month(s): {', '.join(months)}{tag}")

        years = sorted({mm.split('-')[0] for s in coverage.values() for mm in s})
        print("\nCore-pair completeness per year:")
        for yr in years:
            have = [s for s in _CORE
                    if any(mm.startswith(yr) for mm in coverage.get(s, ()))]
            missing = [s for s in _CORE if s not in have]
            status = "OK — runnable" if not missing else f"MISSING {', '.join(missing)}"
            print(f"  {yr}: {status}")
        print("\nNext: python run_backtest_histdata.py --years " + " ".join(years))
    return 0


if __name__ == "__main__":
    sys.exit(main())

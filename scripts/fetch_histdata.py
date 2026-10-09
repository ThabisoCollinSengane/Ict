#!/usr/bin/env python3
"""Fetch HistData.com M1 zips programmatically (stdlib only).

HistData has no API: each download is a form POST to /get.php carrying a per-page
`tk` token (+ date/platform/timeframe/fxpair) that must first be scraped from the
product page, using the same cookie session. This script automates that so the
Codespace can self-serve the missing years instead of dozens of manual downloads.

Output zips are named exactly as HistData names them, so scripts/prepare_histdata.py
ingests them unchanged:
    HISTDATA_COM_ASCII_EURUSD_M12025.zip        (annual, past year)
    HISTDATA_COM_ASCII_EURUSD_M1202601.zip      (monthly, current year)
    HISTDATA_COM_MT_UDXUSD_M12025.zip           (Dollar Index is MT-only)

Pairs: EURUSD GBPUSD EURGBP NZDUSD AUDNZD are ASCII; UDXUSD is MT.
Past years download as one annual zip; the current year must go month-by-month
(HistData only exposes completed months).

Usage:
    python scripts/fetch_histdata.py --years 2025 --dest /tmp/histdata_dl
    python scripts/fetch_histdata.py --years 2026 --months 1 2 3 4 5 6 --dest /tmp/histdata_dl
    python scripts/fetch_histdata.py --selftest        # parse-only, no network
"""
from __future__ import annotations

import argparse
import http.cookiejar
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://www.histdata.com"
# Core FX + the gold complex. XAUUSD (gold), XAGUSD (silver) and AUDUSD are the
# DXY+silver+AUDUSD intraday gate for the gold build; HistData serves all three
# under the same ASCII 1-minute product, so they route exactly like the FX pairs.
ASCII_PAIRS = ("EURUSD", "GBPUSD", "EURGBP", "NZDUSD", "AUDNZD",
               "AUDUSD", "XAUUSD", "XAGUSD",
               # US indices: HistData ASCII codes. SPXUSD=US500 (S&P), NSXUSD=US100
               # (Nasdaq100). Dow/US30 is not in HistData free ASCII — supply
               # separately if you want US30 as the confirmer.
               "SPXUSD", "NSXUSD")
MT_PAIRS = ("UDXUSD",)
ALL_PAIRS = ASCII_PAIRS + MT_PAIRS
_UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
_FORM_FIELDS = ("tk", "date", "datemonth", "platform", "timeframe", "fxpair")


def _platform_of(pair: str) -> str:
    return "MT" if pair in MT_PAIRS else "ASCII"


def _referer(pair: str, year: int, month: int | None) -> str:
    seg = "ascii" if _platform_of(pair) == "ASCII" else "metatrader"
    tail = f"{pair.lower()}/{year}" + (f"/{month}" if month else "")
    return f"{BASE}/download-free-forex-historical-data/?/{seg}/1-minute-bar-quotes/{tail}"


def parse_form_fields(html: str) -> dict:
    """Extract the hidden download-form inputs. Tolerant of attribute order."""
    out = {}
    for name in _FORM_FIELDS:
        m = (re.search(rf'name=["\']{name}["\'][^>]*value=["\']([^"\']*)["\']', html)
             or re.search(rf'value=["\']([^"\']*)["\'][^>]*name=["\']{name}["\']', html)
             or re.search(rf'id=["\']{name}["\'][^>]*value=["\']([^"\']*)["\']', html))
        if m:
            out[name] = m.group(1)
    return out


def _opener() -> urllib.request.OpenerDirector:
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", _UA)]
    return op


def _out_name(pair: str, year: int, month: int | None) -> str:
    plat = _platform_of(pair)
    stamp = f"{year}{month:02d}" if month else f"{year}"
    return f"HISTDATA_COM_{plat}_{pair}_M1{stamp}.zip"


def download_one(pair: str, year: int, month: int | None, dest: str,
                 retries: int = 3) -> tuple[bool, str]:
    """Return (ok, message). Skips if the target zip already exists and is valid."""
    out = os.path.join(dest, _out_name(pair, year, month))
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return True, f"skip (have {os.path.basename(out)})"
    referer = _referer(pair, year, month)
    last = ""
    for attempt in range(1, retries + 1):
        try:
            op = _opener()
            html = op.open(urllib.request.Request(referer), timeout=60).read().decode(
                "utf-8", "ignore")
            fields = parse_form_fields(html)
            if "tk" not in fields:
                last = "no tk token (page shape changed or blocked)"
                time.sleep(2 * attempt)
                continue
            body = urllib.parse.urlencode(fields).encode()
            req = urllib.request.Request(f"{BASE}/get.php", data=body)
            req.add_header("Referer", referer)
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            blob = op.open(req, timeout=180).read()
            if blob[:2] != b"PK":
                last = f"not a zip (got {blob[:48]!r})"
                time.sleep(2 * attempt)
                continue
            os.makedirs(dest, exist_ok=True)
            with open(out, "wb") as f:
                f.write(blob)
            return True, f"ok {os.path.basename(out)} ({len(blob)//1024} KB)"
        except Exception as e:  # noqa: BLE001 - report and retry any transport error
            last = f"{type(e).__name__}: {e}"
            time.sleep(2 * attempt)
    return False, f"FAILED after {retries}: {last}"


def _selftest() -> int:
    sample = (
        '<form id="file_down" method="POST" action="/get.php">'
        '<input type="hidden" name="tk" value="abc123">'
        '<input type="hidden" name="date" value="2025">'
        '<input type="hidden" name="datemonth" value="2025">'
        '<input type="hidden" name="platform" value="ASCII">'
        '<input type="hidden" name="timeframe" value="M1">'
        '<input type="hidden" name="fxpair" value="EURUSD"></form>')
    f = parse_form_fields(sample)
    assert f.get("tk") == "abc123", f
    assert f.get("fxpair") == "EURUSD", f
    assert _out_name("EURUSD", 2025, None) == "HISTDATA_COM_ASCII_EURUSD_M12025.zip"
    assert _out_name("UDXUSD", 2026, 3) == "HISTDATA_COM_MT_UDXUSD_M1202603.zip"
    assert "metatrader" in _referer("UDXUSD", 2025, None)
    assert "ascii" in _referer("EURUSD", 2026, 6)
    print("selftest OK — form parsing, naming, referer routing all pass")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, nargs="+", default=[2025])
    ap.add_argument("--months", type=int, nargs="*", default=None,
                    help="month numbers; required for the current year. Omit for past-year annual.")
    ap.add_argument("--pairs", nargs="+", default=list(ALL_PAIRS))
    ap.add_argument("--dest", default="/tmp/histdata_dl")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    jobs = []
    for y in a.years:
        months = a.months if a.months else [None]  # None → annual download
        for m in months:
            for p in a.pairs:
                jobs.append((p, y, m))
    print(f"fetching {len(jobs)} HistData file(s) → {a.dest}")
    ok = fail = 0
    fails = []
    for p, y, m in jobs:
        good, msg = download_one(p, y, m, a.dest)
        tag = "  ok " if good else "FAIL "
        print(f"  {tag}{p} {y}{'' if m is None else '-%02d' % m}: {msg}")
        if good:
            ok += 1
        else:
            fail += 1
            fails.append(f"{p} {y}{'' if m is None else '-%02d' % m}: {msg}")
        time.sleep(1)  # be polite to HistData
    print(f"\ndone: {ok} ok, {fail} failed")
    if fails:
        print("FAILURES (these years/pairs won't be testable):")
        for f in fails:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

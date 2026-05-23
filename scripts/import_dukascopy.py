"""Import Dukascopy historical M1 OHLCV + tick-count into data/store/.

Dukascopy publishes free historical bars at:
    https://datafeed.dukascopy.com/datafeed/{SYMBOL}/{YYYY}/{MM-1:02}/{DD:02}/
        {HH:02}h_BID_candles_min_1.bi5

Each .bi5 file is LZMA-compressed, holding 60 records (one per minute of
that hour). Each record is 24 bytes big-endian:

    uint32   seconds since the hour start
    float32  Open
    float32  Close
    float32  Low
    float32  High
    float32  Volume  (tick count)

Run locally (or from a GitHub Actions runner with network):

    python scripts/import_dukascopy.py --symbols EURUSD,GBPUSD --days 60

Writes / merges into data/store/{symbol}_M1.csv.gz.

Network failures are retried with backoff; per-hour file failures are
logged and skipped (gaps in the resulting series).
"""

from __future__ import annotations

import argparse
import io
import lzma
import struct
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import requests

# Repo root: parent of /scripts
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from data import store  # noqa: E402


BASE_URL = "https://datafeed.dukascopy.com/datafeed"
RECORD = struct.Struct(">I f f f f f")   # 24 bytes per minute candle
USER_AGENT = "ICT-strategy-importer/1.0"


def _url(symbol: str, ts: datetime) -> str:
    return (f"{BASE_URL}/{symbol}/"
            f"{ts.year:04d}/{ts.month - 1:02d}/{ts.day:02d}/"
            f"{ts.hour:02d}h_BID_candles_min_1.bi5")


def _fetch_hour(symbol: str, hour_start: datetime,
                retries: int = 4, backoff: float = 2.0) -> bytes | None:
    url = _url(symbol, hour_start)
    headers = {"User-Agent": USER_AGENT}
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, timeout=20)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.content
        except Exception as e:
            if attempt == retries - 1:
                print(f"  ! {url} failed after {retries} tries: {e}")
                return None
            time.sleep(backoff ** attempt)
    return None


def _parse_hour(payload: bytes, hour_start: datetime) -> list[tuple]:
    if not payload:
        return []
    raw = lzma.decompress(payload)
    out = []
    for off in range(0, len(raw), RECORD.size):
        chunk = raw[off:off + RECORD.size]
        if len(chunk) != RECORD.size:
            break
        sec_offset, o, c, l, h, v = RECORD.unpack(chunk)
        ts = hour_start + timedelta(seconds=int(sec_offset))
        out.append((ts, float(o), float(h), float(l), float(c), float(v)))
    return out


def _looks_like_forex_price(p: float) -> bool:
    return 0.01 < p < 1000.0


def fetch_symbol(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    rows = []
    cur = start
    total_hours = int((end - start).total_seconds() // 3600)
    done = 0
    while cur < end:
        if cur.weekday() < 5 or (cur.weekday() == 6 and cur.hour >= 22):
            payload = _fetch_hour(symbol, cur)
            if payload is not None:
                rows.extend(_parse_hour(payload, cur))
        done += 1
        if done % 24 == 0:
            print(f"    {symbol}: {done}/{total_hours}h fetched, {len(rows)} bars")
        cur += timedelta(hours=1)

    if not rows:
        return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    df = pd.DataFrame(rows, columns=["Datetime", "Open", "High", "Low", "Close", "Volume"])
    df = df.set_index("Datetime")
    df.index = df.index.tz_localize("UTC")

    # Sanity: if Open looks wildly out of range, decoder is wrong for this pair.
    sample = df["Open"].dropna().head(10).tolist()
    if sample and not any(_looks_like_forex_price(p) for p in sample):
        print(f"  ! {symbol}: decoded prices look wrong, sample={sample[:3]}. "
              f"Format may differ for this instrument; aborting save.")
        return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    return df.sort_index()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default="EURUSD,GBPUSD,EURGBP,USDJPY,USDCAD,USDCHF",
                        help="comma-separated forex pairs")
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--end", default=None, help="UTC end date YYYY-MM-DD; defaults to today")
    args = parser.parse_args()

    end_dt = (datetime.strptime(args.end, "%Y-%m-%d").replace(tzinfo=timezone.utc)
              if args.end else datetime.now(tz=timezone.utc).replace(minute=0, second=0, microsecond=0))
    start_dt = end_dt - timedelta(days=args.days)
    print(f"Window: {start_dt.isoformat()} -> {end_dt.isoformat()}")

    for sym in args.symbols.split(","):
        sym = sym.strip()
        if not sym:
            continue
        print(f"\n--- {sym} ---")
        df = fetch_symbol(sym, start_dt, end_dt)
        if df.empty:
            print(f"  {sym}: no data collected")
            continue
        store.write_m1(sym, df)
        print(f"  {sym}: wrote {len(df)} bars to {store.m1_path(sym)}")
        print(f"  sample: {df.iloc[0].to_dict()}")


if __name__ == "__main__":
    main()

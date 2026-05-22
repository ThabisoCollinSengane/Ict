"""Download yfinance OHLCV bars and write them to data/yf/ as CSV.

Run this LOCALLY (where the network can reach Yahoo Finance), then commit
the resulting CSVs. backtest.py will prefer the cache over a live yfinance
call, so the backtest then runs anywhere — including environments without
outbound network access.

Usage:
    python scripts/cache_yf_data.py
"""

import os
import sys

import pandas as pd
import yfinance as yf

TICKERS = {
    "GBPUSD": "GBPUSD=X",
    "EURUSD": "EURUSD=X",
    "EURGBP": "EURGBP=X",
    "USDJPY": "USDJPY=X",
    "USDCAD": "USDCAD=X",
    "USDSEK": "USDSEK=X",
    "USDCHF": "USDCHF=X",
}

# yfinance intraday history limits: 5m -> 60d, 15m/60m -> 60d, 1d -> years.
JOBS = [("5m", "60d")]

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "yf")


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, ticker in TICKERS.items():
        for interval, period in JOBS:
            df = yf.download(ticker, period=period, interval=interval,
                             progress=False, auto_adjust=False)
            if df is None or df.empty:
                print(f"  SKIP {name} {interval}: no data")
                continue
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df[["Open", "High", "Low", "Close"]].dropna()
            path = os.path.join(OUT, f"{name}_{interval}.csv")
            df.to_csv(path)
            print(f"  {name} {interval}: {len(df)} bars -> {path}")


if __name__ == "__main__":
    sys.exit(main() or 0)

"""Generate synthetic 5-min OHLCV CSVs in data/yf/ so the backtest can run
in environments without network access. Pure smoke-test data — DOES NOT
represent real market behavior. Use the real cache workflow for actual
backtests.
"""

import os
import math
import random
from datetime import datetime, timedelta, timezone

import pandas as pd

random.seed(42)

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "yf")
os.makedirs(OUT, exist_ok=True)

PAIRS = {
    "EURUSD": 1.0800,
    "GBPUSD": 1.2700,
    "EURGBP": 0.8500,
    "USDJPY": 150.00,
    "USDCAD": 1.3500,
    "USDSEK": 10.50,
    "USDCHF": 0.8800,
}

# 60 trading days, M5 bars during fx hours (24/5 sun-fri).
start = datetime(2025, 3, 1, 0, 0, tzinfo=timezone.utc)
days = 60
bars_per_day = 24 * 12  # 288

for name, base in PAIRS.items():
    rows = []
    px = base
    pip = 0.01 if name.endswith("JPY") else 0.0001
    # Per-pair daily-cycle anchor so D1 forms clear ITH/ITL pivots.
    d1_seed = random.Random(hash(name) & 0xFFFFFFFF)
    daily_targets = [base + d1_seed.gauss(0, 200) * pip for _ in range(days + 1)]
    for d in range(days):
        day_start = start + timedelta(days=d)
        if day_start.weekday() >= 5:  # skip weekends
            continue
        day_open = daily_targets[d]
        day_close = daily_targets[d + 1]
        for i in range(bars_per_day):
            t = day_start + timedelta(minutes=5 * i)
            frac = i / bars_per_day
            # Linear drift open->close plus intraday wave + noise
            mid = day_open + (day_close - day_open) * frac
            wave = math.sin(i * 0.07) * 30 * pip
            noise = random.gauss(0, 2) * pip
            c = mid + wave + noise
            h = c + abs(random.gauss(0, 2)) * pip
            l = c - abs(random.gauss(0, 2)) * pip
            o = px
            rows.append((t, o, h, l, c))
            px = c

    df = pd.DataFrame(rows, columns=["Datetime", "Open", "High", "Low", "Close"])
    df = df.set_index("Datetime")
    path = os.path.join(OUT, f"{name}_5m.csv")
    df.to_csv(path)
    print(f"  {name}: {len(df)} bars -> {path}")

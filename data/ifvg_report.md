# Inversion FVG (IFVG) backtest — market-structure stop + costs

Core condition: a FVG violated by a **full-body close outside it** inverts to a supply/demand zone. Entry one TF lower (D1→H4, H4→H1, H1→M15, M15→M5) on a **confirmation close** — a candle that wicks into the zone AND closes back OUT in the trade direction (rejection proven, price moving away). **Stop = market structure, capped at 10 pips on every entry** (R defined off that stop); **target = nearest HTF liquidity (prior-day / prior-week high-low, ≥1R away)**. Spread + slippage on both fills.

_pairs: EURUSD, GBPUSD, NZDUSD · coverage: EURUSD 2022, EURUSD 2023, EURUSD 2024, EURUSD 2025, GBPUSD 2022, GBPUSD 2023, GBPUSD 2024, GBPUSD 2025, NZDUSD 2022, NZDUSD 2023, NZDUSD 2024, NZDUSD 2025_

MaxDD is peak-to-trough of the cumulative-R curve. `total` = summed R.

## In-sample (2022/2023)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 3730 | 28% | 0.81 | -646.6R | -0.16R | -1.11R | -604.6R
| H1 | 1150 | 31% | 0.75 | -247.5R | -0.19R | -1.11R | -221.3R
| H4 | 366 | 34% | 0.99 | -48.3R | -0.00R | -1.11R | -1.7R
| D1 | 92 | 28% | 0.81 | -25.1R | -0.15R | -1.11R | -14.2R

## Out-of-sample (2024/2025)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 4282 | 29% | 0.73 | -996.9R | -0.23R | -1.12R | -984.9R
| H1 | 1091 | 32% | 0.82 | -175.1R | -0.14R | -1.11R | -154.0R
| H4 | 276 | 34% | 0.91 | -37.2R | -0.06R | -1.11R | -17.6R
| D1 | 79 | 25% | 0.48 | -34.0R | -0.43R | -1.11R | -33.6R

## Read

IS PF 0.81 (n=5338, WR 29%) · OOS PF 0.75 (n=5728, WR 30%). Not positive in both splits — the raw inversion edge doesn't hold; nothing to ship.

_report generated on commit `3df0568`_

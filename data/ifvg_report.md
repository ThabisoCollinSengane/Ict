# Inversion FVG (IFVG) backtest — market-structure stop + costs

Core condition: a FVG violated by a **full-body close outside it** inverts to a supply/demand zone. Entry one TF lower (D1→H4, H4→H1, H1→M15, M15→M5) on a **confirmation close** — a candle that wicks into the zone AND closes back OUT in the trade direction (rejection proven, price moving away). **Stop = market structure, capped at 10 pips on every entry** (R defined off that stop); target 2R. **Spread + slippage applied on both fills.**

_pairs: EURUSD, GBPUSD, NZDUSD · coverage: EURUSD 2022, EURUSD 2023, EURUSD 2024, EURUSD 2025, GBPUSD 2022, GBPUSD 2023, GBPUSD 2024, GBPUSD 2025, NZDUSD 2022, NZDUSD 2023, NZDUSD 2024, NZDUSD 2025_

MaxDD is peak-to-trough of the cumulative-R curve. `total` = summed R.

## In-sample (2022/2023)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 4022 | 33% | 0.78 | -708.3R | -0.18R | -1.11R | -705.9R
| H1 | 1243 | 33% | 0.83 | -177.8R | -0.13R | -1.11R | -158.3R
| H4 | 378 | 37% | 0.97 | -38.7R | -0.02R | -1.11R | -7.1R
| D1 | 89 | 34% | 0.86 | -15.4R | -0.10R | -1.11R | -8.9R

## Out-of-sample (2024/2025)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 4543 | 32% | 0.73 | -989.6R | -0.22R | -1.11R | -982.3R
| H1 | 1122 | 34% | 0.85 | -150.5R | -0.11R | -1.11R | -128.2R
| H4 | 292 | 35% | 0.89 | -26.0R | -0.08R | -1.11R | -22.4R
| D1 | 78 | 28% | 0.67 | -31.2R | -0.26R | -1.11R | -20.3R

## Read

IS PF 0.80 (n=5732, WR 33%) · OOS PF 0.76 (n=6035, WR 33%). Not positive in both splits — the raw inversion edge doesn't hold; nothing to ship.

_report generated on commit `6c6af96`_

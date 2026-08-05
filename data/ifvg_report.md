# Inversion FVG (IFVG) backtest — market-structure stop + costs

Core condition: a FVG violated by a **full-body close outside it** inverts to a supply/demand zone. Entry one TF lower (D1→H4, H4→H1, H1→M15, M15→M5): M15/H1/H4 on a >40%-wick rejection candle, D1 at the zone edge. **Stop = market structure, capped at 10 pips on every entry** (R defined off that stop); target 2R. **Spread + slippage applied on both fills.**

_pairs: EURUSD, GBPUSD, NZDUSD · coverage: EURUSD 2022, EURUSD 2024, GBPUSD 2022, GBPUSD 2024, NZDUSD 2022, NZDUSD 2024_

MaxDD is peak-to-trough of the cumulative-R curve. `total` = summed R.

## In-sample (2022)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 1972 | 34% | 0.79 | -331.5R | -0.16R | -1.11R | -321.0R
| H1 | 616 | 32% | 0.77 | -119.0R | -0.18R | -1.11R | -110.1R
| H4 | 179 | 38% | 1.03 | -21.4R | +0.02R | -1.11R | +4.1R
| D1 | 50 | 54% | 1.98 | -5.6R | +0.50R | +1.81R | +25.1R

## Out-of-sample (2024)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 2007 | 30% | 0.63 | -647.9R | -0.32R | -1.17R | -643.5R
| H1 | 560 | 31% | 0.71 | -134.3R | -0.23R | -1.11R | -131.1R
| H4 | 150 | 33% | 0.81 | -30.0R | -0.14R | -1.11R | -21.6R
| D1 | 48 | 46% | 1.38 | -9.4R | +0.23R | -1.11R | +11.3R

## Read

IS PF 0.81 (n=2817, WR 34%) · OOS PF 0.66 (n=2765, WR 31%). Not positive in both splits — the raw inversion edge doesn't hold; nothing to ship.

_report generated on commit `c2dd2e6`_

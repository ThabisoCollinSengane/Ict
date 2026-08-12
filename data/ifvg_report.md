# Inversion FVG (IFVG) backtest — market-structure stop + costs

Core condition: a FVG violated by a **full-body close outside it** inverts to a supply/demand zone. **Swing-structure entry (SAME TF, H1/H4 only):** after the full-body-close inversion, wait for the first confirmed fractal swing (low for demand / high for supply, 2 bars each side) that HOLDS at the zone; enter on the confirmation bar's close, **stop just beyond the swing** (the structure itself — not a 10-pip cap). **Target = fixed 2R**. Spread + slippage on both fills.

_pairs: EURUSD, GBPUSD, NZDUSD · coverage: EURUSD 2022, EURUSD 2023, EURUSD 2024, EURUSD 2025, GBPUSD 2022, GBPUSD 2023, GBPUSD 2024, GBPUSD 2025, NZDUSD 2022, NZDUSD 2023, NZDUSD 2024, NZDUSD 2025_

MaxDD is peak-to-trough of the cumulative-R curve. `total` = summed R.

## In-sample (2022/2023)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | | — | 0 | — | — | — | — | — |
| H1 | 918 | 31% | 0.80 | -139.9R | -0.15R | -1.05R | -135.1R
| H4 | 256 | 36% | 1.04 | -23.6R | +0.02R | -1.02R | +6.1R
| D1 | | — | 0 | — | — | — | — | — |

## Out-of-sample (2024/2025)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | | — | 0 | — | — | — | — | — |
| H1 | 830 | 33% | 0.83 | -115.5R | -0.12R | -1.06R | -103.1R
| H4 | 252 | 40% | 1.20 | -12.2R | +0.13R | -1.02R | +31.9R
| D1 | | — | 0 | — | — | — | — | — |

## Read

IS PF 0.85 (n=1174, WR 32%) · OOS PF 0.91 (n=1082, WR 34%). Not positive in both splits — the raw inversion edge doesn't hold; nothing to ship.
## Actual entries taken (sample of the first 30 — full log in data/ifvg_trades.csv)

_2256 entries total._

| time (UTC) | pair | TF | dir | entry | stop | target | stop pips | R |
|---|---|---|---|---|---|---|---|---|
| 2022-01-03 15:00 | NZDUSD | H1 | sell | 0.67835 | 0.67972 | 0.67561 | 13.7 | -1.08 |
| 2022-01-03 16:00 | GBPUSD | H1 | sell | 1.34770 | 1.34867 | 1.34576 | 9.7 | -1.11 |
| 2022-01-03 17:00 | EURUSD | H1 | sell | 1.12945 | 1.13013 | 1.12809 | 6.8 | -1.16 |
| 2022-01-04 00:00 | NZDUSD | H1 | buy | 0.67956 | 0.67838 | 0.68192 | 11.8 | -1.10 |
| 2022-01-04 03:00 | EURUSD | H1 | sell | 1.12895 | 1.13081 | 1.12523 | 18.6 | -1.06 |
| 2022-01-04 04:00 | EURUSD | H4 | sell | 1.12730 | 1.13104 | 1.11982 | 37.4 | -1.03 |
| 2022-01-04 09:00 | GBPUSD | H1 | buy | 1.35161 | 1.34776 | 1.35931 | 38.5 | +1.97 |
| 2022-01-04 16:00 | NZDUSD | H1 | buy | 0.68032 | 0.67969 | 0.68158 | 6.3 | -1.17 |
| 2022-01-05 08:00 | GBPUSD | H4 | buy | 1.35717 | 1.35211 | 1.36729 | 50.6 | -1.02 |
| 2022-01-05 10:00 | EURUSD | H1 | buy | 1.13369 | 1.13020 | 1.14067 | 34.9 | -1.03 |
| 2022-01-05 23:00 | EURUSD | H1 | sell | 1.13122 | 1.13215 | 1.12936 | 9.3 | +1.88 |
| 2022-01-06 07:00 | NZDUSD | H1 | sell | 0.67556 | 0.67686 | 0.67296 | 13.0 | -1.09 |
| 2022-01-06 12:00 | GBPUSD | H1 | buy | 1.35301 | 1.35148 | 1.35607 | 15.3 | +1.92 |
| 2022-01-07 04:00 | EURUSD | H1 | buy | 1.13146 | 1.12970 | 1.13498 | 17.6 | -1.07 |
| 2022-01-07 08:00 | GBPUSD | H4 | buy | 1.35818 | 1.35260 | 1.36934 | 55.8 | +1.98 |
| 2022-01-09 19:00 | GBPUSD | H1 | buy | 1.35940 | 1.35724 | 1.36372 | 21.6 | -1.05 |
| 2022-01-09 20:00 | NZDUSD | H4 | sell | 0.67695 | 0.67838 | 0.67409 | 14.3 | +1.92 |
| 2022-01-10 13:00 | NZDUSD | H1 | sell | 0.67534 | 0.67581 | 0.67440 | 4.7 | -1.21 |
| 2022-01-10 14:00 | EURUSD | H1 | sell | 1.13232 | 1.13357 | 1.12982 | 12.5 | -1.09 |
| 2022-01-11 03:00 | GBPUSD | H1 | buy | 1.36103 | 1.35784 | 1.36741 | 31.9 | -1.04 |
| 2022-01-11 16:00 | GBPUSD | H4 | buy | 1.36372 | 1.35602 | 1.37912 | 77.0 | -1.02 |
| 2022-01-11 19:00 | EURUSD | H1 | buy | 1.13708 | 1.13608 | 1.13908 | 10.0 | -1.11 |
| 2022-01-11 22:00 | GBPUSD | H1 | buy | 1.36440 | 1.36269 | 1.36782 | 17.1 | -1.07 |
| 2022-01-11 22:00 | NZDUSD | H1 | buy | 0.67917 | 0.67783 | 0.68185 | 13.4 | -1.09 |
| 2022-01-12 12:00 | EURUSD | H4 | buy | 1.14496 | 1.13537 | 1.16414 | 95.9 | -1.01 |
| 2022-01-13 20:00 | GBPUSD | H4 | buy | 1.37270 | 1.36994 | 1.37822 | 27.6 | -1.04 |
| 2022-01-16 16:00 | NZDUSD | H4 | buy | 0.67976 | 0.67907 | 0.68114 | 6.9 | -1.15 |
| 2022-01-18 20:00 | EURUSD | H1 | sell | 1.13221 | 1.13314 | 1.13035 | 9.3 | -1.12 |
| 2022-01-19 05:00 | NZDUSD | H1 | buy | 0.67971 | 0.67751 | 0.68411 | 22.0 | -1.05 |
| 2022-01-19 10:00 | GBPUSD | H1 | buy | 1.36276 | 1.36194 | 1.36440 | 8.2 | -1.13 |


_report generated on commit `a3174a6`_

# Inversion FVG (IFVG) backtest

Core condition tested: a FVG violated by a **full-body close outside it** inverts to a supply/demand zone; entry on the LTF retest rejection (wick >40% of range), stop beyond the wick, target 2R. Detection TF → entry TF: H4→H1, H1→M15, M15→M5.

_pairs: EURUSD, GBPUSD, NZDUSD · coverage: EURUSD 2022, EURUSD 2024, GBPUSD 2022, GBPUSD 2024, NZDUSD 2022, NZDUSD 2024_

MaxDD is peak-to-trough of the cumulative-R curve. `total` = summed R.

## In-sample (2022)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 1972 | 38% | 1.21 | -40.0R | +0.13R | -1.00R | +255.0R
| H1 | 616 | 39% | 1.30 | -15.0R | +0.18R | -1.00R | +113.0R
| H4 | 179 | 45% | 1.67 | -12.0R | +0.36R | -1.00R | +64.8R
| D1 | 50 | 60% | 3.00 | -5.0R | +0.80R | +2.00R | +40.0R

## Out-of-sample (2024)

| TF | n | WR | PF | MaxDD | mean R | median R | total |
|---|---|---|---|---|---|---|---|
| M15 | 2007 | 37% | 1.17 | -28.0R | +0.10R | -1.00R | +210.0R
| H1 | 560 | 39% | 1.26 | -17.0R | +0.16R | -1.00R | +88.0R
| H4 | 150 | 33% | 1.00 | -25.0R | +0.00R | -1.00R | +0.0R
| D1 | 48 | 50% | 1.92 | -4.0R | +0.46R | -0.03R | +22.1R

## Read

IS PF 1.28 (n=2817, WR 39%) · OOS PF 1.18 (n=2765, WR 37%). Both splits positive — the full-body-close inversion carries an edge worth a proper (spread/slippage-aware) follow-up.

_report generated on commit `cfd1e58`_

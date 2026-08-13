# What separates winning MM IFVG adds from losers

Isolated **98 MM continuation legs** from the trade dump. Overall: **WR 31% · PF 0.60 · meanR -0.27**. Each table below is the SAME legs bucketed by one tag — a value with clearly higher WR/PF that HOLDS in both IS and OOS is a shippable quality filter; one that flips between splits is noise.

_IS = 2022-23, OOS = 2024-25. R = (exit−entry)·dir / |entry−stop|._

## Headline — strongest separators

| tag | best value (WR, n) | worst value (WR, n) |
|---|---|---|
| ifvg_tf | 10T (50%, 24) | 240T (15%, 13) |
| pattern | ob (32%, 65) | fvg (31%, 29) |
| entry_tf | m5 (31%, 98) | m5 (31%, 98) |
| htf_smt | False (35%, 17) | True (30%, 81) |
| pair | EURUSD (32%, 71) | GBPUSD (26%, 27) |
| profile | london (35%, 49) | ny (27%, 49) |
| direction | -1 (32%, 60) | 1 (29%, 38) |
| draw_score | 2 (38%, 39) | 3 (25%, 8) |
| conf_bucket | ≥4 (37%, 52) | 3 (20%, 20) |
| crt_tf | D (29%, 35) | 240T (27%, 11) |
| mstruct_minor_sweep | False (32%, 90) | True (12%, 8) |
| amd_swept_pdliq | False (26%, 42) | True (22%, 18) |
| soj_type | dual (35%, 34) | single (30%, 56) |

## Win / loss economics

| | n | avg pips | median pips | max pips | avg R |
|---|---|---|---|---|---|
| **wins** | 30 | 23.16 | 9.60 | 74.60 | 1.05 |
| losses | 68 | -6.86 | -9.35 | -0.40 | -1.06 |

_Per-add expectancy: **2.33 pips**, **-0.27 R**. Biggest win 74.60 pips / 3.21R._

## Specs of the winning adds (winners only)

For the winning legs only: how many, their share, and their pip size — so the 'good entry' profile is explicit.

### winners by `ifvg_tf`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| 10T | 12 | 40% | 23.34 | 9.60 | 74.60 |
| 5T | 8 | 27% | 18.95 | 9.60 | 34.60 |
| 60T | 3 | 10% | 25.41 | 32.13 | 34.60 |
| 15T | 3 | 10% | 32.90 | 34.60 | 54.50 |
| 240T | 2 | 7% | 22.05 | 22.05 | 34.50 |
| 30T | 2 | 7% | 22.05 | 22.05 | 34.50 |

### winners by `pattern`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| ob | 21 | 70% | 24.22 | 9.60 | 74.60 |
| fvg | 9 | 30% | 20.69 | 9.60 | 34.60 |

### winners by `entry_tf`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| m5 | 30 | 100% | 23.16 | 9.60 | 74.60 |

### winners by `pair`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| EURUSD | 23 | 77% | 21.01 | 9.60 | 74.60 |
| GBPUSD | 7 | 23% | 30.21 | 34.50 | 54.50 |

### winners by `draw_score`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| 2 | 15 | 50% | 20.75 | 9.60 | 54.50 |
| 1 | 13 | 43% | 26.12 | 34.50 | 74.60 |
| 3 | 2 | 7% | 22.05 | 22.05 | 34.50 |

### winners by `conf_bucket`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| ≥4 | 19 | 63% | 20.11 | 9.60 | 34.60 |
| <3 | 7 | 23% | 29.93 | 34.50 | 54.50 |
| 3 | 4 | 13% | 25.82 | 9.60 | 74.60 |

## Full breakdown by tag (all legs)

### by `ifvg_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 5T | 27 | 30% | 0.53 | -0.32 | —/— | 30%/0.53 |
| 10T | 24 | 50% | 0.92 | -0.04 | —/— | 50%/0.92 |
| 15T | 17 | 18% | 0.40 | -0.44 | —/— | 18%/0.40 |
| 240T | 13 | 15% | 0.31 | -0.55 | —/— | 15%/0.31 |
| 30T | 8 | 25% | 0.31 | -0.54 | —/— | 25%/0.31 |
| 60T | 5 | 60% | 2.28 | 0.58 | —/— | 60%/2.28 |
| 20T | 4 | 0% | 0.00 | -1.06 | —/— | 0%/0.00 |

### by `pattern`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ob | 65 | 32% | 0.72 | -0.17 | —/— | 32%/0.72 |
| fvg | 29 | 31% | 0.49 | -0.35 | —/— | 31%/0.49 |
| breaker | 4 | 0% | 0.00 | -1.13 | —/— | 0%/0.00 |

### by `entry_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| m5 | 98 | 31% | 0.60 | -0.27 | —/— | 31%/0.60 |

### by `htf_smt`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| True | 81 | 30% | 0.58 | -0.28 | —/— | 30%/0.58 |
| False | 17 | 35% | 0.69 | -0.19 | —/— | 35%/0.69 |

### by `pair`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| EURUSD | 71 | 32% | 0.71 | -0.18 | —/— | 32%/0.71 |
| GBPUSD | 27 | 26% | 0.38 | -0.46 | —/— | 26%/0.38 |

### by `profile`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| london | 49 | 35% | 0.71 | -0.18 | —/— | 35%/0.71 |
| ny | 49 | 27% | 0.48 | -0.36 | —/— | 27%/0.48 |

### by `direction`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| -1 | 60 | 32% | 0.67 | -0.21 | —/— | 32%/0.67 |
| 1 | 38 | 29% | 0.48 | -0.36 | —/— | 29%/0.48 |

### by `draw_score`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 1 | 51 | 25% | 0.48 | -0.36 | —/— | 25%/0.48 |
| 2 | 39 | 38% | 0.75 | -0.15 | —/— | 38%/0.75 |
| 3 | 8 | 25% | 0.47 | -0.37 | —/— | 25%/0.47 |

### by `conf_bucket`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ≥4 | 52 | 37% | 0.80 | -0.11 | —/— | 37%/0.80 |
| <3 | 26 | 27% | 0.53 | -0.34 | —/— | 27%/0.53 |
| 3 | 20 | 20% | 0.31 | -0.55 | —/— | 20%/0.31 |

### by `crt_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| nan | 0 | — | — | — | —/— | —/— |
| D | 35 | 29% | 0.51 | -0.33 | —/— | 29%/0.51 |
| 240T | 11 | 27% | 0.55 | -0.29 | —/— | 27%/0.55 |

### by `mstruct_minor_sweep`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| False | 90 | 32% | 0.64 | -0.23 | —/— | 32%/0.64 |
| True | 8 | 12% | 0.18 | -0.72 | —/— | 12%/0.18 |

### by `amd_swept_pdliq`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| False | 42 | 26% | 0.46 | -0.39 | —/— | 26%/0.46 |
| nan | 0 | — | — | — | —/— | —/— |
| True | 18 | 22% | 0.31 | -0.54 | —/— | 22%/0.31 |

### by `soj_type`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| single | 56 | 30% | 0.68 | -0.20 | —/— | 30%/0.68 |
| dual | 34 | 35% | 0.65 | -0.22 | —/— | 35%/0.65 |
| nan | 0 | — | — | — | —/— | —/— |


# What separates winning MM IFVG adds from losers

Isolated **14 MM continuation legs** from the trade dump. Overall: **WR 50% · PF 3.65 · meanR 1.05**. Each table below is the SAME legs bucketed by one tag — a value with clearly higher WR/PF that HOLDS in both IS and OOS is a shippable quality filter; one that flips between splits is noise.

_IS = 2022-23, OOS = 2024-25. R = (exit−entry)·dir / |entry−stop|._

## Headline — strongest separators

| tag | best value (WR, n) | worst value (WR, n) |
|---|---|---|
| ifvg_tf | 240T (62%, 8) | 240T (62%, 8) |
| pattern | fvg (56%, 9) | fvg (56%, 9) |
| entry_tf | m5 (50%, 14) | m5 (50%, 14) |
| htf_smt | True (46%, 13) | True (46%, 13) |
| pair | EURUSD (50%, 10) | EURUSD (50%, 10) |
| profile | ny (56%, 9) | ny (56%, 9) |
| session_phase | ny_judas (56%, 9) | ny_judas (56%, 9) |
| direction | -1 (50%, 8) | -1 (50%, 8) |
| draw_score | 2 (40%, 10) | 2 (40%, 10) |
| conf_bucket | <3 (50%, 8) | <3 (50%, 8) |
| target_type | fib_extension (44%, 9) | fib_extension (44%, 9) |
| mstruct_minor_sweep | False (50%, 12) | False (50%, 12) |

## Win / loss economics

| | n | avg pips | median pips | max pips | avg R | avg stop pips |
|---|---|---|---|---|---|---|
| **wins** | 7 | 26.26 | 31.20 | 37.29 | 2.27 | 13.57 |
| losses | 7 | -4.14 | -2.90 | -0.40 | -1.09 | 3.71 |

_Per-add expectancy: **11.06 pips**, **1.05 R**. Biggest win 37.29 pips / 3.73R. If winners carry WIDER stops than losers (13.57 vs 3.71), the entry-precision fix should tighten them and lift R._

## Good timeframe cascades (PF>1 in BOTH splits, n≥8)

| IFVG TF | n | IS PF | OOS PF |
|---|---|---|---|
| 240T | 8 | ∞ | 3.52 |

## Fib alignment

Each MM add inherits the position's target. This shows whether the winning adds ride the strategy's **fib** targets or **liquidity** draws (ITH/ITL/PDH-PDL) — i.e. how the existing fib logic aligns with the MM continuation.

| target family | n | WR | PF | avg win pips |
|---|---|---|---|---|
| fib | 9 | 44% | 2.71 | 21.67 |
| liquidity/other | 5 | 60% | 6.24 | 32.37 |

## Specs of the winning adds (winners only)

For the winning legs only: how many, their share, and their pip size — so the 'good entry' profile is explicit.

### winners by `ifvg_tf`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| 240T | 5 | 71% | 28.80 | 31.30 | 37.29 |
| 10T | 1 | 14% | 9.60 | 9.60 | 9.60 |
| 5T | 1 | 14% | 30.20 | 30.20 | 30.20 |

### winners by `pattern`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| fvg | 5 | 71% | 23.26 | 31.20 | 34.60 |
| breaker | 1 | 14% | 37.29 | 37.29 | 37.29 |
| ob | 1 | 14% | 30.20 | 30.20 | 30.20 |

### winners by `entry_tf`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| m5 | 7 | 100% | 26.26 | 31.20 | 37.29 |

### winners by `pair`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| EURUSD | 5 | 71% | 23.04 | 30.20 | 34.60 |
| GBPUSD | 2 | 29% | 34.29 | 34.29 | 37.29 |

### winners by `draw_score`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| 2 | 4 | 57% | 27.92 | 32.40 | 37.29 |
| 1 | 2 | 29% | 20.45 | 20.45 | 31.30 |
| 3 | 1 | 14% | 31.20 | 31.20 | 31.20 |

### winners by `conf_bucket`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| <3 | 4 | 57% | 22.77 | 22.10 | 37.29 |
| 3 | 2 | 29% | 31.25 | 31.25 | 31.30 |
| ≥4 | 1 | 14% | 30.20 | 30.20 | 30.20 |

## Full breakdown by tag (all legs)

### by `ifvg_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 240T | 8 | 62% | 10.28 | 1.79 | 100%/∞ | 40%/3.52 |
| 5T | 2 | 50% | 2.89 | 0.99 | 0%/0.00 | 100%/∞ |
| 10T | 2 | 50% | 0.87 | -0.07 | —/— | 50%/0.87 |
| 60T | 1 | 0% | 0.00 | -1.05 | 0%/0.00 | —/— |
| 15T | 1 | 0% | — | — | —/— | 0%/— |

### by `pattern`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| fvg | 9 | 56% | 4.37 | 1.01 | 50%/1.97 | 60%/∞ |
| ob | 3 | 33% | 2.73 | 0.96 | —/— | 33%/2.73 |
| breaker | 2 | 50% | 3.21 | 1.28 | 100%/∞ | 0%/0.00 |

### by `entry_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| m5 | 14 | 50% | 3.65 | 1.05 | 60%/3.75 | 44%/3.56 |

### by `htf_smt`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| True | 13 | 46% | 2.93 | 0.84 | 60%/3.75 | 38%/2.18 |
| False | 1 | 100% | ∞ | 3.12 | —/— | 100%/∞ |

### by `pair`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| EURUSD | 10 | 50% | 4.10 | 0.98 | 50%/0.95 | 50%/6.95 |
| GBPUSD | 4 | 50% | 3.18 | 1.18 | 67%/6.53 | 0%/0.00 |

### by `profile`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ny | 9 | 56% | 4.21 | 1.33 | 67%/6.56 | 50%/3.13 |
| london | 5 | 40% | 1.86 | 0.30 | 50%/0.94 | 33%/∞ |

### by `session_phase`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ny_judas | 9 | 56% | 4.21 | 1.33 | 67%/6.56 | 50%/3.13 |
| london_judas | 5 | 40% | 1.86 | 0.30 | 50%/0.94 | 33%/∞ |

### by `direction`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| -1 | 8 | 50% | 2.48 | 0.69 | 0%/0.00 | 67%/6.95 |
| 1 | 6 | 50% | 7.09 | 1.69 | 100%/∞ | 0%/0.00 |

### by `draw_score`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 2 | 10 | 40% | 1.99 | 0.54 | 50%/2.25 | 33%/1.76 |
| 1 | 3 | 67% | ∞ | 2.05 | 100%/∞ | 50%/∞ |
| 3 | 1 | 100% | ∞ | 3.12 | —/— | 100%/∞ |

### by `conf_bucket`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| <3 | 8 | 50% | 3.00 | 0.74 | 67%/4.49 | 40%/1.66 |
| 3 | 3 | 67% | 5.98 | 1.73 | 50%/2.99 | 100%/∞ |
| ≥4 | 3 | 33% | 2.73 | 0.96 | —/— | 33%/2.73 |

### by `target_type`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| fib_extension | 9 | 44% | 2.71 | 0.78 | 33%/1.78 | 50%/4.47 |
| pdh_pdl | 4 | 50% | 3.54 | 0.98 | 100%/∞ | 33%/2.69 |
| round_number | 1 | 100% | ∞ | 3.13 | 100%/∞ | —/— |

### by `crt_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| nan | 0 | — | — | — | —/— | —/— |
| D | 5 | 40% | 3.52 | 0.97 | —/— | 40%/3.52 |
| 240T | 2 | 100% | ∞ | 2.00 | 100%/∞ | 100%/∞ |

### by `mstruct_minor_sweep`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| False | 12 | 50% | 3.86 | 1.05 | 75%/7.47 | 38%/2.18 |
| True | 2 | 50% | 2.98 | 1.04 | 0%/0.00 | 100%/∞ |

### by `amd_swept_pdliq`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| nan | 0 | — | — | — | —/— | —/— |
| False | 4 | 25% | 0.44 | -0.43 | 100%/∞ | 0%/0.00 |
| True | 4 | 50% | 4.49 | 1.21 | 50%/3.57 | 50%/∞ |

### by `soj_type`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| single | 7 | 57% | 3.71 | 1.00 | 67%/3.92 | 50%/3.52 |
| dual | 5 | 40% | 3.60 | 0.96 | —/— | 40%/3.60 |
| nan | 0 | — | — | — | —/— | —/— |


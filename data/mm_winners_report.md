# What separates winning MM IFVG adds from losers

Isolated **1075 MM continuation legs** from the trade dump. Overall: **WR 21% · PF 0.46 · meanR -0.45**. Each table below is the SAME legs bucketed by one tag — a value with clearly higher WR/PF that HOLDS in both IS and OOS is a shippable quality filter; one that flips between splits is noise.

_IS = 2022-23, OOS = 2024-25. R = (exit−entry)·dir / |entry−stop|._

## Headline — strongest separators

| tag | best value (WR, n) | worst value (WR, n) |
|---|---|---|
| ifvg_tf | 60T (24%, 94) | 1T (16%, 77) |
| pattern | fvg (29%, 265) | breaker (14%, 462) |
| entry_tf | m1 (24%, 316) | m5 (20%, 759) |
| htf_smt | True (21%, 1075) | True (21%, 1075) |
| pair | GBPUSD (22%, 592) | EURUSD (20%, 483) |
| profile | ny (22%, 612) | london (21%, 463) |
| session_phase | unknown (21%, 1075) | unknown (21%, 1075) |
| direction | -1 (23%, 522) | 1 (20%, 553) |
| draw_score | 0 (21%, 1075) | 0 (21%, 1075) |
| conf_bucket | <3 (21%, 1075) | <3 (21%, 1075) |
| target_type | range_equilibrium (35%, 20) | equal_hl (9%, 44) |
| mstruct_minor_sweep | False (21%, 1075) | False (21%, 1075) |

## Win / loss economics

| | n | avg pips | median pips | max pips | avg R | avg stop pips |
|---|---|---|---|---|---|---|
| **wins** | 230 | 20.28 | 9.60 | 114.50 | 1.54 | 14.89 |
| losses | 845 | -4.00 | -3.10 | -0.40 | -1.14 | 3.55 |

_Per-add expectancy: **1.19 pips**, **-0.45 R**. Biggest win 114.50 pips / 3.72R. If winners carry WIDER stops than losers (14.89 vs 3.55), the entry-precision fix should tighten them and lift R._

## Good timeframe cascades (PF>1 in BOTH splits, n≥8)

_None held PF>1 in both splits at n≥8 — the cascade edge is thin/noisy._

## Fib alignment

Each MM add inherits the position's target. This shows whether the winning adds ride the strategy's **fib** targets or **liquidity** draws (ITH/ITL/PDH-PDL) — i.e. how the existing fib logic aligns with the MM continuation.

| target family | n | WR | PF | avg win pips |
|---|---|---|---|---|
| fib | 141 | 25% | 0.65 | 20.95 |
| liquidity/other | 934 | 21% | 0.44 | 20.16 |

## Specs of the winning adds (winners only)

For the winning legs only: how many, their share, and their pip size — so the 'good entry' profile is explicit.

### winners by `ifvg_tf`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| D | 71 | 31% | 19.42 | 9.60 | 39.30 |
| W | 58 | 25% | 20.96 | 9.60 | 114.50 |
| 240T | 36 | 16% | 20.83 | 9.60 | 54.60 |
| 60T | 23 | 10% | 18.14 | 9.60 | 35.40 |
| 15T | 18 | 8% | 22.34 | 29.90 | 35.10 |
| 1T | 12 | 5% | 19.18 | 9.50 | 54.50 |
| 5T | 12 | 5% | 22.61 | 30.20 | 34.50 |

### winners by `pattern`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| ob | 90 | 39% | 19.82 | 9.60 | 54.60 |
| fvg | 77 | 33% | 20.28 | 9.60 | 74.50 |
| breaker | 63 | 27% | 20.95 | 9.60 | 114.50 |

### winners by `entry_tf`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| m5 | 154 | 67% | 21.10 | 9.60 | 114.50 |
| m1 | 76 | 33% | 18.64 | 9.60 | 74.50 |

### winners by `pair`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| GBPUSD | 132 | 57% | 21.78 | 9.50 | 114.50 |
| EURUSD | 98 | 43% | 18.27 | 9.60 | 54.60 |

### winners by `draw_score`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| 0 | 230 | 100% | 20.28 | 9.60 | 114.50 |

### winners by `conf_bucket`

| value | wins | % of wins | avg win pips | median | max |
|---|---|---|---|---|---|
| <3 | 230 | 100% | 20.28 | 9.60 | 114.50 |

## Full breakdown by tag (all legs)

### by `ifvg_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| D | 329 | 22% | 0.49 | -0.43 | 21%/0.51 | 22%/0.47 |
| W | 264 | 22% | 0.43 | -0.47 | 23%/0.36 | 21%/0.47 |
| 240T | 150 | 24% | 0.56 | -0.35 | 26%/0.66 | 21%/0.44 |
| 60T | 94 | 24% | 0.58 | -0.35 | 26%/0.62 | 22%/0.52 |
| 15T | 92 | 20% | 0.45 | -0.49 | 25%/0.54 | 9%/0.28 |
| 1T | 77 | 16% | 0.23 | -0.71 | 12%/0.16 | 22%/0.36 |
| 5T | 69 | 17% | 0.42 | -0.53 | 19%/0.46 | 14%/0.35 |

### by `pattern`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| breaker | 462 | 14% | 0.23 | -0.78 | 15%/0.28 | 11%/0.17 |
| ob | 348 | 26% | 0.63 | -0.28 | 25%/0.61 | 26%/0.66 |
| fvg | 265 | 29% | 0.93 | -0.05 | 29%/0.84 | 29%/1.08 |

### by `entry_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| m5 | 759 | 20% | 0.46 | -0.47 | 20%/0.43 | 21%/0.49 |
| m1 | 316 | 24% | 0.48 | -0.43 | 27%/0.61 | 19%/0.32 |

### by `htf_smt`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| True | 1075 | 21% | 0.46 | -0.45 | 22%/0.48 | 20%/0.44 |

### by `pair`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| GBPUSD | 592 | 22% | 0.48 | -0.44 | 23%/0.50 | 22%/0.46 |
| EURUSD | 483 | 20% | 0.45 | -0.47 | 21%/0.46 | 19%/0.43 |

### by `profile`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ny | 612 | 22% | 0.47 | -0.44 | 22%/0.48 | 22%/0.46 |
| london | 463 | 21% | 0.45 | -0.47 | 23%/0.48 | 18%/0.42 |

### by `session_phase`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| unknown | 1075 | 21% | 0.46 | -0.45 | 22%/0.48 | 20%/0.44 |

### by `direction`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 1 | 553 | 20% | 0.43 | -0.49 | 20%/0.41 | 20%/0.45 |
| -1 | 522 | 23% | 0.50 | -0.42 | 25%/0.56 | 21%/0.44 |

### by `draw_score`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 0 | 1075 | 21% | 0.46 | -0.45 | 22%/0.48 | 20%/0.44 |

### by `conf_bucket`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| <3 | 1075 | 21% | 0.46 | -0.45 | 22%/0.48 | 20%/0.44 |

### by `target_type`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| swing | 587 | 21% | 0.47 | -0.45 | 22%/0.50 | 20%/0.45 |
| round_number | 194 | 22% | 0.37 | -0.53 | 22%/0.38 | 20%/0.34 |
| fib_extension | 141 | 25% | 0.65 | -0.29 | 26%/0.65 | 24%/0.63 |
| pdh_pdl | 73 | 19% | 0.46 | -0.47 | 23%/0.64 | 12%/0.22 |
| equal_hl | 44 | 9% | 0.15 | -0.86 | 4%/0.04 | 14%/0.31 |
| range_equilibrium | 20 | 35% | 0.75 | -0.15 | 33%/0.85 | 38%/0.65 |
| pwh_pwl | 16 | 31% | 0.47 | -0.40 | 22%/0.29 | 43%/0.79 |

### by `crt_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| nan | 0 | — | — | — | —/— | —/— |

### by `mstruct_minor_sweep`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| False | 1075 | 21% | 0.46 | -0.45 | 22%/0.48 | 20%/0.44 |

### by `amd_swept_pdliq`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| nan | 0 | — | — | — | —/— | —/— |

### by `soj_type`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| nan | 0 | — | — | — | —/— | —/— |


# What separates winning MM IFVG adds from losers

Isolated **266 MM continuation legs** from the trade dump. Overall: **WR 16% · PF 1.09 · meanR nan**. Each table below is the SAME legs bucketed by one tag — a value with clearly higher WR/PF that HOLDS in both IS and OOS is a shippable quality filter; one that flips between splits is noise.

_IS = 2022-23, OOS = 2024-25. R = (exit−entry)·dir / |entry−stop|._

## Headline — strongest separators

| tag | best value (WR, n) | worst value (WR, n) |
|---|---|---|
| ifvg_tf | 20T (38%, 8) | 15T (0%, 12) |
| pattern | fvg (18%, 121) | breaker (14%, 22) |
| entry_tf | m5 (17%, 240) | m1 (8%, 26) |
| htf_smt | True (17%, 230) | False (8%, 36) |
| pair | GBPUSD (19%, 90) | EURUSD (15%, 176) |
| profile | ny (17%, 137) | london (16%, 129) |
| direction | 1 (17%, 93) | -1 (16%, 173) |
| draw_score | 3 (50%, 8) | 0 (3%, 32) |
| conf_bucket | 3 (19%, 64) | ≥4 (14%, 101) |
| crt_tf | 240T (21%, 19) | D (11%, 125) |
| mstruct_minor_sweep | False (17%, 230) | True (11%, 36) |
| amd_swept_pdliq | False (18%, 147) | True (10%, 50) |
| soj_type | single (19%, 154) | dual (15%, 62) |

## Full breakdown by tag

### by `ifvg_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| W | 71 | 10% | 0.81 | nan | 14%/0.39 | 8%/1.17 |
| D | 68 | 6% | 0.23 | nan | 3%/0.15 | 8%/0.27 |
| 1T | 38 | 32% | 1.82 | nan | 40%/2.40 | 22%/1.34 |
| 5T | 25 | 20% | 1.21 | nan | 22%/0.92 | 19%/1.32 |
| 10T | 19 | 21% | 1.11 | nan | 25%/1.92 | 18%/0.78 |
| 240T | 12 | 33% | 1.84 | nan | 30%/2.38 | 50%/0.85 |
| 15T | 12 | 0% | 0.00 | nan | 0%/0.00 | 0%/0.00 |
| 60T | 8 | 25% | 1.16 | nan | 0%/0.00 | 50%/1.77 |
| 20T | 8 | 38% | 8.46 | nan | 33%/5.67 | 50%/∞ |
| 30T | 5 | 40% | 1.74 | nan | 67%/∞ | 0%/0.00 |

### by `pattern`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ob | 123 | 15% | 1.05 | nan | 24%/1.46 | 10%/0.89 |
| fvg | 121 | 18% | 1.59 | nan | 19%/1.32 | 17%/2.34 |
| breaker | 22 | 14% | 0.31 | nan | 0%/0.00 | 16%/0.31 |

### by `entry_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| m5 | 240 | 17% | 1.38 | nan | 20%/1.39 | 14%/1.37 |
| m1 | 26 | 8% | 0.12 | nan | 25%/0.91 | 5%/0.06 |

### by `htf_smt`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| True | 230 | 17% | 1.22 | nan | 20%/1.27 | 15%/1.18 |
| False | 36 | 8% | 0.42 | nan | 40%/3.84 | 3%/0.09 |

### by `pair`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| EURUSD | 176 | 15% | 0.91 | nan | 15%/0.99 | 14%/0.87 |
| GBPUSD | 90 | 19% | 1.60 | nan | 28%/2.21 | 9%/1.07 |

### by `profile`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ny | 137 | 17% | 1.03 | nan | 19%/1.36 | 15%/0.84 |
| london | 129 | 16% | 1.17 | nan | 24%/1.38 | 11%/1.03 |

### by `direction`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| -1 | 173 | 16% | 0.96 | nan | 19%/1.02 | 13%/0.91 |
| 1 | 93 | 17% | 1.45 | nan | 23%/2.52 | 12%/0.92 |

### by `draw_score`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| 2 | 139 | 19% | 1.40 | nan | 26%/1.97 | 15%/1.12 |
| 1 | 87 | 13% | 0.62 | nan | 17%/0.95 | 10%/0.44 |
| 0 | 32 | 3% | 0.10 | nan | 5%/0.15 | 0%/0.00 |
| 3 | 8 | 50% | 10.91 | nan | 50%/∞ | 50%/6.34 |

### by `conf_bucket`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| ≥4 | 101 | 14% | 0.86 | nan | 14%/0.46 | 14%/1.40 |
| <3 | 101 | 17% | 0.99 | nan | 25%/1.98 | 11%/0.62 |
| 3 | 64 | 19% | 1.63 | nan | 25%/2.46 | 14%/1.18 |

### by `crt_tf`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| D | 125 | 11% | 0.70 | nan | 17%/0.50 | 9%/0.81 |
| nan | 0 | — | — | — | —/— | —/— |
| 240T | 19 | 21% | 1.41 | nan | 36%/8.48 | 0%/0.00 |

### by `mstruct_minor_sweep`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| False | 230 | 17% | 1.23 | nan | 22%/1.64 | 13%/1.01 |
| True | 36 | 11% | 0.33 | nan | 13%/0.46 | 8%/0.18 |

### by `amd_swept_pdliq`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| False | 147 | 18% | 1.44 | nan | 29%/2.00 | 9%/1.01 |
| nan | 0 | — | — | — | —/— | —/— |
| True | 50 | 10% | 0.35 | nan | 0%/0.00 | 16%/0.49 |

### by `soj_type`

| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |
|---|---|---|---|---|---|---|
| single | 154 | 19% | 1.28 | nan | 29%/1.82 | 14%/1.00 |
| dual | 62 | 15% | 1.04 | nan | 19%/1.66 | 12%/0.81 |
| nan | 0 | — | — | — | —/— | —/— |


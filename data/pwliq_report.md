# Previous-week high/low (PWH/PWL) reaction study

The P41 question one timeframe up: does sweeping a **weekly** pool (PWH/PWL) predict a better reversal, the way sweeping a **daily** pool (PDH/PDL) did? Measured on the full trade set (all pairs, 2022-2025). `amd_liq_run` classifies the pool the AMD sweep ran, weekly-priority.

_trades: 810 · with a classified sweep pool: 566 · IS = 2022-23, OOS = 2024-25_

**Watch n:** weekly sweeps are rarer than daily. A bucket under ~15 per split is noise, not signal — the P41 discipline (consistent in BOTH years, adequate n) applies.

## By pool the sweep ran

| pool | n IS/OOS | WR IS | WR OOS | PF IS | PF OOS | meanR IS | meanR OOS |
|---|---|---|---|---|---|---|---|
| `pwh` | 0/3 | — | 33.3% | — | 33.35 | — | +0.80R |
| `pwl` | 2/3 | 50.0% | 66.7% | 0.59 | 21.43 | +0.68R | +2.21R |
| `pdh` | 27/38 | 51.9% | 50.0% | 3.58 | 21.77 | +0.86R | +0.84R |
| `pdl` | 17/33 | 47.1% | 39.4% | 1.84 | 2.70 | +0.62R | +0.54R |
| `eqh` | 117/105 | 45.3% | 43.8% | 3.23 | 3.96 | +0.63R | +0.62R |
| `eql` | 91/84 | 45.1% | 51.2% | 2.93 | 5.54 | +0.78R | +1.02R |
| `vah` | 5/2 | 40.0% | 0.0% | 0.47 | 0.00 | +0.29R | -1.04R |
| `val` | 2/0 | 50.0% | — | 2.57 | — | +0.55R | — |
| `none` | 22/15 | 31.8% | 53.3% | 1.95 | 0.43 | +0.84R | +0.75R |

## Rolled up — weekly vs daily vs none (the money table)

| group | n IS/OOS | WR IS | WR OOS | PF IS | PF OOS | meanR IS | meanR OOS |
|---|---|---|---|---|---|---|---|
| weekly (PWH/PWL) | 2/6 | 50.0% | 50.0% | 0.59 | 29.43 | +0.68R | +1.27R |
| daily (PDH/PDL) | 44/71 | 50.0% | 45.1% | 2.65 | 5.77 | +0.76R | +0.70R |
| equal H/L | 208/189 | 45.2% | 47.1% | 3.12 | 4.88 | +0.69R | +0.81R |
| value area | 7/2 | 42.9% | 0.0% | 2.42 | 0.00 | +0.39R | -1.04R |
| no major pool | 128/153 | 45.3% | 45.8% | 3.25 | 2.80 | +0.82R | +0.78R |

## Verdict — is a PWH/PWL sizing lever justified?

⚠️ **INCONCLUSIVE — sample too small.** Weekly sweeps: 2 IS / 6 OOS. Below ~10-15 per split, WR/PF are noise. Weekly pools are swept far less often than daily ones, so even 4yr may not give a tradeable sample. Report the numbers; do NOT ship a lever on this n.

PWH/PWL remain valuable where they already are: as **target** levels (P17) and confluence sources (P18) — that use doesn't need a large sweep sample.

_report generated on commit `5a77cd5`_

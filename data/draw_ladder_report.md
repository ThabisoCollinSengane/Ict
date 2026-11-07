# Draw-on-liquidity ladder — how price reacts to each rung

_trades: 810 · IS = 2022-23, OOS = 2024-25_

## A · Targets — how price reacts to each draw type it aims at

`hit` = reached the target (vs stopped/other). IS = 2022-23, OOS = 2024-25.

| target type | n IS/OOS | WR IS | WR OOS | hit IS | hit OOS | PF IS | PF OOS |
|---|---|---|---|---|---|---|---|
| `pwh_pwl` | 4/8 | 50.0% | 37.5% | 25% | 38% | 26.78 | 7.55 |
| `pdh_pdl` | 47/53 | 44.7% | 45.3% | 21% | 30% | 2.31 | 7.19 |
| `ith_liquidity` | 1/7 | 100.0% | 42.9% | 100% | 29% | inf | 1.27 |
| `itl_liquidity` | 4/9 | 0.0% | 44.4% | 0% | 22% | 0.00 | 162.33 |
| `fib_extension` | 217/218 | 44.7% | 46.3% | 26% | 36% | 2.81 | 4.40 |
| `equal_hl` | 39/48 | 48.7% | 43.8% | 28% | 33% | 3.84 | 4.27 |
| `swing` | 48/69 | 41.7% | 49.3% | 31% | 41% | 4.10 | 8.23 |
| `round_number` | 29/9 | 62.1% | 44.4% | 34% | 33% | 8.57 | 0.27 |

## B · The ladder — when the raid is done, where does price deliver?

For each rung: of trades where that pool was an UNSWEPT draw ahead at entry, the share price DELIVERED to (max-favorable-excursion reached the pool), plus the median distance to it. This is the ICT draw cascade, measured.

| rung | n IS/OOS (draw ahead) | delivered IS | delivered OOS | median dist IS | median dist OOS |
|---|---|---|---|---|---|
| previous session | 143/175 | 78% | 87% | 7 | 6 |
| 3-day | 389/421 | 0% | 0% | 62 | 42 |
| weekly | 250/277 | 8% | 7% | 167 | 105 |
| 30-day | 374/421 | 0% | 0% | 189 | 125 |
| 60-day | 359/421 | 0% | 0% | 283 | 190 |

_A rung with few trades 'ahead' means price had usually already taken that pool by entry (it sits behind the fade) — itself a finding: the nearer rungs get consumed first, exactly the cascade order._

_report generated on commit `64052de`_

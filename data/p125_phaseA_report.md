# P125 Phase A — which 1-hour read carried the 42% win rate?

Leaky original engine (M15 / H4 / D still read the unfinished candle, no stop slippage, no same-bar fix),
measurement mode (R100k, breakers off). In each arm, ONE group's H1 read uses only the CLOSED H1 candle.
Base + MM, EURUSD / GBPUSD / NZDUSD. All legs: n / win rate / profit factor; first legs: average R.

| Arm (H1 made honest for…) | 2022-23 n / WR / PF / avg R | 2024-25 n / WR / PF / avg R |
|---|---|---|
| nothing (`mleaky`, reference) | 472 / 42.2% / 1.97 / +0.66 | 478 / 44.1% / 4.83 / +0.90 |
| the traded pairs only (`mpairH1`) | 455 / 41.1% / 2.12 / +0.64 | 466 / 41.2% / 3.53 / +0.76 |
| EURGBP / AUDNZD only (`mcrossH1`) | 465 / 39.1% / 1.84 / +0.58 | 463 / 42.5% / 4.05 / +0.84 |
| **the dollar (UDXUSD) only (`mdxyH1`)** | **298 / 28.5% / 1.17 / +0.15** | **308 / 29.9% / 1.46 / +0.25** |
| all of them (`md60`) | 296 / 26.4% / 1.18 / +0.14 | 304 / 28.9% / 1.34 / +0.19 |

Regression: the original R1k engine (`leaky`, 2022-23) reproduced 424 / 42.2% / PF 3.13 exactly.
MM-channel trades alone: 27-30% WR in every 2022-23 arm, 33-38% in 2024-25 — the collapse is in the base strategy.

**Verdict:** making ONLY the dollar's H1 read honest produces the whole collapse (42% -> 28-30% win rate,
~470 -> ~300 trades); the pairs' own H1 and the EURGBP/AUDNZD cross barely matter. The 42% came from the
dollar gate seeing where the CURRENT hour's DXY candle would close. Everything else in the stack was
close to neutral to the leak.

**What it does not show:** these arms keep M15/H4/D leaky and leave out stop slippage, so even the
28-30% / PF 1.2-1.5 rows are optimistic; the fully honest engine is 18-23% / PF 0.69-0.81 (P119).

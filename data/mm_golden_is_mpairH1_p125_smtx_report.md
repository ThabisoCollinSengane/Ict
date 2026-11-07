# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 467, unique setups 238, simulated 238. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 47% / 1.79 / +21.4 | 11% / 0.26 / -35.0 | reversal |
| shift>=2 & cont | IS | 63 | 44% / 1.57 / +19.8 | 16% / 0.38 / -33.0 | reversal |
| shift>=2 & none | IS | 6 | 33% / 1.00 / +0.0 | 33% / 1.00 / +0.0 | continuation |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift<2 | IS | 95 | 48% / 1.88 / +43.0 | 14% / 0.32 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

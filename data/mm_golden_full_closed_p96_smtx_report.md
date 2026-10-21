# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 890, unique setups 452, simulated 452. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 48% / 1.87 / +24.4 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & smt | OOS | 37 | 57% / 2.51 / +24.1 | 11% / 0.24 / -25.0 | reversal |
| shift>=2 & cont | IS | 64 | 50% / 1.96 / +30.8 | 16% / 0.37 / -34.0 | reversal |
| shift>=2 & cont | OOS | 55 | 47% / 1.77 / +21.8 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 8 | 75% / 6.00 / +10.0 | 12% / 0.29 / -5.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.33 / +14.0 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | IS | 94 | 49% / 1.87 / +41.7 | 15% / 0.35 / -52.0 | reversal |
| shift<2 | OOS | 92 | 52% / 2.10 / +47.2 | 22% / 0.56 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

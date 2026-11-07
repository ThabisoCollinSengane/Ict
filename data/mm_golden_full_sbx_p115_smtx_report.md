# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 887, unique setups 448, simulated 448. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 54 | 50% / 1.96 / +25.1 | 9% / 0.20 / -39.0 | reversal |
| shift>=2 & smt | OOS | 34 | 53% / 2.25 / +20.0 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | IS | 65 | 45% / 1.58 / +20.8 | 15% / 0.36 / -35.0 | reversal |
| shift>=2 & cont | OOS | 56 | 52% / 2.13 / +29.8 | 14% / 0.33 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 21 | 57% / 2.45 / +13.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.33 / +14.0 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | IS | 95 | 51% / 1.99 / +46.7 | 14% / 0.32 / -56.0 | reversal |
| shift<2 | OOS | 89 | 52% / 2.06 / +44.4 | 18% / 0.44 / -41.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

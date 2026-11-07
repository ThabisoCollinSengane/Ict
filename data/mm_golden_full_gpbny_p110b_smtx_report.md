# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 702, unique setups 359, simulated 359. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 43 | 58% / 2.62 / +29.2 | 9% / 0.21 / -31.0 | reversal |
| shift>=2 & smt | OOS | 31 | 55% / 2.43 / +20.0 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & cont | IS | 43 | 51% / 2.04 / +21.8 | 14% / 0.32 / -25.0 | reversal |
| shift>=2 & cont | OOS | 43 | 60% / 3.02 / +33.6 | 14% / 0.32 / -25.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 6 | 67% / 4.00 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 18 | 56% / 2.35 / +10.8 | 11% / 0.25 / -12.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 3.20 / +11.0 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 73 | 51% / 1.99 / +35.7 | 15% / 0.35 / -40.0 | reversal |
| shift<2 | OOS | 80 | 50% / 1.96 / +37.2 | 20% / 0.50 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

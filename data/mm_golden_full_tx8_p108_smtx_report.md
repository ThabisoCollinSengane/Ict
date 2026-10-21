# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 908, unique setups 457, simulated 457. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 48% / 1.82 / +23.1 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & smt | OOS | 36 | 56% / 2.38 / +22.1 | 14% / 0.32 / -21.0 | reversal |
| shift>=2 & cont | IS | 67 | 46% / 1.69 / +24.8 | 15% / 0.35 / -37.0 | reversal |
| shift>=2 & cont | OOS | 58 | 52% / 2.12 / +30.8 | 14% / 0.32 / -34.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 19 | 58% / 2.51 / +12.1 | 16% / 0.38 / -10.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 95 | 52% / 2.08 / +49.7 | 14% / 0.32 / -56.0 | reversal |
| shift<2 | OOS | 94 | 51% / 2.01 / +45.4 | 20% / 0.51 / -37.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

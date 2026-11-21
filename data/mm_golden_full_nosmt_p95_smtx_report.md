# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 1073, unique setups 520, simulated 520. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 58 | 50% / 1.96 / +27.1 | 12% / 0.27 / -37.0 | reversal |
| shift>=2 & smt | OOS | 40 | 48% / 1.72 / +15.1 | 12% / 0.29 / -25.0 | reversal |
| shift>=2 & cont | IS | 79 | 47% / 1.70 / +29.5 | 16% / 0.39 / -40.0 | reversal |
| shift>=2 & cont | OOS | 67 | 49% / 1.92 / +30.8 | 13% / 0.31 / -40.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 50% / 2.00 / +5.0 | continuation |
| shift>=2 & none | OOS | 10 | 30% / 0.86 / -1.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & noref | IS | 22 | 68% / 4.01 / +21.1 | 14% / 0.32 / -13.0 | reversal |
| shift>=2 & noref | OOS | 20 | 55% / 2.44 / +13.0 | 5% / 0.11 / -17.0 | reversal |
| shift<2 | IS | 105 | 52% / 2.15 / +57.7 | 15% / 0.36 / -57.0 | reversal |
| shift<2 | OOS | 109 | 54% / 2.30 / +63.4 | 20% / 0.51 / -43.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

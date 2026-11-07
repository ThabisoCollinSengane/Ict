# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 780, unique setups 398, simulated 398. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 50 | 54% / 2.31 / +29.1 | 10% / 0.22 / -35.0 | reversal |
| shift>=2 & smt | OOS | 33 | 58% / 2.58 / +22.1 | 12% / 0.28 / -21.0 | reversal |
| shift>=2 & cont | IS | 55 | 44% / 1.55 / +17.0 | 16% / 0.39 / -28.0 | reversal |
| shift>=2 & cont | OOS | 48 | 58% / 2.79 / +34.8 | 10% / 0.23 / -33.0 | reversal |
| shift>=2 & none | IS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 19 | 58% / 2.53 / +12.3 | 11% / 0.24 / -13.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 76 | 47% / 1.74 / +29.7 | 14% / 0.34 / -43.0 | reversal |
| shift<2 | OOS | 88 | 51% / 2.01 / +42.4 | 20% / 0.51 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

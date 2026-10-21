# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 767, unique setups 394, simulated 394. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 13% / 0.31 / -27.0 | reversal |
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | IS | 55 | 44% / 1.55 / +17.0 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & cont | OOS | 47 | 57% / 2.69 / +32.8 | 11% / 0.24 / -32.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 19 | 63% / 3.18 / +15.3 | 11% / 0.24 / -13.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 79 | 47% / 1.71 / +29.7 | 14% / 0.32 / -46.0 | reversal |
| shift<2 | OOS | 88 | 51% / 2.01 / +42.4 | 20% / 0.51 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

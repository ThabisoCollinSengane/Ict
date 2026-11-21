# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 629, unique setups 319, simulated 319. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 43 | 56% / 2.49 / +27.1 | 7% / 0.15 / -34.0 | reversal |
| shift>=2 & smt | OOS | 26 | 54% / 2.18 / +14.1 | 19% / 0.48 / -11.0 | reversal |
| shift>=2 & cont | IS | 47 | 47% / 1.71 / +17.8 | 15% / 0.35 / -26.0 | reversal |
| shift>=2 & cont | OOS | 39 | 59% / 2.83 / +28.6 | 15% / 0.36 / -21.0 | reversal |
| shift>=2 & none | IS | 5 | 40% / 1.33 / +1.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & none | OOS | 6 | 67% / 4.00 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 13 | 62% / 2.96 / +9.8 | 8% / 0.17 / -10.0 | reversal |
| shift>=2 & noref | OOS | 10 | 50% / 2.00 / +5.0 | 10% / 0.22 / -7.0 | reversal |
| shift<2 | IS | 57 | 49% / 1.88 / +25.6 | 12% / 0.28 / -36.0 | reversal |
| shift<2 | OOS | 73 | 51% / 1.98 / +34.6 | 19% / 0.47 / -31.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

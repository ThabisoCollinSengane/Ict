# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 833, unique setups 456, simulated 456. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 50 | 52% / 2.05 / +25.2 | 8% / 0.17 / -38.0 | reversal |
| shift>=2 & smt | OOS | 34 | 47% / 1.64 / +11.5 | 18% / 0.43 / -16.0 | reversal |
| shift>=2 & cont | IS | 65 | 45% / 1.58 / +20.8 | 15% / 0.36 / -35.0 | reversal |
| shift>=2 & cont | OOS | 64 | 48% / 1.88 / +28.2 | 11% / 0.25 / -43.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 60% / 3.00 / +8.0 | continuation |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | IS | 15 | 40% / 1.39 / +3.2 | 13% / 0.31 / -9.0 | reversal |
| shift>=2 & noref | OOS | 22 | 59% / 2.89 / +17.0 | 18% / 0.44 / -10.0 | reversal |
| shift<2 | IS | 96 | 50% / 1.95 / +45.7 | 15% / 0.34 / -54.0 | reversal |
| shift<2 | OOS | 91 | 55% / 2.35 / +54.4 | 20% / 0.49 / -37.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

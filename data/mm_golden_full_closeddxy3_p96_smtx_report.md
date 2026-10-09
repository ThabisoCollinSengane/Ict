# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 959, unique setups 480, simulated 480. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 50% / 2.01 / +27.4 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & smt | OOS | 41 | 54% / 2.22 / +23.1 | 15% / 0.34 / -23.0 | reversal |
| shift>=2 & cont | IS | 68 | 49% / 1.85 / +29.8 | 18% / 0.43 / -32.0 | reversal |
| shift>=2 & cont | OOS | 62 | 47% / 1.73 / +23.8 | 13% / 0.30 / -38.0 | reversal |
| shift>=2 & none | IS | 9 | 44% / 1.60 / +3.0 | 44% / 1.60 / +3.0 | continuation |
| shift>=2 & none | OOS | 6 | 67% / 4.00 / +6.0 | 17% / 0.40 / -3.0 | reversal |
| shift>=2 & noref | IS | 25 | 60% / 2.81 / +18.1 | 12% / 0.27 / -16.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.67 / +16.0 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | IS | 96 | 50% / 1.95 / +45.7 | 15% / 0.34 / -54.0 | reversal |
| shift<2 | OOS | 100 | 50% / 1.93 / +45.2 | 22% / 0.56 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 499, unique setups 253, simulated 253. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 47% / 1.75 / +21.1 | 13% / 0.29 / -34.0 | reversal |
| shift>=2 & cont | IS | 69 | 48% / 1.80 / +28.8 | 16% / 0.38 / -36.0 | reversal |
| shift>=2 & none | IS | 10 | 30% / 0.86 / -1.0 | 60% / 3.00 / +8.0 | continuation |
| shift>=2 & noref | IS | 19 | 63% / 3.15 / +15.1 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 100 | 51% / 2.04 / +50.7 | 13% / 0.30 / -61.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

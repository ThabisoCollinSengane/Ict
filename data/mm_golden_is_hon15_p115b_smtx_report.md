# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 426, unique setups 236, simulated 236. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 50 | 52% / 2.05 / +25.2 | 8% / 0.17 / -38.0 | reversal |
| shift>=2 & cont | IS | 65 | 45% / 1.58 / +20.8 | 15% / 0.36 / -35.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 60% / 3.00 / +8.0 | continuation |
| shift>=2 & noref | IS | 15 | 40% / 1.39 / +3.2 | 13% / 0.31 / -9.0 | reversal |
| shift<2 | IS | 96 | 50% / 1.95 / +45.7 | 15% / 0.34 / -54.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

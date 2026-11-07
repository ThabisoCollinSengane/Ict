# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 525, unique setups 257, simulated 257. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 55% / 2.40 / +30.7 | 10% / 0.23 / -34.0 | reversal |
| shift>=2 & cont | IS | 66 | 48% / 1.85 / +28.8 | 17% / 0.40 / -33.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & noref | IS | 16 | 69% / 4.01 / +15.1 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | IS | 119 | 54% / 2.31 / +70.8 | 14% / 0.33 / -68.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

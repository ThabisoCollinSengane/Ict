# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 541, unique setups 264, simulated 264. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 51 | 53% / 2.20 / +28.7 | 10% / 0.22 / -36.0 | reversal |
| shift>=2 & cont | IS | 67 | 48% / 1.79 / +27.8 | 16% / 0.39 / -34.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & noref | IS | 17 | 71% / 4.41 / +17.1 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | IS | 122 | 52% / 2.19 / +67.8 | 14% / 0.32 / -71.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

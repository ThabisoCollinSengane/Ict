# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 428, unique setups 219, simulated 219. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 47 | 55% / 2.35 / +28.2 | 11% / 0.24 / -32.0 | reversal |
| shift>=2 & cont | IS | 57 | 47% / 1.76 / +22.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 19 | 63% / 3.15 / +15.1 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 88 | 51% / 2.04 / +44.7 | 10% / 0.23 / -61.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

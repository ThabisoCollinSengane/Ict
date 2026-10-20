# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 458, unique setups 267, simulated 267. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 52 | 40% / 1.29 / +9.1 | 15% / 0.36 / -28.0 | reversal |
| shift>=2 & cont | IS | 71 | 44% / 1.52 / +20.8 | 21% / 0.54 / -26.0 | reversal |
| shift>=2 & none | IS | 5 | 80% / 8.00 / +7.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & noref | IS | 31 | 55% / 2.43 / +20.0 | 16% / 0.38 / -16.0 | reversal |
| shift<2 | IS | 108 | 43% / 1.46 / +28.4 | 15% / 0.35 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

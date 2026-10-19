# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 398, unique setups 204, simulated 204. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 13% / 0.31 / -27.0 | reversal |
| shift>=2 & cont | IS | 55 | 44% / 1.55 / +17.0 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 19 | 63% / 3.18 / +15.3 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 79 | 47% / 1.71 / +29.7 | 14% / 0.32 / -46.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

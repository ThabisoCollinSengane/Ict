# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 411, unique setups 207, simulated 207. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 50 | 54% / 2.31 / +29.1 | 10% / 0.22 / -35.0 | reversal |
| shift>=2 & cont | IS | 55 | 44% / 1.55 / +17.0 | 16% / 0.39 / -28.0 | reversal |
| shift>=2 & none | IS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & noref | IS | 19 | 58% / 2.53 / +12.3 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 76 | 47% / 1.74 / +29.7 | 14% / 0.34 / -43.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

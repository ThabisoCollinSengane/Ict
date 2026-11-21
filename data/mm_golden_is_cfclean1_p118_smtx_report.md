# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 65, unique setups 42, simulated 42. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 7 | 14% / 0.01 / -5.9 | 14% / 0.33 / -4.0 | continuation |
| shift>=2 & cont | IS | 9 | 44% / 1.36 / +1.8 | 11% / 0.25 / -6.0 | reversal |
| shift>=2 & noref | IS | 7 | 43% / 1.50 / +2.0 | 0% / 0.00 / -7.0 | reversal |
| shift<2 | IS | 19 | 63% / 3.43 / +17.0 | 11% / 0.24 / -13.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

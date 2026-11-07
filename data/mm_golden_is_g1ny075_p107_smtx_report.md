# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 402, unique setups 202, simulated 202. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 43 | 63% / 3.20 / +35.2 | 5% / 0.10 / -37.0 | reversal |
| shift>=2 & cont | IS | 53 | 49% / 1.88 / +23.8 | 11% / 0.26 / -35.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 62% / 3.33 / +7.0 | continuation |
| shift>=2 & noref | IS | 16 | 62% / 3.05 / +12.3 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | IS | 82 | 52% / 2.17 / +45.6 | 13% / 0.31 / -49.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

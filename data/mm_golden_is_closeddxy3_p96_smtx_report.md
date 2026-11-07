# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 529, unique setups 254, simulated 254. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 56 | 50% / 2.01 / +27.4 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & cont | IS | 68 | 49% / 1.85 / +29.8 | 18% / 0.43 / -32.0 | reversal |
| shift>=2 & none | IS | 9 | 44% / 1.60 / +3.0 | 44% / 1.60 / +3.0 | continuation |
| shift>=2 & noref | IS | 25 | 60% / 2.81 / +18.1 | 12% / 0.27 / -16.0 | reversal |
| shift<2 | IS | 96 | 50% / 1.95 / +45.7 | 15% / 0.34 / -54.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

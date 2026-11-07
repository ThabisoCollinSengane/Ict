# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 420, unique setups 218, simulated 218. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 47 | 53% / 2.23 / +26.1 | 9% / 0.19 / -35.0 | reversal |
| shift>=2 & cont | IS | 61 | 43% / 1.45 / +15.8 | 16% / 0.39 / -31.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 19 | 63% / 3.15 / +15.1 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 83 | 47% / 1.75 / +33.2 | 13% / 0.31 / -50.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

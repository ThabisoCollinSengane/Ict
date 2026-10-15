# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 403, unique setups 207, simulated 207. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 46 | 57% / 2.57 / +30.1 | 9% / 0.19 / -34.0 | reversal |
| shift>=2 & cont | IS | 55 | 42% / 1.40 / +12.8 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & none | IS | 7 | 43% / 1.50 / +2.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & noref | IS | 19 | 63% / 3.18 / +15.3 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 80 | 49% / 1.85 / +34.7 | 12% / 0.29 / -50.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

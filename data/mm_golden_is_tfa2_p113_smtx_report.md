# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 449, unique setups 226, simulated 226. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 55% / 2.33 / +29.2 | 12% / 0.28 / -31.0 | reversal |
| shift>=2 & cont | IS | 61 | 46% / 1.66 / +21.8 | 16% / 0.39 / -31.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 19 | 63% / 3.18 / +15.3 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | IS | 89 | 51% / 1.99 / +43.7 | 10% / 0.23 / -62.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

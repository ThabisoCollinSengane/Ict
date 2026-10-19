# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 849, unique setups 426, simulated 426. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 55% / 2.33 / +29.2 | 12% / 0.28 / -31.0 | reversal |
| shift>=2 & smt | OOS | 34 | 53% / 2.25 / +20.0 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | IS | 61 | 46% / 1.66 / +21.8 | 16% / 0.39 / -31.0 | reversal |
| shift>=2 & cont | OOS | 57 | 53% / 2.20 / +31.8 | 14% / 0.33 / -33.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 12% / 0.29 / -5.0 | reversal |
| shift>=2 & noref | IS | 19 | 63% / 3.18 / +15.3 | 11% / 0.24 / -13.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 3.20 / +11.0 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 89 | 51% / 1.99 / +43.7 | 10% / 0.23 / -62.0 | reversal |
| shift<2 | OOS | 88 | 55% / 2.28 / +49.7 | 19% / 0.48 / -37.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

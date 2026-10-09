# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 988, unique setups 481, simulated 481. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 52 | 54% / 2.28 / +30.7 | 10% / 0.21 / -37.0 | reversal |
| shift>=2 & smt | OOS | 30 | 60% / 2.84 / +22.1 | 13% / 0.31 / -18.0 | reversal |
| shift>=2 & cont | IS | 67 | 48% / 1.79 / +27.8 | 16% / 0.39 / -34.0 | reversal |
| shift>=2 & cont | OOS | 56 | 54% / 2.26 / +32.5 | 16% / 0.38 / -29.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 57% / 2.67 / +5.0 | continuation |
| shift>=2 & none | OOS | 5 | 40% / 1.33 / +1.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & noref | IS | 17 | 71% / 4.41 / +17.1 | 6% / 0.12 / -14.0 | reversal |
| shift>=2 & noref | OOS | 11 | 55% / 2.40 / +7.0 | 0% / 0.00 / -11.0 | reversal |
| shift<2 | IS | 122 | 52% / 2.19 / +67.8 | 14% / 0.32 / -71.0 | reversal |
| shift<2 | OOS | 114 | 57% / 2.60 / +75.8 | 18% / 0.45 / -51.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 350, unique setups 185, simulated 185. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 55% / 2.29 / +18.1 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & cont | OOS | 46 | 54% / 2.32 / +27.5 | 13% / 0.30 / -28.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 18 | 61% / 3.23 / +14.2 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | OOS | 82 | 48% / 1.78 / +33.3 | 22% / 0.56 / -28.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

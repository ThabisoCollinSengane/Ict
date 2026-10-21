# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 420, unique setups 207, simulated 207. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 29 | 62% / 3.10 / +23.1 | 14% / 0.32 / -17.0 | reversal |
| shift>=2 & cont | OOS | 53 | 55% / 2.36 / +32.5 | 15% / 0.36 / -29.0 | reversal |
| shift>=2 & none | OOS | 5 | 40% / 1.33 / +1.0 | 0% / 0.00 / -5.0 | reversal |
| shift>=2 & noref | OOS | 13 | 46% / 1.88 / +5.6 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | OOS | 107 | 59% / 2.71 / +75.1 | 17% / 0.40 / -53.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

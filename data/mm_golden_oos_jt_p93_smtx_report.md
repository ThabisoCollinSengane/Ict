# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 419, unique setups 207, simulated 207. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 29 | 62% / 3.10 / +23.1 | 14% / 0.32 / -17.0 | reversal |
| shift>=2 & cont | OOS | 52 | 54% / 2.28 / +30.5 | 17% / 0.42 / -25.0 | reversal |
| shift>=2 & none | OOS | 6 | 33% / 1.00 / +0.0 | 17% / 0.40 / -3.0 | reversal |
| shift>=2 & noref | OOS | 12 | 50% / 2.23 / +6.6 | 0% / 0.00 / -12.0 | reversal |
| shift<2 | OOS | 108 | 57% / 2.55 / +71.1 | 19% / 0.45 / -48.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

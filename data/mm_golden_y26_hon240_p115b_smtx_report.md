# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 167, unique setups 81, simulated 81. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 15 | 40% / 1.33 / +3.0 | 20% / 0.50 / -6.0 | reversal |
| shift>=2 & cont | OOS | 9 | 22% / 0.57 / -3.0 | 11% / 0.25 / -6.0 | reversal |
| shift>=2 & none | OOS | 8 | 38% / 1.35 / +1.6 | 0% / 0.00 / -8.0 | reversal |
| shift>=2 & noref | OOS | 15 | 33% / 1.00 / +0.0 | 20% / 0.50 / -6.0 | reversal |
| shift<2 | OOS | 34 | 38% / 1.12 / +2.5 | 26% / 0.72 / -7.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

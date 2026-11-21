# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 177, unique setups 99, simulated 99. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 16 | 38% / 1.02 / +0.2 | 19% / 0.46 / -7.0 | reversal |
| shift>=2 & cont | OOS | 25 | 32% / 0.99 / -0.2 | 12% / 0.27 / -16.0 | reversal |
| shift>=2 & none | OOS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | OOS | 11 | 36% / 1.26 / +1.6 | 0% / 0.00 / -11.0 | reversal |
| shift<2 | OOS | 41 | 44% / 1.39 / +9.0 | 17% / 0.35 / -22.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

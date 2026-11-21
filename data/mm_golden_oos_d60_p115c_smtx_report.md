# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 451, unique setups 236, simulated 236. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 43 | 56% / 2.53 / +29.0 | 19% / 0.46 / -19.0 | reversal |
| shift>=2 & cont | OOS | 60 | 42% / 1.46 / +15.6 | 20% / 0.50 / -24.0 | reversal |
| shift>=2 & none | OOS | 15 | 47% / 1.91 / +6.7 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | OOS | 19 | 47% / 1.77 / +7.2 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | OOS | 99 | 46% / 1.66 / +34.0 | 17% / 0.41 / -48.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

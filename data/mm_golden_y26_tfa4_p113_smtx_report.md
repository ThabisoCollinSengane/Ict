# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 177, unique setups 96, simulated 96. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 16 | 44% / 1.39 / +3.5 | 12% / 0.29 / -10.0 | reversal |
| shift>=2 & cont | OOS | 16 | 25% / 0.67 / -4.0 | 12% / 0.29 / -10.0 | reversal |
| shift>=2 & none | OOS | 8 | 38% / 1.04 / +0.2 | 0% / 0.00 / -8.0 | reversal |
| shift>=2 & noref | OOS | 15 | 53% / 2.63 / +9.9 | 13% / 0.31 / -9.0 | reversal |
| shift<2 | OOS | 41 | 51% / 1.97 / +19.5 | 15% / 0.34 / -23.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

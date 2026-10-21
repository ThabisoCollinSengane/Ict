# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 207, unique setups 106, simulated 106. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 22 | 59% / 2.89 / +17.0 | 14% / 0.32 / -13.0 | reversal |
| shift>=2 & cont | OOS | 31 | 68% / 4.28 / +32.2 | 10% / 0.21 / -22.0 | reversal |
| shift>=2 & none | OOS | 4 | 50% / 2.00 / +2.0 | 25% / 0.67 / -1.0 | reversal |
| shift>=2 & noref | OOS | 8 | 75% / 6.00 / +10.0 | 0% / 0.00 / -8.0 | reversal |
| shift<2 | OOS | 41 | 51% / 2.00 / +19.5 | 24% / 0.65 / -11.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

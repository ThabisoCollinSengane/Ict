# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 354, unique setups 217, simulated 217. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 45 | 42% / 1.28 / +7.2 | 16% / 0.37 / -24.0 | reversal |
| shift>=2 & cont | OOS | 57 | 37% / 1.22 / +7.6 | 18% / 0.43 / -27.0 | reversal |
| shift>=2 & none | OOS | 12 | 33% / 1.00 / +0.0 | 25% / 0.67 / -3.0 | reversal |
| shift>=2 & noref | OOS | 24 | 50% / 2.01 / +11.5 | 4% / 0.09 / -21.0 | reversal |
| shift<2 | OOS | 79 | 38% / 1.12 / +5.7 | 15% / 0.33 / -45.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

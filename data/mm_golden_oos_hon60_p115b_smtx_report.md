# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 138, unique setups 79, simulated 79. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 10 | 60% / 3.00 / +8.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & cont | OOS | 20 | 35% / 0.94 / -0.7 | 25% / 0.67 / -5.0 | reversal |
| shift>=2 & none | OOS | 6 | 67% / 4.00 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | OOS | 9 | 56% / 2.97 / +6.6 | 11% / 0.25 / -6.0 | reversal |
| shift<2 | OOS | 34 | 47% / 1.69 / +11.9 | 15% / 0.34 / -19.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

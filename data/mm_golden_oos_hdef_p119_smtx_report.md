# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 231, unique setups 132, simulated 132. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 21 | 38% / 0.95 / -0.7 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & cont | OOS | 34 | 32% / 1.01 / +0.2 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & none | OOS | 8 | 38% / 1.20 / +1.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 13 | 31% / 0.96 / -0.4 | 0% / 0.00 / -13.0 | reversal |
| shift<2 | OOS | 56 | 39% / 1.18 / +6.0 | 18% / 0.39 / -28.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

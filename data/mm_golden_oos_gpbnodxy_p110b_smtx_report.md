# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 345, unique setups 178, simulated 178. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 55% / 2.29 / +18.1 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & cont | OOS | 39 | 56% / 2.49 / +25.3 | 15% / 0.36 / -21.0 | reversal |
| shift>=2 & none | OOS | 9 | 67% / 4.00 / +9.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 16 | 56% / 2.83 / +11.6 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | OOS | 83 | 48% / 1.81 / +34.8 | 20% / 0.52 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

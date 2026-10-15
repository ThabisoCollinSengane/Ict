# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 328, unique setups 168, simulated 168. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 25 | 52% / 2.01 / +12.1 | 16% / 0.38 / -13.0 | reversal |
| shift>=2 & cont | OOS | 39 | 56% / 2.49 / +25.3 | 13% / 0.29 / -24.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 16 | 56% / 2.83 / +11.6 | 12% / 0.29 / -10.0 | reversal |
| shift<2 | OOS | 79 | 49% / 1.89 / +35.8 | 20% / 0.51 / -31.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

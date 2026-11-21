# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 369, unique setups 193, simulated 193. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 60% / 2.86 / +26.1 | 11% / 0.26 / -23.0 | reversal |
| shift>=2 & cont | OOS | 44 | 59% / 2.87 / +32.7 | 11% / 0.26 / -29.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 22% / 0.57 / -3.0 | reversal |
| shift>=2 & noref | OOS | 20 | 60% / 3.06 / +15.2 | 10% / 0.22 / -14.0 | reversal |
| shift<2 | OOS | 85 | 49% / 1.84 / +35.7 | 22% / 0.58 / -28.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

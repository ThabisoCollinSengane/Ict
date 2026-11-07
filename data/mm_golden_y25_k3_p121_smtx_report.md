# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 90, unique setups 56, simulated 56. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 16 | 44% / 1.56 / +5.0 | 25% / 0.67 / -4.0 | reversal |
| shift>=2 & cont | OOS | 18 | 56% / 2.50 / +12.0 | 17% / 0.40 / -9.0 | reversal |
| shift>=2 & none | OOS | 2 | 0% / 0.00 / -2.0 | 50% / 2.00 / +1.0 | continuation |
| shift>=2 & noref | OOS | 7 | 71% / 5.00 / +8.0 | 14% / 0.33 / -4.0 | reversal |
| shift<2 | OOS | 13 | 38% / 0.88 / -0.9 | 15% / 0.36 / -7.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

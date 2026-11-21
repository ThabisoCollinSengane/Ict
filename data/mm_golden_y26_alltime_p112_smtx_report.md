# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 166, unique setups 89, simulated 89. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 15 | 40% / 1.16 / +1.5 | 13% / 0.31 / -9.0 | reversal |
| shift>=2 & cont | OOS | 14 | 29% / 0.80 / -2.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 6 | 33% / 1.17 / +0.6 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 40 | 52% / 2.08 / +20.5 | 15% / 0.35 / -22.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

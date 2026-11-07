# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 419, unique setups 222, simulated 222. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 36 | 56% / 2.38 / +22.1 | 19% / 0.48 / -15.0 | reversal |
| shift>=2 & cont | OOS | 60 | 52% / 2.03 / +29.7 | 20% / 0.50 / -24.0 | reversal |
| shift>=2 & none | OOS | 13 | 38% / 1.25 / +2.0 | 23% / 0.60 / -4.0 | reversal |
| shift>=2 & noref | OOS | 22 | 50% / 1.98 / +10.2 | 5% / 0.10 / -19.0 | reversal |
| shift<2 | OOS | 91 | 46% / 1.61 / +29.7 | 20% / 0.49 / -37.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

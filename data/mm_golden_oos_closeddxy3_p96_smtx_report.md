# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 407, unique setups 213, simulated 213. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 39 | 54% / 2.23 / +22.1 | 15% / 0.36 / -21.0 | reversal |
| shift>=2 & cont | OOS | 56 | 46% / 1.69 / +20.5 | 16% / 0.38 / -29.0 | reversal |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 18 | 67% / 4.49 / +17.5 | 6% / 0.12 / -15.0 | reversal |
| shift<2 | OOS | 92 | 50% / 1.89 / +40.5 | 23% / 0.59 / -29.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

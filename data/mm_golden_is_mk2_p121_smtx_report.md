# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 606, unique setups 303, simulated 303. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 60 | 35% / 1.03 / +1.1 | 17% / 0.40 / -30.0 | reversal |
| shift>=2 & cont | IS | 80 | 45% / 1.64 / +27.5 | 21% / 0.54 / -29.0 | reversal |
| shift>=2 & none | IS | 6 | 67% / 4.00 / +6.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 33 | 55% / 2.40 / +21.0 | 15% / 0.36 / -18.0 | reversal |
| shift<2 | IS | 124 | 47% / 1.73 / +48.4 | 15% / 0.34 / -70.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

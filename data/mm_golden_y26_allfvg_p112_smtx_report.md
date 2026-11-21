# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 152, unique setups 81, simulated 81. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 15 | 40% / 1.16 / +1.5 | 13% / 0.31 / -9.0 | reversal |
| shift>=2 & cont | OOS | 13 | 23% / 0.60 / -4.0 | 15% / 0.36 / -7.0 | reversal |
| shift>=2 & none | OOS | 6 | 33% / 1.17 / +0.6 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 12 | 50% / 2.37 / +6.9 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | OOS | 35 | 57% / 2.50 / +22.5 | 11% / 0.26 / -23.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

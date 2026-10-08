# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 405, unique setups 208, simulated 208. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 37 | 57% / 2.51 / +24.1 | 14% / 0.31 / -22.0 | reversal |
| shift>=2 & cont | OOS | 52 | 50% / 1.95 / +24.5 | 15% / 0.36 / -28.0 | reversal |
| shift>=2 & none | OOS | 11 | 45% / 1.67 / +4.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | OOS | 18 | 61% / 3.41 / +14.5 | 6% / 0.12 / -15.0 | reversal |
| shift<2 | OOS | 90 | 49% / 1.81 / +36.7 | 21% / 0.54 / -33.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

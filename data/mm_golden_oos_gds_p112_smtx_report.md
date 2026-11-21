# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 367, unique setups 192, simulated 192. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 55% / 2.29 / +18.1 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & cont | OOS | 46 | 52% / 2.12 / +24.5 | 15% / 0.36 / -25.0 | reversal |
| shift>=2 & none | OOS | 11 | 55% / 2.40 / +7.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | OOS | 18 | 61% / 3.23 / +14.2 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | OOS | 86 | 49% / 1.84 / +36.5 | 20% / 0.49 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

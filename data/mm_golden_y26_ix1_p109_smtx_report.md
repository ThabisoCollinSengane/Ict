# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 149, unique setups 80, simulated 80. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 10 | 50% / 1.69 / +3.5 | 0% / 0.00 / -10.0 | reversal |
| shift>=2 & cont | OOS | 14 | 21% / 0.55 / -5.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & none | OOS | 8 | 38% / 1.04 / +0.2 | 0% / 0.00 / -8.0 | reversal |
| shift>=2 & noref | OOS | 13 | 46% / 1.98 / +5.9 | 15% / 0.36 / -7.0 | reversal |
| shift<2 | OOS | 35 | 49% / 1.79 / +14.3 | 17% / 0.41 / -17.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

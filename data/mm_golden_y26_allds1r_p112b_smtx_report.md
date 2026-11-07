# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 149, unique setups 81, simulated 81. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 13 | 46% / 1.50 / +3.5 | 8% / 0.17 / -10.0 | reversal |
| shift>=2 & cont | OOS | 13 | 23% / 0.60 / -4.0 | 15% / 0.36 / -7.0 | reversal |
| shift>=2 & none | OOS | 7 | 43% / 1.34 / +1.2 | 0% / 0.00 / -7.0 | reversal |
| shift>=2 & noref | OOS | 13 | 46% / 1.98 / +5.9 | 15% / 0.36 / -7.0 | reversal |
| shift<2 | OOS | 35 | 54% / 2.22 / +19.5 | 14% / 0.33 / -20.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

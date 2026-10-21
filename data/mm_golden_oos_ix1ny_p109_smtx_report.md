# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 372, unique setups 195, simulated 195. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 57% / 2.54 / +23.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | OOS | 50 | 54% / 2.29 / +29.5 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 83 | 49% / 1.84 / +34.7 | 19% / 0.48 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

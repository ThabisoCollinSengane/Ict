# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 391, unique setups 203, simulated 203. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 54% / 2.26 / +20.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | OOS | 53 | 53% / 2.19 / +29.5 | 17% / 0.41 / -26.0 | reversal |
| shift>=2 & none | OOS | 11 | 45% / 1.67 / +4.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | OOS | 18 | 61% / 3.23 / +14.2 | 6% / 0.12 / -15.0 | reversal |
| shift<2 | OOS | 86 | 49% / 1.80 / +34.7 | 23% / 0.61 / -26.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

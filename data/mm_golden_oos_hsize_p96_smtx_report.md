# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 382, unique setups 198, simulated 198. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 57% / 2.54 / +23.1 | 14% / 0.33 / -20.0 | reversal |
| shift>=2 & cont | OOS | 51 | 53% / 2.20 / +28.5 | 16% / 0.37 / -27.0 | reversal |
| shift>=2 & none | OOS | 11 | 55% / 2.40 / +7.0 | 27% / 0.75 / -2.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 84 | 50% / 1.89 / +36.7 | 21% / 0.55 / -30.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

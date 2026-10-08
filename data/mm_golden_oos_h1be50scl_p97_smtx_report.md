# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 382, unique setups 198, simulated 198. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | OOS | 51 | 53% / 2.20 / +28.5 | 16% / 0.37 / -27.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & noref | OOS | 19 | 63% / 3.54 / +16.2 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | OOS | 85 | 51% / 1.93 / +38.7 | 21% / 0.54 / -31.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

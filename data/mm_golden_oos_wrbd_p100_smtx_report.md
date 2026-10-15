# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 392, unique setups 203, simulated 203. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 37 | 54% / 2.24 / +21.1 | 16% / 0.39 / -19.0 | reversal |
| shift>=2 & cont | OOS | 51 | 53% / 2.24 / +28.9 | 16% / 0.37 / -27.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & noref | OOS | 19 | 63% / 3.54 / +16.2 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | OOS | 86 | 50% / 1.89 / +37.7 | 21% / 0.53 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

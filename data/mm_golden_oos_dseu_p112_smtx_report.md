# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 329, unique setups 168, simulated 168. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 31 | 55% / 2.29 / +18.1 | 16% / 0.38 / -16.0 | reversal |
| shift>=2 & cont | OOS | 41 | 54% / 2.25 / +23.5 | 15% / 0.34 / -23.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.79 / +12.2 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | OOS | 72 | 47% / 1.74 / +28.2 | 24% / 0.62 / -21.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

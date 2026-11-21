# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 380, unique setups 192, simulated 192. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | OOS | 51 | 53% / 2.20 / +28.5 | 16% / 0.37 / -27.0 | reversal |
| shift>=2 & none | OOS | 9 | 56% / 2.50 / +6.0 | 11% / 0.25 / -6.0 | reversal |
| shift>=2 & noref | OOS | 15 | 60% / 3.09 / +11.2 | 0% / 0.00 / -15.0 | reversal |
| shift<2 | OOS | 84 | 52% / 2.08 / +42.7 | 20% / 0.51 / -33.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

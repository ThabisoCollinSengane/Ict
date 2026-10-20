# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 551, unique setups 272, simulated 272. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 53 | 34% / 0.97 / -0.9 | 17% / 0.41 / -26.0 | reversal |
| shift>=2 & cont | IS | 72 | 47% / 1.76 / +28.8 | 19% / 0.48 / -30.0 | reversal |
| shift>=2 & none | IS | 5 | 60% / 3.00 / +4.0 | 40% / 1.33 / +1.0 | reversal |
| shift>=2 & noref | IS | 32 | 56% / 2.57 / +22.0 | 16% / 0.37 / -17.0 | reversal |
| shift<2 | IS | 110 | 45% / 1.67 / +40.0 | 14% / 0.32 / -65.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

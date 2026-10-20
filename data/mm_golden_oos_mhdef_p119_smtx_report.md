# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 438, unique setups 275, simulated 275. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 52 | 44% / 1.42 / +12.2 | 19% / 0.48 / -22.0 | reversal |
| shift>=2 & cont | OOS | 76 | 39% / 1.35 / +15.6 | 16% / 0.38 / -40.0 | reversal |
| shift>=2 & none | OOS | 16 | 38% / 1.20 / +2.0 | 31% / 0.91 / -1.0 | reversal |
| shift>=2 & noref | OOS | 28 | 39% / 1.34 / +5.6 | 14% / 0.33 / -16.0 | reversal |
| shift<2 | OOS | 103 | 39% / 1.17 / +10.3 | 15% / 0.32 / -60.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

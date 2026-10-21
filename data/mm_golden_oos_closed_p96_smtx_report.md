# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 375, unique setups 195, simulated 195. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 35 | 57% / 2.54 / +23.1 | 11% / 0.26 / -23.0 | reversal |
| shift>=2 & cont | OOS | 50 | 48% / 1.79 / +20.5 | 18% / 0.44 / -23.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 12% / 0.29 / -5.0 | reversal |
| shift>=2 & noref | OOS | 16 | 69% / 4.11 / +15.6 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 86 | 51% / 1.98 / +40.5 | 23% / 0.61 / -26.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

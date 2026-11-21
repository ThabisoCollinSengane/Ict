# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 104, unique setups 59, simulated 59. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 12 | 58% / 2.54 / +7.7 | 0% / 0.00 / -12.0 | reversal |
| shift>=2 & cont | IS | 17 | 53% / 2.10 / +8.8 | 18% / 0.43 / -8.0 | reversal |
| shift>=2 & none | IS | 4 | 75% / 6.00 / +5.0 | 25% / 0.67 / -1.0 | reversal |
| shift>=2 & noref | IS | 5 | 60% / 3.00 / +4.0 | 20% / 0.50 / -2.0 | reversal |
| shift<2 | IS | 21 | 57% / 2.67 / +15.0 | 14% / 0.33 / -12.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

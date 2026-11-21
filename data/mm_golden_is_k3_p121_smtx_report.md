# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 157, unique setups 92, simulated 92. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 21 | 38% / 1.08 / +1.1 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & cont | IS | 21 | 52% / 2.08 / +10.8 | 14% / 0.33 / -12.0 | reversal |
| shift>=2 & none | IS | 4 | 75% / 6.00 / +5.0 | 25% / 0.67 / -1.0 | reversal |
| shift>=2 & noref | IS | 8 | 50% / 2.00 / +4.0 | 0% / 0.00 / -8.0 | reversal |
| shift<2 | IS | 38 | 55% / 2.47 / +25.0 | 5% / 0.11 / -32.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

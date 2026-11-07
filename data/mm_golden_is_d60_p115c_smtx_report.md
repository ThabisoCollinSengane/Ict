# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 473, unique setups 246, simulated 246. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 38 | 61% / 3.25 / +31.8 | 8% / 0.17 / -29.0 | reversal |
| shift>=2 & cont | IS | 73 | 47% / 1.71 / +27.8 | 21% / 0.52 / -28.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 17% / 0.40 / -3.0 | reversal |
| shift>=2 & noref | IS | 25 | 48% / 1.71 / +9.3 | 20% / 0.50 / -10.0 | reversal |
| shift<2 | IS | 104 | 43% / 1.53 / +31.0 | 12% / 0.29 / -65.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 509, unique setups 257, simulated 257. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 49% / 1.89 / +24.1 | 11% / 0.24 / -37.0 | reversal |
| shift>=2 & cont | IS | 69 | 49% / 1.91 / +31.8 | 14% / 0.34 / -39.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 50% / 2.00 / +5.0 | continuation |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 10% / 0.22 / -14.0 | reversal |
| shift<2 | IS | 103 | 50% / 1.99 / +50.7 | 13% / 0.29 / -64.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

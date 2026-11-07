# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 497, unique setups 252, simulated 252. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 54 | 50% / 1.96 / +25.1 | 13% / 0.30 / -33.0 | reversal |
| shift>=2 & cont | IS | 69 | 51% / 2.02 / +34.8 | 16% / 0.38 / -36.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & noref | IS | 20 | 60% / 2.78 / +14.3 | 10% / 0.22 / -14.0 | reversal |
| shift<2 | IS | 100 | 49% / 1.88 / +44.7 | 13% / 0.30 / -61.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 44, unique setups 29, simulated 29. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 6 | 17% / 0.40 / -3.0 | 17% / 0.40 / -3.0 | continuation |
| shift>=2 & cont | IS | 4 | 50% / 2.00 / +2.0 | 0% / 0.00 / -4.0 | reversal |
| shift>=2 & noref | IS | 4 | 75% / 6.00 / +5.0 | 25% / 0.67 / -1.0 | reversal |
| shift<2 | IS | 15 | 53% / 2.29 / +9.0 | 13% / 0.31 / -9.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

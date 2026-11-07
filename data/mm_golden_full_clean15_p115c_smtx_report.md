# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 60, unique setups 32, simulated 32. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 8 | 0% / 0.00 / -8.0 | 25% / 0.67 / -2.0 | continuation |
| shift>=2 & cont | IS | 5 | 40% / 1.33 / +1.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & noref | IS | 6 | 33% / 1.00 / +0.0 | 17% / 0.40 / -3.0 | reversal |
| shift<2 | IS | 13 | 54% / 2.33 / +8.0 | 15% / 0.36 / -7.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 53, unique setups 35, simulated 35. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 3 | 67% / 2.72 / +1.7 | 0% / 0.00 / -3.0 | reversal |
| shift>=2 & cont | IS | 9 | 67% / 4.00 / +9.0 | 11% / 0.25 / -6.0 | reversal |
| shift>=2 & none | IS | 2 | 50% / 2.00 / +1.0 | 50% / 2.00 / +1.0 | continuation |
| shift>=2 & noref | IS | 5 | 60% / 3.00 / +4.0 | 0% / 0.00 / -5.0 | reversal |
| shift<2 | IS | 16 | 69% / 4.40 / +17.0 | 19% / 0.46 / -7.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 60, unique setups 40, simulated 40. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 7 | 14% / 0.01 / -5.9 | 14% / 0.33 / -4.0 | continuation |
| shift>=2 & cont | IS | 9 | 44% / 1.60 / +3.0 | 11% / 0.25 / -6.0 | reversal |
| shift>=2 & noref | IS | 6 | 50% / 2.00 / +3.0 | 0% / 0.00 / -6.0 | reversal |
| shift<2 | IS | 18 | 67% / 4.00 / +18.0 | 11% / 0.25 / -12.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

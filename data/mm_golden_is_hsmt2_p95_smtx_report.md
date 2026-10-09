# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 385, unique setups 184, simulated 184. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 40 | 57% / 2.54 / +26.2 | 12% / 0.29 / -25.0 | reversal |
| shift>=2 & cont | IS | 47 | 43% / 1.39 / +10.5 | 19% / 0.47 / -20.0 | reversal |
| shift>=2 & none | IS | 5 | 20% / 0.50 / -2.0 | 40% / 1.33 / +1.0 | continuation |
| shift>=2 & noref | IS | 18 | 67% / 4.00 / +18.0 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | IS | 74 | 55% / 2.42 / +46.7 | 12% / 0.28 / -47.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

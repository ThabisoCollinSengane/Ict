# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 488, unique setups 258, simulated 258. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 49 | 55% / 2.49 / +31.6 | 10% / 0.23 / -34.0 | reversal |
| shift>=2 & cont | IS | 73 | 41% / 1.37 / +15.8 | 18% / 0.43 / -34.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & noref | IS | 28 | 50% / 1.99 / +12.9 | 14% / 0.33 / -16.0 | reversal |
| shift<2 | IS | 100 | 47% / 1.73 / +38.7 | 11% / 0.25 / -67.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

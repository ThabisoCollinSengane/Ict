# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 452, unique setups 260, simulated 260. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 50 | 42% / 1.38 / +11.1 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & cont | IS | 70 | 43% / 1.47 / +18.8 | 21% / 0.55 / -25.0 | reversal |
| shift>=2 & none | IS | 5 | 80% / 8.00 / +7.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & noref | IS | 30 | 53% / 2.29 / +18.0 | 17% / 0.40 / -15.0 | reversal |
| shift<2 | IS | 105 | 43% / 1.47 / +28.4 | 15% / 0.36 / -57.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

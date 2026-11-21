# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 458, unique setups 265, simulated 265. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 51 | 39% / 1.23 / +7.1 | 16% / 0.37 / -27.0 | reversal |
| shift>=2 & cont | IS | 71 | 42% / 1.43 / +17.8 | 21% / 0.54 / -26.0 | reversal |
| shift>=2 & none | IS | 5 | 80% / 8.00 / +7.0 | 20% / 0.50 / -2.0 | reversal |
| shift>=2 & noref | IS | 30 | 53% / 2.29 / +18.0 | 17% / 0.40 / -15.0 | reversal |
| shift<2 | IS | 108 | 44% / 1.57 / +34.4 | 16% / 0.37 / -57.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

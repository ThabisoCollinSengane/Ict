# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 701, unique setups 364, simulated 364. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.71 / +31.1 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & smt | OOS | 28 | 46% / 1.73 / +11.0 | 18% / 0.43 / -13.0 | reversal |
| shift>=2 & cont | IS | 54 | 41% / 1.38 / +12.0 | 15% / 0.35 / -30.0 | reversal |
| shift>=2 & cont | OOS | 42 | 60% / 2.93 / +31.8 | 10% / 0.21 / -30.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 16 | 69% / 4.05 / +15.3 | 12% / 0.29 / -10.0 | reversal |
| shift>=2 & noref | OOS | 10 | 60% / 3.00 / +8.0 | 0% / 0.00 / -10.0 | reversal |
| shift<2 | IS | 76 | 47% / 1.74 / +29.7 | 13% / 0.30 / -46.0 | reversal |
| shift<2 | OOS | 79 | 48% / 1.79 / +31.4 | 19% / 0.47 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

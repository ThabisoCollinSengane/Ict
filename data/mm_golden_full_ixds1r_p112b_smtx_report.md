# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 838, unique setups 420, simulated 420. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.59 / +30.2 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & smt | OOS | 34 | 53% / 2.13 / +18.1 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | IS | 59 | 42% / 1.44 / +14.8 | 15% / 0.36 / -32.0 | reversal |
| shift>=2 & cont | OOS | 56 | 54% / 2.29 / +32.8 | 12% / 0.29 / -35.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 19 | 58% / 2.51 / +12.1 | 16% / 0.38 / -10.0 | reversal |
| shift>=2 & noref | OOS | 13 | 62% / 3.20 / +11.0 | 8% / 0.17 / -10.0 | reversal |
| shift<2 | IS | 91 | 52% / 2.08 / +47.7 | 12% / 0.28 / -58.0 | reversal |
| shift<2 | OOS | 86 | 52% / 2.12 / +44.4 | 19% / 0.46 / -38.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

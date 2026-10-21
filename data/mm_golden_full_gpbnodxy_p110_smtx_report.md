# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 721, unique setups 366, simulated 366. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 47 | 53% / 2.15 / +25.2 | 11% / 0.24 / -32.0 | reversal |
| shift>=2 & smt | OOS | 28 | 50% / 1.86 / +12.1 | 18% / 0.43 / -13.0 | reversal |
| shift>=2 & cont | IS | 49 | 51% / 2.03 / +24.8 | 12% / 0.28 / -31.0 | reversal |
| shift>=2 & cont | OOS | 44 | 52% / 2.14 / +23.6 | 14% / 0.32 / -26.0 | reversal |
| shift>=2 & none | IS | 9 | 33% / 1.00 / +0.0 | 56% / 2.50 / +6.0 | continuation |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 19 | 58% / 2.53 / +12.3 | 11% / 0.24 / -13.0 | reversal |
| shift>=2 & noref | OOS | 12 | 58% / 2.80 / +9.0 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | IS | 78 | 53% / 2.15 / +42.7 | 14% / 0.33 / -45.0 | reversal |
| shift<2 | OOS | 72 | 46% / 1.69 / +26.0 | 22% / 0.57 / -24.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

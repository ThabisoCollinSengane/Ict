# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 860, unique setups 459, simulated 459. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 54 | 50% / 1.95 / +25.5 | 19% / 0.45 / -24.0 | reversal |
| shift>=2 & smt | OOS | 49 | 37% / 1.16 / +5.0 | 22% / 0.58 / -16.0 | reversal |
| shift>=2 & cont | IS | 63 | 46% / 1.67 / +22.8 | 19% / 0.47 / -27.0 | reversal |
| shift>=2 & cont | OOS | 55 | 47% / 1.78 / +22.0 | 15% / 0.34 / -31.0 | reversal |
| shift>=2 & none | IS | 7 | 29% / 0.80 / -1.0 | 43% / 1.50 / +2.0 | continuation |
| shift>=2 & none | OOS | 13 | 31% / 0.89 / -1.0 | 31% / 0.89 / -1.0 | continuation |
| shift>=2 & noref | IS | 22 | 55% / 2.28 / +12.8 | 18% / 0.44 / -10.0 | reversal |
| shift>=2 & noref | OOS | 20 | 50% / 2.00 / +10.0 | 10% / 0.22 / -14.0 | reversal |
| shift<2 | IS | 97 | 47% / 1.75 / +38.5 | 15% / 0.37 / -52.0 | reversal |
| shift<2 | OOS | 79 | 47% / 1.69 / +27.4 | 16% / 0.39 / -40.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

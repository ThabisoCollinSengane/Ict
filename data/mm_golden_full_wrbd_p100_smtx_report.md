# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 936, unique setups 474, simulated 474. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 55 | 49% / 1.89 / +24.1 | 11% / 0.24 / -37.0 | reversal |
| shift>=2 & smt | OOS | 39 | 54% / 2.23 / +22.1 | 15% / 0.36 / -21.0 | reversal |
| shift>=2 & cont | IS | 69 | 49% / 1.91 / +31.8 | 14% / 0.34 / -39.0 | reversal |
| shift>=2 & cont | OOS | 58 | 53% / 2.31 / +34.2 | 14% / 0.32 / -34.0 | reversal |
| shift>=2 & none | IS | 10 | 40% / 1.33 / +2.0 | 50% / 2.00 / +5.0 | continuation |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 10% / 0.22 / -14.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.39 / +14.4 | 12% / 0.27 / -11.0 | reversal |
| shift<2 | IS | 103 | 50% / 1.99 / +50.7 | 13% / 0.29 / -64.0 | reversal |
| shift<2 | OOS | 93 | 52% / 2.06 / +46.4 | 20% / 0.51 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

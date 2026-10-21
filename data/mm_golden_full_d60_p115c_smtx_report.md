# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 961, unique setups 498, simulated 498. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 38 | 61% / 3.25 / +31.8 | 8% / 0.17 / -29.0 | reversal |
| shift>=2 & smt | OOS | 49 | 53% / 2.26 / +29.0 | 20% / 0.51 / -19.0 | reversal |
| shift>=2 & cont | IS | 73 | 47% / 1.71 / +27.8 | 21% / 0.52 / -28.0 | reversal |
| shift>=2 & cont | OOS | 65 | 45% / 1.67 / +22.9 | 18% / 0.45 / -29.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 17% / 0.40 / -3.0 | reversal |
| shift>=2 & none | OOS | 17 | 47% / 1.92 / +7.7 | 35% / 1.09 / +1.0 | reversal |
| shift>=2 & noref | IS | 25 | 48% / 1.71 / +9.3 | 20% / 0.50 / -10.0 | reversal |
| shift>=2 & noref | OOS | 17 | 47% / 1.78 / +7.0 | 12% / 0.27 / -11.0 | reversal |
| shift<2 | IS | 104 | 43% / 1.53 / +31.0 | 12% / 0.29 / -65.0 | reversal |
| shift<2 | OOS | 104 | 46% / 1.64 / +35.0 | 15% / 0.36 / -56.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

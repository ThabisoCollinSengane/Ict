# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 167, unique setups 91, simulated 91. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 19 | 47% / 1.65 / +6.5 | 5% / 0.11 / -16.0 | reversal |
| shift>=2 & cont | OOS | 17 | 18% / 0.43 / -8.0 | 18% / 0.43 / -8.0 | continuation |
| shift>=2 & none | OOS | 6 | 33% / 0.76 / -0.8 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 8 | 50% / 2.60 / +4.9 | 12% / 0.29 / -5.0 | reversal |
| shift<2 | OOS | 41 | 56% / 2.42 / +25.5 | 15% / 0.34 / -23.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

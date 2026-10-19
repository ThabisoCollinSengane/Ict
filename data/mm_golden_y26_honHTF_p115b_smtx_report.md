# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 105, unique setups 63, simulated 63. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 14 | 50% / 2.00 / +7.0 | 7% / 0.15 / -11.0 | reversal |
| shift>=2 & cont | OOS | 10 | 10% / 0.22 / -7.0 | 30% / 0.86 / -1.0 | continuation |
| shift>=2 & none | OOS | 5 | 20% / 0.58 / -1.4 | 0% / 0.00 / -5.0 | reversal |
| shift>=2 & noref | OOS | 8 | 38% / 1.20 / +1.0 | 12% / 0.29 / -5.0 | reversal |
| shift<2 | OOS | 26 | 38% / 1.09 / +1.5 | 31% / 0.89 / -2.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

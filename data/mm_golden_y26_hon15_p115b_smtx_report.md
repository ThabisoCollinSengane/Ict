# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 154, unique setups 96, simulated 96. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 17 | 41% / 1.40 / +4.0 | 12% / 0.27 / -11.0 | reversal |
| shift>=2 & cont | OOS | 16 | 19% / 0.46 / -7.0 | 12% / 0.29 / -10.0 | reversal |
| shift>=2 & none | OOS | 10 | 40% / 1.15 / +0.8 | 0% / 0.00 / -10.0 | reversal |
| shift>=2 & noref | OOS | 14 | 50% / 2.31 / +7.9 | 14% / 0.33 / -8.0 | reversal |
| shift<2 | OOS | 39 | 41% / 1.36 / +8.2 | 18% / 0.44 / -18.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

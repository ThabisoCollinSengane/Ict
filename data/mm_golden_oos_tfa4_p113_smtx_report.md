# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 391, unique setups 202, simulated 202. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 34 | 50% / 2.10 / +17.8 | 18% / 0.43 / -16.0 | reversal |
| shift>=2 & cont | OOS | 50 | 50% / 1.98 / +23.9 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & none | OOS | 11 | 45% / 1.67 / +4.0 | 18% / 0.44 / -5.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 90 | 52% / 2.04 / +44.0 | 20% / 0.50 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

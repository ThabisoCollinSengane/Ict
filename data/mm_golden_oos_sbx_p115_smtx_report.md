# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 378, unique setups 195, simulated 195. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 32 | 53% / 2.27 / +19.0 | 16% / 0.37 / -17.0 | reversal |
| shift>=2 & cont | OOS | 50 | 52% / 2.11 / +26.5 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | OOS | 19 | 63% / 3.54 / +16.2 | 11% / 0.24 / -13.0 | reversal |
| shift<2 | OOS | 84 | 51% / 1.98 / +39.7 | 18% / 0.43 / -39.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

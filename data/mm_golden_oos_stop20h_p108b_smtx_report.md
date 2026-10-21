# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 365, unique setups 190, simulated 190. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 32 | 56% / 2.44 / +20.1 | 12% / 0.29 / -20.0 | reversal |
| shift>=2 & cont | OOS | 48 | 52% / 2.12 / +25.5 | 17% / 0.40 / -24.0 | reversal |
| shift>=2 & none | OOS | 7 | 43% / 1.50 / +2.0 | 29% / 0.80 / -1.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 86 | 50% / 1.89 / +37.7 | 20% / 0.49 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

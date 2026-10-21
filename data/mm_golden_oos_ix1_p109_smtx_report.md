# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 321, unique setups 183, simulated 183. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | OOS | 48 | 56% / 2.51 / +31.5 | 17% / 0.40 / -24.0 | reversal |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 77 | 52% / 2.03 / +37.7 | 17% / 0.41 / -38.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

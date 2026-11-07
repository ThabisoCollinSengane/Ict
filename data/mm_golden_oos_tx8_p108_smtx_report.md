# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 389, unique setups 201, simulated 201. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 34 | 56% / 2.41 / +21.1 | 15% / 0.34 / -19.0 | reversal |
| shift>=2 & cont | OOS | 52 | 52% / 2.11 / +27.5 | 15% / 0.36 / -28.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | OOS | 17 | 65% / 3.83 / +15.2 | 6% / 0.12 / -14.0 | reversal |
| shift<2 | OOS | 88 | 50% / 1.89 / +38.7 | 20% / 0.51 / -34.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 369, unique setups 190, simulated 190. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 33 | 55% / 2.27 / +19.1 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | OOS | 48 | 52% / 2.12 / +25.5 | 15% / 0.34 / -27.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 30% / 0.86 / -1.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 0% / 0.00 / -16.0 | reversal |
| shift<2 | OOS | 83 | 52% / 2.03 / +40.7 | 19% / 0.48 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

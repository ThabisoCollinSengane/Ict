# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 317, unique setups 167, simulated 167. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 27 | 52% / 2.01 / +13.1 | 15% / 0.35 / -15.0 | reversal |
| shift>=2 & cont | OOS | 44 | 57% / 2.57 / +29.5 | 11% / 0.26 / -29.0 | reversal |
| shift>=2 & none | OOS | 8 | 50% / 2.00 / +4.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.79 / +12.2 | 0% / 0.00 / -14.0 | reversal |
| shift<2 | OOS | 74 | 49% / 1.81 / +30.5 | 20% / 0.51 / -29.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

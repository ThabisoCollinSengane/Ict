# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 360, unique setups 187, simulated 187. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 30 | 53% / 2.15 / +16.1 | 17% / 0.40 / -15.0 | reversal |
| shift>=2 & cont | OOS | 50 | 54% / 2.29 / +29.5 | 14% / 0.33 / -29.0 | reversal |
| shift>=2 & none | OOS | 10 | 50% / 2.00 / +5.0 | 20% / 0.50 / -4.0 | reversal |
| shift>=2 & noref | OOS | 16 | 62% / 3.46 / +13.2 | 6% / 0.13 / -13.0 | reversal |
| shift<2 | OOS | 81 | 52% / 2.03 / +39.7 | 19% / 0.45 / -36.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 723, unique setups 374, simulated 374. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 45 | 58% / 2.71 / +31.1 | 9% / 0.20 / -33.0 | reversal |
| shift>=2 & smt | OOS | 30 | 50% / 1.87 / +13.1 | 13% / 0.31 / -18.0 | reversal |
| shift>=2 & cont | IS | 54 | 41% / 1.38 / +12.0 | 15% / 0.35 / -30.0 | reversal |
| shift>=2 & cont | OOS | 49 | 55% / 2.44 / +30.8 | 10% / 0.23 / -34.0 | reversal |
| shift>=2 & none | IS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & none | OOS | 8 | 62% / 3.33 / +7.0 | 25% / 0.67 / -2.0 | reversal |
| shift>=2 & noref | IS | 17 | 71% / 4.45 / +17.3 | 12% / 0.27 / -11.0 | reversal |
| shift>=2 & noref | OOS | 11 | 64% / 3.50 / +10.0 | 0% / 0.00 / -11.0 | reversal |
| shift<2 | IS | 77 | 47% / 1.70 / +28.7 | 13% / 0.30 / -47.0 | reversal |
| shift<2 | OOS | 77 | 49% / 1.90 / +34.2 | 18% / 0.44 / -35.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

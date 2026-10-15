# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 723, unique setups 401, simulated 401. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 41 | 59% / 2.66 / +28.2 | 10% / 0.22 / -29.0 | reversal |
| shift>=2 & smt | OOS | 33 | 52% / 2.12 / +18.0 | 15% / 0.36 / -18.0 | reversal |
| shift>=2 & cont | IS | 54 | 44% / 1.56 / +16.8 | 17% / 0.40 / -27.0 | reversal |
| shift>=2 & cont | OOS | 53 | 53% / 2.29 / +31.5 | 15% / 0.36 / -29.0 | reversal |
| shift>=2 & none | IS | 8 | 38% / 1.20 / +1.0 | 50% / 2.00 / +4.0 | continuation |
| shift>=2 & none | OOS | 6 | 50% / 2.00 / +3.0 | 33% / 1.00 / +0.0 | reversal |
| shift>=2 & noref | IS | 20 | 60% / 2.76 / +14.1 | 10% / 0.22 / -14.0 | reversal |
| shift>=2 & noref | OOS | 14 | 64% / 3.60 / +13.0 | 7% / 0.15 / -11.0 | reversal |
| shift<2 | IS | 89 | 52% / 2.09 / +46.7 | 11% / 0.25 / -59.0 | reversal |
| shift<2 | OOS | 83 | 53% / 2.13 / +42.7 | 16% / 0.37 / -44.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

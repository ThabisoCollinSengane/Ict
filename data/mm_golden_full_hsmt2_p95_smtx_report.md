# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 706, unique setups 339, simulated 339. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | IS | 40 | 57% / 2.54 / +26.2 | 12% / 0.29 / -25.0 | reversal |
| shift>=2 & smt | OOS | 27 | 41% / 1.38 / +6.0 | 11% / 0.25 / -18.0 | reversal |
| shift>=2 & cont | IS | 47 | 43% / 1.39 / +10.5 | 19% / 0.47 / -20.0 | reversal |
| shift>=2 & cont | OOS | 40 | 62% / 3.22 / +33.3 | 5% / 0.11 / -34.0 | reversal |
| shift>=2 & none | IS | 5 | 20% / 0.50 / -2.0 | 40% / 1.33 / +1.0 | continuation |
| shift>=2 & none | OOS | 6 | 67% / 4.00 / +6.0 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | IS | 18 | 67% / 4.00 / +18.0 | 11% / 0.25 / -12.0 | reversal |
| shift>=2 & noref | OOS | 15 | 60% / 3.00 / +12.0 | 7% / 0.14 / -12.0 | reversal |
| shift<2 | IS | 74 | 55% / 2.42 / +46.7 | 12% / 0.28 / -47.0 | reversal |
| shift<2 | OOS | 67 | 54% / 2.30 / +38.6 | 27% / 0.73 / -13.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

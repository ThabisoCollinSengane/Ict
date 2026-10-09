# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 312, unique setups 149, simulated 149. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 24 | 42% / 1.43 / +6.0 | 12% / 0.29 / -15.0 | reversal |
| shift>=2 & cont | OOS | 36 | 64% / 3.41 / +31.3 | 6% / 0.12 / -30.0 | reversal |
| shift>=2 & none | OOS | 6 | 67% / 4.00 / +6.0 | 0% / 0.00 / -6.0 | reversal |
| shift>=2 & noref | OOS | 18 | 56% / 2.64 / +11.5 | 11% / 0.25 / -12.0 | reversal |
| shift<2 | OOS | 65 | 55% / 2.37 / +38.9 | 26% / 0.71 / -14.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

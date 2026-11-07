# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 407, unique setups 199, simulated 199. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 32 | 53% / 2.27 / +19.0 | 12% / 0.29 / -20.0 | reversal |
| shift>=2 & cont | OOS | 50 | 52% / 2.11 / +26.5 | 16% / 0.38 / -26.0 | reversal |
| shift>=2 & none | OOS | 12 | 42% / 1.43 / +3.0 | 25% / 0.67 / -3.0 | reversal |
| shift>=2 & noref | OOS | 18 | 67% / 4.00 / +16.1 | 6% / 0.12 / -15.0 | reversal |
| shift<2 | OOS | 87 | 48% / 1.76 / +33.8 | 21% / 0.52 / -33.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

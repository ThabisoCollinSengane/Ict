# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 330, unique setups 195, simulated 195. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 28 | 61% / 2.92 / +21.1 | 14% / 0.33 / -16.0 | reversal |
| shift>=2 & cont | OOS | 49 | 51% / 2.10 / +26.2 | 18% / 0.45 / -22.0 | reversal |
| shift>=2 & none | OOS | 4 | 50% / 2.00 / +2.0 | 0% / 0.00 / -4.0 | reversal |
| shift>=2 & noref | OOS | 12 | 42% / 1.57 / +3.6 | 8% / 0.18 / -9.0 | reversal |
| shift<2 | OOS | 102 | 54% / 2.23 / +58.0 | 20% / 0.49 / -42.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

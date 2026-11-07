# P92 — reversal vs continuation by Episode-22 SMT reading

events logged 258, unique setups 162, simulated 162. R units, 2R target, stop 3-10 pips, 240 M1 bars max, 0.5 pip friction.

| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |
|---|---|---|---|---|---|
| shift>=2 & smt | OOS | 14 | 50% / 2.00 / +7.0 | 14% / 0.33 / -8.0 | reversal |
| shift>=2 & cont | OOS | 38 | 55% / 2.37 / +23.3 | 16% / 0.38 / -20.0 | reversal |
| shift>=2 & none | OOS | 1 | 0% / 0.00 / -1.0 | 100% / inf / +2.0 | continuation |
| shift>=2 & noref | OOS | 9 | 56% / 2.23 / +4.9 | 11% / 0.25 / -6.0 | reversal |
| shift<2 | OOS | 100 | 56% / 2.46 / +64.4 | 12% / 0.27 / -64.0 | reversal |

Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; `shift>=2 & cont/none` -> continuation better in BOTH halves.

# P126 NULL A — independent random walks

Outcome: sign(DXY at the END of the current H1 candle − DXY NOW), now = open of the first M1 bar starting at t. Coin = 50% for ANY rule. Cell = n decisions/days, hit% (lift vs 50 ± DAY-CLUSTERED SE). A rule passes (spec §8) only with the same sign beyond 2 SE in IS, OOS AND 2026, hit >= 55% (FOLLOW) or <= 45% (FADE) every period, and Null A / Null B pooled within 2 SE.

## Coverage

| period | days | decisions | with outcome | UDXUSD move ok% | EURUSD move ok% | GBPUSD move ok% | NZDUSD move ok% | EURGBP move ok% | AUDNZD move ok% | XAUUSD move ok% | SPXUSD move ok% | NSXUSD move ok% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IS | 520 | 31200 | 31200 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |
| OOS | 523 | 31380 | 31380 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |
| 2026 | 202 | 12120 | 12120 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |

'move ok%' = share of decisions where that symbol had a completed M1 bar this hour (0% = symbol missing -> its rule makes no call). The :00 decisions never have one (5 of 60 per day), so ~92% is full coverage.

## Stage 1 — main outcome (pass cells)

| rule | IS | OOS | 2026 |
|---|---|---|---|
| dxy_hour | 28600/520d 50.4% (+0.4±0.6) | 28765/523d 49.5% (-0.5±0.6) | 11110/202d 49.8% (-0.2±1.0) |
| dxy_m5_bos | 6551/520d 50.4% (+0.4±0.9) | 6567/523d 49.2% (-0.8±0.8) | 2561/202d 51.2% (+1.2±1.4) |
| dxy_m15_bos | 6684/512d 50.8% (+0.8±1.1) | 6552/517d 50.2% (+0.2±1.1) | 2577/196d 50.8% (+0.8±1.9) |
| cross_hour | 14183/520d 50.3% (+0.3±0.8) | 14262/523d 50.1% (+0.1±0.8) | 5455/202d 49.2% (-0.8±1.2) |
| gold_hour | 28600/520d 50.3% (+0.3±0.6) | 28765/523d 50.0% (-0.0±0.5) | 11110/202d 50.7% (+0.7±1.0) |
| index_hour | 28600/520d 49.4% (-0.6±0.6) | 28765/523d 49.2% (-0.8±0.6) | 11110/202d 47.9% (-2.1±0.9) |
| vote | 24659/520d 50.8% (+0.8±0.6) | 24663/523d 49.9% (-0.1±0.6) | 9733/202d 49.4% (-0.6±1.0) |

Reported only (not a pass cell; trap 1 — the pairs ARE most of DXY):

| rule | IS | OOS | 2026 |
|---|---|---|---|
| pairs_hour | 28600/520d 50.5% (+0.5±0.6) | 28765/523d 50.0% (-0.0±0.6) | 11110/202d 49.2% (-0.8±0.9) |
## Bounce-trap check (diagnostic, not a pass cell)

Rule = fade the last completed M1 candle. Scored against the hour close measured from the LAST CLOSED M1 close (the broken 'now') vs from the OPEN of the next minute (the study's 'now'). With bid-quote noise the broken version reads below 50% on noise alone; the fixed one must read ~50%.

| 'now' = | IS | OOS | 2026 | ALL |
|---|---|---|---|---|
| last close (broken) | 50.1 (+0.1±0.3) | 49.8 (-0.2±0.3) | 49.6 (-0.4±0.4) | 49.9 (-0.1±0.2) |
| next open (used) | 50.1 (+0.1±0.3) | 49.8 (-0.2±0.3) | 49.6 (-0.4±0.4) | 49.9 (-0.1±0.2) |

## Secondary outcome (descriptive) — does the rule call the H1 candle's own htf_bias break?

Scored only where the CURRENT H1 candle's full-hour close breaks the prior 8 H1 bars (the leaky gate's +1/-1, lookback 8). Not 50% on a random walk — compare with the null.

| rule | IS | OOS | 2026 | share of decisions with a break |
|---|---|---|---|---|
| dxy_hour | 82.1 (+32.1±1.0) | 82.9 (+32.9±1.0) | 84.7 (+34.7±1.5) | 22.1% |
| dxy_m5_bos | 96.6 (+46.6±0.5) | 96.1 (+46.1±0.5) | 96.6 (+46.6±0.7) | 22.1% |
| dxy_m15_bos | 99.6 (+49.6±0.3) | 99.2 (+49.2±0.3) | 99.4 (+49.4±0.4) | 22.1% |
| cross_hour | 50.9 (+0.9±2.2) | 48.9 (-1.1±2.1) | 48.4 (-1.6±3.1) | 22.1% |
| gold_hour | 48.6 (-1.4±1.6) | 50.3 (+0.3±1.5) | 49.4 (-0.6±2.4) | 22.1% |
| index_hour | 46.4 (-3.6±1.5) | 49.9 (-0.1±1.5) | 50.6 (+0.6±2.4) | 22.1% |
| vote | 77.3 (+27.3±1.2) | 78.1 (+28.1±1.0) | 80.7 (+30.7±1.7) | 22.1% |

## Splits (read only for a rule that passes) — minutes left in the hour and session

| rule | split | 0-15 min left | 15-30 min left | 30-45 min left | 45-60 min left | london | ny |
|---|---|---|---|---|---|---|---|
| dxy_hour | IS | 50.0 (+0.0±0.8) | 49.8 (-0.2±0.8) | 51.0 (+1.0±0.8) | 51.2 (+1.2±0.9) | 49.2 (-0.8±1.0) | 51.2 (+1.2±0.8) |
| dxy_hour | OOS | 50.3 (+0.3±0.7) | 49.6 (-0.4±0.8) | 48.8 (-1.2±0.8) | 49.3 (-0.7±0.8) | 50.3 (+0.3±0.9) | 49.0 (-1.0±0.8) |
| dxy_hour | 2026 | 50.3 (+0.3±1.3) | 49.5 (-0.5±1.3) | 49.9 (-0.1±1.3) | 49.2 (-0.8±1.5) | 52.2 (+2.2±1.5) | 48.2 (-1.8±1.2) |
| dxy_m5_bos | IS | 49.5 (-0.5±1.4) | 51.2 (+1.2±1.4) | 51.3 (+1.3±1.5) | 49.4 (-0.6±1.6) | 48.9 (-1.1±1.3) | 51.4 (+1.4±1.1) |
| dxy_m5_bos | OOS | 49.1 (-0.9±1.4) | 49.7 (-0.3±1.4) | 48.5 (-1.5±1.5) | 49.4 (-0.6±1.5) | 50.1 (+0.1±1.3) | 48.6 (-1.4±1.1) |
| dxy_m5_bos | 2026 | 51.6 (+1.6±2.3) | 53.8 (+3.8±2.3) | 48.3 (-1.7±2.3) | 51.2 (+1.2±2.3) | 55.1 (+5.1±2.2) | 48.5 (-1.5±1.8) |
| dxy_m15_bos | IS | 51.4 (+1.4±1.7) | 49.4 (-0.6±1.8) | 50.7 (+0.7±2.0) | 51.7 (+1.7±2.0) | 49.8 (-0.2±1.7) | 51.5 (+1.5±1.4) |
| dxy_m15_bos | OOS | 50.7 (+0.7±1.7) | 50.2 (+0.2±1.9) | 50.6 (+0.6±1.9) | 49.5 (-0.5±2.0) | 51.3 (+1.3±1.7) | 49.4 (-0.6±1.4) |
| dxy_m15_bos | 2026 | 53.1 (+3.1±2.7) | 52.3 (+2.3±2.9) | 48.9 (-1.1±3.2) | 48.7 (-1.3±3.2) | 54.7 (+4.7±2.9) | 48.3 (-1.7±2.4) |
| cross_hour | IS | 50.1 (+0.1±1.1) | 49.9 (-0.1±1.2) | 50.7 (+0.7±1.1) | 50.8 (+0.8±1.2) | 52.1 (+2.1±1.2) | 49.1 (-0.9±1.0) |
| cross_hour | OOS | 50.5 (+0.5±1.1) | 49.6 (-0.4±1.1) | 50.4 (+0.4±1.1) | 49.7 (-0.3±1.2) | 49.0 (-1.0±1.2) | 50.8 (+0.8±1.1) |
| cross_hour | 2026 | 50.8 (+0.8±1.7) | 46.2 (-3.8±1.7) | 48.4 (-1.6±1.7) | 52.3 (+2.3±1.8) | 49.3 (-0.7±1.9) | 49.1 (-0.9±1.5) |
| gold_hour | IS | 49.7 (-0.3±0.8) | 49.9 (-0.1±0.8) | 51.1 (+1.1±0.8) | 50.6 (+0.6±0.8) | 49.4 (-0.6±0.8) | 50.9 (+0.9±0.7) |
| gold_hour | OOS | 50.5 (+0.5±0.7) | 50.7 (+0.7±0.8) | 49.5 (-0.5±0.8) | 48.8 (-1.2±0.8) | 49.9 (-0.1±0.9) | 50.0 (+0.0±0.7) |
| gold_hour | 2026 | 49.3 (-0.7±1.3) | 50.6 (+0.6±1.4) | 51.8 (+1.8±1.3) | 51.0 (+1.0±1.3) | 51.4 (+1.4±1.5) | 50.2 (+0.2±1.2) |
| index_hour | IS | 49.5 (-0.5±0.7) | 49.5 (-0.5±0.8) | 48.7 (-1.3±0.8) | 50.3 (+0.3±0.8) | 50.2 (+0.2±0.8) | 48.9 (-1.1±0.7) |
| index_hour | OOS | 48.6 (-1.4±0.8) | 49.3 (-0.7±0.8) | 49.1 (-0.9±0.8) | 50.2 (+0.2±0.8) | 47.8 (-2.2±0.9) | 50.1 (+0.1±0.7) |
| index_hour | 2026 | 46.7 (-3.3±1.1) | 49.8 (-0.2±1.2) | 47.8 (-2.2±1.2) | 47.2 (-2.8±1.4) | 47.9 (-2.1±1.4) | 48.0 (-2.0±1.2) |
| vote | IS | 50.9 (+0.9±0.8) | 49.9 (-0.1±0.9) | 50.8 (+0.8±0.9) | 51.7 (+1.7±0.9) | 50.4 (+0.4±0.9) | 51.0 (+1.0±0.8) |
| vote | OOS | 50.3 (+0.3±0.8) | 50.2 (+0.2±0.8) | 49.2 (-0.8±0.8) | 49.6 (-0.4±0.8) | 49.8 (-0.2±0.9) | 49.9 (-0.1±0.7) |
| vote | 2026 | 48.8 (-1.2±1.4) | 49.7 (-0.3±1.3) | 49.3 (-0.7±1.3) | 49.8 (-0.2±1.2) | 51.4 (+1.4±1.5) | 48.0 (-2.0±1.1) |

## Stage 0 — the accuracy bar

### (2) The engine's DXY H1 read as a forecast of THIS target (grid)

leaky = htf_bias on the H1 candle containing t, full-hour close (what the leaky engine used); honest = htf_bias on the last CLOSED H1 candle. Hit = read's sign = sign(hour close − now), on decisions where the read is non-zero.

| read | IS | OOS | 2026 | ALL | share non-zero |
|---|---|---|---|---|---|
| leaky | 6780/351d 83.7% (+33.7±0.8) | 7044/374d 85.1% (+35.1±0.8) | 2664/135d 84.8% (+34.8±1.4) | 16488/860d 84.5% (+34.5±0.5) | 22.1% |
| honest | 6948/351d 47.8% (-2.2±1.4) | 6804/353d 49.5% (-0.5±1.5) | 2508/129d 47.5% (-2.5±2.6) | 16260/833d 48.5% (-1.5±1.0) | 21.8% |


### Null A seed robustness (pooled lift / SE, z) — verdict uses seed offset 0 only

| seed offset | dxy_hour | dxy_m5_bos | dxy_m15_bos | cross_hour | gold_hour | index_hour | vote | pairs_hour |
|---|---|---|---|---|---|---|---|---|
| 0 | -0.19 | +0.04 | +0.77 | +0.11 | +0.60 | -2.54 | +0.43 | +0.24 |
| 1000 | -0.34 | -0.45 | -1.98 | +0.32 | +0.62 | +1.70 | +0.06 | +0.42 |
| 2000 | -0.04 | +1.03 | +0.47 | -0.12 | -1.14 | -0.09 | +0.02 | +1.28 |
| 3000 | +0.41 | +1.49 | +0.68 | -0.72 | -0.40 | +1.15 | +0.60 | -0.91 |

A calibrated null gives z ~ N(0,1): about 1 in 20 cells beyond ±2 by chance.


# P126 NULL B — DXY-correlated walks + bid-quote noise

Outcome: sign(DXY at the END of the current H1 candle − DXY NOW), now = open of the first M1 bar starting at t. Coin = 50% for ANY rule. Cell = n decisions/days, hit% (lift vs 50 ± DAY-CLUSTERED SE). A rule passes (spec §8) only with the same sign beyond 2 SE in IS, OOS AND 2026, hit >= 55% (FOLLOW) or <= 45% (FADE) every period, and Null A / Null B pooled within 2 SE.

## Coverage

| period | days | decisions | with outcome | UDXUSD move ok% | EURUSD move ok% | GBPUSD move ok% | NZDUSD move ok% | EURGBP move ok% | AUDNZD move ok% | XAUUSD move ok% | SPXUSD move ok% | NSXUSD move ok% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IS | 520 | 31200 | 31200 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |
| OOS | 523 | 31380 | 31380 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |
| 2026 | 202 | 12120 | 12120 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 | 92 |

'move ok%' = share of decisions where that symbol had a completed M1 bar this hour (0% = symbol missing -> its rule makes no call). The :00 decisions never have one (5 of 60 per day), so ~92% is full coverage.

## Stage 1 — main outcome (pass cells)

| rule | IS | OOS | 2026 |
|---|---|---|---|
| dxy_hour | 28600/520d 50.2% (+0.2±0.6) | 28765/523d 49.6% (-0.4±0.5) | 11110/202d 49.9% (-0.1±0.9) |
| dxy_m5_bos | 4488/519d 51.0% (+1.0±0.9) | 4355/523d 48.6% (-1.4±1.0) | 1651/202d 49.1% (-0.9±1.5) |
| dxy_m15_bos | 5214/498d 49.3% (-0.7±1.3) | 5067/498d 48.7% (-1.3±1.2) | 1971/191d 50.1% (+0.1±2.1) |
| cross_hour | 14003/520d 50.5% (+0.5±0.8) | 14049/523d 50.1% (+0.1±0.8) | 5425/202d 49.5% (-0.5±1.4) |
| gold_hour | 28600/520d 50.3% (+0.3±0.5) | 28765/523d 50.1% (+0.1±0.6) | 11110/202d 51.2% (+1.2±0.9) |
| index_hour | 28600/520d 51.0% (+1.0±0.6) | 28765/523d 49.5% (-0.5±0.5) | 11110/202d 49.7% (-0.3±0.9) |
| vote | 24739/520d 50.6% (+0.6±0.6) | 25001/523d 49.4% (-0.6±0.6) | 9631/202d 50.1% (+0.1±0.9) |

Reported only (not a pass cell; trap 1 — the pairs ARE most of DXY):

| rule | IS | OOS | 2026 |
|---|---|---|---|
| pairs_hour | 28600/520d 50.8% (+0.8±0.6) | 28765/523d 49.7% (-0.3±0.6) | 11110/202d 51.0% (+1.0±0.9) |
## Bounce-trap check (diagnostic, not a pass cell)

Rule = fade the last completed M1 candle. Scored against the hour close measured from the LAST CLOSED M1 close (the broken 'now') vs from the OPEN of the next minute (the study's 'now'). With bid-quote noise the broken version reads below 50% on noise alone; the fixed one must read ~50%.

| 'now' = | IS | OOS | 2026 | ALL |
|---|---|---|---|---|
| last close (broken) | 52.6 (+2.6±0.3) | 52.1 (+2.1±0.3) | 52.8 (+2.8±0.4) | 52.4 (+2.4±0.2) |
| next open (used) | 50.3 (+0.3±0.3) | 49.7 (-0.3±0.3) | 50.4 (+0.4±0.4) | 50.1 (+0.1±0.2) |

## Secondary outcome (descriptive) — does the rule call the H1 candle's own htf_bias break?

Scored only where the CURRENT H1 candle's full-hour close breaks the prior 8 H1 bars (the leaky gate's +1/-1, lookback 8). Not 50% on a random walk — compare with the null.

| rule | IS | OOS | 2026 | share of decisions with a break |
|---|---|---|---|---|
| dxy_hour | 84.4 (+34.4±0.9) | 84.9 (+34.9±1.0) | 83.3 (+33.3±1.5) | 18.2% |
| dxy_m5_bos | 97.5 (+47.5±0.5) | 97.5 (+47.5±0.5) | 97.8 (+47.8±0.7) | 18.2% |
| dxy_m15_bos | 99.7 (+49.7±0.2) | 99.8 (+49.8±0.2) | 99.6 (+49.6±0.4) | 18.2% |
| cross_hour | 44.6 (-5.4±2.4) | 43.2 (-6.8±2.4) | 45.0 (-5.0±3.9) | 18.2% |
| gold_hour | 58.3 (+8.3±1.6) | 59.0 (+9.0±1.5) | 61.9 (+11.9±2.8) | 18.2% |
| index_hour | 55.4 (+5.4±1.6) | 58.8 (+8.8±1.6) | 56.9 (+6.9±2.5) | 18.2% |
| vote | 80.0 (+30.0±1.1) | 81.3 (+31.3±1.1) | 80.9 (+30.9±1.8) | 18.2% |

## Splits (read only for a rule that passes) — minutes left in the hour and session

| rule | split | 0-15 min left | 15-30 min left | 30-45 min left | 45-60 min left | london | ny |
|---|---|---|---|---|---|---|---|
| dxy_hour | IS | 49.3 (-0.7±0.7) | 50.6 (+0.6±0.8) | 50.7 (+0.7±0.8) | 50.4 (+0.4±0.8) | 50.2 (+0.2±0.9) | 50.3 (+0.3±0.8) |
| dxy_hour | OOS | 50.3 (+0.3±0.7) | 49.6 (-0.4±0.8) | 49.3 (-0.7±0.7) | 48.8 (-1.2±0.8) | 49.9 (-0.1±0.9) | 49.3 (-0.7±0.7) |
| dxy_hour | 2026 | 49.0 (-1.0±1.2) | 50.7 (+0.7±1.2) | 51.1 (+1.1±1.2) | 48.4 (-1.6±1.3) | 49.3 (-0.7±1.6) | 50.3 (+0.3±1.2) |
| dxy_m5_bos | IS | 52.0 (+2.0±1.7) | 51.1 (+1.1±1.6) | 49.9 (-0.1±1.7) | 51.2 (+1.2±1.8) | 51.5 (+1.5±1.4) | 50.7 (+0.7±1.2) |
| dxy_m5_bos | OOS | 49.9 (-0.1±1.6) | 49.2 (-0.8±1.7) | 48.9 (-1.1±1.7) | 46.5 (-3.5±1.8) | 49.4 (-0.6±1.6) | 48.1 (-1.9±1.2) |
| dxy_m5_bos | 2026 | 46.9 (-3.1±2.7) | 52.4 (+2.4±2.8) | 51.2 (+1.2±2.7) | 46.3 (-3.7±2.8) | 48.6 (-1.4±2.4) | 49.5 (-0.5±1.9) |
| dxy_m15_bos | IS | 49.8 (-0.2±2.0) | 48.6 (-1.4±2.0) | 51.3 (+1.3±2.2) | 47.7 (-2.3±2.2) | 49.1 (-0.9±1.9) | 49.4 (-0.6±1.6) |
| dxy_m15_bos | OOS | 50.0 (+0.0±2.0) | 47.2 (-2.8±2.1) | 48.4 (-1.6±2.1) | 49.1 (-0.9±2.1) | 49.6 (-0.4±2.0) | 48.1 (-1.9±1.5) |
| dxy_m15_bos | 2026 | 46.0 (-4.0±3.6) | 46.9 (-3.1±3.6) | 52.4 (+2.4±3.6) | 54.1 (+4.1±3.2) | 50.1 (+0.1±3.2) | 50.2 (+0.2±2.5) |
| cross_hour | IS | 50.9 (+0.9±1.1) | 50.5 (+0.5±1.1) | 50.1 (+0.1±1.1) | 50.8 (+0.8±1.1) | 51.4 (+1.4±1.3) | 50.0 (-0.0±1.0) |
| cross_hour | OOS | 49.8 (-0.2±1.0) | 50.3 (+0.3±1.1) | 50.4 (+0.4±1.1) | 49.8 (-0.2±1.1) | 49.8 (-0.2±1.2) | 50.3 (+0.3±1.0) |
| cross_hour | 2026 | 47.9 (-2.1±1.7) | 50.2 (+0.2±2.0) | 49.2 (-0.8±1.9) | 51.3 (+1.3±1.8) | 49.8 (-0.2±1.9) | 49.3 (-0.7±1.7) |
| gold_hour | IS | 51.3 (+1.3±0.7) | 50.8 (+0.8±0.8) | 49.0 (-1.0±0.8) | 49.8 (-0.2±0.8) | 50.2 (+0.2±0.9) | 50.3 (+0.3±0.7) |
| gold_hour | OOS | 50.6 (+0.6±0.8) | 50.0 (-0.0±0.8) | 50.7 (+0.7±0.8) | 48.8 (-1.2±0.8) | 50.0 (-0.0±0.9) | 50.2 (+0.2±0.8) |
| gold_hour | 2026 | 49.3 (-0.7±1.1) | 51.8 (+1.8±1.4) | 52.3 (+2.3±1.3) | 51.4 (+1.4±1.4) | 52.4 (+2.4±1.5) | 50.4 (+0.4±1.1) |
| index_hour | IS | 50.5 (+0.5±0.7) | 51.6 (+1.6±0.8) | 51.1 (+1.1±0.8) | 50.8 (+0.8±0.8) | 51.8 (+1.8±0.9) | 50.5 (+0.5±0.7) |
| index_hour | OOS | 49.7 (-0.3±0.8) | 49.2 (-0.8±0.8) | 49.6 (-0.4±0.8) | 49.8 (-0.2±0.8) | 50.3 (+0.3±0.9) | 49.0 (-1.0±0.7) |
| index_hour | 2026 | 50.4 (+0.4±1.2) | 48.6 (-1.4±1.3) | 49.9 (-0.1±1.2) | 50.0 (+0.0±1.3) | 47.8 (-2.2±1.4) | 51.0 (+1.0±1.1) |
| vote | IS | 50.3 (+0.3±0.8) | 51.1 (+1.1±0.9) | 50.3 (+0.3±0.9) | 50.7 (+0.7±0.8) | 51.3 (+1.3±0.9) | 50.2 (+0.2±0.8) |
| vote | OOS | 50.2 (+0.2±0.8) | 48.8 (-1.2±0.8) | 49.5 (-0.5±0.8) | 49.0 (-1.0±0.8) | 49.8 (-0.2±1.0) | 49.1 (-0.9±0.7) |
| vote | 2026 | 48.5 (-1.5±1.2) | 49.8 (-0.2±1.4) | 52.0 (+2.0±1.3) | 49.9 (-0.1±1.4) | 49.6 (-0.4±1.5) | 50.4 (+0.4±1.2) |

## Stage 0 — the accuracy bar

### (2) The engine's DXY H1 read as a forecast of THIS target (grid)

leaky = htf_bias on the H1 candle containing t, full-hour close (what the leaky engine used); honest = htf_bias on the last CLOSED H1 candle. Hit = read's sign = sign(hour close − now), on decisions where the read is non-zero.

| read | IS | OOS | 2026 | ALL | share non-zero |
|---|---|---|---|---|---|
| leaky | 5856/324d 85.2% (+35.2±0.8) | 5424/317d 86.8% (+36.8±0.9) | 2340/123d 87.5% (+37.5±1.2) | 13620/764d 86.2% (+36.2±0.5) | 18.2% |
| honest | 6024/335d 45.3% (-4.7±1.6) | 5544/310d 49.7% (-0.3±1.7) | 2340/130d 50.6% (+0.6±2.6) | 13908/775d 47.9% (-2.1±1.1) | 18.6% |


### Null B seed robustness (pooled lift / SE, z) — verdict uses seed offset 0 only

| seed offset | dxy_hour | dxy_m5_bos | dxy_m15_bos | cross_hour | gold_hour | index_hour | vote | pairs_hour |
|---|---|---|---|---|---|---|---|---|
| 0 | -0.28 | -0.44 | -1.03 | +0.35 | +0.95 | +0.51 | +0.01 | +0.95 |
| 1000 | -1.15 | -0.30 | -0.73 | +1.67 | +0.93 | +1.60 | +1.42 | -0.16 |
| 2000 | -0.57 | -0.67 | +0.34 | -0.10 | -0.62 | -0.10 | -0.31 | -0.35 |
| 3000 | +1.46 | +0.62 | +0.98 | -1.30 | -0.53 | +1.28 | +0.78 | +0.36 |

A calibrated null gives z ~ N(0,1): about 1 in 20 cells beyond ±2 by chance.


# Yahoo replay — WHOLE algo (base + MM), last 60d, reporting last 20d

_data span: 2026-07-14 23:00:00+00:00 → 2026-10-06 21:00:00+00:00 (17041 5m bars)_
_STARTING_CASH=1000 · MM_standalone=0 · MM_continuation=0 · SMT_req=0 · withdraw=1_

_reporting window: trades opened at/after **2026-09-16 21:00:00+00:00** — 7 of 39 trades in the fetched span; the earlier part is HTF warm-up._

## HTF warm-up check

| timeframe | bars available | cascade wants | |
|---|---|---|---|
| W | 13 | 20 | **THIN** |
| D | 73 | 30 | ok |
| H4 | 373 | 20 | ok |

> ⚠️ **W under-warmed.** The draw cascade is a hard 0/3 gate, so entries are SUPPRESSED and this count is a FLOOR, not an estimate. Fetch a longer period and use `--since` to report a short window off a warm context.

## HOW MANY TRADES

**7 entries in the last 20 days.**

## Trades by model

| model | trades | wins | net ZAR |
|---|---|---|---|
| base breakout | 6 | 2 | +132.5 |
| base judas | 1 | 1 | +35.5 |

## Gate funnel

```
checks                   6360
in_killzone              6360  (+0)
drawdown_halt               0  (-6360)
nfp_fomc_ok              5174  (+5174)
news_clear               6299  (+1125)
consolidation_found        36  (-6263)
mss_h1_m15_m5_ok          112  (+76)
breakout_confirmed         65  (-47)
target_found               39  (-26)
units_nonzero              39  (+0)
risk_cap_ok                39  (+0)
entry_opened               39  (+0)
```

## All trades

_7 trades, 3 wins, net +168.0 ZAR_

```
                opened_at   pair  direction    entry     exit        pnl entry_model reason
2026-09-18 11:15:00+00:00 EURUSD         -1 1.147094 1.147134  -1.480000    breakout   stop
2026-09-21 11:45:00+00:00 EURUSD          1 1.149251 1.148211 -38.480000    breakout   stop
2026-09-22 07:30:00+00:00 EURUSD         -1 1.145648 1.145688  -1.480000    breakout   stop
2026-09-23 07:05:00+00:00 GBPUSD         -1 1.330926 1.327472 127.813247    breakout target
2026-09-25 11:00:00+00:00 GBPUSD          1 1.325060 1.325010  -1.850000    breakout   stop
2026-09-29 07:10:00+00:00 EURUSD         -1 1.136015 1.135055  35.520000       judas   stop
2026-10-06 11:00:00+00:00 EURUSD          1 1.124696 1.125656  47.987520    breakout   stop
```

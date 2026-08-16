# Yahoo replay — consolidation gate A/B (last 7d)

_data span: 2026-08-05 23:00:00+00:00 → 2026-08-14 21:25:00+00:00 (1980 5m bars)_

Same live gate stack, run twice: shipped gate vs loosened (MIN_RANGE_BARS 8→4, MAX_RANGE_PIPS 35→50, MIN_TOUCHES 2→1). More `consolidation_found` = more Judas-reversal opportunities.

## Current (shipped) gate

```
checks                    387
in_killzone               387  (+0)
drawdown_halt               0  (-387)
nfp_fomc_ok               387  (+387)
news_clear                387  (+0)
consolidation_found         3  (-384)
mss_h1_m15_m5_ok            7  (+4)
breakout_confirmed          8  (+1)
target_found                5  (-3)
units_nonzero               5  (+0)
risk_cap_ok                 5  (+0)
entry_opened                5  (+0)
```

_5 trades, 2 wins, net +80.5 ZAR_

```
                opened_at   pair  direction    entry     exit        pnl entry_model reason
2026-08-11 07:30:00+00:00 EURUSD         -1 1.153978 1.154475  -9.184006    breakout   stop
2026-08-12 12:30:00+00:00 EURUSD          1 1.155492 1.154452 -19.240000    breakout   stop
2026-08-13 12:45:00+00:00 EURUSD          1 1.154291 1.153251 -19.240000    breakout   stop
2026-08-14 08:00:00+00:00 GBPUSD          1 1.351707 1.355424  68.754031    breakout target
2026-08-14 07:00:00+00:00 EURUSD          1 1.154958 1.158172  59.457886    breakout target
```

## Loosened consolidation gate

```
checks                    412
in_killzone               412  (+0)
drawdown_halt               0  (-412)
nfp_fomc_ok               412  (+412)
news_clear                412  (+0)
consolidation_found         0  (-412)
mss_h1_m15_m5_ok           14  (+14)
breakout_confirmed          5  (-9)
target_found                3  (-2)
units_nonzero               3  (+0)
risk_cap_ok                 3  (+0)
entry_opened                3  (+0)
```

_3 trades, 2 wins, net +109.0 ZAR_

```
                opened_at   pair  direction    entry     exit        pnl entry_model reason
2026-08-12 12:30:00+00:00 EURUSD          1 1.155492 1.154452 -19.240000    breakout   stop
2026-08-14 08:00:00+00:00 GBPUSD          1 1.351707 1.355424  68.754031    breakout target
2026-08-14 07:00:00+00:00 EURUSD          1 1.154958 1.158172  59.457886       judas target
```

## Read

- consolidation_found: **3 → 0**  (entries: 5 → 3)
- More entries with comparable win-quality = loosen it live. More entries but the new ones lose = the tight coil was doing real work.

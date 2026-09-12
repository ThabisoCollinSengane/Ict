# Yahoo replay — WHOLE algo (base + MM), last 7d

_data span: 2026-08-05 23:00:00+00:00 → 2026-08-14 21:25:00+00:00 (1980 5m bars)_
_STARTING_CASH=1000 · MM_standalone=1 · MM_continuation=1 · SMT_req=1 · withdraw=0_

## Trades by model

| model | trades | wins | net ZAR |
|---|---|---|---|
| MM standalone/adds | 1 | 0 | -124.6 |
| base breakout | 5 | 2 | +224.7 |

## Gate funnel

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
risk_cap_halved             4  (-1)
risk_cap_ok                 5  (+1)
entry_opened                5  (+0)
```

## MM counters

```
mm_checks                  252
mm_std_no_sweep            115
mm_std_wrong_half          105
mm_std_not_filled          52
mm_blocked_no_ifvg         36
mm_std_no_smt              35
mm_blocked_favour          33
mm_std_no_structure        33
mm_blocked_no_structure    30
mm_blocked_no_smt          16
mm_std_no_target           15
mm_std_no_ifvg             12
mm_std_no_entry            11
mm_blocked_no_entry        8
mm_std_wide_gap            4
mm_blocked_not_filled      4
mm_added                   1
mm_blocked_min_target      1
```

## All trades

_6 trades, 2 wins, net +100.0 ZAR_

```
                opened_at   pair  direction    entry     exit         pnl entry_model reason
2026-08-11 07:30:00+00:00 EURUSD         -1 1.153978 1.154475  -45.920030    breakout   stop
2026-08-12 12:30:00+00:00 EURUSD          1 1.155492 1.155452   -1.850000    breakout   stop
2026-08-12 12:45:00+00:00 EURUSD          1 1.155758 1.154411 -124.634498    breakout   stop
2026-08-13 12:45:00+00:00 EURUSD          1 1.154291 1.153251  -48.100000    breakout   stop
2026-08-14 08:00:00+00:00 GBPUSD          1 1.351707 1.355424  171.885077    breakout target
2026-08-14 07:00:00+00:00 EURUSD          1 1.154958 1.158172  148.644715    breakout target
```

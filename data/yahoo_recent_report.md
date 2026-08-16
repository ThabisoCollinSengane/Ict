# Yahoo replay — WHOLE algo (base + MM), last 7d

_data span: 2026-08-05 23:00:00+00:00 → 2026-08-14 21:25:00+00:00 (1980 5m bars)_
_STARTING_CASH=1000 · MM_standalone=1 · MM_continuation=1 · SMT_req=1 · withdraw=0_

## Trades by model

| model | trades | wins | net ZAR |
|---|---|---|---|
| base breakout | 3 | 2 | +607.5 |

## Gate funnel

```
checks                    413
in_killzone               413  (+0)
drawdown_halt               0  (-413)
nfp_fomc_ok               413  (+413)
news_clear                413  (+0)
consolidation_found         7  (-406)
mss_h1_m15_m5_ok           12  (+5)
breakout_confirmed         13  (+1)
target_found               10  (-3)
units_nonzero              10  (+0)
risk_cap_ok                 3  (-7)
risk_cap_skip               7  (+4)
entry_opened                3  (-4)
```

## MM counters

```
mm_checks                  184
mm_std_wrong_half          120
mm_std_no_sweep            116
mm_std_not_filled          53
mm_std_no_smt              41
mm_std_no_structure        35
mm_blocked_no_ifvg         33
mm_blocked_no_structure    30
mm_blocked_no_smt          16
mm_std_no_ifvg             15
mm_std_no_target           15
mm_blocked_favour          14
mm_std_no_entry            11
mm_blocked_no_entry        8
mm_std_wide_gap            4
mm_blocked_min_target      1
mm_blocked_not_filled      1
```

## All trades

_3 trades, 2 wins, net +607.5 ZAR_

```
                opened_at   pair  direction    entry     exit        pnl entry_model reason
2026-08-11 07:30:00+00:00 EURUSD         -1 1.153978 1.154475 -45.920030    breakout   stop
2026-08-14 08:00:00+00:00 GBPUSD          1 1.351707 1.355424 343.770154    breakout target
2026-08-14 07:05:00+00:00 EURUSD          1 1.154824 1.158172 309.628485    breakout target
```

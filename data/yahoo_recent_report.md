# Yahoo recent replay — what blocked (last 7d)

_data span: 2026-08-05 23:00:00+00:00 → 2026-08-14 21:25:00+00:00  (1980 5m bars)_

Same `_maybe_open` gate stack as the live engine. The gate where the count COLLAPSES to ~0 is what's blocking entries.

## Gate funnel (pipeline order)

```
checks                      387
in_killzone                 387   (+0)
drawdown_halt                 0   (-387)
daily_loss_halt               0   (+0)
consec_loss_pause             0   (+0)
nfp_fomc_ok                 387   (+387)
news_clear                  387   (+0)
consolidation_found           3   (-384)
mss_h1_m15_m5_ok              7   (+4)
target_found                  5   (-2)
units_nonzero                 5   (+0)
risk_cap_ok                   5   (+0)
entry_opened                  5   (+0)
```

## Other gate counters

```
pyramid_blocked_favour       59
pyramid_blocked_min_target   37
intermarket_signal           35
pair_matches                 35
pyramid_blocked_low_im       33
breakout_confirmed           8
daily_bias_ok                7
h1_bias_ok                   7
h4_bias_ok                   7
m5_fvg_correct_dir           5
rr_ok                        5
weekly_amd_confirmed         5
soj_sweep                    5
soj_retest                   4
crt_turtle_soup              4
manipulation_correct_dir     3
phase_london_judas           3
gt_pool_sweep                3
structure_stop_used          3
htf_draw_partial             2
mstruct_align                2
m1_stop_used                 2
phase_ny_judas               2
gt_disp_wick                 2
stop_capped_10pip            2
dealing_range_ok             1
ny_continuation              1
mstruct_minor_sweep          1
soj_judas                    1
gt_judas_reversal            1
gt_mp_discount               1
gt_macro_window              1
```

## Trades opened: 5

```
                opened_at   pair  direction    entry     exit        pnl entry_model reason
2026-08-11 07:30:00+00:00 EURUSD         -1 1.153978 1.154475  -9.184006    breakout   stop
2026-08-12 12:30:00+00:00 EURUSD          1 1.155492 1.154452 -19.240000    breakout   stop
2026-08-13 12:45:00+00:00 EURUSD          1 1.154291 1.153251 -19.240000    breakout   stop
2026-08-14 08:00:00+00:00 GBPUSD          1 1.351707 1.355424  68.754031    breakout target
2026-08-14 07:00:00+00:00 EURUSD          1 1.154958 1.158172  59.457886    breakout target
```

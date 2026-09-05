# HistData backtest — 2024–2025 (2 yr)

## Results

```
trades                     571
win_rate_pct               42.7
profit_factor              4.17
starting_equity_ZAR        1000
ending_equity_ZAR          122240.83
pnl_ZAR                    121240.83
pnl_pct                    12124.08
max_drawdown_pct           -7.79
avg_win_ZAR                653.8
avg_loss_ZAR               -117.08
withdrawn_total_ZAR        116007.3
withdrawal_count           19
working_balance_ZAR        6233.53
working_max_drawdown_pct   20.66
```

## Gate funnel

```
checks                         58790
in_killzone                    58790
news_clear                     50398
nfp_fomc_ok                    43656
intermarket_signal             1868
pair_matches                   1868
mss_h1_m15_m5_ok               646
daily_bias_ok                  646
h1_bias_ok                     646
h4_bias_ok                     646
dealing_range_ok               50
consolidation_found            398
manipulation_correct_dir       334
m5_fvg_correct_dir             398
target_found                   398
rr_ok                          398
units_nonzero                  398
limit_placed                   0
entry_opened                   322
pyramid_added                  6
pyramid_blocked_min_target     883
drawdown_halt                  7022
daily_loss_halt                790
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      249
daily_pair_cap                 866
weekly_amd_confirmed           98
session_handover_closed        2
htf_draw_full_cascade          88
htf_draw_partial               281
htf_draw_counter               145
htf_fvg_5050_hit               25
ote_zone                       3
choch_confirmed                28
low_conviction                 0
judas_divergence               0
ny_continuation                160
pm_gate_pair_news              0
mm_golden_checked              2788
mm_golden_amd_ok               879
mm_golden_opened               243
pyramid_blocked_favour         3987
breakout_confirmed             328
soj_retest                     255
soj_sweep                      356
crt_turtle_soup                208
golden_rule_no                 220
mstruct_align                  374
phase_ny_judas                 212
gt_pool_sweep                  285
gt_disp_wick                   293
structure_stop_used            367
stop_capped_10pip              253
risk_cap_ok                    322
golden_rule_yes                143
phase_london_judas             193
gt_mp_discount                 67
gt_mp_extreme                  18
mm_golden_no_draw              561
soj_judas                      101
mstruct_minor_sweep            56
london_judas_ny_echo           13
pyramid_blocked_low_im         2697
smt_pair_opposing              37
sr_attempted                   219
sr_prev_session_ok             219
sr_enough_bars                 219
sr_consol_found                219
sr_consol_no_sweep             133
sr_fail_no_sweep               53
sr_pdliq_attempted             133
mm_golden_no_amd               122
sr_breakout_found              47
session_range_found            24
mm_golden_daily_cap            842
mm_golden_wrong_sweep          945
gt_macro_window                57
smt_pair_confirmed             97
m1_stop_used                   31
dxy_fvg_room                   74
gt_judas_reversal              52
sr_fail_low_swept_no_close_back 34
sr_fail_high_swept_no_close_back 46
sr_pdliq_width_ok              4
sr_pdliq_sweep                 4
pdliq_sweep_sized              87
golden_rule_sized              123
risk_cap_skip                  76
mm_golden_risk_cap             75
target_score_sized             148
crt_sweep_sized                69
pyramid_blocked_no_pattern     6
htf_fvg_breakout_sized         11
ny_continuation_gated          3
```

_income: R116,007 across 19 withdrawals · working balance R6,234_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            316   128  40.5%     60007.73   3.40
OB             215    94  43.7%     53834.22   5.81
BREAKER         25    15  60.0%      5382.34   5.78
other           15     7  46.7%      2016.55   2.98

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER M15            5     4  80.0%   3.70
BREAKER M5            20    11  55.0%   8.61
FVG H1                67    29  43.3%   4.83
FVG M15               65    31  47.7%   4.16
FVG M5               184    68  37.0%   2.65
OB M15                34    19  55.9%   9.19
OB M5                181    75  41.4%   5.31
other ?               15     7  46.7%   2.98

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            12     7  58.3%   4.88
BREAKER GBPUSD             9     6  66.7%  43.35
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               168    68  40.5%   3.72
FVG GBPUSD               136    56  41.2%   3.11
FVG NZDUSD                12     4  33.3%   3.03
OB EURUSD                136    58  42.6%   5.00
OB GBPUSD                 64    30  46.9%   6.13
OB NZDUSD                 15     6  40.0%  10.35
other EURUSD               4     2  50.0%  21.46
other GBPUSD              11     5  45.5%   2.35
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                    15     7  46.7%     134.44   2.98
amd_breaker_m15              4     3  75.0%     410.97   3.53
amd_breaker_m5              17    10  58.8%     213.66   9.46
amd_fvg_h1                  57    24  42.1%     192.81   3.76
amd_fvg_m15                 59    28  47.5%     272.96   3.97
amd_fvg_m5                 169    60  35.5%     131.67   2.61
amd_ob_m15                  26    12  46.2%     292.14   6.24
amd_ob_m5                  159    65  40.9%     216.85   4.81
mss_breaker_m15              1     1 100.0%     111.00    inf
mss_breaker_m5               3     1  33.3%      -1.58   0.90
mss_fvg_h1                  10     5  50.0%     704.98  10.73
mss_fvg_m15                  5     3  60.0%     366.31  72.84
mss_fvg_m5                  11     6  54.5%     170.97   4.15
mss_ob_m15                   7     6  85.7%     593.14 719.22
mss_ob_m5                   22    10  45.5%     338.49  12.16
pyramid_im0.8_fvg_m5         3     1  33.3%      -5.49   0.91
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         1     1 100.0%      88.80    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              521   226  43.4%    119034.99   4.49
session_range           43    17  39.5%      2442.32   1.66
(no AMD)                 7     1  14.3%      -236.48   0.46
```

_Session-range widths (n=219): median=28.1 p75=36.5 p90=52.1 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           353   152  43.1%     76903.38   3.83
against          187    80  42.8%     33795.99   4.62

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               184  42.9%   3.78
EURUSD SHORT against             136  41.2%   5.18
GBPUSD LONG against               51  47.1%   3.55
GBPUSD SHORT golden              169  43.2%   3.87
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           72    27  37.5%     12909.11   4.23
opposing            34    20  58.8%     10858.00  10.13
no divergence      434   185  42.6%     86932.26   3.77
```

# HistData backtest — 2024–2025 (2 yr)

## Results

```
trades                     457
win_rate_pct               44.0
profit_factor              3.93
starting_equity_ZAR        1000
ending_equity_ZAR          104446.99
pnl_ZAR                    103446.99
pnl_pct                    10344.7
max_drawdown_pct           -16.88
avg_win_ZAR                690.09
avg_loss_ZAR               -137.74
withdrawn_total_ZAR        97535.72
withdrawal_count           17
working_balance_ZAR        6911.27
working_max_drawdown_pct   18.72
```

## Gate funnel

```
checks                         60236
in_killzone                    60236
news_clear                     51600
nfp_fomc_ok                    44586
intermarket_signal             1995
pair_matches                   1995
mss_h1_m15_m5_ok               681
daily_bias_ok                  681
h1_bias_ok                     681
h4_bias_ok                     681
dealing_range_ok               43
consolidation_found            384
manipulation_correct_dir       319
m5_fvg_correct_dir             386
target_found                   386
rr_ok                          386
units_nonzero                  386
limit_placed                   0
entry_opened                   331
pyramid_added                  4
pyramid_blocked_min_target     823
drawdown_halt                  7236
daily_loss_halt                769
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      344
daily_pair_cap                 989
weekly_amd_confirmed           104
session_handover_closed        1
htf_draw_full_cascade          71
htf_draw_partial               284
htf_draw_counter               140
htf_fvg_5050_hit               17
ote_zone                       3
choch_confirmed                20
low_conviction                 0
judas_divergence               0
ny_continuation                147
pm_gate_pair_news              0
mm_golden_checked              3639
mm_golden_amd_ok               1099
mm_golden_no_draw              900
breakout_confirmed             351
soj_retest                     239
soj_sweep                      346
crt_turtle_soup                183
golden_rule_no                 206
mstruct_align                  369
phase_ny_judas                 193
gt_pool_sweep                  272
gt_disp_wick                   282
structure_stop_used            359
stop_capped_10pip              244
risk_cap_ok                    331
mm_golden_corr_block           1311
pyramid_blocked_favour         3392
golden_rule_yes                154
phase_london_judas             198
gt_mp_discount                 57
gt_mp_extreme                  12
soj_judas                      107
mstruct_minor_sweep            50
london_judas_ny_echo           8
pyramid_blocked_low_im         1925
smt_pair_opposing              37
sr_attempted                   207
sr_prev_session_ok             207
sr_enough_bars                 207
sr_consol_found                207
sr_consol_no_sweep             95
sr_fail_no_sweep               52
sr_pdliq_attempted             95
mm_golden_no_amd               85
sr_breakout_found              88
session_range_found            26
mm_golden_wrong_sweep          727
gt_macro_window                56
smt_pair_confirmed             100
m1_stop_used                   27
mm_golden_opened               122
mm_golden_daily_cap            417
dxy_fvg_room                   74
gt_judas_reversal              46
sr_fail_low_swept_no_close_back 13
sr_fail_high_swept_no_close_back 30
golden_rule_sized              133
target_score_sized             144
crt_sweep_sized                63
pdliq_sweep_sized              76
pyramid_blocked_no_pattern     6
risk_cap_skip                  55
sr_pdliq_width_ok              3
sr_pdliq_sweep                 3
htf_fvg_breakout_sized         7
mm_golden_risk_cap             77
ny_continuation_gated          3
```

_income: R97,536 across 17 withdrawals · working balance R6,911_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            271   117  43.2%     58022.77   3.46
OB             159    71  44.7%     40446.74   5.17
BREAKER         17     9  52.9%      2506.71   3.67
other           10     4  40.0%      2470.76   3.35

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER M15            4     3  75.0%   1.78
BREAKER M5            13     6  46.2%   7.90
FVG H1                60    29  48.3%   5.91
FVG M15               49    24  49.0%   4.20
FVG M5               162    64  39.5%   2.58
OB M15                20    10  50.0%   4.51
OB M5                139    61  43.9%   5.30
other ?               10     4  40.0%   3.35

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             9     4  44.4%   2.40
BREAKER GBPUSD             6     4  66.7%  20.49
BREAKER NZDUSD             2     1  50.0%   4.43
FVG EURUSD               140    61  43.6%   3.79
FVG GBPUSD               118    51  43.2%   3.00
FVG NZDUSD                13     5  38.5%   8.66
OB EURUSD                105    45  42.9%   4.77
OB GBPUSD                 39    20  51.3%   4.35
OB NZDUSD                 15     6  40.0%  10.22
other EURUSD               2     0   0.0%   0.00
other GBPUSD               8     4  50.0%   3.46
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                    10     4  40.0%     247.08   3.35
amd_breaker_m15              3     2  66.7%     132.83   1.61
amd_breaker_m5              10     5  50.0%     200.25   9.27
amd_fvg_h1                  50    24  48.0%     275.26   5.20
amd_fvg_m15                 40    19  47.5%     313.62   4.14
amd_fvg_m5                 146    56  38.4%     145.95   2.50
amd_ob_m15                  13     4  30.8%     115.13   1.93
amd_ob_m5                  118    50  42.4%     216.49   4.59
mss_breaker_m15              1     1 100.0%     111.00    inf
mss_breaker_m5               3     1  33.3%      -1.77   0.89
mss_fvg_h1                  10     5  50.0%     602.19   8.97
mss_fvg_m15                  8     5  62.5%     271.89   6.81
mss_fvg_m5                  12     6  50.0%     162.89   4.20
mss_ob_m15                   7     6  85.7%     593.14 719.22
mss_ob_m5                   21    11  52.4%     440.56  10.53
news_fvg_m5                  1     1 100.0%     443.68    inf
pyramid_im0.8_fvg_m5         2     0   0.0%     -88.15   0.00
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         1     1 100.0%     159.84    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              420   187  44.5%    103212.62   4.24
session_range           30    13  43.3%       501.67   1.17
(no AMD)                 7     1  14.3%      -267.31   0.43
```

_Session-range widths (n=207): median=33.5 p75=48.0 p90=80.6 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           246   116  47.2%     63923.41   3.78
against          181    73  40.3%     27192.23   3.54

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               126  46.0%   3.85
EURUSD SHORT against             130  40.0%   4.37
GBPUSD LONG against               51  41.2%   2.13
GBPUSD SHORT golden              120  48.3%   3.71
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           79    33  41.8%     15955.83   4.23
opposing            34    18  52.9%      8026.12   5.45
no divergence      314   138  43.9%     67133.69   3.49
```

# HistData backtest — 2024–2025 (2 yr)

## Results

```
trades                     385
win_rate_pct               44.4
profit_factor              4.29
starting_equity_ZAR        1000
ending_equity_ZAR          75258.41
pnl_ZAR                    74258.41
pnl_pct                    7425.84
max_drawdown_pct           -10.21
avg_win_ZAR                566.45
avg_loss_ZAR               -105.63
withdrawn_total_ZAR        66703.2
withdrawal_count           16
working_balance_ZAR        8555.21
working_max_drawdown_pct   15.92
```

## Gate funnel

```
checks                         60935
in_killzone                    60935
news_clear                     58701
nfp_fomc_ok                    50596
intermarket_signal             2573
pair_matches                   2573
mss_h1_m15_m5_ok               911
daily_bias_ok                  911
h1_bias_ok                     911
h4_bias_ok                     911
dealing_range_ok               74
consolidation_found            492
manipulation_correct_dir       414
m5_fvg_correct_dir             519
target_found                   519
rr_ok                          519
units_nonzero                  519
limit_placed                   0
entry_opened                   380
pyramid_added                  5
pyramid_blocked_min_target     685
drawdown_halt                  1032
daily_loss_halt                458
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      314
daily_pair_cap                 1182
weekly_amd_confirmed           154
session_handover_closed        0
htf_draw_full_cascade          150
htf_draw_partial               339
htf_draw_counter               157
htf_fvg_5050_hit               29
ote_zone                       3
choch_confirmed                28
low_conviction                 0
judas_divergence               0
ny_continuation                217
pm_gate_pair_news              0
breakout_confirmed             501
soj_retest                     322
soj_sweep                      475
crt_turtle_soup                255
golden_rule_no                 254
mstruct_align                  490
phase_ny_judas                 273
gt_pool_sweep                  386
gt_disp_wick                   379
structure_stop_used            480
stop_capped_10pip              339
risk_cap_ok                    380
pyramid_blocked_favour         3136
golden_rule_yes                226
phase_london_judas             254
gt_mp_discount                 85
gt_mp_extreme                  21
soj_judas                      153
mstruct_minor_sweep            60
london_judas_ny_echo           15
pyramid_blocked_low_im         1623
smt_pair_opposing              41
sr_attempted                   43
sr_prev_session_ok             43
sr_enough_bars                 43
sr_consol_found                43
sr_consol_no_sweep             38
sr_fail_low_swept_no_close_back 21
sr_pdliq_attempted             38
sr_pdliq_width_ok              3
gt_macro_window                68
smt_pair_confirmed             135
m1_stop_used                   39
session_range_found            5
dxy_fvg_room                   91
gt_judas_reversal              57
sr_fail_high_swept_no_close_back 15
golden_rule_sized              198
crt_sweep_sized                93
pdliq_sweep_sized              108
target_score_sized             190
risk_cap_skip                  139
htf_fvg_breakout_sized         15
pyramid_blocked_no_pattern     6
phase_ny_extend                1
ny_continuation_gated          3
phase_london_watch             1
sr_fail_no_sweep               2
phase_london_breakout          1
```

_income: R66,703 across 16 withdrawals · working balance R8,555_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            223    92  41.3%     35553.74   3.38
OB             148    70  47.3%     35583.23   5.92
BREAKER         14     9  64.3%      3121.44   7.76

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER M15            2     2 100.0%    inf
BREAKER M5            12     7  58.3%   5.18
FVG H1                52    25  48.1%   6.73
FVG M15               40    16  40.0%   2.74
FVG M5               131    51  38.9%   2.58
OB M15                21    13  61.9%   6.83
OB M5                127    57  44.9%   5.74

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             7     5  71.4% 136.49
BREAKER GBPUSD             3     2  66.7%   7.27
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               120    50  41.7%   3.81
FVG GBPUSD                88    38  43.2%   3.31
FVG NZDUSD                15     4  26.7%   1.03
OB EURUSD                101    43  42.6%   4.87
OB GBPUSD                 31    21  67.7%   6.64
OB NZDUSD                 16     6  37.5%   9.98
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     1 100.0%     990.67    inf
amd_breaker_m5               9     6  66.7%     215.85   5.68
amd_fvg_h1                  37    18  48.6%     245.94   6.24
amd_fvg_m15                 28    10  35.7%     134.68   2.21
amd_fvg_m5                 103    37  35.9%     104.63   2.68
amd_ob_m15                  13     6  46.2%     211.70   3.28
amd_ob_m5                  100    45  45.0%     214.42   5.49
mss_breaker_m15              1     1 100.0%     199.80    inf
mss_breaker_m5               3     1  33.3%      -3.89   0.75
mss_fvg_h1                  15     7  46.7%     438.45   7.56
mss_fvg_m15                 11     6  54.5%     287.78   6.29
mss_fvg_m5                  24    12  50.0%      82.51   2.18
mss_ob_m15                   7     6  85.7%     593.14 719.22
mss_ob_m5                   27    12  44.4%     262.12   6.68
news_fvg_m5                  1     1 100.0%     443.68    inf
pyramid_im0.8_fvg_m5         2     0   0.0%     -88.15   0.00
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         1     1 100.0%      88.80    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              353   158  44.8%     72502.30   4.48
session_range            3     2  66.7%       721.24  44.32
(no AMD)                29    11  37.9%      1034.88   1.59
```

_Session-range widths (n=43): median=28.6 p75=48.2 p90=52.7 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           146    73  50.0%     32869.98   4.39
against          204    86  42.2%     31670.73   4.06

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                85  47.1%   4.52
EURUSD SHORT against             143  40.6%   4.24
GBPUSD LONG against               61  45.9%   3.71
GBPUSD SHORT golden               61  54.1%   4.23
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           89    36  40.4%     15533.66   3.84
opposing            41    25  61.0%     12847.28   8.13
no divergence      220    98  44.5%     36159.77   3.83
```

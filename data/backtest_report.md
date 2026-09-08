# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     454
win_rate_pct               41.9
profit_factor              2.77
starting_equity_ZAR        1000
ending_equity_ZAR          52494.61
pnl_ZAR                    51494.61
pnl_pct                    5149.46
max_drawdown_pct           -19.36
avg_win_ZAR                424.46
avg_loss_ZAR               -110.42
withdrawn_total_ZAR        47388.68
withdrawal_count           15
working_balance_ZAR        5105.94
working_max_drawdown_pct   26.23
```

## Gate funnel

```
checks                         58593
in_killzone                    58593
news_clear                     53385
nfp_fomc_ok                    45919
intermarket_signal             2998
pair_matches                   2998
mss_h1_m15_m5_ok               1037
daily_bias_ok                  1037
h1_bias_ok                     1037
h4_bias_ok                     1037
dealing_range_ok               95
consolidation_found            497
manipulation_correct_dir       413
m5_fvg_correct_dir             481
target_found                   481
rr_ok                          481
units_nonzero                  481
limit_placed                   0
entry_opened                   413
pyramid_added                  13
pyramid_blocked_min_target     404
drawdown_halt                  3723
daily_loss_halt                801
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      838
daily_pair_cap                 2145
weekly_amd_confirmed           170
session_handover_closed        5
htf_draw_full_cascade          89
htf_draw_partial               345
htf_draw_counter               195
htf_fvg_5050_hit               19
ote_zone                       10
choch_confirmed                9
low_conviction                 0
judas_divergence               3
ny_continuation                178
pm_gate_pair_news              0
dxy_flat                       33591
dxy_directional                9345
eurgbp_directional             7507
mss_no_dxy                     1941
mm_golden_checked              5362
mm_golden_amd_ok               2623
mm_golden_ob_failed            2071
im_score_low                   4988
breakout_confirmed             532
soj_judas                      184
soj_sweep                      441
crt_turtle_soup                241
golden_rule_yes                202
phase_ny_judas                 225
gt_pool_sweep                  369
gt_disp_wick                   347
structure_stop_used            451
stop_capped_10pip              361
risk_cap_ok                    413
pyramid_blocked_favour         2498
mm_golden_wrong_sweep          791
dxy_fvg_room                   67
mstruct_align                  478
phase_london_judas             281
gt_macro_window                89
mm_golden_corr_block           443
pyramid_blocked_low_im         901
eurgbp_flat                    85
eurgbp_flat_gbp_blocked        52
mm_golden_via_own_ob           112
mm_golden_smt_yes              72
mm_golden_no_draw              42
golden_rule_no                 191
mm_golden_other_pair_open      1262
mm_golden_ob_untested          409
soj_retest                     257
smt_pair_opposing              56
gt_mp_discount                 116
smt_pair_confirmed             118
mstruct_minor_sweep            90
m1_stop_used                   30
gt_mp_extreme                  30
mm_golden_via_cascade          1
mm_golden_opened               28
mm_golden_daily_cap            158
gt_judas_reversal              47
sr_attempted                   379
sr_prev_session_ok             379
sr_enough_bars                 379
sr_consol_found                362
sr_breakout_found              242
session_range_found            31
mm_golden_no_smt               41
mss_no_pair                    20
sr_consol_no_sweep             78
sr_fail_no_sweep               35
sr_pdliq_attempted             95
mm_golden_no_amd               85
ny_continuation_gated          6
london_judas_ny_echo           6
sr_fail_high_swept_no_close_back 15
golden_rule_sized              150
mm_golden_no_retrace           30
crt_sweep_sized                75
risk_cap_skip                  68
target_score_sized             134
mm_golden_risk_cap             2
pdliq_sweep_sized              68
htf_fvg_breakout_sized         7
sr_fail_both_swept             11
sr_fail_low_swept_no_close_back 17
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R47,389 across 15 withdrawals · working balance R5,106_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            308   136  44.2%     38906.24   3.11
OB             127    49  38.6%     12665.69   2.37
BREAKER         18     5  27.8%       -72.68   0.95
other            1     0   0.0%        -4.63   0.00

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             2     1  50.0%   2.22
BREAKER M15            5     2  40.0%   2.91
BREAKER M5            11     2  18.2%   0.14
FVG H1                37    17  45.9%   6.05
FVG M15               46    23  50.0%   3.73
FVG M5               225    96  42.7%   2.74
OB M15                31    14  45.2%   2.52
OB M5                 96    35  36.5%   2.34
other ?                1     0   0.0%   0.00

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             4     1  25.0%   0.49
BREAKER GBPUSD             8     4  50.0%  11.48
BREAKER NZDUSD             6     0   0.0%   0.00
FVG EURUSD                92    41  44.6%   4.73
FVG GBPUSD               165    74  44.8%   2.51
FVG NZDUSD                51    21  41.2%   2.72
OB EURUSD                 44    16  36.4%   2.07
OB GBPUSD                 43    20  46.5%   4.80
OB NZDUSD                 40    13  32.5%   0.80
other EURUSD               1     0   0.0%   0.00
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                     1     0   0.0%      -4.63   0.00
amd_breaker_h1               1     0   0.0%     -28.86   0.00
amd_breaker_m15              1     0   0.0%    -168.17   0.00
amd_breaker_m5               8     2  25.0%     -29.54   0.39
amd_fvg_h1                  30    16  53.3%     226.29   8.94
amd_fvg_m15                 35    17  48.6%     140.46   3.14
amd_fvg_m5                 186    85  45.7%     142.92   3.36
amd_ob_m15                  18     8  44.4%     116.97   2.79
amd_ob_m5                   75    27  36.0%     109.37   2.39
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              4     2  50.0%     237.87   4.92
mss_breaker_m5               3     0   0.0%    -218.33   0.00
mss_fvg_h1                   5     1  20.0%     -58.34   0.11
mss_fvg_m15                  8     5  62.5%     252.84   8.57
mss_fvg_m5                  29    10  34.5%     -21.45   0.77
mss_ob_m15                  13     6  46.2%      27.90   1.81
mss_ob_m5                   20     7  35.0%      91.75   2.06
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%    -185.72   0.00
pyramid_im1.0_fvg_m15        1     1 100.0%     158.17    inf
pyramid_im1.0_fvg_m5         2     0   0.0%     -23.59   0.00
pyramid_wamd1.0_fvg_h1       2     0   0.0%     -43.71   0.00
pyramid_wamd1.0_fvg_m15       1     0   0.0%     -12.49   0.00
pyramid_wamd1.0_fvg_m5       6     1  16.7%     -20.29   0.22
pyramid_wamd1.0_ob_m5        1     1 100.0%     159.84    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              417   175  42.0%     49737.75   2.85
session_range           29    13  44.8%      2231.11   2.51
(no AMD)                 8     2  25.0%      -474.24   0.43
```

_Session-range widths (n=379): median=59.5 p75=77.1 p90=100.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           179    73  40.8%     23805.93   2.98
against          178    83  46.6%     24549.18   3.65

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                50  30.0%   2.53
EURUSD SHORT against              91  47.3%   4.34
GBPUSD LONG against               87  46.0%   2.92
GBPUSD SHORT golden              129  45.0%   3.12
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           94    41  43.6%     14840.48   3.66
opposing            54    26  48.1%      5129.03   3.44
no divergence      209    89  42.6%     28385.60   3.08
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             30    12  40.0%       695.39   1.46
2            117    49  41.9%      8084.28   1.93
3            195    81  41.5%     23381.62   2.97
4             96    39  40.6%     16634.78   3.57
5             15     8  53.3%      2581.93   4.96

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           290  41.7%   3.14      164  42.1%   2.10
NFP week Mon/Tue          41  46.3%   2.71      413  41.4%   2.77
Rate decision             41  48.8%   2.54      413  41.2%   2.80
PD prov (sweep)          375  42.1%   3.01       79  40.5%   1.75
Seasonal lean              0   0.0%   0.00      454  41.9%   2.77
HTF OB Context           162  39.5%   2.89      292  43.2%   2.69
D1 Draw                  399  41.9%   3.00       55  41.8%   1.63
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 8     2  25.0%      2296.46   5.64
continuation         154    62  40.3%     18785.82   2.76
(none)               292   126  43.2%     30412.33   2.69

Liq type          Trades    WR%     PF
----------------------------------------
breaker               31  45.2%   3.19
d1_fvg                99  36.4%   2.50
ob                    10  30.0%   2.99
pdhl                  14  42.9%   4.20
w_fvg                  8  62.5%   5.89
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     2  66.7%       310.70   2.14
equal_hl             396   165  41.7%     48058.13   3.01
(none)                55    23  41.8%      3125.78   1.63
```

# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     370
win_rate_pct               43.8
profit_factor              3.38
starting_equity_ZAR        1000
ending_equity_ZAR          55195.1
pnl_ZAR                    54195.1
pnl_pct                    5419.51
max_drawdown_pct           -13.24
avg_win_ZAR                475.09
avg_loss_ZAR               -109.47
withdrawn_total_ZAR        48627.27
withdrawal_count           16
working_balance_ZAR        6567.83
working_max_drawdown_pct   19.34
```

## Gate funnel

```
checks                         59167
in_killzone                    59167
news_clear                     55618
nfp_fomc_ok                    47465
intermarket_signal             2834
pair_matches                   2834
mss_h1_m15_m5_ok               957
daily_bias_ok                  957
h1_bias_ok                     957
h4_bias_ok                     957
dealing_range_ok               33
consolidation_found            456
manipulation_correct_dir       406
m5_fvg_correct_dir             456
target_found                   456
rr_ok                          456
units_nonzero                  456
limit_placed                   0
entry_opened                   343
pyramid_added                  9
pyramid_blocked_min_target     339
drawdown_halt                  2313
daily_loss_halt                563
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1926
weekly_amd_confirmed           157
session_handover_closed        3
htf_draw_full_cascade          112
htf_draw_partial               294
htf_draw_counter               186
htf_fvg_5050_hit               9
ote_zone                       2
choch_confirmed                11
low_conviction                 0
judas_divergence               2
ny_continuation                187
pm_gate_pair_news              0
dxy_flat                       34805
mm_quad_1a                     12302
mm_quad_selected               21976
mm_golden_checked              21976
mm_golden_amd_ok               11585
mm_golden_ob_failed            8701
mm_quad_other_pair             22562
dxy_directional                10516
eurgbp_flat                    1925
eurgbp_flat_gbp_blocked        1388
breakout_confirmed             546
sr_attempted                   1797
sr_prev_session_ok             1797
sr_enough_bars                 1797
sr_consol_found                1652
sr_breakout_found              566
session_range_found            30
soj_retest                     229
soj_sweep                      411
golden_rule_no                 228
mstruct_align                  442
phase_ny_judas                 232
gt_pool_sweep                  365
structure_stop_used            426
stop_capped_10pip              368
risk_cap_ok                    343
mm_golden_other_pair_open      1236
pyramid_blocked_low_im         1068
eurgbp_directional             6183
soj_judas                      182
crt_turtle_soup                213
golden_rule_yes                220
gt_disp_wick                   335
m1_stop_used                   30
pyramid_blocked_favour         1852
dxy_fvg_room                   56
phase_london_judas             236
gt_macro_window                60
im_score_low                   4057
mm_quad_2a                     10136
mm_golden_corr_block           85
mm_quad_2b                     9758
mm_golden_wrong_sweep          7916
mm_quad_none_eurgbp_flat       567
mm_golden_via_own_ob           859
mm_golden_smt_yes              654
mm_golden_im_eurgbp            366
mm_golden_ob_untested          1731
mm_golden_no_smt               279
mm_quad_1b                     12342
smt_pair_opposing              57
gt_mp_discount                 85
mm_golden_no_retrace           204
mm_golden_im_ok                288
mm_golden_no_draw              269
smt_pair_confirmed             144
mstruct_minor_sweep            71
mm_golden_via_cascade          74
gt_judas_reversal              45
sr_consol_no_sweep             735
sr_fail_no_sweep               431
sr_pdliq_attempted             880
mm_golden_no_amd               867
sr_fail_high_swept_no_close_back 50
gt_mp_extreme                  18
mm_golden_opened               18
mm_golden_daily_cap            287
ny_continuation_gated          6
sr_fail_low_swept_no_close_back 84
sr_fail_both_swept             158
london_judas_ny_echo           7
mm_quad_none_dxy_flat          135
mm_golden_ob_none              16
target_score_sized             126
crt_sweep_sized                72
risk_cap_skip                  113
golden_rule_sized              181
mm_golden_risk_cap             1
pdliq_sweep_sized              63
htf_fvg_breakout_sized         3
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
sr_fail_no_tail                12
```

_income: R48,627 across 16 withdrawals · working balance R6,568_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            269   119  44.2%     41987.73   3.61
OB              88    37  42.0%     12114.42   3.31
BREAKER         13     6  46.2%        92.95   1.06

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            4     1  25.0%   0.99
BREAKER M5             8     4  50.0%   1.07
FVG H1                41    17  41.5%   3.74
FVG M15               40    17  42.5%   7.03
FVG M5               188    85  45.2%   3.19
OB M15                14     6  42.9%   3.04
OB M5                 74    31  41.9%   3.33

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            10     4  40.0%   0.50
BREAKER GBPUSD             3     2  66.7%   2.38
FVG EURUSD               123    51  41.5%   4.24
FVG GBPUSD               135    65  48.1%   3.26
FVG NZDUSD                11     3  27.3%   1.88
OB EURUSD                 52    16  30.8%   1.27
OB GBPUSD                 29    16  55.2%   9.95
OB NZDUSD                  7     5  71.4%  41.56
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              2     0   0.0%    -429.78   0.00
amd_breaker_m5               5     3  60.0%     -10.70   0.88
amd_fvg_h1                  35    16  45.7%     205.75   4.33
amd_fvg_m15                 31    12  38.7%     161.82   4.65
amd_fvg_m5                 167    79  47.3%     157.12   3.57
amd_ob_m15                  11     6  54.5%      73.17   3.87
amd_ob_m5                   58    23  39.7%     110.74   2.49
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     1  50.0%     427.00   8.10
mss_breaker_m5               3     1  33.3%      29.26   4.24
mss_fvg_h1                   5     1  20.0%     -43.60   0.42
mss_fvg_m15                  7     4  57.1%     423.52  77.31
mss_fvg_m5                  13     5  38.5%      27.50   1.22
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   16     8  50.0%     310.16   9.74
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  1     0   0.0%     -46.25   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         2     1  50.0%      -4.63   0.90
pyramid_im1.0_fvg_m5         2     0   0.0%     -23.59   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              331   145  43.8%     50710.25   3.53
session_range           28    12  42.9%      2287.93   2.10
(no AMD)                11     5  45.5%      1196.92   2.91
```

_Session-range widths (n=1797): median=59.6 p75=85.9 p90=108.3 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           156    75  48.1%     28673.59   3.62
against          196    79  40.3%     23055.41   3.10

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                63  41.3%   2.56
EURUSD SHORT against             122  36.9%   3.15
GBPUSD LONG against               74  45.9%   3.02
GBPUSD SHORT golden               93  52.7%   4.50
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          105    48  45.7%     18172.43   3.68
opposing            42    20  47.6%      3934.50   5.09
no divergence      205    86  42.0%     29622.07   3.09
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             27     7  25.9%      -364.63   0.80
2             93    42  45.2%     13454.61   3.95
3            159    68  42.8%     22857.73   3.10
4             79    35  44.3%     15140.06   3.97
5             11     9  81.8%      2990.70   8.01

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           244  44.3%   3.80      126  42.9%   2.58
NFP week Mon/Tue          36  58.3%   3.50      334  42.2%   3.37
Rate decision             33  42.4%   2.08      337  43.9%   3.59
PD prov (sweep)          331  44.1%   3.26       39  41.0%   4.54
Seasonal lean              0   0.0%   0.00      370  43.8%   3.38
HTF OB Context            96  50.0%   4.56      274  41.6%   2.90
D1 Draw                  321  44.5%   3.68       49  38.8%   2.04
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 6     1  16.7%      -331.96   0.46
continuation          90    47  52.2%     23816.64   4.98
(none)               274   114  41.6%     30710.42   2.90

Liq type          Trades    WR%     PF
----------------------------------------
breaker               20  50.0%   2.83
d1_fvg                58  48.3%   4.46
ob                     4  75.0% 371.94
pdhl                   8  37.5%   0.68
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             320   142  44.4%     49700.57   3.67
(none)                49    19  38.8%      4296.81   2.04
```

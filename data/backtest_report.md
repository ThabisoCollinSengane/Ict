# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     447
win_rate_pct               42.5
profit_factor              3.16
starting_equity_ZAR        1000
ending_equity_ZAR          60611.32
pnl_ZAR                    59611.32
pnl_pct                    5961.13
max_drawdown_pct           -15.91
avg_win_ZAR                459.14
avg_loss_ZAR               -107.49
withdrawn_total_ZAR        53559.4
withdrawal_count           17
working_balance_ZAR        7051.92
working_max_drawdown_pct   26.17
```

## Gate funnel

```
checks                         58555
in_killzone                    58555
news_clear                     53706
nfp_fomc_ok                    46559
intermarket_signal             2992
pair_matches                   2992
mss_h1_m15_m5_ok               1056
daily_bias_ok                  1056
h1_bias_ok                     1056
h4_bias_ok                     1056
dealing_range_ok               90
consolidation_found            522
manipulation_correct_dir       451
m5_fvg_correct_dir             504
target_found                   504
rr_ok                          504
units_nonzero                  504
limit_placed                   0
entry_opened                   405
pyramid_added                  14
pyramid_blocked_min_target     386
drawdown_halt                  3433
daily_loss_halt                744
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      630
daily_pair_cap                 2158
weekly_amd_confirmed           176
session_handover_closed        4
htf_draw_full_cascade          115
htf_draw_partial               340
htf_draw_counter               189
htf_fvg_5050_hit               17
ote_zone                       14
choch_confirmed                11
low_conviction                 0
judas_divergence               3
ny_continuation                198
pm_gate_pair_news              0
dxy_flat                       34197
dxy_directional                9574
eurgbp_directional             7165
im_score_low                   4703
mm_golden_checked              5254
mm_golden_amd_ok               2572
mm_golden_ob_failed            2019
mss_no_dxy                     1915
eurgbp_flat                    444
eurgbp_flat_gbp_blocked        321
breakout_confirmed             560
sr_attempted                   380
sr_prev_session_ok             380
sr_enough_bars                 380
sr_consol_found                363
sr_breakout_found              219
session_range_found            29
soj_retest                     269
soj_sweep                      466
golden_rule_no                 204
mstruct_align                  508
phase_ny_judas                 246
gt_pool_sweep                  395
structure_stop_used            472
stop_capped_10pip              385
risk_cap_ok                    405
mm_golden_other_pair_open      1266
pyramid_blocked_low_im         978
soj_judas                      197
crt_turtle_soup                271
golden_rule_yes                234
gt_disp_wick                   369
m1_stop_used                   32
pyramid_blocked_favour         2471
dxy_fvg_room                   73
phase_london_judas             288
gt_macro_window                77
mss_no_pair                    21
mm_golden_wrong_sweep          789
mm_golden_via_own_ob           109
mm_golden_smt_yes              78
mm_golden_opened               28
mm_golden_no_draw              48
mm_golden_ob_untested          399
mm_golden_corr_block           372
smt_pair_opposing              55
gt_mp_discount                 126
smt_pair_confirmed             120
mstruct_minor_sweep            74
gt_mp_extreme                  36
mm_golden_via_cascade          5
mm_golden_daily_cap            155
gt_judas_reversal              48
mm_golden_no_smt               36
sr_consol_no_sweep             96
sr_fail_no_sweep               36
sr_pdliq_attempted             113
mm_golden_no_amd               100
london_judas_ny_echo           6
sr_fail_high_swept_no_close_back 15
golden_rule_sized              176
target_score_sized             149
mm_golden_no_retrace           40
crt_sweep_sized                83
pdliq_sweep_sized              90
risk_cap_skip                  99
mm_golden_risk_cap             2
ny_continuation_gated          3
htf_fvg_breakout_sized         7
sr_fail_both_swept             24
sr_fail_low_swept_no_close_back 21
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R53,559 across 17 withdrawals · working balance R7,052_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            304   133  43.8%     44133.07   3.53
OB             125    51  40.8%     15201.39   2.75
BREAKER         17     6  35.3%       281.49   1.19
other            1     0   0.0%        -4.63   0.00

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             2     1  50.0%   0.46
BREAKER M15            4     2  50.0%   3.85
BREAKER M5            11     3  27.3%   0.49
FVG H1                39    18  46.2%   4.81
FVG M15               45    23  51.1%   4.59
FVG M5               220    92  41.8%   3.21
OB M15                29    14  48.3%   2.86
OB M5                 96    37  38.5%   2.73
other ?                1     0   0.0%   0.00

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             6     3  50.0%   2.09
BREAKER GBPUSD             6     3  50.0%  14.52
BREAKER NZDUSD             5     0   0.0%   0.00
FVG EURUSD               110    47  42.7%   4.00
FVG GBPUSD               156    72  46.2%   3.20
FVG NZDUSD                38    14  36.8%   3.56
OB EURUSD                 48    16  33.3%   1.58
OB GBPUSD                 42    23  54.8%   6.55
OB NZDUSD                 35    12  34.3%   1.15
other EURUSD               1     0   0.0%   0.00
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                     1     0   0.0%      -4.63   0.00
amd_breaker_h1               1     0   0.0%    -140.48   0.00
amd_breaker_m15              1     0   0.0%     -93.43   0.00
amd_breaker_m5               7     1  14.3%     -38.93   0.30
amd_fvg_h1                  32    18  56.2%     223.27   6.26
amd_fvg_m15                 34    17  50.0%     139.93   3.81
amd_fvg_m5                 190    85  44.7%     164.29   3.69
amd_ob_m15                  17     8  47.1%     129.48   3.34
amd_ob_m5                   78    30  38.5%     127.45   2.70
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              3     2  66.7%     325.83   5.52
mss_breaker_m5               4     2  50.0%     -63.44   0.61
mss_fvg_h1                   5     0   0.0%     -64.44   0.00
mss_fvg_m15                  7     5  71.4%     305.15  18.70
mss_fvg_m5                  19     6  31.6%      -4.35   0.94
mss_ob_m15                  12     6  50.0%      30.46   1.83
mss_ob_m5                   18     7  38.9%     149.63   2.88
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%    -185.72   0.00
pyramid_im1.0_fvg_m15        1     1 100.0%     158.17    inf
pyramid_im1.0_fvg_m5         3     1  33.3%      13.57   1.86
pyramid_wamd1.0_fvg_h1       2     0   0.0%     -43.71   0.00
pyramid_wamd1.0_fvg_m15       2     0   0.0%     -54.81   0.00
pyramid_wamd1.0_fvg_m5       6     0   0.0%     -56.29   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              413   176  42.6%     56304.94   3.17
session_range           28    11  39.3%      3065.83   3.07
(no AMD)                 6     3  50.0%       240.56   2.04
```

_Session-range widths (n=380): median=59.5 p75=77.1 p90=95.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           181    84  46.4%     30009.51   3.61
against          188    80  42.6%     25648.57   3.51

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                59  37.3%   2.48
EURUSD SHORT against             106  41.5%   3.44
GBPUSD LONG against               82  43.9%   3.63
GBPUSD SHORT golden              122  50.8%   4.08
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           93    45  48.4%     20059.70   5.06
opposing            53    25  47.2%      6079.42   3.46
no divergence      223    94  42.2%     29518.96   3.07
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             34    13  38.2%       915.90   1.61
2            103    45  43.7%     10295.80   2.57
3            204    82  40.2%     26892.73   2.97
4             95    43  45.3%     19469.77   4.53
5             10     6  60.0%      1920.51   6.21

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           289  42.6%   3.47      158  42.4%   2.50
NFP week Mon/Tue          33  48.5%   3.20      414  42.0%   3.15
Rate decision             38  52.6%   3.52      409  41.6%   3.12
PD prov (sweep)          381  42.8%   3.34       66  40.9%   2.22
Seasonal lean              0   0.0%   0.00      447  42.5%   3.16
HTF OB Context           148  43.2%   3.56      299  42.1%   2.94
D1 Draw                  393  42.0%   3.29       54  46.3%   2.45
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 9     3  33.3%      2573.96   6.21
continuation         139    61  43.9%     22700.29   3.42
(none)               299   126  42.1%     34337.08   2.94

Liq type          Trades    WR%     PF
----------------------------------------
breaker               31  48.4%   3.43
d1_fvg                91  42.9%   3.61
ob                     7  28.6%   6.91
pdhl                  12  33.3%   1.41
w_fvg                  7  57.1%   8.68
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 2     2 100.0%       583.86    inf
equal_hl             391   163  41.7%     52662.59   3.27
(none)                54    25  46.3%      6364.87   2.45
```

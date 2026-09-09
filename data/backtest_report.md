# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     912
win_rate_pct               26.4
profit_factor              1.49
starting_equity_ZAR        1000
ending_equity_ZAR          18011.59
pnl_ZAR                    17011.59
pnl_pct                    1701.16
max_drawdown_pct           -45.35
avg_win_ZAR                215.31
avg_loss_ZAR               -51.98
withdrawn_total_ZAR        12378.14
withdrawal_count           3
working_balance_ZAR        5633.45
working_max_drawdown_pct   45.35
```

## Gate funnel

```
checks                         54778
in_killzone                    54778
news_clear                     44741
nfp_fomc_ok                    37336
intermarket_signal             5878
pair_matches                   5878
mss_h1_m15_m5_ok               3493
daily_bias_ok                  3493
h1_bias_ok                     3493
h4_bias_ok                     3493
dealing_range_ok               679
consolidation_found            1046
manipulation_correct_dir       726
m5_fvg_correct_dir             881
target_found                   881
rr_ok                          881
units_nonzero                  881
limit_placed                   0
entry_opened                   869
pyramid_added                  23
pyramid_blocked_min_target     850
drawdown_halt                  8106
daily_loss_halt                1343
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      7174
daily_pair_cap                 5753
weekly_amd_confirmed           451
session_handover_closed        24
htf_draw_full_cascade          118
htf_draw_partial               878
htf_draw_counter               1042
htf_fvg_5050_hit               112
ote_zone                       146
choch_confirmed                26
low_conviction                 0
judas_divergence               15
ny_continuation                293
pm_gate_pair_news              0
dxy_real_used                  83216
dxy_directional                20989
eurgbp_directional             16653
im_score_low                   11679
mss_no_dxy                     2065
mm_golden_checked              16831
mm_golden_amd_ok               7113
mm_golden_via_own_ob           650
mm_golden_smt_yes              502
mm_golden_im_dxy_opposes       199
mm_golden_no_smt               219
mm_golden_ob_failed            5088
mss_no_pair                    320
dxy_fvg_room                   227
crt_turtle_soup                492
golden_rule_yes                438
mstruct_align                  1058
mstruct_minor_sweep            380
phase_london_judas             604
gt_pool_sweep                  718
gt_disp_wick                   615
m1_stop_used                   118
stop_capped_10pip              532
risk_cap_ok                    869
pyramid_blocked_favour         6074
soj_retest                     532
soj_sweep                      732
phase_ny_judas                 477
gt_judas_reversal              191
structure_stop_used            763
soj_judas                      200
breakout_confirmed             1239
mm_golden_wrong_sweep          4553
gt_macro_window                200
mm_golden_corr_block           1210
golden_rule_no                 432
mm_golden_other_pair_open      3192
eurgbp_flat                    123
eurgbp_flat_gbp_blocked        89
pyramid_blocked_low_im         493
mm_golden_ob_untested          1172
sr_attempted                   1138
sr_prev_session_ok             1138
sr_enough_bars                 1138
sr_consol_found                1028
sr_breakout_found              424
session_range_found            30
mm_golden_im_eurgbp            195
dxy_flat                       3420
smt_pair_opposing              139
gt_mp_discount                 271
smt_pair_confirmed             226
mm_golden_im_ok                108
mm_golden_no_draw              88
london_judas_ny_echo           28
gt_mp_extreme                  121
mm_golden_via_cascade          71
sr_consol_no_sweep             355
sr_fail_high_swept_no_close_back 44
sr_pdliq_attempted             465
mm_golden_no_amd               410
sr_fail_no_sweep               195
sr_pdliq_width_ok              2
sr_pdliq_sweep                 2
sr_fail_low_swept_no_close_back 21
ny_continuation_gated          170
mm_golden_no_retrace           116
mm_golden_opened               20
mm_golden_daily_cap            353
phase_ny_extend                7
sr_fail_both_swept             95
mm_golden_ob_none              16
phase_london_watch             11
crt_sweep_sized                56
target_score_sized             107
pdliq_sweep_sized              41
golden_rule_sized              94
htf_fvg_breakout_sized         10
risk_cap_skip                  12
```

_income: R12,378 across 3 withdrawals · working balance R5,633_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            478   137  28.7%      6657.28   1.35
OB             338    80  23.7%      1940.81   1.15
BREAKER         96    24  25.0%      8413.50   4.06

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             4     1  25.0%   0.20
BREAKER M15           21     4  19.0%   2.13
BREAKER M5            71    19  26.8%   5.16
FVG H1                79    19  24.1%   2.71
FVG M15               87    26  29.9%   0.79
FVG M5               312    92  29.5%   1.27
OB M15                95    20  21.1%   0.81
OB M5                243    60  24.7%   1.29

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            31    11  35.5%   4.61
BREAKER GBPUSD            43     9  20.9%   4.54
BREAKER NZDUSD            22     4  18.2%   2.29
FVG EURUSD               149    33  22.1%   1.11
FVG GBPUSD               253    84  33.2%   1.71
FVG NZDUSD                76    20  26.3%   0.92
OB EURUSD                109    20  18.3%   0.60
OB GBPUSD                130    37  28.5%   1.34
OB NZDUSD                 99    23  23.2%   1.40
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              6     1  16.7%     -14.74   0.29
amd_breaker_m5              45    12  26.7%     172.47   6.99
amd_fvg_h1                  46    11  23.9%      81.02   3.95
amd_fvg_m15                 61    16  26.2%     -26.15   0.56
amd_fvg_m5                 251    78  31.1%       4.79   1.12
amd_ob_m15                  56    14  25.0%      10.19   1.26
amd_ob_m5                  151    41  27.2%      24.93   1.68
mss_breaker_h1               4     1  25.0%     -63.71   0.20
mss_breaker_m15             15     3  20.0%      42.34   2.77
mss_breaker_m5              26     7  26.9%      13.87   1.55
mss_fvg_h1                  29     7  24.1%      23.48   1.53
mss_fvg_m15                 21     9  42.9%      26.52   1.52
mss_fvg_m5                  51    11  21.6%      36.54   2.49
mss_ob_m15                  39     6  15.4%     -33.66   0.24
mss_ob_m5                   87    19  21.8%     -10.86   0.73
news_fvg_h1                  1     0   0.0%     -46.25   0.00
pyramid_im1.0_fvg_h1         2     1  50.0%      63.45   7.02
pyramid_im1.0_fvg_m15        3     1  33.3%      22.20   4.13
pyramid_im1.0_fvg_m5         6     2  33.3%       4.07   1.25
pyramid_im1.0_ob_m5          5     0   0.0%     -27.57   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%     -17.58   0.00
pyramid_wamd1.0_fvg_m15       2     0   0.0%      -2.31   0.00
pyramid_wamd1.0_fvg_m5       4     1  25.0%      18.31   2.62
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              837   220  26.3%     18518.72   1.58
session_range           31    10  32.3%      -121.65   0.85
(no AMD)                44    11  25.0%     -1385.48   0.40
```

_Session-range widths (n=1138): median=60.3 p75=83.0 p90=108.3 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           320    88  27.5%      3823.33   1.28
against          395   106  26.8%     11245.05   1.87

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                88  22.7%   0.47
EURUSD SHORT against             201  21.9%   1.69
GBPUSD LONG against              194  32.0%   2.07
GBPUSD SHORT golden              232  29.3%   1.60
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          174    58  33.3%      2817.81   1.41
opposing           100    21  21.0%      3947.75   2.19
no divergence      441   115  26.1%      8302.82   1.50
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              6     3  50.0%       892.80  29.89
1             70    14  20.0%     -1200.08   0.57
2            273    63  23.1%      3933.75   1.44
3            342   101  29.5%      6770.46   1.46
4            191    50  26.2%      5968.05   1.86
5             30    10  33.3%       646.62   1.39

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           615  27.8%   1.68      297  23.6%   1.12
NFP week Mon/Tue         100  29.0%   1.80      812  26.1%   1.45
Rate decision             55  25.5%   1.13      857  26.5%   1.51
PD prov (sweep)          663  27.9%   1.56      249  22.5%   1.27
Seasonal lean              0   0.0%   0.00      912  26.4%   1.49
HTF OB Context           347  23.9%   1.29      565  28.0%   1.67
D1 Draw                  776  27.2%   1.54      136  22.1%   1.23
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                17     3  17.6%       140.45   1.12
continuation         330    80  24.2%      4777.39   1.31
(none)               565   158  28.0%     12093.75   1.67

Liq type          Trades    WR%     PF
----------------------------------------
breaker               71  31.0%   1.46
d1_fvg               217  22.1%   1.29
ob                     9  33.3%   0.42
pdhl                  31  16.1%   1.89
w_fvg                 19  26.3%   0.76
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 9     1  11.1%      -292.30   0.10
equal_hl             767   210  27.4%     15928.40   1.56
(none)               136    30  22.1%      1375.49   1.23
```

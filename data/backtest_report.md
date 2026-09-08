# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     388
win_rate_pct               43.6
profit_factor              3.5
starting_equity_ZAR        1000
ending_equity_ZAR          56395.51
pnl_ZAR                    55395.51
pnl_pct                    5539.55
max_drawdown_pct           -13.52
avg_win_ZAR                459.04
avg_loss_ZAR               -101.29
withdrawn_total_ZAR        49407.78
withdrawal_count           16
working_balance_ZAR        6987.73
working_max_drawdown_pct   21.89
```

## Gate funnel

```
checks                         59079
in_killzone                    59079
news_clear                     56209
nfp_fomc_ok                    48206
intermarket_signal             2844
pair_matches                   2844
mss_h1_m15_m5_ok               966
daily_bias_ok                  966
h1_bias_ok                     966
h4_bias_ok                     966
dealing_range_ok               33
consolidation_found            460
manipulation_correct_dir       412
m5_fvg_correct_dir             460
target_found                   460
rr_ok                          460
units_nonzero                  460
limit_placed                   0
entry_opened                   347
pyramid_added                  9
pyramid_blocked_min_target     324
drawdown_halt                  1510
daily_loss_halt                661
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1954
weekly_amd_confirmed           162
session_handover_closed        2
htf_draw_full_cascade          113
htf_draw_partial               293
htf_draw_counter               194
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               2
ny_continuation                188
pm_gate_pair_news              0
mm_golden_checked              5446
mm_golden_amd_ok               2930
mm_golden_ob_failed            2306
breakout_confirmed             557
sr_attempted                   420
sr_prev_session_ok             420
sr_enough_bars                 420
sr_consol_found                403
sr_breakout_found              245
session_range_found            30
soj_retest                     224
soj_sweep                      412
golden_rule_no                 224
mstruct_align                  445
phase_ny_judas                 231
gt_pool_sweep                  366
structure_stop_used            429
stop_capped_10pip              370
risk_cap_ok                    347
mm_golden_other_pair_open      1293
pyramid_blocked_low_im         1064
soj_judas                      188
crt_turtle_soup                215
golden_rule_yes                226
gt_disp_wick                   338
m1_stop_used                   31
pyramid_blocked_favour         1931
dxy_fvg_room                   57
phase_london_judas             241
gt_macro_window                62
mm_golden_corr_block           62
mm_golden_wrong_sweep          863
mm_golden_via_own_ob           109
mm_golden_smt_yes              79
mm_golden_no_draw              46
mm_golden_ob_untested          462
smt_pair_opposing              57
gt_mp_discount                 91
smt_pair_confirmed             147
mstruct_minor_sweep            67
mm_golden_via_cascade          5
mm_golden_opened               32
mm_golden_daily_cap            189
gt_judas_reversal              43
mm_golden_no_smt               35
gt_mp_extreme                  18
sr_consol_no_sweep             105
sr_fail_no_sweep               41
sr_pdliq_attempted             122
mm_golden_no_amd               109
ny_continuation_gated          6
london_judas_ny_echo           7
sr_fail_high_swept_no_close_back 17
sr_fail_low_swept_no_close_back 21
target_score_sized             126
crt_sweep_sized                72
risk_cap_skip                  113
golden_rule_sized              187
mm_golden_risk_cap             1
mm_golden_no_retrace           47
pdliq_sweep_sized              66
mm_golden_ob_none              1
sr_fail_both_swept             26
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R49,408 across 16 withdrawals · working balance R6,988_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            284   122  43.0%     41280.09   3.47
OB              91    41  45.1%     13191.74   3.73
BREAKER         12     6  50.0%       928.30   2.48
other            1     0   0.0%        -4.63   0.00

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             9     4  44.4%   6.13
FVG H1                44    18  40.9%   3.28
FVG M15               39    16  41.0%   6.28
FVG M5               201    88  43.8%   3.19
OB M15                15     8  53.3%   9.34
OB M5                 76    33  43.4%   3.34
other ?                1     0   0.0%   0.00

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             8     4  50.0%   0.89
BREAKER GBPUSD             4     2  50.0%  21.73
FVG EURUSD               128    53  41.4%   4.21
FVG GBPUSD               144    66  45.8%   3.07
FVG NZDUSD                12     3  25.0%   1.45
OB EURUSD                 52    17  32.7%   1.52
OB GBPUSD                 31    18  58.1%  10.10
OB NZDUSD                  8     6  75.0%  43.57
other EURUSD               1     0   0.0%   0.00
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                     1     0   0.0%      -4.63   0.00
amd_breaker_m15              1     0   0.0%    -541.12   0.00
amd_breaker_m5               6     3  50.0%      55.96   6.21
amd_fvg_h1                  38    17  44.7%     174.89   3.73
amd_fvg_m15                 30    11  36.7%     150.56   4.31
amd_fvg_m5                 180    82  45.6%     149.20   3.45
amd_ob_m15                  12     8  66.7%     223.71  12.32
amd_ob_m5                   60    25  41.7%      93.67   2.42
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   5     1  20.0%     -43.60   0.42
mss_fvg_m15                  7     4  57.1%     337.16  61.75
mss_fvg_m5                  12     5  41.7%      61.10   1.59
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   16     8  50.0%     310.16   9.74
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%     -43.94   0.00
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
m15_range              348   152  43.7%     51942.94   3.67
session_range           29    12  41.4%      2255.64   2.07
(no AMD)                11     5  45.5%      1196.92   2.91
```

_Session-range widths (n=420): median=57.3 p75=72.0 p90=100.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           174    82  47.1%     30580.90   3.97
against          194    78  40.2%     22622.32   3.06

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                70  41.4%   3.15
EURUSD SHORT against             119  37.8%   3.16
GBPUSD LONG against               75  44.0%   2.87
GBPUSD SHORT golden              104  51.0%   4.53
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          108    49  45.4%     19177.64   3.99
opposing            43    20  46.5%      3490.98   3.48
no divergence      217    91  41.9%     30534.61   3.27
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             27     7  25.9%      -380.58   0.79
2             94    43  45.7%     14515.59   4.49
3            172    71  41.3%     22832.09   3.08
4             85    39  45.9%     15250.25   4.04
5              9     8  88.9%      3061.53  15.01

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           251  45.0%   4.10      137  40.9%   2.44
NFP week Mon/Tue          33  63.6%   4.77      355  41.7%   3.39
Rate decision             34  41.2%   1.95      354  43.8%   3.75
PD prov (sweep)          351  43.6%   3.33       37  43.2%   5.53
Seasonal lean              0   0.0%   0.00      388  43.6%   3.50
HTF OB Context           106  50.0%   5.18      282  41.1%   2.91
D1 Draw                  341  43.4%   3.55       47  44.7%   3.16
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 8     2  25.0%      1291.90   4.06
continuation          98    51  52.0%     22704.56   5.26
(none)               282   116  41.1%     31399.04   2.91

Liq type          Trades    WR%     PF
----------------------------------------
breaker               24  50.0%   2.84
d1_fvg                61  47.5%   5.27
ob                     7  57.1%  10.15
pdhl                   8  50.0%   0.96
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             340   147  43.2%     48558.63   3.54
(none)                47    21  44.7%      6639.16   3.16
```

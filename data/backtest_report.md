# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     363
win_rate_pct               44.4
profit_factor              3.73
starting_equity_ZAR        1000
ending_equity_ZAR          56238.66
pnl_ZAR                    55238.66
pnl_pct                    5523.87
max_drawdown_pct           -13.24
avg_win_ZAR                469.0
avg_loss_ZAR               -100.35
withdrawn_total_ZAR        49250.93
withdrawal_count           16
working_balance_ZAR        6987.73
working_max_drawdown_pct   21.89
```

## Gate funnel

```
checks                         59213
in_killzone                    59213
news_clear                     56437
nfp_fomc_ok                    48413
intermarket_signal             2882
pair_matches                   2882
mss_h1_m15_m5_ok               983
daily_bias_ok                  983
h1_bias_ok                     983
h4_bias_ok                     983
dealing_range_ok               33
consolidation_found            462
manipulation_correct_dir       414
m5_fvg_correct_dir             462
target_found                   462
rr_ok                          462
units_nonzero                  462
limit_placed                   0
entry_opened                   349
pyramid_added                  9
pyramid_blocked_min_target     333
drawdown_halt                  1510
daily_loss_halt                556
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1974
weekly_amd_confirmed           162
session_handover_closed        2
htf_draw_full_cascade          114
htf_draw_partial               294
htf_draw_counter               194
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               2
ny_continuation                188
pm_gate_pair_news              0
dxy_flat                       35582
dxy_directional                10639
eurgbp_flat                    1946
eurgbp_flat_gbp_blocked        1394
mm_golden_checked              5583
mm_golden_amd_ok               3144
mm_golden_ob_failed            2329
breakout_confirmed             570
sr_attempted                   433
sr_prev_session_ok             433
sr_enough_bars                 433
sr_consol_found                416
sr_breakout_found              258
session_range_found            30
soj_retest                     226
soj_sweep                      414
golden_rule_no                 225
mstruct_align                  447
phase_ny_judas                 232
gt_pool_sweep                  368
structure_stop_used            431
stop_capped_10pip              372
risk_cap_ok                    349
mm_golden_other_pair_open      1321
pyramid_blocked_low_im         1010
eurgbp_directional             6247
soj_judas                      188
crt_turtle_soup                215
golden_rule_yes                227
gt_disp_wick                   340
m1_stop_used                   31
pyramid_blocked_favour         1856
dxy_fvg_room                   57
phase_london_judas             242
gt_macro_window                63
im_score_low                   4099
mm_golden_corr_block           69
mm_golden_wrong_sweep          896
mm_golden_via_own_ob           284
mm_golden_smt_yes              217
mm_golden_im_eurgbp            97
mm_golden_ob_untested          469
smt_pair_opposing              58
gt_mp_discount                 91
mm_golden_im_ok                61
mm_golden_no_draw              55
smt_pair_confirmed             147
mstruct_minor_sweep            68
mm_golden_via_cascade          12
mm_golden_no_smt               79
gt_judas_reversal              44
mm_golden_im_dxy_opposes       59
mm_golden_no_retrace           49
gt_mp_extreme                  18
sr_consol_no_sweep             105
sr_fail_no_sweep               41
sr_pdliq_attempted             122
mm_golden_no_amd               109
ny_continuation_gated          6
london_judas_ny_echo           7
mm_golden_opened               5
mm_golden_daily_cap            44
sr_fail_high_swept_no_close_back 17
sr_fail_low_swept_no_close_back 21
target_score_sized             127
crt_sweep_sized                72
risk_cap_skip                  113
golden_rule_sized              188
mm_golden_risk_cap             1
pdliq_sweep_sized              66
mm_golden_ob_none              1
sr_fail_both_swept             26
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R49,251 across 16 withdrawals · working balance R6,988_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            268   117  43.7%     41393.99   3.70
OB              85    38  44.7%     12868.58   3.96
BREAKER         10     6  60.0%       976.09   2.69

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             7     4  57.1%  14.19
FVG H1                40    16  40.0%   3.41
FVG M15               39    16  41.0%   6.28
FVG M5               189    85  45.0%   3.44
OB M15                13     7  53.8%  26.72
OB M5                 72    31  43.1%   3.46

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             8     4  50.0%   0.89
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               119    50  42.0%   4.41
FVG GBPUSD               137    64  46.7%   3.34
FVG NZDUSD                12     3  25.0%   1.85
OB EURUSD                 51    16  31.4%   1.42
OB GBPUSD                 26    16  61.5%  17.99
OB NZDUSD                  8     6  75.0%  43.57
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     0   0.0%    -541.12   0.00
amd_breaker_m5               4     3  75.0%      95.89  24.04
amd_fvg_h1                  34    15  44.1%     171.82   4.01
amd_fvg_m15                 30    11  36.7%     150.56   4.31
amd_fvg_m5                 168    79  47.0%     165.32   3.76
amd_ob_m15                  10     7  70.0%     250.38 136.01
amd_ob_m5                   56    23  41.1%     100.96   2.54
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   5     1  20.0%     -43.60   0.42
mss_fvg_m15                  7     4  57.1%     337.16  61.75
mss_fvg_m5                  12     5  41.7%      61.10   1.59
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   16     8  50.0%     299.18   9.43
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
m15_range              323   144  44.6%     51776.84   3.95
session_range           29    12  41.4%      2264.89   2.08
(no AMD)                11     5  45.5%      1196.92   2.91
```

_Session-range widths (n=433): median=55.5 p75=72.0 p90=95.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           148    74  50.0%     30170.76   4.57
against          195    78  40.0%     22530.11   3.06

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                58  43.1%   3.12
EURUSD SHORT against             120  37.5%   3.19
GBPUSD LONG against               75  44.0%   2.83
GBPUSD SHORT golden               90  54.4%   5.59
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          108    49  45.4%     19002.23   3.96
opposing            44    20  45.5%      3487.96   3.47
no divergence      191    83  43.5%     30210.68   3.62
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             27     8  29.6%       311.52   1.23
2             93    43  46.2%     14556.84   4.54
3            157    65  41.4%     22391.23   3.16
4             76    36  47.4%     14800.91   4.51
5              9     8  88.9%      3061.53  15.01

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           235  46.0%   4.38      128  41.4%   2.59
NFP week Mon/Tue          32  62.5%   4.66      331  42.6%   3.64
Rate decision             33  39.4%   1.94      330  44.8%   4.05
PD prov (sweep)          326  44.5%   3.57       37  43.2%   5.43
Seasonal lean              0   0.0%   0.00      363  44.4%   3.73
HTF OB Context            90  52.2%   5.81      273  41.8%   3.07
D1 Draw                  317  44.2%   3.71       46  45.7%   3.85
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 7     2  28.6%      1326.68   4.43
continuation          83    45  54.2%     21881.67   5.93
(none)               273   114  41.8%     32030.31   3.07

Liq type          Trades    WR%     PF
----------------------------------------
breaker               20  50.0%   2.80
d1_fvg                52  51.9%   5.97
ob                     5  60.0%  23.87
pdhl                   7  42.9%   0.91
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             316   139  44.0%     47568.74   3.69
(none)                46    21  45.7%      7472.20   3.85
```

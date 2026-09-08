# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     456
win_rate_pct               38.8
profit_factor              2.55
starting_equity_ZAR        1000
ending_equity_ZAR          43693.44
pnl_ZAR                    42693.44
pnl_pct                    4269.34
max_drawdown_pct           -26.84
avg_win_ZAR                397.27
avg_loss_ZAR               -99.01
withdrawn_total_ZAR        37390.75
withdrawal_count           12
working_balance_ZAR        6302.68
working_max_drawdown_pct   28.15
```

## Gate funnel

```
checks                         58494
in_killzone                    58494
news_clear                     54568
nfp_fomc_ok                    46727
intermarket_signal             2371
pair_matches                   2371
mss_h1_m15_m5_ok               1796
daily_bias_ok                  1796
h1_bias_ok                     1796
h4_bias_ok                     1796
dealing_range_ok               197
consolidation_found            569
manipulation_correct_dir       473
m5_fvg_correct_dir             533
target_found                   533
rr_ok                          533
units_nonzero                  533
limit_placed                   0
entry_opened                   414
pyramid_added                  15
pyramid_blocked_min_target     435
drawdown_halt                  2466
daily_loss_halt                787
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      772
daily_pair_cap                 2481
weekly_amd_confirmed           250
session_handover_closed        7
htf_draw_full_cascade          140
htf_draw_partial               387
htf_draw_counter               562
htf_fvg_5050_hit               33
ote_zone                       12
choch_confirmed                7
low_conviction                 0
judas_divergence               0
ny_continuation                253
pm_gate_pair_news              0
mm_golden_checked              5307
mm_golden_amd_ok               2664
mm_golden_ob_failed            2133
breakout_confirmed             499
sr_attempted                   389
sr_prev_session_ok             389
sr_enough_bars                 389
sr_consol_found                371
sr_breakout_found              222
session_range_found            22
soj_retest                     284
soj_sweep                      478
golden_rule_no                 206
mstruct_align                  552
phase_ny_judas                 296
gt_pool_sweep                  422
structure_stop_used            501
stop_capped_10pip              380
risk_cap_ok                    414
mm_golden_other_pair_open      1284
pyramid_blocked_favour         2617
soj_judas                      194
crt_turtle_soup                270
golden_rule_yes                274
gt_disp_wick                   332
m1_stop_used                   32
dxy_fvg_room                   82
phase_london_judas             301
gt_macro_window                106
mm_golden_corr_block           438
pyramid_blocked_low_im         847
mm_golden_wrong_sweep          670
mm_golden_via_own_ob           107
mm_golden_smt_yes              76
mm_golden_no_draw              49
mm_golden_no_smt               36
mm_golden_ob_untested          387
smt_pair_confirmed             153
mm_golden_via_cascade          5
mm_golden_opened               27
mm_golden_daily_cap            159
smt_pair_opposing              47
mstruct_minor_sweep            82
gt_judas_reversal              43
gt_mp_discount                 95
gt_mp_extreme                  25
sr_consol_no_sweep             103
sr_fail_no_sweep               30
sr_pdliq_attempted             121
mm_golden_no_amd               92
ny_continuation_gated          37
london_judas_ny_echo           7
sr_fail_high_swept_no_close_back 16
mm_golden_no_retrace           32
pdliq_sweep_sized              54
golden_rule_sized              184
crt_sweep_sized                92
target_score_sized             169
risk_cap_skip                  119
sr_fail_both_swept             34
sr_fail_low_swept_no_close_back 23
phase_london_watch             1
htf_fvg_breakout_sized         3
```

_income: R37,391 across 12 withdrawals · working balance R6,303_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            307   122  39.7%     28390.70   2.52
OB             131    51  38.9%     14705.33   2.85
BREAKER         18     4  22.2%      -402.59   0.62

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     0   0.0%   0.00
BREAKER M15            2     0   0.0%   0.00
BREAKER M5            15     4  26.7%   1.33
FVG H1                35    18  51.4%   4.00
FVG M15               53    19  35.8%   2.05
FVG M5               219    85  38.8%   2.40
OB M15                30    13  43.3%   3.82
OB M5                101    38  37.6%   2.65

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             6     4  66.7%  33.15
BREAKER GBPUSD             5     0   0.0%   0.00
BREAKER NZDUSD             7     0   0.0%   0.00
FVG EURUSD               100    37  37.0%   3.24
FVG GBPUSD               165    71  43.0%   2.26
FVG NZDUSD                42    14  33.3%   2.44
OB EURUSD                 39    12  30.8%   5.17
OB GBPUSD                 49    22  44.9%   3.09
OB NZDUSD                 43    17  39.5%   1.66
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_h1               1     0   0.0%    -140.48   0.00
amd_breaker_m15              1     0   0.0%     -31.22   0.00
amd_breaker_m5              12     3  25.0%       5.61   1.14
amd_fvg_h1                  27    17  63.0%     245.48   4.57
amd_fvg_m15                 38    11  28.9%      53.14   1.70
amd_fvg_m5                 179    75  41.9%      91.92   2.60
amd_ob_m15                  15     7  46.7%     106.90   2.57
amd_ob_m5                   70    24  34.3%     110.32   2.87
mss_breaker_m15              1     0   0.0%    -393.36   0.00
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   5     1  20.0%      76.01   2.62
mss_fvg_m15                 13     6  46.2%      86.18   2.37
mss_fvg_m5                  32     8  25.0%      38.50   1.57
mss_ob_m15                  14     6  42.9%     171.82   7.87
mss_ob_m5                   26    10  38.5%      88.37   2.05
news_ob_m5                   4     3  75.0%     138.81   3.67
pyramid_im1.0_fvg_h1         1     0   0.0%    -174.82   0.00
pyramid_im1.0_fvg_m15        2     2 100.0%     380.62    inf
pyramid_im1.0_fvg_m5         5     2  40.0%       6.29   1.22
pyramid_im1.0_ob_m5          1     1 100.0%     159.84    inf
pyramid_wamd1.0_fvg_h1       2     0   0.0%      -4.90   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -17.14   0.00
pyramid_wamd1.0_ob_m15       1     0   0.0%     -38.48   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              423   161  38.1%     39178.09   2.54
session_range           21     9  42.9%      1241.36   1.91
(no AMD)                12     7  58.3%      2273.99   3.77
```

_Session-range widths (n=389): median=54.6 p75=72.0 p90=95.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           175    71  40.6%     20896.96   2.79
against          189    75  39.7%     16827.54   2.82

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                45  35.6%   4.89
EURUSD SHORT against             100  37.0%   3.29
GBPUSD LONG against               89  42.7%   2.45
GBPUSD SHORT golden              130  42.3%   2.44
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          106    47  44.3%     14704.96   3.83
opposing            46    19  41.3%      1857.56   1.62
no divergence      212    80  37.7%     21161.98   2.67
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              2     2 100.0%       290.06    inf
1             34    12  35.3%       756.70   1.50
2            113    37  32.7%      5927.46   1.85
3            193    77  39.9%     19171.45   2.61
4             99    40  40.4%     13316.31   3.14
5             15     9  60.0%      3231.46   4.19

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           296  38.2%   2.56      160  40.0%   2.52
NFP week Mon/Tue          41  48.8%   3.12      415  37.8%   2.49
Rate decision             39  56.4%   6.46      417  37.2%   2.35
PD prov (sweep)          372  40.3%   2.68       84  32.1%   1.97
Seasonal lean              0   0.0%   0.00      456  38.8%   2.55
HTF OB Context           166  36.7%   2.52      290  40.0%   2.56
D1 Draw                  396  39.4%   2.74       60  35.0%   1.41
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 8     2  25.0%      1429.04   4.42
continuation         158    59  37.3%     17346.83   2.46
(none)               290   116  40.0%     23917.57   2.56

Liq type          Trades    WR%     PF
----------------------------------------
breaker               32  37.5%   2.29
d1_fvg               100  37.0%   2.45
ob                    12  25.0%   1.64
pdhl                  12  33.3%   6.49
w_fvg                 10  50.0%   3.47
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 2     0   0.0%      -280.79   0.00
equal_hl             394   156  39.6%     41296.19   2.78
(none)                60    21  35.0%      1678.03   1.41
```

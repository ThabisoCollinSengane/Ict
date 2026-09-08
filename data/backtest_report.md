# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     367
win_rate_pct               44.4
profit_factor              3.55
starting_equity_ZAR        1000
ending_equity_ZAR          55388.38
pnl_ZAR                    54388.38
pnl_pct                    5438.84
max_drawdown_pct           -10.24
avg_win_ZAR                464.7
avg_loss_ZAR               -104.7
withdrawn_total_ZAR        48400.65
withdrawal_count           16
working_balance_ZAR        6987.73
working_max_drawdown_pct   21.89
```

## Gate funnel

```
checks                         59191
in_killzone                    59191
news_clear                     56316
nfp_fomc_ok                    48305
intermarket_signal             2877
pair_matches                   2877
mss_h1_m15_m5_ok               983
daily_bias_ok                  983
h1_bias_ok                     983
h4_bias_ok                     983
dealing_range_ok               33
consolidation_found            465
manipulation_correct_dir       417
m5_fvg_correct_dir             465
target_found                   465
rr_ok                          465
units_nonzero                  465
limit_placed                   0
entry_opened                   346
pyramid_added                  9
pyramid_blocked_min_target     318
drawdown_halt                  1510
daily_loss_halt                661
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1957
weekly_amd_confirmed           162
session_handover_closed        2
htf_draw_full_cascade          118
htf_draw_partial               293
htf_draw_counter               194
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               2
ny_continuation                188
pm_gate_pair_news              0
mm_golden_checked              5535
mm_golden_amd_ok               3079
mm_golden_ob_failed            2333
breakout_confirmed             574
sr_attempted                   420
sr_prev_session_ok             420
sr_enough_bars                 420
sr_consol_found                403
sr_breakout_found              245
session_range_found            30
soj_retest                     229
soj_sweep                      417
golden_rule_no                 224
mstruct_align                  450
phase_ny_judas                 231
gt_pool_sweep                  369
structure_stop_used            434
stop_capped_10pip              375
risk_cap_ok                    346
mm_golden_other_pair_open      1311
pyramid_blocked_low_im         1036
soj_judas                      188
crt_turtle_soup                215
golden_rule_yes                231
gt_disp_wick                   341
m1_stop_used                   31
pyramid_blocked_favour         1861
dxy_fvg_room                   57
phase_london_judas             246
gt_macro_window                62
mm_golden_corr_block           69
mm_golden_wrong_sweep          878
mm_golden_via_own_ob           231
mm_golden_smt_yes              172
mm_golden_no_draw              159
mm_golden_ob_untested          462
smt_pair_opposing              57
gt_mp_discount                 91
smt_pair_confirmed             152
mstruct_minor_sweep            67
mm_golden_via_cascade          5
mm_golden_opened               12
mm_golden_daily_cap            89
gt_judas_reversal              43
mm_golden_no_smt               64
gt_mp_extreme                  18
sr_consol_no_sweep             105
sr_fail_no_sweep               41
sr_pdliq_attempted             122
mm_golden_no_amd               109
ny_continuation_gated          6
london_judas_ny_echo           7
sr_fail_high_swept_no_close_back 17
sr_fail_low_swept_no_close_back 21
golden_rule_sized              193
risk_cap_skip                  119
target_score_sized             126
crt_sweep_sized                72
mm_golden_risk_cap             1
mm_golden_no_retrace           47
pdliq_sweep_sized              66
mm_golden_ob_none              1
sr_fail_both_swept             26
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R48,401 across 16 withdrawals · working balance R6,988_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            271   118  43.5%     40754.90   3.48
OB              86    39  45.3%     12657.39   3.91
BREAKER         10     6  60.0%       976.09   2.69

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             7     4  57.1%  14.19
FVG H1                43    18  41.9%   3.32
FVG M15               39    16  41.0%   6.28
FVG M5               189    84  44.4%   3.19
OB M15                14     8  57.1%  24.21
OB M5                 72    31  43.1%   3.46

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             8     4  50.0%   0.89
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               121    51  42.1%   4.20
FVG GBPUSD               138    64  46.4%   3.11
FVG NZDUSD                12     3  25.0%   1.45
OB EURUSD                 52    17  32.7%   1.49
OB GBPUSD                 26    16  61.5%  17.16
OB NZDUSD                  8     6  75.0%  43.57
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     0   0.0%    -541.12   0.00
amd_breaker_m5               4     3  75.0%      95.89  24.04
amd_fvg_h1                  37    17  45.9%     180.66   3.79
amd_fvg_m15                 30    11  36.7%     150.56   4.31
amd_fvg_m5                 168    78  46.4%     156.50   3.46
amd_ob_m15                  11     8  72.7%     206.08 123.23
amd_ob_m5                   56    23  41.1%     100.82   2.53
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   5     1  20.0%     -43.60   0.42
mss_fvg_m15                  7     4  57.1%     337.16  61.75
mss_fvg_m5                  12     5  41.7%      61.10   1.59
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   16     8  50.0%     301.28   9.49
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
m15_range              327   146  44.6%     50935.81   3.74
session_range           29    12  41.4%      2255.64   2.07
(no AMD)                11     5  45.5%      1196.92   2.91
```

_Session-range widths (n=420): median=57.3 p75=72.0 p90=100.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           153    76  49.7%     29713.95   4.14
against          194    78  40.2%     22482.14   3.04

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                62  43.5%   3.11
EURUSD SHORT against             119  37.8%   3.14
GBPUSD LONG against               75  44.0%   2.87
GBPUSD SHORT golden               91  53.8%   4.91
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          107    48  44.9%     19044.70   3.97
opposing            43    20  46.5%      3348.81   3.38
no divergence      197    86  43.7%     29802.59   3.36
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             27     7  25.9%      -380.67   0.79
2             91    42  46.2%     14285.18   4.48
3            160    68  42.5%     22774.92   3.18
4             79    37  46.8%     14530.80   4.05
5              9     8  88.9%      3061.53  15.01

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           238  45.8%   4.19      129  41.9%   2.45
NFP week Mon/Tue          32  62.5%   4.66      335  42.7%   3.45
Rate decision             34  41.2%   1.95      333  44.7%   3.82
PD prov (sweep)          330  44.5%   3.38       37  43.2%   5.45
Seasonal lean              0   0.0%   0.00      367  44.4%   3.55
HTF OB Context            96  53.1%   5.36      271  41.3%   2.94
D1 Draw                  320  44.4%   3.61       47  44.7%   3.16
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 7     2  28.6%       688.43   2.78
continuation          89    49  55.1%     22719.70   5.56
(none)               271   112  41.3%     30980.24   2.94

Liq type          Trades    WR%     PF
----------------------------------------
breaker               21  52.4%   2.85
d1_fvg                55  50.9%   5.20
ob                     6  66.7%  27.74
pdhl                   8  50.0%   0.96
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             319   141  44.2%     47549.60   3.60
(none)                47    21  44.7%      6641.06   3.16
```

# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     371
win_rate_pct               44.7
profit_factor              3.81
starting_equity_ZAR        1000
ending_equity_ZAR          60549.28
pnl_ZAR                    59549.28
pnl_pct                    5954.93
max_drawdown_pct           -10.24
avg_win_ZAR                486.44
avg_loss_ZAR               -103.41
withdrawn_total_ZAR        53561.55
withdrawal_count           16
working_balance_ZAR        6987.73
working_max_drawdown_pct   21.89
```

## Gate funnel

```
checks                         59181
in_killzone                    59181
news_clear                     56408
nfp_fomc_ok                    48401
intermarket_signal             2901
pair_matches                   2901
mss_h1_m15_m5_ok               985
daily_bias_ok                  985
h1_bias_ok                     985
h4_bias_ok                     985
dealing_range_ok               33
consolidation_found            467
manipulation_correct_dir       420
m5_fvg_correct_dir             467
target_found                   467
rr_ok                          467
units_nonzero                  467
limit_placed                   0
entry_opened                   346
pyramid_added                  9
pyramid_blocked_min_target     329
drawdown_halt                  1510
daily_loss_halt                556
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1959
weekly_amd_confirmed           162
session_handover_closed        2
htf_draw_full_cascade          120
htf_draw_partial               293
htf_draw_counter               194
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               2
ny_continuation                189
pm_gate_pair_news              0
mm_golden_checked              5556
mm_golden_amd_ok               3076
sr_attempted                   676
sr_prev_session_ok             676
sr_enough_bars                 676
sr_consol_found                659
sr_breakout_found              374
mm_golden_ob_failed            2061
breakout_confirmed             572
session_range_found            29
soj_retest                     234
soj_sweep                      422
golden_rule_no                 225
mstruct_align                  452
phase_ny_judas                 233
gt_pool_sweep                  371
structure_stop_used            436
stop_capped_10pip              378
risk_cap_ok                    346
mm_golden_other_pair_open      1272
pyramid_blocked_low_im         1022
soj_judas                      188
crt_turtle_soup                214
golden_rule_yes                232
gt_disp_wick                   343
m1_stop_used                   31
pyramid_blocked_favour         1877
dxy_fvg_room                   57
phase_london_judas             246
gt_macro_window                62
mm_golden_corr_block           69
mm_golden_wrong_sweep          891
mm_golden_ob_none              533
mm_golden_ob_untested          304
smt_pair_opposing              59
gt_mp_discount                 91
mm_golden_via_own_ob           173
mm_golden_no_draw              159
smt_pair_confirmed             152
mstruct_minor_sweep            71
mm_golden_via_cascade          5
mm_golden_opened               16
mm_golden_daily_cap            139
gt_judas_reversal              44
sr_consol_no_sweep             190
sr_fail_high_swept_no_close_back 32
sr_pdliq_attempted             207
gt_mp_extreme                  18
sr_fail_no_sweep               74
mm_golden_no_amd               109
ny_continuation_gated          6
sr_fail_both_swept             40
london_judas_ny_echo           6
sr_fail_low_swept_no_close_back 44
golden_rule_sized              195
risk_cap_skip                  121
target_score_sized             125
crt_sweep_sized                72
mm_golden_risk_cap             3
pdliq_sweep_sized              66
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              2
sr_pdliq_sweep                 2
```

_income: R53,562 across 16 withdrawals · working balance R6,988_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            271   117  43.2%     42836.79   3.63
OB              88    41  46.6%     15352.47   4.55
BREAKER         10     6  60.0%       976.09   2.69
other            2     2 100.0%       383.93    inf

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             7     4  57.1%  14.19
FVG H1                41    17  41.5%   3.96
FVG M15               40    16  40.0%   6.25
FVG M5               190    84  44.2%   3.27
OB M15                14     9  64.3%  56.73
OB M5                 74    32  43.2%   3.83
other ?                2     2 100.0%    inf

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             8     4  50.0%   0.89
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               123    52  42.3%   4.46
FVG GBPUSD               136    62  45.6%   3.12
FVG NZDUSD                12     3  25.0%   1.85
OB EURUSD                 52    17  32.7%   1.52
OB GBPUSD                 28    18  64.3%  22.43
OB NZDUSD                  8     6  75.0%  43.57
other GBPUSD               2     2 100.0%    inf
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                     2     2 100.0%     191.96    inf
amd_breaker_m15              1     0   0.0%    -541.12   0.00
amd_breaker_m5               4     3  75.0%      95.89  24.04
amd_fvg_h1                  35    16  45.7%     202.99   4.66
amd_fvg_m15                 31    11  35.5%     148.48   4.31
amd_fvg_m5                 169    78  46.2%     164.90   3.53
amd_ob_m15                  12     9  75.0%     275.04 178.97
amd_ob_m5                   58    24  41.4%     122.92   2.93
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      31.73   5.84
mss_fvg_h1                   5     1  20.0%     -43.60   0.42
mss_fvg_m15                  7     4  57.1%     337.16  61.75
mss_fvg_m5                  12     5  41.7%      61.10   1.59
mss_ob_m15                   2     0   0.0%     -19.98   0.00
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
m15_range              330   147  44.5%     53876.90   3.91
session_range           30    14  46.7%      4475.46   3.16
(no AMD)                11     5  45.5%      1196.92   2.91
```

_Session-range widths (n=676): median=50.7 p75=69.8 p90=100.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           156    79  50.6%     34393.93   4.70
against          195    78  40.0%     22617.56   3.06

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                63  44.4%   3.57
EURUSD SHORT against             120  37.5%   3.15
GBPUSD LONG against               75  44.0%   2.87
GBPUSD SHORT golden               93  54.8%   5.57
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          107    48  44.9%     19041.00   3.96
opposing            44    20  45.5%      3484.23   3.47
no divergence      200    89  44.5%     34486.27   3.77
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             25     7  28.0%       110.48   1.08
2             92    42  45.7%     14439.84   4.51
3            160    68  42.5%     22882.22   3.19
4             83    39  47.0%     18543.14   4.64
5             10     9  90.0%      3456.97  16.82

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           243  46.5%   4.46      128  41.4%   2.60
NFP week Mon/Tue          32  62.5%   4.66      339  43.1%   3.74
Rate decision             34  41.2%   2.07      337  45.1%   4.11
PD prov (sweep)          335  44.8%   3.65       36  44.4%   5.65
Seasonal lean              0   0.0%   0.00      371  44.7%   3.81
HTF OB Context           101  53.5%   5.89      270  41.5%   3.05
D1 Draw                  326  44.5%   3.81       45  46.7%   3.77
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 7     2  28.6%      1326.68   4.43
continuation          94    52  55.3%     26489.24   5.99
(none)               270   112  41.5%     31733.36   3.05

Liq type          Trades    WR%     PF
----------------------------------------
breaker               24  54.2%   2.75
d1_fvg                55  50.9%   5.74
ob                     6  66.7%  26.95
pdhl                  10  50.0%   3.73
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             325   144  44.3%     52200.10   3.80
(none)                45    21  46.7%      7151.46   3.77
```

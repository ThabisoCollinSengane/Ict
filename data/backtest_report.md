# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     473
win_rate_pct               42.3
profit_factor              3.74
starting_equity_ZAR        1000
ending_equity_ZAR          101263.82
pnl_ZAR                    100263.82
pnl_pct                    10026.38
max_drawdown_pct           -12.13
avg_win_ZAR                684.07
avg_loss_ZAR               -133.88
withdrawn_total_ZAR        95414.77
withdrawal_count           17
working_balance_ZAR        5849.05
working_max_drawdown_pct   24.52
```

## Gate funnel

```
checks                         58544
in_killzone                    58544
news_clear                     53168
nfp_fomc_ok                    45160
intermarket_signal             2420
pair_matches                   2420
mss_h1_m15_m5_ok               804
daily_bias_ok                  804
h1_bias_ok                     804
h4_bias_ok                     804
dealing_range_ok               35
consolidation_found            395
manipulation_correct_dir       354
m5_fvg_correct_dir             393
target_found                   393
rr_ok                          393
units_nonzero                  393
limit_placed                   0
entry_opened                   327
pyramid_added                  10
pyramid_blocked_min_target     447
drawdown_halt                  3995
daily_loss_halt                698
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      174
daily_pair_cap                 1804
weekly_amd_confirmed           143
session_handover_closed        2
htf_draw_full_cascade          83
htf_draw_partial               261
htf_draw_counter               179
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               2
ny_continuation                160
pm_gate_pair_news              0
mm_golden_checked              4651
mm_golden_amd_ok               1992
mm_golden_no_draw              1774
breakout_confirmed             435
sr_attempted                   265
sr_prev_session_ok             265
sr_enough_bars                 265
sr_consol_found                248
sr_breakout_found              109
session_range_found            26
soj_retest                     216
soj_sweep                      358
golden_rule_no                 215
mstruct_align                  382
phase_ny_judas                 201
gt_pool_sweep                  320
structure_stop_used            365
stop_capped_10pip              316
risk_cap_ok                    327
mm_golden_corr_block           1087
pyramid_blocked_low_im         1102
soj_judas                      142
crt_turtle_soup                180
golden_rule_yes                169
gt_disp_wick                   297
m1_stop_used                   28
pyramid_blocked_favour         2300
dxy_fvg_room                   59
phase_london_judas             203
gt_macro_window                58
mm_golden_wrong_sweep          742
smt_pair_opposing              46
gt_mp_discount                 79
smt_pair_confirmed             129
mm_golden_opened               136
mm_golden_daily_cap            724
mstruct_minor_sweep            64
gt_judas_reversal              41
gt_mp_extreme                  18
sr_consol_no_sweep             99
sr_fail_no_sweep               41
sr_pdliq_attempted             116
mm_golden_no_amd               106
ny_continuation_gated          4
london_judas_ny_echo           7
sr_fail_high_swept_no_close_back 15
risk_cap_skip                  66
golden_rule_sized              139
target_score_sized             108
crt_sweep_sized                63
sr_fail_low_swept_no_close_back 18
mm_golden_risk_cap             82
pdliq_sweep_sized              46
sr_fail_both_swept             25
pyramid_blocked_no_pattern     1
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
```

_income: R95,415 across 17 withdrawals · working balance R5,849_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            329   134  40.7%     63626.18   3.38
OB             117    52  44.4%     25413.97   3.99
BREAKER         20    10  50.0%      6251.93   5.97
other            7     4  57.1%      4971.73 274.88

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            5     2  40.0%   1.75
BREAKER M5            14     7  50.0%  41.43
FVG H1                43    19  44.2%   6.95
FVG M15               51    16  31.4%   3.05
FVG M5               235    99  42.1%   3.06
OB M15                18     9  50.0%   4.25
OB M5                 99    43  43.4%   3.96
other ?                7     4  57.1% 274.88

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            12     6  50.0%   1.88
BREAKER GBPUSD             8     4  50.0%  13.66
FVG EURUSD               144    53  36.8%   3.80
FVG GBPUSD               173    79  45.7%   3.20
FVG NZDUSD                12     2  16.7%   1.10
OB EURUSD                 72    26  36.1%   2.87
OB GBPUSD                 38    21  55.3%   7.38
OB NZDUSD                  7     5  71.4%  19.13
other EURUSD               1     1 100.0%    inf
other GBPUSD               6     3  50.0% 252.86
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_None                     7     4  57.1%     710.25 274.88
amd_breaker_m15              3     1  33.3%      28.91   1.10
amd_breaker_m5               9     4  44.4%     469.85  41.23
amd_fvg_h1                  38    18  47.4%     338.29   7.04
amd_fvg_m15                 42    11  26.2%      67.89   1.93
amd_fvg_m5                 215    93  43.3%     187.28   2.97
amd_ob_m15                  16     9  56.2%     157.30   4.49
amd_ob_m5                   83    36  43.4%     232.99   3.76
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     1  50.0%     378.90   4.50
mss_breaker_m5               5     3  60.0%     222.91  42.19
mss_fvg_h1                   4     1  25.0%      29.76   3.92
mss_fvg_m15                  7     4  57.1%     422.93  69.83
mss_fvg_m5                  12     6  50.0%     356.34   6.93
mss_ob_m15                   2     0   0.0%     -19.98   0.00
mss_ob_m5                   14     6  42.9%     258.01   7.36
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%     -43.94   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         1     0   0.0%     -97.12   0.00
pyramid_im1.0_fvg_m5         2     0   0.0%     -23.59   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
pyramid_wamd1.0_ob_m5        2     1  50.0%      -6.66   0.92
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              425   180  42.4%     96772.20   4.01
session_range           40    16  40.0%      2953.86   1.72
(no AMD)                 8     4  50.0%       537.76   3.11
```

_Session-range widths (n=265): median=57.3 p75=77.1 p90=106.2 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           269   120  44.6%     73938.84   3.84
against          185    73  39.5%     25478.08   3.62

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               116  37.9%   3.23
EURUSD SHORT against             113  37.2%   3.66
GBPUSD LONG against               72  43.1%   3.52
GBPUSD SHORT golden              153  49.7%   4.29
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           96    44  45.8%     21562.25   5.51
opposing            39    17  43.6%      5404.62   6.45
no divergence      319   132  41.4%     72450.05   3.41
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             27     8  29.6%       415.19   1.32
2            107    46  43.0%     21180.24   3.81
3            194    79  40.7%     38128.42   3.44
4            125    54  43.2%     33776.70   4.02
5             19    12  63.2%      6646.64   7.95

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           307  44.6%   4.14      166  38.0%   2.96
NFP week Mon/Tue          42  54.8%   3.58      431  41.1%   3.76
Rate decision             49  38.8%   2.73      424  42.7%   3.91
PD prov (sweep)          434  41.9%   3.50       39  46.2%   9.79
Seasonal lean              0   0.0%   0.00      473  42.3%   3.74
HTF OB Context           176  44.9%   4.48      297  40.7%   3.18
D1 Draw                  410  42.2%   4.06       63  42.9%   2.44
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 1     1 100.0%      1566.14    inf
continuation         175    78  44.6%     53864.16   4.38
(none)               297   121  40.7%     44833.51   3.18

Liq type          Trades    WR%     PF
----------------------------------------
breaker               39  46.2%   4.79
d1_fvg               104  44.2%   4.14
ob                     5  80.0%  26.97
pdhl                  16  31.2%   3.55
w_fvg                 12  50.0%   6.72
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     2  66.7%       524.06   4.03
equal_hl             407   171  42.0%     89424.67   4.06
(none)                63    27  42.9%     10315.09   2.44
```

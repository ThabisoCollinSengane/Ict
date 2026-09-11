# HistData backtest — 2024–2025 (2 yr)

## Results

```
trades                     385
win_rate_pct               44.4
profit_factor              4.28
starting_equity_ZAR        1000
ending_equity_ZAR          75332.75
pnl_ZAR                    74332.75
pnl_pct                    7433.28
max_drawdown_pct           -10.21
avg_win_ZAR                567.03
avg_loss_ZAR               -105.74
withdrawn_total_ZAR        66777.54
withdrawal_count           16
working_balance_ZAR        8555.21
working_max_drawdown_pct   15.92
```

## Gate funnel

```
checks                         60935
in_killzone                    60935
news_clear                     58701
nfp_fomc_ok                    50596
intermarket_signal             2573
pair_matches                   2573
mss_h1_m15_m5_ok               911
daily_bias_ok                  911
h1_bias_ok                     911
h4_bias_ok                     911
dealing_range_ok               74
consolidation_found            523
manipulation_correct_dir       445
m5_fvg_correct_dir             519
target_found                   519
rr_ok                          519
units_nonzero                  519
limit_placed                   0
entry_opened                   380
pyramid_added                  5
pyramid_blocked_min_target     685
drawdown_halt                  1032
daily_loss_halt                458
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      314
daily_pair_cap                 1182
weekly_amd_confirmed           154
session_handover_closed        0
htf_draw_full_cascade          150
htf_draw_partial               339
htf_draw_counter               157
htf_fvg_5050_hit               29
ote_zone                       3
choch_confirmed                28
low_conviction                 0
judas_divergence               0
ny_continuation                217
pm_gate_pair_news              0
dxy_flat                       39224
dxy_directional                9876
eurgbp_directional             5097
im_score_low                   3474
breakout_confirmed             501
soj_retest                     322
soj_sweep                      475
crt_turtle_soup                255
golden_rule_no                 254
mstruct_align                  490
phase_ny_judas                 274
gt_pool_sweep                  386
gt_disp_wick                   379
structure_stop_used            480
stop_capped_10pip              339
risk_cap_ok                    380
pyramid_blocked_favour         3136
eurgbp_flat                    2670
eurgbp_flat_gbp_blocked        1938
golden_rule_yes                226
phase_london_judas             256
gt_mp_discount                 85
gt_mp_extreme                  21
soj_judas                      153
mstruct_minor_sweep            60
london_judas_ny_echo           15
pyramid_blocked_low_im         1623
smt_pair_opposing              41
sr_attempted                   43
sr_prev_session_ok             43
sr_enough_bars                 43
sr_consol_found                43
sr_breakout_found              30
session_range_found            36
gt_macro_window                68
smt_pair_confirmed             135
m1_stop_used                   39
dxy_fvg_room                   91
gt_judas_reversal              57
sr_consol_no_sweep             8
sr_fail_high_swept_no_close_back 2
sr_pdliq_attempted             8
golden_rule_sized              198
crt_sweep_sized                93
sr_fail_low_swept_no_close_back 4
pdliq_sweep_sized              110
target_score_sized             190
risk_cap_skip                  139
htf_fvg_breakout_sized         15
pyramid_blocked_no_pattern     6
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
ny_continuation_gated          3
sr_fail_no_sweep               2
```

_income: R66,778 across 16 withdrawals · working balance R8,555_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            223    92  41.3%     35652.60   3.39
OB             148    70  47.3%     35558.71   5.90
BREAKER         14     9  64.3%      3121.44   7.76

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER M15            2     2 100.0%    inf
BREAKER M5            12     7  58.3%   5.18
FVG H1                52    25  48.1%   6.76
FVG M15               40    16  40.0%   2.74
FVG M5               131    51  38.9%   2.58
OB M15                21    13  61.9%   6.83
OB M5                127    57  44.9%   5.72

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             7     5  71.4% 136.49
BREAKER GBPUSD             3     2  66.7%   7.27
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               120    50  41.7%   3.81
FVG GBPUSD                88    38  43.2%   3.33
FVG NZDUSD                15     4  26.7%   1.03
OB EURUSD                101    43  42.6%   4.87
OB GBPUSD                 31    21  67.7%   6.64
OB NZDUSD                 16     6  37.5%   9.73
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     1 100.0%     990.67    inf
amd_breaker_m5               9     6  66.7%     215.85   5.68
amd_fvg_h1                  38    19  50.0%     252.48   6.53
amd_fvg_m15                 31    11  35.5%     156.46   2.45
amd_fvg_m5                 115    43  37.4%      91.67   2.45
amd_ob_m15                  13     6  46.2%     211.70   3.28
amd_ob_m5                  106    47  44.3%     201.29   5.16
mss_breaker_m15              1     1 100.0%     199.80    inf
mss_breaker_m5               3     1  33.3%      -3.89   0.75
mss_fvg_h1                  14     6  42.9%     441.53   7.17
mss_fvg_m15                  8     5  62.5%     260.79   6.57
mss_fvg_m5                  12     6  50.0%     184.63   3.71
mss_ob_m15                   7     6  85.7%     593.14 719.22
mss_ob_m5                   21    10  47.6%     340.86   8.83
news_fvg_m5                  1     1 100.0%     443.68    inf
pyramid_im0.8_fvg_m5         2     0   0.0%     -88.15   0.00
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         1     1 100.0%      88.80    inf
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              353   158  44.8%     72502.30   4.48
session_range           25    12  48.0%      1953.99   2.34
(no AMD)                 7     1  14.3%      -123.53   0.62
```

_Session-range widths (n=43): median=28.6 p75=48.2 p90=52.7 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           146    73  50.0%     32968.84   4.40
against          204    86  42.2%     31670.73   4.06

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                85  47.1%   4.52
EURUSD SHORT against             143  40.6%   4.24
GBPUSD LONG against               61  45.9%   3.71
GBPUSD SHORT golden               61  54.1%   4.25
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           89    36  40.4%     15533.66   3.84
opposing            41    25  61.0%     12946.14   8.19
no divergence      220    98  44.5%     36159.77   3.83
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         236   131  55.5%     78762.37   9.15
3-day        114    34  29.8%     -1704.65   0.80
30-day        19     3  15.8%     -1633.82   0.32
60-day        16     3  18.8%     -1091.15   0.45
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          191    81  42.4%     23988.67   3.05
  on 240T        149    60  40.3%     18688.74   3.16
  on D            42    21  50.0%      5299.93   2.73
clear            194    90  46.4%     50344.09   5.61
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        112    57  50.9%     27366.41   5.06
             60T         95    49  51.6%     21009.09   4.95
             D           17     8  47.1%      6357.32   5.43
down (-1)    all         87    40  46.0%     18731.61   4.94
             60T         77    35  45.5%     16995.18   5.02
             D           10     5  50.0%      1736.44   4.29
none         all        186    74  39.8%     28234.73   3.54

with rev                151    74  49.0%     35704.36   5.38
against                  48    23  47.9%     10393.67   4.10
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
1             14     7  50.0%      2194.61   3.35
2             86    35  40.7%     13621.88   4.55
3            181    83  45.9%     36469.99   4.63
4             92    40  43.5%     16687.49   3.53
5             12     6  50.0%      5358.79   5.40

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           278  45.3%   4.13      107  42.1%   4.85
NFP week Mon/Tue          48  52.1%   6.12      337  43.3%   4.03
Rate decision             28  53.6%  10.02      357  43.7%   4.12
PD prov (sweep)          324  42.0%   3.65       61  57.4%   8.43
Seasonal lean              0   0.0%   0.00      385  44.4%   4.28
HTF OB Context           129  45.0%   4.81      256  44.1%   3.92
D1 Draw                  350  44.6%   4.28       35  42.9%   4.35
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
continuation         129    58  45.0%     35651.58   4.81
(none)               256   113  44.1%     38681.18   3.92

Liq type          Trades    WR%     PF
----------------------------------------
breaker               17  41.2%   5.56
d1_fvg                73  41.1%   4.78
ob                     3 100.0%    inf
pdhl                  16  56.2%   1.46
w_fvg                 20  45.0%   6.85
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 2     0   0.0%      -191.89   0.00
equal_hl             348   156  44.8%     68724.79   4.32
(none)                35    15  42.9%      5799.85   4.35
```

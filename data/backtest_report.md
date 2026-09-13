# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     351
win_rate_pct               42.7
profit_factor              3.31
starting_equity_ZAR        1000
ending_equity_ZAR          48959.57
pnl_ZAR                    47959.57
pnl_pct                    4795.96
max_drawdown_pct           -13.24
avg_win_ZAR                458.31
avg_loss_ZAR               -103.42
withdrawn_total_ZAR        42017.86
withdrawal_count           16
working_balance_ZAR        6941.71
working_max_drawdown_pct   21.58
```

## Gate funnel

```
checks                         59346
in_killzone                    59346
news_clear                     56280
nfp_fomc_ok                    48204
intermarket_signal             2910
pair_matches                   2910
mss_h1_m15_m5_ok               985
daily_bias_ok                  985
h1_bias_ok                     985
h4_bias_ok                     985
dealing_range_ok               33
consolidation_found            475
manipulation_correct_dir       428
m5_fvg_correct_dir             474
target_found                   474
rr_ok                          474
units_nonzero                  474
limit_placed                   0
entry_opened                   342
pyramid_added                  9
pyramid_blocked_min_target     299
drawdown_halt                  1758
daily_loss_halt                598
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      218
daily_pair_cap                 1956
weekly_amd_confirmed           164
session_handover_closed        2
htf_draw_full_cascade          131
htf_draw_partial               289
htf_draw_counter               199
htf_fvg_5050_hit               8
ote_zone                       2
choch_confirmed                12
low_conviction                 0
judas_divergence               1
ny_continuation                199
pm_gate_pair_news              0
dxy_flat                       35361
dxy_directional                10669
eurgbp_flat                    1915
eurgbp_flat_gbp_blocked        1370
breakout_confirmed             567
sr_attempted                   40
sr_prev_session_ok             40
sr_enough_bars                 40
sr_consol_found                39
sr_breakout_found              20
session_range_found            29
soj_retest                     236
soj_sweep                      430
golden_rule_no                 229
mstruct_align                  459
phase_ny_judas                 249
gt_pool_sweep                  382
structure_stop_used            444
stop_capped_10pip              390
target_rung_far                127
risk_cap_ok                    342
pyramid_blocked_low_im         961
eurgbp_directional             6308
soj_judas                      194
crt_turtle_soup                223
golden_rule_yes                235
gt_disp_wick                   350
m1_stop_used                   30
pyramid_blocked_favour         1806
dxy_fvg_room                   56
phase_london_judas             237
gt_macro_window                63
im_score_low                   4116
smt_pair_opposing              59
gt_mp_discount                 91
smt_pair_confirmed             144
mstruct_minor_sweep            69
gt_judas_reversal              50
gt_mp_extreme                  18
ny_continuation_gated          6
london_judas_ny_echo           6
sr_consol_no_sweep             11
sr_fail_no_sweep               4
sr_pdliq_attempted             12
sr_fail_low_swept_no_close_back 5
target_score_sized             159
crt_sweep_sized                78
risk_cap_skip                  132
golden_rule_sized              196
pdliq_sweep_sized              66
htf_fvg_breakout_sized         2
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
sr_fail_high_swept_no_close_back 1
sr_fail_both_swept             1
```

_income: R42,018 across 16 withdrawals · working balance R6,942_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            262   111  42.4%     38325.91   3.39
OB              80    34  42.5%      8912.63   3.14
BREAKER          9     5  55.6%       721.03   2.24

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            2     1  50.0%   1.80
BREAKER M5             6     3  50.0%   6.37
FVG H1                38    15  39.5%   4.49
FVG M15               39    15  38.5%   3.08
FVG M5               185    81  43.8%   3.27
OB M15                12     6  50.0%  12.16
OB M5                 68    28  41.2%   2.93

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             7     3  42.9%   0.46
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               116    47  40.5%   4.01
FVG GBPUSD               133    61  45.9%   3.42
FVG NZDUSD                13     3  23.1%   0.79
OB EURUSD                 49    15  30.6%   1.07
OB GBPUSD                 24    14  58.3%  15.57
OB NZDUSD                  7     5  71.4%  13.17
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     0   0.0%    -541.12   0.00
amd_breaker_m5               3     2  66.7%      44.61   9.04
amd_fvg_h1                  33    14  42.4%     209.56   4.50
amd_fvg_m15                 30    10  33.3%      67.31   1.77
amd_fvg_m5                 164    75  45.7%     153.53   3.57
amd_ob_m15                   9     6  66.7%     125.51  61.91
amd_ob_m5                   53    21  39.6%      79.34   2.20
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      29.96   4.60
mss_fvg_h1                   4     1  25.0%      32.07   5.07
mss_fvg_m15                  7     4  57.1%     423.52  77.31
mss_fvg_m5                  12     5  41.7%      61.10   1.59
mss_ob_m15                   3     0   0.0%     -25.28   0.00
mss_ob_m5                   15     7  46.7%     243.59   7.41
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
m15_range              313   134  42.8%     45795.41   3.53
session_range           28    12  42.9%      2284.26   2.10
(no AMD)                10     4  40.0%      -120.10   0.81
```

_Session-range widths (n=40): median=59.6 p75=83.0 p90=100.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           141    68  48.2%     27167.62   4.04
against          190    74  38.9%     20609.18   3.01

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                55  41.8%   2.65
EURUSD SHORT against             117  35.9%   2.87
GBPUSD LONG against               73  43.8%   3.33
GBPUSD SHORT golden               86  52.3%   4.87
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          106    48  45.3%     20256.16   4.06
opposing            44    20  45.5%      3390.28   3.41
no divergence      181    74  40.9%     24130.36   3.17
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         255   107  42.0%     30081.49   3.00
3-day         64    28  43.8%     10200.23   3.71
30-day        10     5  50.0%      3804.37  15.05
60-day        22    10  45.5%      3873.49   3.30
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     165    68  41.2%   3.01
near             no      90    39  43.3%   2.97
3-day           yes      36    14  38.9%   3.19
3-day            no      28    14  50.0%   5.13
30-day          yes       7     4  57.1%  15.42
30-day           no       3     1  33.3%   9.50
60-day          yes      18     9  50.0%   3.02
60-day           no       4     1  25.0%  34.78
```

**61 of 96 far-rung trades (64%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            214    95  44.4%     34093.32   3.96
OB              45    20  44.4%      9655.35   3.60
none (projection)      92    35  38.0%      4210.91   1.76
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             14     7  50.0%   2.12
near    fib_extension       132    57  43.2%   3.19
near    fvg                  29     9  31.0%   2.62
near    pdh_pdl              27    12  44.4%   4.43
near    pwh_pwl               3     0   0.0%   0.00
near    round_number         21     9  42.9%   3.95
near    swing                27    13  48.1%   2.88
d3      equal_hl              7     4  57.1%   3.78
d3      fib_extension        36    15  41.7%   3.31
d3      fvg                   4     2  50.0%   5.96
d3      round_number          4     1  25.0%   2.34
d3      swing                11     5  45.5%   5.02
d30     fib_extension         5     3  60.0% 177.07
d60     fib_extension        17     7  41.2%   2.40
d60     round_number          3     1  33.3%  50.30
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          108    44  40.7%     10561.33   2.23
  on 240T         78    36  46.2%      9613.54   2.80
  on D            30     8  26.7%       947.79   1.29
clear            243   106  43.6%     37398.25   4.07
```

## Entry vs the DAILY FVG / PD array (P74)

Every entry measured against the day's draw: how far the fill sat from the nearest unmitigated DAILY FVG, and whether that gap points the way we are trading (`with`) or the other way (`against`). Completed daily candles only — the forming bar carries hours that have not happened yet.

**Alignment with the daily FVG:** 140 of 351 (39.9%) entries traded WITH the gap, 211 (60.1%) against it.

```
Align         Trades  Wins    WR%      P&L ZAR     PF  medDist
----------------------------------------------------------------
with             140    60  42.9%     24867.67   3.76     46.4
against          211    90  42.7%     23091.90   2.96     14.9
```

**Distance from the daily FVG**

```
Dist pips     Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside            79    37  46.8%     13812.19   3.92
0-10              30     9  30.0%      1156.71   1.54
10-25             56    28  50.0%      8479.82   4.43
25-50             75    33  44.0%     12940.78   6.88
50-100            63    28  44.4%      9576.78   2.87
>100              48    15  31.2%      1993.30   1.48
```

**Alignment x where the gap sits** (`ahead` = we travel toward it)

```
Align     Pos        Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
with      inside         13     7  53.8%      5413.36  17.00
with      ahead           1     0   0.0%       -10.41   0.00
with      behind        126    53  42.1%     19464.72   3.25
against   inside         66    30  45.5%      8398.83   2.91
against   ahead         120    53  44.2%     13324.08   3.00
against   behind         25     7  28.0%      1368.99   2.88
```

**Nearest daily PD array of any kind** (fvg / ifvg / ob)

```
Type     Align      Trades  Wins    WR%      P&L ZAR     PF  medDist
--------------------------------------------------------------------
fvg      with          109    50  45.9%     23054.52   4.16     44.4
fvg      against       172    78  45.3%     21862.53   3.36     11.1
ob       with           24     8  33.3%        64.14   1.05     10.9
ob       against        46    14  30.4%      2978.39   2.04      0.0
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        122    54  44.3%     25060.24   6.00
             60T        103    44  42.7%     19521.44   6.11
             D           19    10  52.6%      5538.80   5.64
down (-1)    all         75    22  29.3%      4166.45   1.82
             60T         71    20  28.2%      2977.68   1.59
             D            4     2  50.0%      1188.76  28.34
none         all        154    74  48.1%     18732.88   2.75

with rev                157    61  38.9%     27589.13   5.02
against                  40    15  37.5%      1637.56   1.51
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             25     7  28.0%       240.62   1.24
2             89    39  43.8%     12417.62   3.91
3            158    65  41.1%     23238.86   3.08
4             70    31  44.3%      9134.06   3.21
5              8     7  87.5%      2811.79  13.87

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           230  44.3%   3.83      121  39.7%   2.28
NFP week Mon/Tue          29  62.1%   6.31      322  41.0%   3.14
Rate decision             30  36.7%   1.31      321  43.3%   3.62
PD prov (sweep)          315  42.5%   3.02       36  44.4%   7.37
Seasonal lean              0   0.0%   0.00      351  42.7%   3.31
HTF OB Context            84  48.8%   3.78      267  40.8%   3.12
D1 Draw                  309  43.0%   3.49       42  40.5%   2.25
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        29.02   1.12
continuation          79    40  50.6%     16333.68   3.90
(none)               267   109  40.8%     31596.87   3.12

Liq type          Trades    WR%     PF
----------------------------------------
breaker               19  47.4%   2.44
d1_fvg                48  47.9%   3.36
ob                     5  60.0%  23.78
pdhl                   6  33.3%   0.56
w_fvg                  6  66.7%  64.86
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             308   132  42.9%     43822.36   3.48
(none)                42    17  40.5%      3939.49   2.25
```

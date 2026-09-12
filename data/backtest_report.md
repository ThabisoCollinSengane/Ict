# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     736
win_rate_pct               43.9
profit_factor              4.01
starting_equity_ZAR        1000
ending_equity_ZAR          140575.71
pnl_ZAR                    139575.71
pnl_pct                    13957.57
max_drawdown_pct           -13.24
avg_win_ZAR                575.74
avg_loss_ZAR               -112.32
withdrawn_total_ZAR        132020.5
withdrawal_count           37
working_balance_ZAR        8555.21
working_max_drawdown_pct   21.89
```

## Gate funnel

```
checks                         120773
in_killzone                    120773
news_clear                     115551
nfp_fomc_ok                    99018
intermarket_signal             5532
pair_matches                   5532
mss_h1_m15_m5_ok               1926
daily_bias_ok                  1926
h1_bias_ok                     1926
h4_bias_ok                     1926
dealing_range_ok               110
consolidation_found            1030
manipulation_correct_dir       904
m5_fvg_correct_dir             1026
target_found                   1026
rr_ok                          1026
units_nonzero                  1026
limit_placed                   0
entry_opened                   722
pyramid_added                  14
pyramid_blocked_min_target     995
drawdown_halt                  2542
daily_loss_halt                1212
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      529
daily_pair_cap                 3141
weekly_amd_confirmed           327
session_handover_closed        2
htf_draw_full_cascade          301
htf_draw_partial               641
htf_draw_counter               338
htf_fvg_5050_hit               34
ote_zone                       5
choch_confirmed                39
low_conviction                 0
judas_divergence               2
ny_continuation                417
pm_gate_pair_news              0
dxy_flat                       74750
dxy_directional                20598
eurgbp_flat                    4610
eurgbp_flat_gbp_blocked        3314
breakout_confirmed             1088
sr_attempted                   84
sr_prev_session_ok             84
sr_enough_bars                 84
sr_consol_found                83
sr_breakout_found              51
session_range_found            65
soj_retest                     571
soj_sweep                      934
golden_rule_no                 498
mstruct_align                  982
phase_ny_judas                 531
gt_pool_sweep                  788
structure_stop_used            956
stop_capped_10pip              752
target_rung_far                359
risk_cap_ok                    722
pyramid_blocked_low_im         2617
eurgbp_directional             11425
soj_judas                      363
crt_turtle_soup                489
golden_rule_yes                473
gt_disp_wick                   750
m1_stop_used                   70
pyramid_blocked_favour         4922
dxy_fvg_room                   156
phase_london_judas             518
gt_macro_window                131
im_score_low                   7597
smt_pair_opposing              112
gt_mp_discount                 180
smt_pair_confirmed             288
mstruct_minor_sweep            132
gt_judas_reversal              114
gt_mp_extreme                  40
ny_continuation_gated          9
london_judas_ny_echo           22
sr_consol_no_sweep             20
sr_fail_no_sweep               6
sr_pdliq_attempted             21
sr_fail_low_swept_no_close_back 9
target_score_sized             384
crt_sweep_sized                177
risk_cap_skip                  304
golden_rule_sized              426
pdliq_sweep_sized              206
htf_fvg_breakout_sized         15
sr_pdliq_width_ok              2
sr_pdliq_sweep                 2
sr_fail_high_swept_no_close_back 4
sr_fail_both_swept             1
pyramid_blocked_no_pattern     6
```

_income: R132,021 across 37 withdrawals · working balance R8,555_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            484   202  41.7%     82696.09   3.54
OB             228   106  46.5%     52625.47   5.17
BREAKER         24    15  62.5%      4254.16   4.49

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            4     3  75.0%   4.00
BREAKER M5            19    11  57.9%   4.79
FVG H1                88    39  44.3%   5.70
FVG M15               77    30  39.0%   4.33
FVG M5               319   133  41.7%   2.84
OB M15                32    19  59.4%   7.72
OB M5                196    87  44.4%   4.88

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            15     9  60.0%   4.34
BREAKER GBPUSD             5     4  80.0%   7.01
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               239    99  41.4%   3.86
FVG GBPUSD               219    97  44.3%   3.56
FVG NZDUSD                26     6  23.1%   1.08
OB EURUSD                148    58  39.2%   3.36
OB GBPUSD                 56    36  64.3%  10.71
OB NZDUSD                 24    12  50.0%   9.80
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              2     1  50.0%     224.77   1.83
amd_breaker_m5              13     9  69.2%     195.24   6.88
amd_fvg_h1                  69    32  46.4%     225.64   5.08
amd_fvg_m15                 60    21  35.0%     192.28   3.43
amd_fvg_m5                 282   119  42.2%     132.94   2.92
amd_ob_m15                  21    12  57.1%     182.59   4.17
amd_ob_m5                  158    69  43.7%     206.84   4.42
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     2 100.0%     587.03    inf
mss_breaker_m5               6     2  33.3%       4.70   1.11
mss_fvg_h1                  18     7  38.9%     486.20   7.49
mss_fvg_m15                 14     8  57.1%     416.73  15.11
mss_fvg_m5                  24    11  45.8%     122.87   2.43
mss_ob_m15                  10     6  60.0%     468.55  58.40
mss_ob_m5                   38    18  47.4%     296.46   7.32
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  3     1  33.3%     118.60   5.05
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         4     1  25.0%     -46.94   0.32
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         3     1  33.3%      13.87   1.88
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              664   293  44.1%    128304.98   4.08
session_range           54    24  44.4%     10450.94   3.92
(no AMD)                18     6  33.3%       819.80   1.68
```

_Session-range widths (n=84): median=44.8 p75=61.5 p90=85.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           284   140  49.3%     69515.05   4.66
against          398   163  41.0%     58532.42   3.48

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               140  45.7%   4.26
EURUSD SHORT against             262  38.9%   3.37
GBPUSD LONG against              136  44.9%   3.72
GBPUSD SHORT golden              144  52.8%   5.04
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          197    85  43.1%     37846.49   4.02
opposing            84    44  52.4%     16740.27   5.00
no divergence      401   174  43.4%     73460.71   3.84
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         505   265  52.5%    146233.81   7.20
3-day        168    47  28.0%     -2258.36   0.84
30-day        27     6  22.2%      -922.99   0.71
60-day        36     5  13.9%     -3476.75   0.32
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     342   177  51.8%   7.45
near             no     163    88  54.0%   6.45
3-day           yes     106    26  24.5%   0.73
3-day            no      62    21  33.9%   1.39
30-day          yes      21     6  28.6%   0.75
30-day           no       6     0   0.0%   0.00
60-day          yes      29     4  13.8%   0.31
60-day           no       7     1  14.3%   0.43
```

**156 of 231 far-rung trades (68%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            468   212  45.3%     94020.95   4.64
OB             114    47  41.2%     27176.25   3.91
none (projection)     154    64  41.6%     18378.52   2.64
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             55    33  60.0%  11.45
near    fib_extension       272   149  54.8%   8.69
near    ith_liquidity         3     1  33.3%   2.28
near    pdh_pdl              71    29  40.8%   3.44
near    pwh_pwl               5     1  20.0%   0.75
near    round_number         32    16  50.0%   8.24
near    swing                65    35  53.8%   5.59
d3      equal_hl             26     8  30.8%   1.50
d3      fib_extension        77    21  27.3%   0.75
d3      ith_liquidity         4     1  25.0%   0.72
d3      itl_liquidity         6     2  33.3%   1.38
d3      pdh_pdl               7     2  28.6%   4.41
d3      pwh_pwl               7     1  14.3%   0.10
d3      round_number         11     4  36.4%   1.81
d3      swing                30     8  26.7%   0.97
d30     fib_extension        17     5  29.4%   0.62
d30     itl_liquidity         4     0   0.0%   0.00
d30     swing                 3     0   0.0%   0.00
d60     fib_extension        25     3  12.0%   0.27
d60     itl_liquidity         3     1  33.3%   1.73
d60     swing                 4     0   0.0%   0.00
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          322   135  41.9%     45331.75   3.08
  on 240T        244   104  42.6%     36212.79   3.34
  on D            78    31  39.7%      9118.97   2.43
clear            414   188  45.4%     94243.96   4.84
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        231   110  47.6%     56851.79   5.43
             60T        194    92  47.4%     44313.11   5.34
             D           37    18  48.6%     12538.68   5.76
down (-1)    all        166    64  38.6%     25634.66   3.28
             60T        147    54  36.7%     19887.82   2.93
             D           19    10  52.6%      5746.83   7.18
none         all        339   149  44.0%     57089.27   3.56

with rev                306   135  44.1%     68816.50   5.16
against                  91    39  42.9%     13669.94   2.82
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             39    13  33.3%       787.56   1.34
2            176    75  42.6%     27363.43   3.71
3            333   144  43.2%     67539.96   4.13
4            165    75  45.5%     34520.55   4.14
5             22    15  68.2%      9247.59   7.44

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           507  45.4%   4.39      229  40.6%   3.12
NFP week Mon/Tue          81  56.8%   6.80      655  42.3%   3.73
Rate decision             57  43.9%   3.69      679  43.9%   4.03
PD prov (sweep)          639  42.7%   3.54       97  51.5%   7.97
Seasonal lean              0   0.0%   0.00      736  43.9%   4.01
HTF OB Context           213  47.9%   5.31      523  42.3%   3.39
D1 Draw                  663  44.3%   4.08       73  39.7%   3.38
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        73.77   1.36
continuation         208   101  48.6%     64150.51   5.37
(none)               523   221  42.3%     75351.44   3.39

Liq type          Trades    WR%     PF
----------------------------------------
breaker               36  47.2%   3.64
d1_fvg               120  45.8%   4.77
ob                     9  66.7%  49.21
pdhl                  16  37.5%   1.77
w_fvg                 32  56.2%  12.08
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     1  33.3%         5.83   1.03
equal_hl             660   293  44.4%    128772.44   4.09
(none)                73    29  39.7%     10797.45   3.38
```

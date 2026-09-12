# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     767
win_rate_pct               43.8
profit_factor              4.81
starting_equity_ZAR        1000
ending_equity_ZAR          148861.39
pnl_ZAR                    147861.39
pnl_pct                    14786.14
max_drawdown_pct           -13.42
avg_win_ZAR                555.6
avg_loss_ZAR               -90.07
withdrawn_total_ZAR        139760.49
withdrawal_count           37
working_balance_ZAR        9100.91
working_max_drawdown_pct   18.24
```

## Gate funnel

```
checks                         120311
in_killzone                    120311
news_clear                     115614
nfp_fomc_ok                    99175
intermarket_signal             5214
pair_matches                   5214
mss_h1_m15_m5_ok               1775
daily_bias_ok                  1775
h1_bias_ok                     1775
h4_bias_ok                     1775
dealing_range_ok               97
consolidation_found            884
manipulation_correct_dir       767
m5_fvg_correct_dir             883
target_found                   883
rr_ok                          883
units_nonzero                  883
limit_placed                   0
entry_opened                   752
pyramid_added                  15
pyramid_blocked_min_target     1060
drawdown_halt                  2446
daily_loss_halt                802
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      535
daily_pair_cap                 3282
weekly_amd_confirmed           298
session_handover_closed        2
htf_draw_full_cascade          190
htf_draw_partial               605
htf_draw_counter               345
htf_fvg_5050_hit               34
ote_zone                       5
choch_confirmed                32
low_conviction                 0
judas_divergence               2
ny_continuation                339
pm_gate_pair_news              0
dxy_flat                       75058
dxy_directional                20300
eurgbp_flat                    4536
eurgbp_flat_gbp_blocked        3332
breakout_confirmed             970
sr_attempted                   76
sr_prev_session_ok             76
sr_enough_bars                 76
sr_consol_found                75
sr_breakout_found              45
session_range_found            57
soj_retest                     513
soj_sweep                      804
golden_rule_no                 445
mstruct_align                  845
phase_ny_judas                 444
gt_pool_sweep                  676
structure_stop_used            818
stop_capped_10pip              624
target_rung_far                249
target_rung_far_floored        16
risk_cap_ok                    752
pyramid_blocked_low_im         2759
eurgbp_directional             11204
soj_judas                      291
crt_turtle_soup                425
golden_rule_yes                390
gt_disp_wick                   663
m1_stop_used                   65
pyramid_blocked_favour         5178
dxy_fvg_room                   138
phase_london_judas             459
gt_macro_window                125
im_score_low                   7577
smt_pair_opposing              97
gt_mp_discount                 175
smt_pair_confirmed             243
mstruct_minor_sweep            124
gt_judas_reversal              105
gt_mp_extreme                  40
ny_continuation_gated          9
london_judas_ny_echo           15
target_rung_far_sized          233
sr_consol_no_sweep             20
sr_fail_no_sweep               6
sr_pdliq_attempted             21
sr_fail_low_swept_no_close_back 9
target_score_sized             337
crt_sweep_sized                143
risk_cap_skip                  131
golden_rule_sized              346
pdliq_sweep_sized              159
pyramid_blocked_no_pattern     7
htf_fvg_breakout_sized         15
sr_pdliq_width_ok              2
sr_pdliq_sweep                 2
sr_fail_high_swept_no_close_back 4
sr_fail_both_swept             1
```

_income: R139,760 across 37 withdrawals · working balance R9,101_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            510   214  42.0%     88404.47   4.10
OB             234   108  46.2%     55205.45   6.78
BREAKER         23    14  60.9%      4251.48   6.88

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            4     3  75.0%  13.81
BREAKER M5            18    10  55.6%   4.95
FVG H1                89    39  43.8%   6.16
FVG M15               85    35  41.2%   4.75
FVG M5               336   140  41.7%   3.41
OB M15                33    21  63.6%  17.07
OB M5                201    87  43.3%   6.11

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            15     9  60.0%  11.95
BREAKER GBPUSD             5     4  80.0%  14.03
BREAKER NZDUSD             3     1  33.3%   2.42
FVG EURUSD               247   103  41.7%   5.09
FVG GBPUSD               233   104  44.6%   3.71
FVG NZDUSD                30     7  23.3%   1.01
OB EURUSD                155    60  38.7%   4.49
OB GBPUSD                 55    35  63.6%  13.32
OB NZDUSD                 24    13  54.2%  14.71
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              2     1  50.0%     420.19   6.59
amd_breaker_m5              11     7  63.6%     175.82   5.51
amd_fvg_h1                  70    32  45.7%     195.50   4.71
amd_fvg_m15                 65    23  35.4%     201.31   3.63
amd_fvg_m5                 297   125  42.1%     136.00   3.42
amd_ob_m15                  22    14  63.6%     263.16  12.48
amd_ob_m5                  161    68  42.2%     216.30   5.63
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     2 100.0%     542.63    inf
mss_breaker_m5               7     3  42.9%      46.80   3.26
mss_fvg_h1                  18     7  38.9%     515.05  13.37
mss_fvg_m15                 17    11  64.7%     429.71  19.38
mss_fvg_m5                  25    12  48.0%     153.61   3.94
mss_ob_m15                  10     6  60.0%     342.36  44.48
mss_ob_m5                   40    19  47.5%     275.22   8.61
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  3     1  33.3%     236.93   9.09
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         4     1  25.0%     -46.94   0.32
pyramid_im0.8_ob_m15         1     1 100.0%     159.84    inf
pyramid_im1.0_fvg_m15        1     0   0.0%    -173.16   0.00
pyramid_im1.0_fvg_m5         4     1  25.0%     -13.64   0.62
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -18.38   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              695   307  44.2%    136764.15   4.90
session_range           53    23  43.4%     10369.68   4.87
(no AMD)                19     6  31.6%       727.56   1.65
```

_Session-range widths (n=76): median=44.3 p75=68.4 p90=86.7 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           301   150  49.8%     76661.99   5.60
against          409   165  40.3%     60864.40   4.21

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               145  46.2%   5.81
EURUSD SHORT against             272  38.6%   4.48
GBPUSD LONG against              137  43.8%   3.67
GBPUSD SHORT golden              156  53.2%   5.45
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          203    87  42.9%     39766.50   4.83
opposing            86    45  52.3%     18434.20   6.71
no divergence      421   183  43.5%     79325.69   4.60
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         511   269  52.6%    150999.35   7.18
3-day        182    53  29.1%      -503.66   0.94
30-day        29     7  24.1%      -776.84   0.63
60-day        45     7  15.6%     -1857.45   0.48
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     347   180  51.9%   7.38
near             no     164    89  54.3%   6.52
3-day           yes     120    32  26.7%   0.88
3-day            no      62    21  33.9%   1.28
30-day          yes      23     7  30.4%   0.66
30-day           no       6     0   0.0%   0.00
60-day          yes      38     6  15.8%   0.48
60-day           no       7     1  14.3%   0.43
```

**181 of 256 far-rung trades (71%) were escalated.** High means P20 pushed them out there and de-escalation is the fix; low means the far target was simply the nearest one available, and only skipping or resizing can touch it.

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            481   218  45.3%     94116.00   5.25
OB             124    50  40.3%     29064.35   4.40
none (projection)     162    68  42.0%     24681.05   4.03
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             56    32  57.1%   8.21
near    fib_extension       274   152  55.5%   8.78
near    ith_liquidity         3     1  33.3%   2.28
near    pdh_pdl              73    30  41.1%   3.50
near    pwh_pwl               5     1  20.0%   0.75
near    round_number         33    17  51.5%   8.66
near    swing                65    35  53.8%   5.77
d3      equal_hl             29     8  27.6%   1.05
d3      fib_extension        85    25  29.4%   0.94
d3      ith_liquidity         5     1  20.0%   0.33
d3      itl_liquidity         8     3  37.5%   2.72
d3      pdh_pdl               7     3  42.9%  16.43
d3      pwh_pwl               7     1  14.3%   0.10
d3      round_number         11     4  36.4%   1.80
d3      swing                30     8  26.7%   0.94
d30     fib_extension        20     7  35.0%   0.71
d30     itl_liquidity         4     0   0.0%   0.00
d30     swing                 3     0   0.0%   0.00
d60     equal_hl              4     0   0.0%   0.00
d60     fib_extension        30     5  16.7%   0.49
d60     itl_liquidity         4     1  25.0%   0.83
d60     swing                 4     0   0.0%   0.00
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          334   141  42.2%     47603.74   3.66
  on 240T        251   108  43.0%     37564.56   3.91
  on D            83    33  39.8%     10039.18   3.02
clear            433   195  45.0%    100257.66   5.79
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        237   113  47.7%     59590.55   6.11
             60T        200    95  47.5%     46403.59   5.79
             D           37    18  48.6%     13186.96   7.74
down (-1)    all        169    63  37.3%     23431.78   3.65
             60T        149    53  35.6%     17109.75   3.11
             D           20    10  50.0%      6322.03   9.65
none         all        361   160  44.3%     64839.06   4.54

with rev                314   136  43.3%     68861.18   5.77
against                  92    40  43.5%     14161.16   3.33
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              2     1  50.0%       109.69  16.81
1             43    16  37.2%      3561.24   2.71
2            182    79  43.4%     30178.91   4.85
3            349   150  43.0%     71812.49   4.80
4            168    75  44.6%     33059.84   4.69
5             23    15  65.2%      9139.24   9.95

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           532  45.3%   5.23      235  40.4%   3.86
NFP week Mon/Tue          80  55.0%   7.87      687  42.5%   4.53
Rate decision             58  44.8%   5.44      709  43.7%   4.77
PD prov (sweep)          664  42.2%   4.13      103  54.4%  12.39
Seasonal lean              0   0.0%   0.00      767  43.8%   4.81
HTF OB Context           223  47.5%   6.36      544  42.3%   4.10
D1 Draw                  684  44.2%   4.81       83  41.0%   4.80
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 5     1  20.0%        73.77   1.36
continuation         218   105  48.2%     65222.66   6.45
(none)               544   230  42.3%     82564.97   4.10

Liq type          Trades    WR%     PF
----------------------------------------
breaker               38  44.7%   3.29
d1_fvg               127  44.9%   5.49
ob                     9  66.7%  47.95
pdhl                  17  41.2%   2.73
w_fvg                 32  59.4%  19.98
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 3     1  33.3%         5.83   1.03
equal_hl             681   301  44.2%    133806.21   4.83
(none)                83    34  41.0%     14049.36   4.80
```

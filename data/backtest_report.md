# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     297
win_rate_pct               41.1
profit_factor              2.62
starting_equity_ZAR        1000
ending_equity_ZAR          27911.08
pnl_ZAR                    26911.08
pnl_pct                    2691.11
max_drawdown_pct           -13.38
avg_win_ZAR                356.41
avg_loss_ZAR               -94.69
withdrawn_total_ZAR        20373.16
withdrawal_count           13
working_balance_ZAR        7537.92
working_max_drawdown_pct   31.6
```

## Gate funnel

```
checks                         60060
in_killzone                    60060
news_clear                     55637
nfp_fomc_ok                    47957
intermarket_signal             3372
pair_matches                   3372
mss_h1_m15_m5_ok               1251
daily_bias_ok                  1251
h1_bias_ok                     1251
h4_bias_ok                     1251
dealing_range_ok               42
consolidation_found            733
manipulation_correct_dir       673
m5_fvg_correct_dir             736
target_found                   736
rr_ok                          736
units_nonzero                  357
limit_placed                   0
entry_opened                   289
pyramid_added                  8
pyramid_blocked_min_target     221
drawdown_halt                  3364
daily_loss_halt                377
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      184
daily_pair_cap                 1739
weekly_amd_confirmed           205
session_handover_closed        0
htf_draw_full_cascade          108
htf_draw_partial               523
htf_draw_counter               191
htf_fvg_5050_hit               12
ote_zone                       1
choch_confirmed                21
low_conviction                 0
judas_divergence               2
ny_continuation                307
pm_gate_pair_news              0
dxy_flat                       35051
dxy_directional                10983
eurgbp_flat                    2094
eurgbp_flat_gbp_blocked        1368
breakout_confirmed             809
sr_attempted                   67
sr_prev_session_ok             67
sr_enough_bars                 67
sr_consol_found                66
sr_breakout_found              41
session_range_found            52
soj_retest                     359
soj_sweep                      657
golden_rule_no                 370
mstruct_align                  696
phase_ny_judas                 370
gt_pool_sweep                  611
structure_stop_used            703
stop_capped_10pip              606
target_rung_far                379
target_rung_skipped            379
risk_cap_ok                    289
eurgbp_directional             6458
soj_judas                      298
crt_turtle_soup                321
golden_rule_yes                335
gt_disp_wick                   513
m1_stop_used                   33
pyramid_blocked_favour         1420
dxy_fvg_room                   87
phase_london_judas             378
gt_macro_window                81
im_score_low                   4047
pyramid_blocked_low_im         708
smt_pair_opposing              115
gt_mp_discount                 88
smt_pair_confirmed             232
mstruct_minor_sweep            120
gt_judas_reversal              63
gt_mp_extreme                  12
sr_consol_no_sweep             17
sr_fail_no_sweep               4
sr_pdliq_attempted             18
london_judas_ny_echo           6
sr_fail_low_swept_no_close_back 7
golden_rule_sized              146
target_score_sized             96
risk_cap_skip                  68
pdliq_sweep_sized              36
ny_continuation_gated          4
crt_sweep_sized                53
htf_fvg_breakout_sized         1
sr_pdliq_width_ok              3
sr_pdliq_sweep                 3
sr_fail_high_swept_no_close_back 4
sr_fail_both_swept             2
```

_income: R20,373 across 13 withdrawals · working balance R7,538_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            230    93  40.4%     20727.27   2.55
OB              60    24  40.0%      4878.68   2.54
BREAKER          7     5  71.4%      1305.13  59.18

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            1     1 100.0%    inf
BREAKER M5             5     3  60.0%  12.89
FVG H1                30    11  36.7%   2.04
FVG M15               30    12  40.0%   3.50
FVG M5               170    70  41.2%   2.49
OB M15                 9     3  33.3%   2.06
OB M5                 51    21  41.2%   2.58

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             5     3  60.0%  12.89
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               107    40  37.4%   2.39
FVG GBPUSD               113    49  43.4%   2.60
FVG NZDUSD                10     4  40.0%   4.12
OB EURUSD                 33     8  24.2%   0.46
OB GBPUSD                 23    13  56.5%   8.97
OB NZDUSD                  4     3  75.0% 106.37
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m5               2     2 100.0%      87.13    inf
amd_fvg_h1                  25    10  40.0%      71.41   2.00
amd_fvg_m15                 23     9  39.1%     109.70   3.07
amd_fvg_m5                 157    67  42.7%      93.68   2.53
amd_ob_m15                   7     3  42.9%      39.37   2.47
amd_ob_m5                   40    16  40.0%      98.03   2.62
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              1     1 100.0%     974.25    inf
mss_breaker_m5               3     1  33.3%      30.81   5.12
mss_fvg_h1                   4     1  25.0%      32.07   5.07
mss_fvg_m15                  5     2  40.0%     187.54   3.41
mss_fvg_m5                   5     2  40.0%      31.67   2.01
mss_ob_m15                   2     0   0.0%     -18.69   0.00
mss_ob_m5                   11     5  45.5%      65.37   2.37
news_fvg_m15                 1     0   0.0%      -9.25   0.00
news_fvg_m5                  2     0   0.0%     -43.94   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     603.06    inf
pyramid_im0.8_fvg_m5         1     1 100.0%      87.87    inf
pyramid_im1.0_fvg_m5         2     0   0.0%     -23.59   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -8.33   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -17.14   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              260   106  40.8%     24435.93   2.70
session_range           28    12  42.9%      2372.41   2.35
(no AMD)                 9     4  44.4%       102.75   1.25
```

_Session-range widths (n=67): median=57.1 p75=77.1 p90=95.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           122    55  45.1%     16330.06   3.47
against          161    60  37.3%      8989.15   1.94

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                46  34.8%   2.04
EURUSD SHORT against              99  35.4%   1.83
GBPUSD LONG against               62  40.3%   2.15
GBPUSD SHORT golden               76  51.3%   4.42
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           86    36  41.9%      8075.39   2.74
opposing            35    13  37.1%       287.09   1.14
no divergence      162    66  40.7%     16956.73   2.79
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         297   122  41.1%     26911.08   2.62
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     192    81  42.2%   2.68
near             no     105    41  39.0%   2.47
```

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG            184    79  42.9%     24464.33   3.74
OB              38    10  26.3%      -611.76   0.83
none (projection)      75    33  44.0%      3058.51   1.76
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             21    11  52.4%   2.04
near    fib_extension       179    75  41.9%   3.04
near    ith_liquidity         3     0   0.0%   0.00
near    pdh_pdl              29    13  44.8%   3.00
near    pwh_pwl               4     2  50.0%   2.87
near    round_number         28    11  39.3%   4.63
near    swing                32    10  31.2%   1.65
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked          106    41  38.7%      9702.04   2.44
  on 240T         78    32  41.0%      7953.49   2.74
  on D            28     9  32.1%      1748.55   1.81
clear            191    81  42.4%     17209.04   2.75
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all        107    47  43.9%     16327.18   5.29
             60T         92    39  42.4%     13211.85   6.01
             D           15     8  53.3%      3115.33   3.67
down (-1)    all         63    17  27.0%      2100.41   1.52
             60T         59    16  27.1%      2563.63   1.73
             D            4     1  25.0%      -463.22   0.07
none         all        127    58  45.7%      8483.50   1.97

with rev                138    53  38.4%     17447.85   3.97
against                  32    11  34.4%       979.74   1.50
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     1 100.0%       116.62    inf
1             23     5  21.7%      -476.03   0.65
2             69    29  42.0%      6101.30   2.93
3            139    55  39.6%     12541.55   2.34
4             55    25  45.5%      6038.54   3.50
5             10     7  70.0%      2589.11  10.67

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           195  41.5%   2.83      102  40.2%   2.18
NFP week Mon/Tue          25  56.0%   3.29      272  39.7%   2.57
Rate decision             24  41.7%   1.28      273  41.0%   2.80
PD prov (sweep)          274  41.2%   2.52       23  39.1%   4.88
Seasonal lean              0   0.0%   0.00      297  41.1%   2.62
HTF OB Context            69  49.3%   5.66      228  38.6%   2.06
D1 Draw                  261  42.5%   2.90       36  30.6%   1.29
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
inside                 4     0   0.0%      -203.73   0.00
continuation          65    34  52.3%     12270.70   6.15
(none)               228    88  38.6%     14844.12   2.06

Liq type          Trades    WR%     PF
----------------------------------------
breaker               16  43.8%   1.47
d1_fvg                37  48.6%   4.31
ob                     5  60.0%  24.57
pdhl                   5  40.0%   7.69
w_fvg                  6  66.7%  65.95
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
d1_fvg                 1     1 100.0%       197.72    inf
equal_hl             260   110  42.3%     25891.49   2.88
(none)                36    11  30.6%       821.88   1.29
```

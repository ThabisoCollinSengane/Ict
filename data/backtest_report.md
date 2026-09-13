# HistData backtest — 2024–pull (3 yr)

## Results

```
trades                     157
win_rate_pct               43.9
profit_factor              4.09
starting_equity_ZAR        1000
ending_equity_ZAR          16630.63
pnl_ZAR                    15630.63
pnl_pct                    1563.06
max_drawdown_pct           -10.79
avg_win_ZAR                299.87
avg_loss_ZAR               -57.5
withdrawn_total_ZAR        8759.59
withdrawal_count           4
working_balance_ZAR        7871.04
working_max_drawdown_pct   15.02
```

## Gate funnel

```
checks                         30688
in_killzone                    30688
news_clear                     29463
nfp_fomc_ok                    25344
intermarket_signal             1730
pair_matches                   1730
mss_h1_m15_m5_ok               681
daily_bias_ok                  681
h1_bias_ok                     681
h4_bias_ok                     681
dealing_range_ok               30
consolidation_found            488
manipulation_correct_dir       438
m5_fvg_correct_dir             489
target_found                   489
rr_ok                          489
units_nonzero                  157
limit_placed                   0
entry_opened                   154
pyramid_added                  3
pyramid_blocked_min_target     278
drawdown_halt                  795
daily_loss_halt                69
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      45
daily_pair_cap                 421
weekly_amd_confirmed           122
session_handover_closed        1
htf_draw_full_cascade          60
htf_draw_partial               406
htf_draw_counter               75
htf_fvg_5050_hit               32
ote_zone                       2
choch_confirmed                32
low_conviction                 0
judas_divergence               0
ny_continuation                203
pm_gate_pair_news              0
dxy_flat                       19338
dxy_directional                5540
eurgbp_directional             2794
im_score_low                   1809
breakout_confirmed             354
soj_retest                     290
soj_sweep                      449
crt_turtle_soup                203
golden_rule_no                 296
mstruct_align                  472
phase_ny_judas                 267
gt_pool_sweep                  376
gt_disp_wick                   352
structure_stop_used            472
stop_capped_10pip              278
risk_cap_ok                    154
pyramid_blocked_favour         1346
eurgbp_flat                    1671
eurgbp_flat_gbp_blocked        1055
golden_rule_yes                167
phase_london_judas             231
gt_mp_discount                 50
gt_mp_extreme                  8
soj_judas                      159
mstruct_minor_sweep            76
london_judas_ny_echo           1
pyramid_blocked_low_im         688
smt_pair_opposing              63
target_rung_far                332
target_rung_skipped            332
sr_attempted                   40
sr_prev_session_ok             40
sr_enough_bars                 40
sr_consol_found                40
sr_breakout_found              25
session_range_found            30
gt_macro_window                62
smt_pair_confirmed             109
m1_stop_used                   17
dxy_fvg_room                   78
gt_judas_reversal              64
sr_consol_no_sweep             11
sr_fail_high_swept_no_close_back 4
sr_pdliq_attempted             11
sr_fail_low_swept_no_close_back 7
target_score_sized             43
pdliq_sweep_sized              16
pyramid_blocked_no_pattern     5
golden_rule_sized              28
crt_sweep_sized                9
sr_pdliq_width_ok              1
sr_pdliq_sweep                 1
htf_fvg_breakout_sized         2
risk_cap_skip                  3
ny_continuation_gated          3
```

_income: R8,760 across 4 withdrawals · working balance R7,871_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG             93    44  47.3%     10960.67   5.04
OB              61    23  37.7%      4638.13   3.01
BREAKER          3     2  66.7%        31.82   1.82

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER M5             3     2  66.7%   1.82
FVG H1                21    11  52.4%   8.80
FVG M15               13     8  61.5%   4.09
FVG M5                59    25  42.4%   3.75
OB M15                 8     3  37.5%   3.56
OB M5                 53    20  37.7%   2.84

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD             1     1 100.0%    inf
BREAKER GBPUSD             2     1  50.0%   0.90
FVG EURUSD                43    19  44.2%   8.06
FVG GBPUSD                43    22  51.2%   3.39
FVG NZDUSD                 7     3  42.9%   2.04
OB EURUSD                 43    14  32.6%   3.10
OB GBPUSD                 14     8  57.1%   3.05
OB NZDUSD                  4     1  25.0%   2.45
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m5               1     1 100.0%      35.15    inf
amd_fvg_h1                  16    10  62.5%     358.13  66.52
amd_fvg_m15                  8     5  62.5%      57.10   2.87
amd_fvg_m5                  52    21  40.4%      63.77   3.35
amd_ob_m15                   6     1  16.7%     112.34   2.26
amd_ob_m5                   45    19  42.2%      85.48   4.31
mss_breaker_m5               2     1  50.0%      -1.67   0.91
mss_fvg_h1                   5     1  20.0%     -91.66   0.22
mss_fvg_m15                  5     3  60.0%      70.65  20.91
mss_fvg_m5                   4     3  75.0%     289.71   4.59
mss_ob_m15                   2     2 100.0%     348.54    inf
mss_ob_m5                    7     1  14.3%     -82.29   0.06
news_fvg_m5                  1     1 100.0%     443.68    inf
pyramid_im0.8_fvg_m5         2     0   0.0%     -19.98   0.00
pyramid_im0.8_ob_m5          1     0   0.0%      -3.70   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range              140    60  42.9%     15049.97   4.44
session_range           15     9  60.0%       818.87   2.81
(no AMD)                 2     0   0.0%      -238.21   0.00
```

_Session-range widths (n=40): median=19.3 p75=27.9 p90=48.0 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden            54    27  50.0%      8133.49   7.21
against           92    38  41.3%      6754.82   3.15

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                26  46.2%  14.89
EURUSD SHORT against              61  36.1%   3.16
GBPUSD LONG against               31  51.6%   3.14
GBPUSD SHORT golden               28  53.6%   3.35
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           41    18  43.9%      3421.89   3.19
opposing            20    11  55.0%      3268.87  10.56
no divergence       85    36  42.4%      8197.56   4.22
```

## Target rung on the cascade ladder (P67)

The pure-price cascade study measured how often price reaches each pool after a daily sweep: 3-day **58%/61%**, 30-day **21%/20%**, 60-day **15%/13%**. This asks which rung the engine actually aimed at. A target out at d30/d60 is one price rarely delivers to — the lever there is skip or resize, NOT hold longer (HTF_TARGET_PREF -22% MaxDD, TRAIL_AT_TP -49%, TP-runner -75% all died aiming further).
```
Rung      Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
near         157    69  43.9%     15630.63   4.09
```

### Far rung × P20 escalation (P70)

Does escalation CREATE the far bucket, or is it just where the nearest qualifying target happened to sit?
```
Rung      Escalated  Trades  Wins    WR%     PF
------------------------------------------------
near            yes     111    44  39.6%   3.64
near             no      46    25  54.3%   6.07
```

## Target on an HTF PD array (P68)

The trader's draw definition: the daily draws are the W1/D1/H4 PD arrays, and the **FVG is the most important** — price gravitates to an unfilled gap even if it takes days. A fib extension is a PROJECTION: nothing rests there and nothing is pulled to it. This asks what the engine actually aimed at.
```
PD array    Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
FVG             91    39  42.9%      8399.48   4.00
OB              28    12  42.9%      1477.03   2.19
none (projection)      38    18  47.4%      5754.12   6.62
```

## Rung x target family (P68)

The question the rung table alone cannot answer: do the far rungs lose because they are FAR, or because they are fib PROJECTIONS rather than real draws? If the loss concentrates in fib_extension, distance was never the variable.
```
Rung    Family           Trades  Wins    WR%     PF
----------------------------------------------------
near    equal_hl             19     7  36.8%   2.44
near    fib_extension        75    35  46.7%   4.47
near    itl_liquidity         3     2  66.7%   0.69
near    pdh_pdl              32    11  34.4%   4.74
near    pwh_pwl               3     0   0.0%   0.00
near    round_number          6     4  66.7%  54.34
near    swing                18    10  55.6%   4.12
```

## Path obstruction (P67)

An unmitigated OPPOSING HTF gap sitting BETWEEN entry and target — somewhere price is drawn to stall on the way to its draw. A statement about where price is going, not what the pattern looks like.
```
Path          Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------
blocked           85    33  38.8%      4668.18   2.28
  on 240T         70    26  37.1%      4033.03   2.51
  on D            15     7  46.7%       635.14   1.66
clear             72    36  50.0%     10962.45   8.69
```

## Dollar reversal day (P64)

DXY swept an intermediate level and CLOSED BACK through it.
The complement of dxy_mstruct_sweep, which only fires while the
intermediate level HOLDS. +1 = dollar reversed up (pairs down),
-1 = dollar reversed down (pairs up). Does the trade agree?
```
DXY rev      TF      Trades  Wins    WR%      P&L ZAR     PF
------------------------------------------------------------
up (+1)      all         55    27  49.1%      9110.53   6.82
             60T         51    26  51.0%      7631.87   8.90
             D            4     1  25.0%      1478.66   3.47
down (-1)    all         30    14  46.7%      2806.67   4.91
             60T         24    10  41.7%      1651.59   3.32
             D            6     4  66.7%      1155.09 155.91
none         all         72    28  38.9%      3713.42   2.34

with rev                 70    34  48.6%      8414.98   5.83
against                  15     7  46.7%      3502.22   7.47
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
1              6     3  50.0%       157.30   1.36
2             45    14  31.1%      1980.48   2.40
3             76    36  47.4%      8637.84   4.88
4             27    15  55.6%      4949.81  10.99
5              3     1  33.3%       -94.81   0.81

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile           110  48.2%   3.85       47  34.0%   4.95
NFP week Mon/Tue          18  44.4%   2.95      139  43.9%   4.45
Rate decision             14  57.1%  30.71      143  42.7%   3.89
PD prov (sweep)          132  43.2%   4.75       25  48.0%   2.32
Seasonal lean              0   0.0%   0.00      157  43.9%   4.09
HTF OB Context            36  47.2%   7.89      121  43.0%   3.16
D1 Draw                  137  44.5%   4.11       20  40.0%   3.92
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
continuation          36    17  47.2%      6830.73   7.89
(none)               121    52  43.0%      8799.89   3.16

Liq type          Trades    WR%     PF
----------------------------------------
breaker                5  60.0%   4.58
d1_fvg                17  35.3%   7.75
ob                     2 100.0%    inf
pdhl                   9  55.6%   5.88
w_fvg                  3  33.3%  17.77
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
equal_hl             137    61  44.5%     14003.58   4.11
(none)                20     8  40.0%      1627.04   3.92
```

# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     63
win_rate_pct               11.1
profit_factor              0.37
starting_equity_ZAR        1000
ending_equity_ZAR          484.06
pnl_ZAR                    -515.94
pnl_pct                    -51.59
max_drawdown_pct           -49.66
avg_win_ZAR                44.11
avg_loss_ZAR               -14.73
```

## Gate funnel

```
checks                         128974
in_killzone                    128974
news_clear                     13606
nfp_fomc_ok                    11360
intermarket_signal             586
pair_matches                   586
mss_h1_m15_m5_ok               120
daily_bias_ok                  120
h1_bias_ok                     120
h4_bias_ok                     120
dealing_range_ok               7
consolidation_found            60
manipulation_correct_dir       57
m5_fvg_correct_dir             62
target_found                   62
rr_ok                          62
units_nonzero                  62
limit_placed                   0
entry_opened                   62
pyramid_added                  1
pyramid_blocked_min_target     20
drawdown_halt                  115142
daily_loss_halt                48
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      4
daily_pair_cap                 577
weekly_amd_confirmed           20
session_handover_closed        1
htf_draw_full_cascade          1
htf_draw_partial               40
htf_draw_counter               28
htf_fvg_5050_hit               3
ote_zone                       0
choch_confirmed                1
low_conviction                 0
judas_divergence               0
ny_continuation                24
pm_gate_pair_news              0
breakout_confirmed             75
sr_attempted                   7
sr_prev_session_ok             7
sr_enough_bars                 7
sr_consol_found                7
sr_breakout_found              4
session_range_found            5
soj_retest                     41
soj_sweep                      59
dxy_fvg_room                   6
golden_rule_no                 36
mstruct_align                  59
phase_ny_judas                 32
gt_pool_sweep                  51
structure_stop_used            62
stop_capped_10pip              54
risk_cap_ok                    62
pyramid_blocked_low_im         170
soj_judas                      18
crt_turtle_soup                28
golden_rule_yes                25
gt_disp_wick                   43
pyramid_blocked_favour         232
phase_london_judas             30
smt_pair_confirmed             16
mstruct_minor_sweep            12
gt_macro_window                13
london_judas_ny_echo           2
smt_pair_opposing              3
gt_judas_reversal              8
sr_consol_no_sweep             2
sr_fail_no_tail                2
sr_pdliq_attempted             2
gt_mp_discount                 5
gt_mp_extreme                  1
```

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG             52     7  13.5%      -375.06   0.45
OB              11     0   0.0%      -140.88   0.00

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
FVG M15                5     0   0.0%   0.00
FVG M5                47     7  14.9%   0.50
OB M5                 11     0   0.0%   0.00

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
FVG EURUSD                28     3  10.7%   0.44
FVG GBPUSD                23     4  17.4%   0.47
FVG NZDUSD                 1     0   0.0%   0.00
OB EURUSD                  8     0   0.0%   0.00
OB GBPUSD                  3     0   0.0%   0.00
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_fvg_m15                  3     0   0.0%     -19.30   0.00
amd_fvg_m5                  44     7  15.9%      -5.76   0.55
amd_ob_m5                    9     0   0.0%     -14.17   0.00
mss_fvg_m15                  2     0   0.0%      -1.06   0.00
mss_fvg_m5                   1     0   0.0%     -19.24   0.00
mss_ob_m5                    2     0   0.0%      -6.66   0.00
news_fvg_m5                  1     0   0.0%     -23.12   0.00
pyramid_im1.0_fvg_m5         1     0   0.0%     -19.24   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range               56     7  12.5%      -416.50   0.43
session_range            5     0   0.0%       -97.77   0.00
(no AMD)                 2     0   0.0%        -1.67   0.00
```

_Session-range widths (n=7): median=49.7 p75=70.9 p90=80.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden            25     5  20.0%       -76.29   0.73
against           37     2   5.4%      -438.26   0.19

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                11  18.2%   0.86
EURUSD SHORT against              25   4.0%   0.23
GBPUSD LONG against               12   8.3%   0.11
GBPUSD SHORT golden               14  21.4%   0.67
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           16     3  18.8%      -104.06   0.47
opposing             3     1  33.3%        -2.41   0.88
no divergence       43     3   7.0%      -408.09   0.33
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     0   0.0%       -19.24   0.00
1              5     1  20.0%        40.91   1.79
2             18     2  11.1%      -134.31   0.44
3             27     2   7.4%      -359.83   0.09
4             10     2  20.0%       -41.99   0.64
5              2     0   0.0%        -1.48   0.00

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile            45   8.9%   0.19       18  16.7%   0.83
NFP week Mon/Tue           8  12.5%   0.76       55  10.9%   0.34
Rate decision              4  25.0%   2.22       59  10.2%   0.28
PD prov (sweep)           60  11.7%   0.39        3   0.0%   0.00
Seasonal lean              0   0.0%   0.00       63  11.1%   0.37
HTF OB Context            12  16.7%   0.32       51   9.8%   0.38
D1 Draw                   43   9.3%   0.19       20  15.0%   0.84
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
continuation          12     2  16.7%       -73.45   0.32
(none)                51     5   9.8%      -442.49   0.38

Liq type          Trades    WR%     PF
----------------------------------------
breaker                4  25.0%   1.81
d1_fvg                 7  14.3%   0.22
pdhl                   1   0.0%   0.00
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
equal_hl              43     4   9.3%      -479.52   0.19
(none)                20     3  15.0%       -36.42   0.84
```

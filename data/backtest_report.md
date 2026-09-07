# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     60
win_rate_pct               11.7
profit_factor              0.33
starting_equity_ZAR        1000
ending_equity_ZAR          482.65
pnl_ZAR                    -517.35
pnl_pct                    -51.74
max_drawdown_pct           -53.54
avg_win_ZAR                36.71
avg_loss_ZAR               -14.61
```

## Gate funnel

```
checks                         128890
in_killzone                    128890
news_clear                     12453
nfp_fomc_ok                    10957
intermarket_signal             587
pair_matches                   587
mss_h1_m15_m5_ok               123
daily_bias_ok                  123
h1_bias_ok                     123
h4_bias_ok                     123
dealing_range_ok               8
consolidation_found            56
manipulation_correct_dir       51
m5_fvg_correct_dir             58
target_found                   58
rr_ok                          58
units_nonzero                  58
limit_placed                   0
entry_opened                   58
pyramid_added                  2
pyramid_blocked_min_target     18
drawdown_halt                  116277
daily_loss_halt                6
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      6
daily_pair_cap                 464
weekly_amd_confirmed           22
session_handover_closed        0
htf_draw_full_cascade          0
htf_draw_partial               37
htf_draw_counter               33
htf_fvg_5050_hit               3
ote_zone                       0
choch_confirmed                1
low_conviction                 0
judas_divergence               0
ny_continuation                22
pm_gate_pair_news              0
breakout_confirmed             73
sr_attempted                   6
sr_prev_session_ok             6
sr_enough_bars                 6
sr_consol_found                6
sr_breakout_found              4
session_range_found            4
soj_retest                     37
soj_sweep                      54
dxy_fvg_room                   6
golden_rule_no                 34
mstruct_align                  55
phase_ny_judas                 30
gt_pool_sweep                  48
structure_stop_used            57
stop_capped_10pip              49
risk_cap_ok                    58
pyramid_blocked_low_im         200
soj_judas                      17
crt_turtle_soup                28
golden_rule_yes                23
gt_disp_wick                   28
pyramid_blocked_favour         287
phase_london_judas             28
smt_pair_confirmed             14
mstruct_minor_sweep            12
gt_macro_window                10
smt_pair_opposing              4
gt_judas_reversal              8
sr_consol_no_sweep             2
sr_fail_no_tail                2
sr_pdliq_attempted             2
gt_mp_discount                 5
gt_mp_extreme                  1
m1_stop_used                   1
london_judas_ny_echo           1
```

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG             51     6  11.8%      -463.15   0.28
OB               9     1  11.1%       -54.21   0.60

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
FVG H1                 1     1 100.0%    inf
FVG M15                4     0   0.0%   0.00
FVG M5                46     5  10.9%   0.28
OB M5                  9     1  11.1%   0.60

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
FVG EURUSD                28     4  14.3%   0.23
FVG GBPUSD                22     2   9.1%   0.36
FVG NZDUSD                 1     0   0.0%   0.00
OB EURUSD                  6     1  16.7%   1.01
OB GBPUSD                  3     0   0.0%   0.00
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_fvg_h1                   1     1 100.0%      17.76    inf
amd_fvg_m15                  3     0   0.0%     -25.65   0.00
amd_fvg_m5                  40     4  10.0%      -9.37   0.25
amd_ob_m5                    6     1  16.7%       0.62   1.05
mss_fvg_m15                  1     0   0.0%      -1.39   0.00
mss_fvg_m5                   3     1  33.3%      11.28  21.33
mss_ob_m5                    3     0   0.0%     -19.30   0.00
news_fvg_m5                  1     0   0.0%     -23.12   0.00
pyramid_im0.8_fvg_m5         1     0   0.0%     -19.42   0.00
pyramid_im1.0_fvg_m5         1     0   0.0%     -19.24   0.00
```

## AMD consolidation source

```
Source              Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
m15_range               54     7  13.0%      -422.63   0.38
session_range            4     0   0.0%       -93.05   0.00
(no AMD)                 2     0   0.0%        -1.67   0.00
```

_Session-range widths (n=6): median=49.7 p75=70.9 p90=80.8 pips (cap=35.0)_

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden            23     4  17.4%      -158.36   0.44
against           36     3   8.3%      -357.61   0.27

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                11  18.2%   0.29
EURUSD SHORT against              23  13.0%   0.38
GBPUSD LONG against               13   0.0%   0.00
GBPUSD SHORT golden               12  16.7%   0.54
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed           14     4  28.6%       -36.82   0.79
opposing             4     0   0.0%       -58.64   0.00
no divergence       41     3   7.3%      -420.51   0.22
```

## Narrative context scoring (P47)

```
Score     Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
0              1     0   0.0%       -19.24   0.00
1              5     1  20.0%       -41.26   0.30
2             19     3  15.8%      -154.66   0.47
3             24     2   8.3%      -188.79   0.32
4              9     1  11.1%       -93.43   0.16
5              2     0   0.0%       -19.98   0.00

Factor                 Fired    WR%     PF   Absent    WR%     PF
--------------------------------------------------------------------
Weekly Profile            42   9.5%   0.28       18  16.7%   0.44
NFP week Mon/Tue           7  14.3%   0.36       53  11.3%   0.33
Rate decision              4   0.0%   0.00       56  12.5%   0.36
PD prov (sweep)           55  10.9%   0.31        5  20.0%   0.60
Seasonal lean              0   0.0%   0.00       60  11.7%   0.33
HTF OB Context            12   8.3%   0.43       48  12.5%   0.31
D1 Draw                   41  12.2%   0.33       19  10.5%   0.34
```

## HTF OB context breakdown (P48)

```
Context           Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
continuation          12     1   8.3%       -90.93   0.43
(none)                48     6  12.5%      -426.43   0.31

Liq type          Trades    WR%     PF
----------------------------------------
breaker                4   0.0%   0.00
d1_fvg                 7  14.3%   0.76
pdhl                   1   0.0%   0.00
```

## D1 narrative draw breakdown (P48)

```
Draw type         Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------------
equal_hl              41     5  12.2%      -345.30   0.33
(none)                19     2  10.5%      -172.05   0.34
```

# HistData backtest — 2022–2025 (4 yr)

## Results

```
trades                     736
win_rate_pct               43.9
profit_factor              4.01
starting_equity_ZAR        1000
ending_equity_ZAR          140555.2
pnl_ZAR                    139555.2
pnl_pct                    13955.52
max_drawdown_pct           -13.24
avg_win_ZAR                575.44
avg_loss_ZAR               -112.13
withdrawn_total_ZAR        131999.99
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
consolidation_found            965
manipulation_correct_dir       845
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
breakout_confirmed             1088
soj_retest                     571
soj_sweep                      934
golden_rule_no                 498
mstruct_align                  982
phase_ny_judas                 529
gt_pool_sweep                  788
structure_stop_used            956
stop_capped_10pip              752
risk_cap_ok                    722
pyramid_blocked_low_im         2617
soj_judas                      363
crt_turtle_soup                489
golden_rule_yes                473
gt_disp_wick                   750
m1_stop_used                   70
pyramid_blocked_favour         4922
dxy_fvg_room                   156
phase_london_judas             514
gt_macro_window                131
smt_pair_opposing              112
gt_mp_discount                 180
smt_pair_confirmed             288
mstruct_minor_sweep            132
gt_judas_reversal              114
gt_mp_extreme                  40
ny_continuation_gated          9
london_judas_ny_echo           22
target_score_sized             384
crt_sweep_sized                177
risk_cap_skip                  304
golden_rule_sized              426
pdliq_sweep_sized              199
phase_london_watch             3
htf_fvg_breakout_sized         15
phase_ny_extend                2
pyramid_blocked_no_pattern     6
phase_london_breakout          1
```

_income: R132,000 across 37 withdrawals · working balance R8,555_

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            484   202  41.7%     82651.07   3.54
OB             228   106  46.5%     52649.98   5.18
BREAKER         24    15  62.5%      4254.16   4.49

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            4     3  75.0%   4.00
BREAKER M5            19    11  57.9%   4.79
FVG H1                88    39  44.3%   5.68
FVG M15               77    30  39.0%   4.33
FVG M5               319   133  41.7%   2.85
OB M15                32    19  59.4%   7.72
OB M5                196    87  44.4%   4.89

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            15     9  60.0%   4.34
BREAKER GBPUSD             5     4  80.0%   7.01
BREAKER NZDUSD             4     2  50.0%   3.36
FVG EURUSD               239    99  41.4%   3.87
FVG GBPUSD               219    97  44.3%   3.56
FVG NZDUSD                26     6  23.1%   1.08
OB EURUSD                148    58  39.2%   3.36
OB GBPUSD                 56    36  64.3%  10.71
OB NZDUSD                 24    12  50.0%  10.01
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              2     1  50.0%     224.77   1.83
amd_breaker_m5              13     9  69.2%     195.24   6.88
amd_fvg_h1                  67    31  46.3%     225.08   4.95
amd_fvg_m15                 55    20  36.4%     172.27   3.13
amd_fvg_m5                 252   102  40.5%     133.95   2.97
amd_ob_m15                  21    12  57.1%     182.59   4.17
amd_ob_m5                  148    66  44.6%     193.30   4.16
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     2 100.0%     587.03    inf
mss_breaker_m5               6     2  33.3%       4.70   1.11
mss_fvg_h1                  20     8  40.0%     457.12   7.75
mss_fvg_m15                 19     9  47.4%     415.58  12.34
mss_fvg_m5                  54    28  51.9%     124.73   2.54
mss_ob_m15                  10     6  60.0%     468.55  58.40
mss_ob_m5                   48    21  43.8%     320.05   7.84
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

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           284   140  49.3%     69416.19   4.66
against          398   163  41.0%     58586.25   3.48

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden               140  45.7%   4.26
EURUSD SHORT against             262  38.9%   3.38
GBPUSD LONG against              136  44.9%   3.72
GBPUSD SHORT golden              144  52.8%   5.03
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          197    85  43.1%     37853.57   4.02
opposing            84    44  52.4%     16641.41   4.98
no divergence      401   174  43.4%     73507.47   3.84
```

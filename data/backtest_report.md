# HistData backtest — 2022–2023 (2 yr)

## Results

```
trades                     389
win_rate_pct               44.7
profit_factor              2.88
starting_equity_ZAR        500
ending_equity_ZAR          273480.83
pnl_ZAR                    272980.83
pnl_pct                    54596.17
max_drawdown_pct           -12.76
avg_win_ZAR                2403.45
avg_loss_ZAR               -675.44
```

## Gate funnel

```
checks                         58909
in_killzone                    58909
news_clear                     58149
nfp_fomc_ok                    49686
intermarket_signal             2789
pair_matches                   2789
mss_h1_m15_m5_ok               917
daily_bias_ok                  917
h1_bias_ok                     917
h4_bias_ok                     917
dealing_range_ok               39
consolidation_found            370
manipulation_correct_dir       331
m5_fvg_correct_dir             401
target_found                   401
rr_ok                          401
units_nonzero                  401
limit_placed                   0
entry_opened                   376
pyramid_added                  13
pyramid_blocked_min_target     372
drawdown_halt                  0
daily_loss_halt                50
consec_loss_pause              0
weekly_cap                     0
weekly_pair_cap                0
daily_cap                      289
daily_pair_cap                 2198
weekly_amd_confirmed           149
session_handover_closed        2
htf_draw_full_cascade          64
htf_draw_partial               279
htf_draw_counter               201
htf_fvg_5050_hit               9
ote_zone                       2
choch_confirmed                8
low_conviction                 0
judas_divergence               2
ny_continuation                151
pm_gate_pair_news              0
breakout_confirmed             502
soj_retest                     214
soj_sweep                      358
golden_rule_no                 206
mstruct_align                  384
phase_ny_judas                 201
gt_pool_sweep                  322
structure_stop_used            370
stop_capped_10pip              316
risk_cap_ok                    376
pyramid_blocked_low_im         1103
soj_judas                      144
crt_turtle_soup                187
golden_rule_yes                181
gt_disp_wick                   306
m1_stop_used                   31
pyramid_blocked_favour         2023
dxy_fvg_room                   50
phase_london_judas             207
gt_macro_window                60
smt_pair_opposing              50
gt_mp_discount                 86
smt_pair_confirmed             118
mstruct_minor_sweep            61
gt_judas_reversal              51
gt_mp_extreme                  16
ny_continuation_gated          6
london_judas_ny_echo           8
pdliq_sweep_sized              48
risk_cap_skip                  25
target_score_sized             97
crt_sweep_sized                49
phase_london_watch             1
pyramid_blocked_no_pattern     1
htf_fvg_breakout_sized         3
phase_ny_extend                1
```

## PD array setup type (FVG / OB / breaker)

```
Setup       Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
FVG            285   126  44.2%    166804.43   2.49
OB              90    40  44.4%     99189.00   4.73
BREAKER         14     8  57.1%      6987.40   2.10

Setup x TF        Trades  Wins    WR%     PF
------------------------------------------
BREAKER H1             1     1 100.0%    inf
BREAKER M15            3     1  33.3%   0.15
BREAKER M5            10     6  60.0%  21.87
FVG H1                39    15  38.5%   3.24
FVG M15               41    15  36.6%   1.65
FVG M5               205    96  46.8%   2.56
OB M15                13     6  46.2%  42.68
OB M5                 77    34  44.2%   4.56

Setup x pair          Trades  Wins    WR%     PF
----------------------------------------------
BREAKER EURUSD            12     6  50.0%   1.96
BREAKER GBPUSD             2     2 100.0%    inf
FVG EURUSD               127    53  41.7%   2.07
FVG GBPUSD               144    70  48.6%   3.39
FVG NZDUSD                14     3  21.4%   0.33
OB EURUSD                 56    18  32.1%   1.92
OB GBPUSD                 26    16  61.5%  20.28
OB NZDUSD                  8     6  75.0% 747.22
```

## Entry-type breakdown

```
Entry type              Trades  Wins    WR%    Avg P&L     PF
------------------------------------------------------------
amd_breaker_m15              1     0   0.0%   -4613.14   0.00
amd_breaker_m5               5     3  60.0%     489.62   7.81
amd_fvg_h1                  32    14  43.8%    1313.66   4.05
amd_fvg_m15                 30    10  33.3%     116.93   1.20
amd_fvg_m5                 161    76  47.2%     553.62   2.62
amd_ob_m15                   9     6  66.7%     536.18  95.63
amd_ob_m5                   57    26  45.6%     701.32   3.01
mss_breaker_h1               1     1 100.0%      64.20    inf
mss_breaker_m15              2     1  50.0%    -145.49   0.75
mss_breaker_m5               5     3  60.0%    1875.84  46.22
mss_fvg_h1                   6     1  16.7%    -546.35   0.07
mss_fvg_m15                  9     4  44.4%    1103.20   3.21
mss_fvg_m5                  32    17  53.1%     756.42   2.36
mss_ob_m15                   3     0   0.0%     -18.62   0.00
mss_ob_m5                   20     8  40.0%    2722.58   9.26
news_fvg_m15                 1     0   0.0%      -4.63   0.00
news_fvg_m5                  2     0   0.0%     -46.25   0.00
pyramid_im0.8_fvg_m15        1     1 100.0%     670.06    inf
pyramid_im0.8_fvg_m5         4     3  75.0%     199.80   5.11
pyramid_im0.8_ob_m15         1     0   0.0%      -7.40   0.00
pyramid_im1.0_fvg_m5         3     0   0.0%     -18.50   0.00
pyramid_wamd1.0_fvg_h1       1     0   0.0%      -9.25   0.00
pyramid_wamd1.0_fvg_m5       3     0   0.0%     -12.58   0.00
```

## Golden rule: SELL GBP / BUY EUR (P44)

```
Rule          Trades  Wins    WR%      P&L ZAR     PF
--------------------------------------------------
golden           161    84  52.2%    161975.98   3.79
against          206    81  39.3%     99477.31   2.26

Pair x dir x rule              Trades    WR%     PF
--------------------------------------------------
EURUSD LONG golden                67  47.8%   2.56
EURUSD SHORT against             128  35.2%   1.69
GBPUSD LONG against               78  46.2%   3.49
GBPUSD SHORT golden               94  55.3%   5.50
```

## Intraday SMT pair preference (P44)

```
SMT pref        Trades  Wins    WR%      P&L ZAR     PF
----------------------------------------------------
confirmed          118    56  47.5%    104023.34   2.86
opposing            50    23  46.0%     12105.21   1.92
no divergence      199    86  43.2%    145324.74   3.13
```

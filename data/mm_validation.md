# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `fab87b2`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM standalone | — | — | — | — | — | 0 | 0 |
| MM standalone + adds | — | — | — | — | — | 0 | 0 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM standalone | — | — | — | — | — | 0 | 0 |
| MM standalone + adds | — | — | — | — | — | 0 | 0 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM standalone | — | — | — | — | — | 0 | 0 |
| MM standalone + adds | — | — | — | — | — | 0 | 0 |

## Verdict

- **MM standalone: ⚠️ inert** — 0 MM adds fired — no setups matched (check IFVG/structure gates)
- **MM standalone + adds: ⚠️ inert** — 0 MM adds fired — no setups matched (check IFVG/structure gates)

_No arm passed the full gate. Same measure-first discipline: nothing ships._

## Crash diagnostics

### Full 4yr / MM standalone — NO SUMMARY

```

Loading and resampling to 5-minute bars (2022 + 2023 + 2024 + 2025)...
  GBPUSD: 1,437,919 M1 → 289,020 M5 bars  2022-01-02 – 2025-12-31  close 1.34740
  EURUSD: 1,439,786 M1 → 289,268 M5 bars  2022-01-02 – 2025-12-31  close 1.17455
  EURGBP: 1,436,073 M1 → 289,103 M5 bars  2022-01-02 – 2025-12-31  close 0.87158
  UDXUSD: 1,235,373 M1 → 251,395 M5 bars  2022-01-03 – 2025-12-31  close 97.96900
  AUDUSD: 1,435,435 M1 → 289,003 M5 bars  2022-01-02 – 2025-12-31  close 0.66733
  NZDUSD: 1,432,732 M1 → 288,780 M5 bars  2022-01-02 – 2025-12-31  close 0.57549
  AUDNZD: 1,436,487 M1 → 288,624 M5 bars  2022-01-02 – 2025-12-31  close 1.15922

Running backtest...
  News CSV: 320 events loaded from data/news_events.csv
  Iterating 289020 5-min bars...
    bar 2000/289020 (2022-01-11 20:50:00+00:00) - active=0 trades=4 equity=484
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 278, in run
    self._mm_standalone(pair, t)
  File "/workspaces/Ict/backtest.py", line 3667, in _mm_standalone
    target, target_type, _ = self._find_target(pair, d, t, entry, stop=stop)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```

### Full 4yr / MM standalone + adds — NO SUMMARY

```
  Optional pairs available: AUDUSD, NZDUSD, AUDNZD

Loading and resampling to 5-minute bars (2022 + 2023 + 2024 + 2025)...
  GBPUSD: 1,437,919 M1 → 289,020 M5 bars  2022-01-02 – 2025-12-31  close 1.34740
  EURUSD: 1,439,786 M1 → 289,268 M5 bars  2022-01-02 – 2025-12-31  close 1.17455
  EURGBP: 1,436,073 M1 → 289,103 M5 bars  2022-01-02 – 2025-12-31  close 0.87158
  UDXUSD: 1,235,373 M1 → 251,395 M5 bars  2022-01-03 – 2025-12-31  close 97.96900
  AUDUSD: 1,435,435 M1 → 289,003 M5 bars  2022-01-02 – 2025-12-31  close 0.66733
  NZDUSD: 1,432,732 M1 → 288,780 M5 bars  2022-01-02 – 2025-12-31  close 0.57549
  AUDNZD: 1,436,487 M1 → 288,624 M5 bars  2022-01-02 – 2025-12-31  close 1.15922

Running backtest...
  News CSV: 320 events loaded from data/news_events.csv
  Iterating 289020 5-min bars...
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 278, in run
    self._mm_standalone(pair, t)
  File "/workspaces/Ict/backtest.py", line 3667, in _mm_standalone
    target, target_type, _ = self._find_target(pair, d, t, entry, stop=stop)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```

### IS 2022-23 / MM standalone — NO SUMMARY

```

Loading and resampling to 5-minute bars (2022 + 2023)...
  GBPUSD: 694,841 M1 → 139,494 M5 bars  2022-01-02 – 2023-12-29  close 1.27305
  EURUSD: 695,383 M1 → 139,717 M5 bars  2022-01-02 – 2023-12-29  close 1.10361
  EURGBP: 694,588 M1 → 139,602 M5 bars  2022-01-02 – 2023-12-29  close 0.86671
  UDXUSD: 601,836 M1 → 121,828 M5 bars  2022-01-03 – 2023-12-29  close 101.04500
  AUDUSD: 693,584 M1 → 139,626 M5 bars  2022-01-02 – 2023-12-29  close 0.68082
  NZDUSD: 691,331 M1 → 139,417 M5 bars  2022-01-02 – 2023-12-29  close 0.63174
  AUDNZD: 693,115 M1 → 139,235 M5 bars  2022-01-02 – 2023-12-29  close 1.07787

Running backtest...
  News CSV: 320 events loaded from data/news_events.csv
  Iterating 139494 5-min bars...
    bar 2000/139494 (2022-01-11 20:50:00+00:00) - active=0 trades=4 equity=484
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 278, in run
    self._mm_standalone(pair, t)
  File "/workspaces/Ict/backtest.py", line 3667, in _mm_standalone
    target, target_type, _ = self._find_target(pair, d, t, entry, stop=stop)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```

### IS 2022-23 / MM standalone + adds — NO SUMMARY

```
  Optional pairs available: AUDUSD, NZDUSD, AUDNZD

Loading and resampling to 5-minute bars (2022 + 2023)...
  GBPUSD: 694,841 M1 → 139,494 M5 bars  2022-01-02 – 2023-12-29  close 1.27305
  EURUSD: 695,383 M1 → 139,717 M5 bars  2022-01-02 – 2023-12-29  close 1.10361
  EURGBP: 694,588 M1 → 139,602 M5 bars  2022-01-02 – 2023-12-29  close 0.86671
  UDXUSD: 601,836 M1 → 121,828 M5 bars  2022-01-03 – 2023-12-29  close 101.04500
  AUDUSD: 693,584 M1 → 139,626 M5 bars  2022-01-02 – 2023-12-29  close 0.68082
  NZDUSD: 691,331 M1 → 139,417 M5 bars  2022-01-02 – 2023-12-29  close 0.63174
  AUDNZD: 693,115 M1 → 139,235 M5 bars  2022-01-02 – 2023-12-29  close 1.07787

Running backtest...
  News CSV: 320 events loaded from data/news_events.csv
  Iterating 139494 5-min bars...
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 278, in run
    self._mm_standalone(pair, t)
  File "/workspaces/Ict/backtest.py", line 3667, in _mm_standalone
    target, target_type, _ = self._find_target(pair, d, t, entry, stop=stop)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```

### OOS 2024-25 / MM standalone — NO SUMMARY

```
  Optional pairs available: AUDUSD, NZDUSD, AUDNZD

Loading and resampling to 5-minute bars (2024 + 2025)...
  GBPUSD: 743,078 M1 → 149,526 M5 bars  2024-01-01 – 2025-12-31  close 1.34740
  EURUSD: 744,403 M1 → 149,551 M5 bars  2024-01-01 – 2025-12-31  close 1.17455
  EURGBP: 741,485 M1 → 149,501 M5 bars  2024-01-01 – 2025-12-31  close 0.87158
  UDXUSD: 633,537 M1 → 129,567 M5 bars  2024-01-02 – 2025-12-31  close 97.96900
  AUDUSD: 741,851 M1 → 149,377 M5 bars  2024-01-01 – 2025-12-31  close 0.66733
  NZDUSD: 741,401 M1 → 149,363 M5 bars  2024-01-01 – 2025-12-31  close 0.57549
  AUDNZD: 743,372 M1 → 149,389 M5 bars  2024-01-01 – 2025-12-31  close 1.15922

Running backtest...
  News CSV: 320 events loaded from data/news_events.csv
  Iterating 149526 5-min bars...
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 278, in run
    self._mm_standalone(pair, t)
  File "/workspaces/Ict/backtest.py", line 3667, in _mm_standalone
    target, target_type, _ = self._find_target(pair, d, t, entry, stop=stop)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```

### OOS 2024-25 / MM standalone + adds — NO SUMMARY

```
  Optional pairs available: AUDUSD, NZDUSD, AUDNZD

Loading and resampling to 5-minute bars (2024 + 2025)...
  GBPUSD: 743,078 M1 → 149,526 M5 bars  2024-01-01 – 2025-12-31  close 1.34740
  EURUSD: 744,403 M1 → 149,551 M5 bars  2024-01-01 – 2025-12-31  close 1.17455
  EURGBP: 741,485 M1 → 149,501 M5 bars  2024-01-01 – 2025-12-31  close 0.87158
  UDXUSD: 633,537 M1 → 129,567 M5 bars  2024-01-02 – 2025-12-31  close 97.96900
  AUDUSD: 741,851 M1 → 149,377 M5 bars  2024-01-01 – 2025-12-31  close 0.66733
  NZDUSD: 741,401 M1 → 149,363 M5 bars  2024-01-01 – 2025-12-31  close 0.57549
  AUDNZD: 743,372 M1 → 149,389 M5 bars  2024-01-01 – 2025-12-31  close 1.15922

Running backtest...
  News CSV: 320 events loaded from data/news_events.csv
  Iterating 149526 5-min bars...
Traceback (most recent call last):
  File "/workspaces/Ict/run_backtest_histdata.py", line 728, in <module>
    main()
  File "/workspaces/Ict/run_backtest_histdata.py", line 216, in main
    backtester.run()
  File "/workspaces/Ict/backtest.py", line 278, in run
    self._mm_standalone(pair, t)
  File "/workspaces/Ict/backtest.py", line 3667, in _mm_standalone
    target, target_type, _ = self._find_target(pair, d, t, entry, stop=stop)
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: too many values to unpack (expected 3)
```


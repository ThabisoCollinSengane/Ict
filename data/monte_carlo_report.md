# Monte Carlo drawdown study (P100)

Trades: 876 from `mm_golden_full_p93_p99_trades.csv` (2022-01-10 to 2025-12-31), 10,000 simulations per method, start R1,000, working capital R6,000.

## Calibration — the real order replayed by this simulator

Working-balance MaxDD 30.70%, total-value MaxDD 15.66%, withdrawn R189,587, worst losing streak 11, lowest balance R961.
Engine reported for the same run: working-balance MaxDD 31.59%, total-value MaxDD 15.66% (the headline figure), withdrawn R176,034.

**Two drawdowns.** The engine's headline MaxDD is measured on TOTAL value (working balance + every rand already withdrawn), which grows as profit is banked, so a loss looks smaller against it. The working-balance figure is the fall of the money actually in the trading account, from its high. That is what you see in MT5.

## Shuffle — same trades, random order

| | median | 75th | 90th | 95th | 99th | worst |
|---|---|---|---|---|---|---|
| Total-value drawdown % (headline measure) | 18.1 | 23.0 | 28.7 | 32.5 | 41.2 | 56.2 |
| Working-balance drawdown % (what MT5 shows) | 27.7 | 31.5 | 35.9 | 38.9 | 45.8 | 62.9 |
| Longest losing streak | 11 | 12 | 14 | 15 | 18 | 23 |
| Withdrawn R k (lower = worse; 50th / 25th / 10th / 5th / 1st / min) | 185.7 | 182.6 | 179.5 | 177.4 | 173.2 | 162.6 |

Total-value drawdown beyond 15.66% (worse than the backtest headline): **66.5%**; beyond 20%: **38.8%**; beyond 30%: **7.9%**. Working-balance drawdown beyond 15%: **100.0%**, 20%: **98.4%**, 30%: **33.4%**, 50%: **0.5%**. Chance the balance ever falls below R500: **0.0%**. Chance of withdrawing less than R100k: **0.0%**.

## Bootstrap — random draw with replacement (a different 4 years)

| | median | 75th | 90th | 95th | 99th | worst |
|---|---|---|---|---|---|---|
| Total-value drawdown % (headline measure) | 18.2 | 23.3 | 29.1 | 33.2 | 41.5 | 65.3 |
| Working-balance drawdown % (what MT5 shows) | 27.7 | 31.7 | 36.1 | 39.1 | 46.1 | 65.3 |
| Longest losing streak | 11 | 12 | 14 | 15 | 18 | 28 |
| Withdrawn R k (lower = worse; 50th / 25th / 10th / 5th / 1st / min) | 185.5 | 170.1 | 155.8 | 148.1 | 133.6 | 113.6 |

Total-value drawdown beyond 15.66% (worse than the backtest headline): **66.3%**; beyond 20%: **39.7%**; beyond 30%: **8.5%**. Working-balance drawdown beyond 15%: **100.0%**, 20%: **97.5%**, 30%: **33.9%**, 50%: **0.4%**. Chance the balance ever falls below R500: **0.0%**. Chance of withdrawing less than R100k: **0.0%**.


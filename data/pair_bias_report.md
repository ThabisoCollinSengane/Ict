# Discretionary-sync playbook — pair x bias x entry x session

_804 base-algo trades analysed (0 MM rows excluded — see data/mm_winners_report.md for those). Source: the trade dump from your last backtest run — no new backtest run for this report._

## Overall

- 804 trades, WR 44.9%, PF 4.95, total P&L 567,575,114 ZAR

## 1. Pair x direction — which pair is reliable on which bias

### Pair x direction

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| EURUSD SHORT | 282 | 38.3 | 4.22 | 99,502,885 | 352,847 |
| GBPUSD SHORT | 163 | 54.6 | 8.06 | 154,249,121 | 946,314 |
| EURUSD LONG | 158 | 48.1 | 5.70 | 164,119,044 | 1,038,728 |
| GBPUSD LONG | 143 | 45.5 | 1.90 | 42,952,802 | 300,369 |
| NZDUSD SHORT | 35 | 37.1 | 16.16 | 99,843,680 | 2,852,677 |
| NZDUSD LONG | 23 | 43.5 | 5.72 | 6,907,583 | 300,330 |

## 2. PD-array family — which entries are good

### By family (fvg / ob / breaker)

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|

### By family + timeframe

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|

## 3. Entry model — Judas reversal vs intermarket breakout

### By entry_model

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| breakout | 433 | 44.6 | 2.16 | 91,796,859 | 212,002 |
| judas | 371 | 45.3 | 8.36 | 475,778,255 | 1,282,421 |

## 4. Session profile — which session performs best at what

### By session profile

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| london | 397 | 46.9 | 5.45 | 260,171,970 | 655,345 |
| ny | 407 | 43.0 | 4.61 | 307,403,144 | 755,290 |

### Session x pair

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| ny / EURUSD | 234 | 41.0 | 4.45 | 202,407,018 | 864,987 |
| london / EURUSD | 206 | 42.7 | 9.55 | 61,214,911 | 297,160 |
| ny / GBPUSD | 173 | 45.7 | 4.98 | 104,996,126 | 606,914 |
| london / GBPUSD | 133 | 56.4 | 3.13 | 92,205,796 | 693,277 |
| london / NZDUSD | 58 | 39.7 | 14.26 | 106,751,263 | 1,840,539 |

### Session x direction

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| ny / SHORT | 242 | 42.6 | 5.49 | 144,896,017 | 598,744 |
| london / SHORT | 238 | 45.0 | 8.70 | 208,699,668 | 876,889 |
| ny / LONG | 165 | 43.6 | 4.07 | 162,507,127 | 984,892 |
| london / LONG | 159 | 49.7 | 2.64 | 51,472,302 | 323,725 |

## 5. Pair x direction x session (the full cross-tab)

### Pair x direction x session

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| EURUSD SHORT / ny | 149 | 36.9 | 2.84 | 53,743,166 | 360,692 |
| EURUSD SHORT / london | 133 | 39.8 | 26.69 | 45,759,718 | 344,058 |
| GBPUSD SHORT / ny | 93 | 51.6 | 30.35 | 91,152,850 | 980,138 |
| EURUSD LONG / ny | 85 | 48.2 | 6.03 | 148,663,851 | 1,748,986 |
| GBPUSD LONG / ny | 80 | 38.8 | 1.59 | 13,843,276 | 173,041 |
| EURUSD LONG / london | 73 | 47.9 | 3.87 | 15,455,193 | 211,715 |
| GBPUSD SHORT / london | 70 | 58.6 | 4.37 | 63,096,270 | 901,375 |
| GBPUSD LONG / london | 63 | 54.0 | 2.19 | 29,109,526 | 462,056 |
| NZDUSD SHORT / london | 35 | 37.1 | 16.16 | 99,843,680 | 2,852,677 |
| NZDUSD LONG / london | 23 | 43.5 | 5.72 | 6,907,583 | 300,330 |

## 6. Intermarket scenario x pair

### Scenario x pair

| value | n | WR% | PF | total P&L ZAR | avg P&L ZAR |
|---|---|---|---|---|---|
| 3a / EURUSD | 141 | 33.3 | 11.81 | 68,414,692 | 485,211 |
| 3b / EURUSD | 131 | 47.3 | 5.83 | 161,058,020 | 1,229,451 |
| 1b / EURUSD | 92 | 45.7 | 2.94 | 13,501,314 | 146,753 |
| 1a / GBPUSD | 69 | 53.6 | 44.05 | 47,962,161 | 695,104 |
| 2b_ip / GBPUSD | 66 | 36.4 | 0.55 | -17,756,453 | -269,037 |
| 1a_ip / GBPUSD | 62 | 56.5 | 1.24 | 4,767,664 | 76,898 |
| 2b / GBPUSD | 54 | 59.3 | 2.43 | 11,330,020 | 209,815 |
| 1a_h4 / GBPUSD | 32 | 53.1 | 86.37 | 101,519,296 | 3,172,478 |
| 2a / EURUSD | 27 | 51.9 | 2.91 | 3,061,024 | 113,371 |
| 1b_ip / EURUSD | 25 | 32.0 | 2.48 | 1,392,936 | 55,717 |
| 1b_h4 / EURUSD | 24 | 45.8 | 1.97 | 16,193,942 | 674,748 |
| N-long / NZDUSD | 23 | 43.5 | 5.72 | 6,907,583 | 300,330 |
| 2b_h4 / GBPUSD | 23 | 39.1 | 89.59 | 49,379,234 | 2,146,923 |
| N-short / NZDUSD | 21 | 38.1 | 5.16 | 19,679,588 | 937,123 |
| N-short_h4 / NZDUSD | 14 | 35.7 | 44.22 | 80,164,092 | 5,726,007 |


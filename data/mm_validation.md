# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `bf03d9c`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | **workDD%** | **withdrawn ZAR** | work bal | #wd | opens |
|---|---|---|---|---|---|---|---|---|
| baseline | 793.00 | 45.10 | 4.83 | 18.29 | 351,358 | 159,392 | 121 | 0 |
| MM standalone | 1441.00 | 24.00 | 0.00 | 225179981372.41 | 21,950 | -23,434,560,864,559 | 35 | 1177 |
| MM standalone + adds | 1918.00 | 22.30 | 0.00 | 225179981372.06 | 28,261 | -29,525,491,286,988 | 34 | 1654 |

## IS 2022-23

| arm | trades | WR% | PF | **workDD%** | **withdrawn ZAR** | work bal | #wd | opens |
|---|---|---|---|---|---|---|---|---|
| baseline | 378.00 | 45.20 | 3.40 | 18.29 | 28,680 | 14,722 | 48 | 0 |
| MM standalone | 893.00 | 27.50 | 0.00 | 225179981372.41 | 21,950 | -23,434,560,865,291 | 35 | 629 |
| MM standalone + adds | 1153.00 | 25.80 | 0.00 | 225179981372.06 | 28,261 | -29,525,491,287,751 | 34 | 889 |

## OOS 2024-25

| arm | trades | WR% | PF | **workDD%** | **withdrawn ZAR** | work bal | #wd | opens |
|---|---|---|---|---|---|---|---|---|
| baseline | 399.00 | 44.60 | 5.24 | 19.64 | 46,594 | 21,737 | 47 | 0 |
| MM standalone | 861.00 | 29.40 | 2.86 | 25.74 | 66,880 | 29,664 | 52 | 489 |
| MM standalone + adds | 958.00 | 25.10 | 0.00 | 212494821993.72 | 30,723 | -30,347,712,569,135 | 34 | 675 |

## Verdict

_Withdrawal model: judged on **working-account DD** (survival) and **total withdrawn** (return), not the compounding curve._

- **MM standalone: 🔴 RED** — withdrew 21,950 ≤ baseline 351,358; working DD 225179981372% — account near-blowup; IS withdrew ≤ baseline
- **MM standalone + adds: 🔴 RED** — withdrew 28,261 ≤ baseline 351,358; working DD 225179981372% — account near-blowup; IS withdrew ≤ baseline; OOS withdrew ≤ baseline

_No arm passed the gate._

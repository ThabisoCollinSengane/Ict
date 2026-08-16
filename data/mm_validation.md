# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `d3da087`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | **workDD%** | **withdrawn ZAR** | work bal | #wd | opens |
|---|---|---|---|---|---|---|---|---|
| baseline | 793.00 | 45.10 | 4.81 | 18.72 | 390,143 | 168,184 | 118 | 0 |
| MM standalone | 1444.00 | 24.20 | 0.00 | 217531180227.73 | 25,864 | -26,287,849,041,030 | 38 | 1180 |
| MM standalone + adds | 1861.00 | 22.00 | 0.00 | 225179981372.21 | 26,216 | -27,551,257,172,562 | 32 | 1613 |

## IS 2022-23

| arm | trades | WR% | PF | **workDD%** | **withdrawn ZAR** | work bal | #wd | opens |
|---|---|---|---|---|---|---|---|---|
| baseline | 378.00 | 45.20 | 3.37 | 18.72 | 30,355 | 14,229 | 53 | 0 |
| MM standalone | 896.00 | 27.90 | 0.00 | 217531180227.73 | 25,864 | -26,287,849,041,762 | 38 | 632 |
| MM standalone + adds | 1096.00 | 25.50 | 0.00 | 225179981372.21 | 26,216 | -27,551,257,173,325 | 32 | 848 |

## OOS 2024-25

| arm | trades | WR% | PF | **workDD%** | **withdrawn ZAR** | work bal | #wd | opens |
|---|---|---|---|---|---|---|---|---|
| baseline | 400.00 | 44.50 | 4.95 | 18.02 | 53,932 | 24,992 | 51 | 0 |
| MM standalone | 861.00 | 29.40 | 2.78 | 25.73 | 69,815 | 31,388 | 54 | 489 |
| MM standalone + adds | 967.00 | 24.70 | 0.00 | 212627315745.85 | 35,109 | -34,119,456,115,798 | 37 | 683 |

## Verdict

_Withdrawal model: judged on **working-account DD** (survival) and **total withdrawn** (return), not the compounding curve._

- **MM standalone: 🔴 RED** — withdrew 25,864 ≤ baseline 390,143; working DD 217531180228% — account near-blowup; IS withdrew ≤ baseline
- **MM standalone + adds: 🔴 RED** — withdrew 26,216 ≤ baseline 390,143; working DD 225179981372% — account near-blowup; IS withdrew ≤ baseline; OOS withdrew ≤ baseline

_No arm passed the gate._

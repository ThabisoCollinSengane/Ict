# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `e5610a7`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM standalone | 1874.00 | 31.20 | 2.98 | -21.19 | 1,164,517,007 | 1091 | 0 |
| MM standalone + adds | 2352.00 | 27.80 | 3.15 | -24.58 | 1,035,495,022 | 1587 | 0 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM standalone | 988.00 | 30.90 | 2.11 | -21.19 | 542,142 | 606 | 0 |
| MM standalone + adds | 1243.00 | 26.70 | 2.05 | -24.58 | 445,429 | 872 | 0 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM standalone | 858.00 | 31.60 | 2.98 | -16.68 | 3,138,487 | 464 | 0 |
| MM standalone + adds | 1063.00 | 29.10 | 3.15 | -18.33 | 3,851,494 | 672 | 0 |

## Verdict

- **MM standalone: 🔴 RED** — full MaxDD -21.19 worse than -12.76; IS MaxDD -21.19 worse than -12.76 by >1pp; OOS MaxDD -16.68 worse than -12.55 by >1pp
- **MM standalone + adds: 🔴 RED** — full MaxDD -24.58 worse than -12.76; IS MaxDD -24.58 worse than -12.76 by >1pp; OOS MaxDD -18.33 worse than -12.55 by >1pp

_No arm passed the full gate. Same measure-first discipline: nothing ships._

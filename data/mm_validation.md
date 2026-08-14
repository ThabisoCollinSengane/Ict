# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `d903391`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM standalone | 1912.00 | 31.20 | 2.47 | -23.36 | 2,858,914,947 | 1133 | 0 |
| MM standalone + adds | 2329.00 | 27.90 | 2.67 | -28.74 | 1,120,313,826 | 1585 | 0 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM standalone | 1010.00 | 30.80 | 1.95 | -23.36 | 913,070 | 630 | 0 |
| MM standalone + adds | 1185.00 | 26.80 | 1.67 | -28.74 | 271,255 | 837 | 0 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM standalone | 869.00 | 31.90 | 2.48 | -18.28 | 4,774,502 | 483 | 0 |
| MM standalone + adds | 1094.00 | 28.70 | 2.67 | -21.17 | 5,929,243 | 704 | 0 |

## Verdict

- **MM standalone: 🔴 RED** — full MaxDD -23.36 worse than -12.76; IS MaxDD -23.36 worse than -12.76 by >1pp; OOS MaxDD -18.28 worse than -12.55 by >1pp
- **MM standalone + adds: 🔴 RED** — full MaxDD -28.74 worse than -12.76; IS MaxDD -28.74 worse than -12.76 by >1pp; OOS MaxDD -21.17 worse than -12.55 by >1pp

_No arm passed the full gate. Same measure-first discipline: nothing ships._

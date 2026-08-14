# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `110879d`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM standalone | 1785.00 | 35.50 | 3.17 | -38.31 | 491,346,237 | 1041 | 0 |
| MM standalone + adds | 2324.00 | 31.20 | 3.20 | -37.82 | 354,013,946 | 1587 | 0 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM standalone | 945.00 | 35.10 | 2.15 | -38.31 | 585,229 | 583 | 0 |
| MM standalone + adds | 1234.00 | 31.40 | 1.97 | -37.82 | 370,515 | 874 | 0 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM standalone | 842.00 | 35.00 | 3.14 | -18.74 | 1,157,467 | 464 | 0 |
| MM standalone + adds | 1058.00 | 31.40 | 3.16 | -17.03 | 1,515,145 | 692 | 0 |

## Verdict

- **MM standalone: 🔴 RED** — full equity 491,346,237≤567,575,614; full MaxDD -38.31 worse than -12.76; IS MaxDD -38.31 worse than -12.76 by >1pp; OOS MaxDD -18.74 worse than -12.55 by >1pp
- **MM standalone + adds: 🔴 RED** — full equity 354,013,946≤567,575,614; full MaxDD -37.82 worse than -12.76; IS MaxDD -37.82 worse than -12.76 by >1pp; OOS MaxDD -17.03 worse than -12.55 by >1pp

_No arm passed the full gate. Same measure-first discipline: nothing ships._

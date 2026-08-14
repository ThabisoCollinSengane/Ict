# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `cae5771`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM standalone | 1937.00 | 31.00 | 2.47 | -23.88 | 2,576,545,262 | 1158 | 0 |
| MM standalone + adds | 2476.00 | 27.60 | 2.65 | -28.79 | 1,734,175,474 | 1726 | 0 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM standalone | 1017.00 | 30.90 | 1.95 | -23.36 | 930,562 | 637 | 0 |
| MM standalone + adds | 1291.00 | 26.70 | 1.79 | -28.79 | 480,924 | 937 | 0 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM standalone | 888.00 | 31.10 | 2.48 | -21.52 | 4,506,037 | 502 | 0 |
| MM standalone + adds | 1129.00 | 28.30 | 2.65 | -22.80 | 5,658,428 | 740 | 0 |

## Verdict

- **MM standalone: 🔴 RED** — full MaxDD -23.88 worse than -12.76; IS MaxDD -23.36 worse than -12.76 by >1pp; OOS MaxDD -21.52 worse than -12.55 by >1pp
- **MM standalone + adds: 🔴 RED** — full MaxDD -28.79 worse than -12.76; IS MaxDD -28.79 worse than -12.76 by >1pp; OOS MaxDD -22.80 worse than -12.55 by >1pp

_No arm passed the full gate. Same measure-first discipline: nothing ships._

# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool.

_run commit: `af9fc86`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM adds | 1133.00 | 34.10 | 6.06 | -16.33 | 348,061,245 | 344 | 0 |
| MM adds + opp-tgt | 2304.00 | 21.70 | 4.88 | -30.26 | 75,843,882 | 1439 | 378 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM adds | 501.00 | 36.50 | 2.87 | -16.33 | 215,601 | 124 | 0 |
| MM adds + opp-tgt | 882.00 | 25.90 | 2.94 | -30.26 | 208,388 | 474 | 160 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM adds | 577.00 | 34.80 | 5.97 | -14.93 | 1,658,018 | 169 | 0 |
| MM adds + opp-tgt | 1186.00 | 22.20 | 4.31 | -21.51 | 531,051 | 745 | 198 |

## Verdict

- **MM adds: 🔴 RED** — full equity 348,061,245≤567,575,614; full MaxDD -16.33 worse than -12.76; IS MaxDD -16.33 worse than -12.76 by >1pp; OOS MaxDD -14.93 worse than -12.55 by >1pp
- **MM adds + opp-tgt: 🔴 RED** — full equity 75,843,882≤567,575,614; full MaxDD -30.26 worse than -12.76; IS MaxDD -30.26 worse than -12.76 by >1pp; OOS MaxDD -21.51 worse than -12.55 by >1pp

_No arm passed the full gate. Same measure-first discipline: nothing ships._

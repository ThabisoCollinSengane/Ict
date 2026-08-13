# Market Maker IFVG-continuation — full-backtest validation

Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + opposing-liquidity target. `adds` = MM legs added, `esc` = targets escalated to the opposing pool. **H1 EU/GU SMT required.**

_run commit: `6de7077`_
_**TRUE 4yr** — 2025 M1 present._

## Full 4yr

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 804.00 | 44.90 | 4.95 | -12.76 | 567,575,614 | 0 | 0 |
| MM adds | 857.00 | 43.40 | 5.77 | -12.95 | 553,824,808 | 55 | 0 |
| MM adds + opp-tgt | 1047.00 | 39.70 | 5.42 | -15.66 | 323,002,269 | 171 | 174 |

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 389.00 | 44.70 | 2.88 | -12.76 | 273,481 | 0 | 0 |
| MM adds | 416.00 | 42.80 | 2.90 | -12.95 | 263,122 | 29 | 0 |
| MM adds + opp-tgt | 484.00 | 40.10 | 2.91 | -15.66 | 225,924 | 66 | 67 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |
|---|---|---|---|---|---|---|---|
| baseline | 409.00 | 45.00 | 4.95 | -12.55 | 2,241,887 | 0 | 0 |
| MM adds | 437.00 | 43.90 | 5.74 | -14.98 | 2,106,276 | 27 | 0 |
| MM adds + opp-tgt | 549.00 | 39.70 | 5.30 | -15.17 | 1,849,239 | 98 | 97 |

## Verdict

- **MM adds: 🔴 RED** — full equity 553,824,808≤567,575,614; full MaxDD -12.95 worse than -12.76; OOS MaxDD -14.98 worse than -12.55 by >1pp
- **MM adds + opp-tgt: 🔴 RED** — full equity 323,002,269≤567,575,614; full MaxDD -15.66 worse than -12.76; IS MaxDD -15.66 worse than -12.76 by >1pp; OOS MaxDD -15.17 worse than -12.55 by >1pp

_No arm passed the full gate. Same measure-first discipline: nothing ships._

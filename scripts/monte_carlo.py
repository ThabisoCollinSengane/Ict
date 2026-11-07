"""P100 — Monte Carlo drawdown study on the engine's own trade list.

    python scripts/monte_carlo.py --dump data/mm_golden_full_p93_p99_trades.csv [--sims 10000]

Question: the backtest shows ONE path (MaxDD -15.66%). How bad could it get if the
same trades had arrived in a different order (shuffle) or if the next four years
draw from the same trade distribution (bootstrap, with replacement)?

Re-sizing: each trade's Rand P&L was earned at some lot size. The lot = equity-tier
base lot (config.EQUITY_TIERS, from sizing equity = min(equity, WITHDRAW_KEEP)) x the
setup's sizing multipliers (1.25x levers, 2x/3x draw cascade). We infer the tier base
from the units, then re-scale the P&L to the tier the SIMULATED account is in, so a
loss early (small account) costs less than the same loss at R6k — as live.

Withdrawals: once a month's worth of trades (n_trades / months) has passed since the
last one and equity > WITHDRAW_KEEP, everything above it is banked, as the engine does.
Drawdown = largest fall of the working balance from its running peak (the peak resets
to the balance left after a withdrawal). Overlapping trades are treated as sequential.

The original order is replayed first as a calibration check against the engine.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

TIERS = [(eq, int(round(l[0] * 100_000))) for eq, l in config.EQUITY_TIERS]   # (min_eq, units)
BASES = sorted({u for _, u in TIERS})
MULTS = sorted({round(d * 1.25 ** k, 6) for d in (1, 2, 3) for k in range(6)})


def tier_units(eq):
    e = min(max(eq, 0.0), config.WITHDRAW_KEEP)
    for mn, u in TIERS:
        if e >= mn:
            return u
    return TIERS[-1][1]


def infer_base(units):
    for b in sorted(BASES, reverse=True):
        r = units / b
        if any(abs(r - m) / m < 0.01 for m in MULTS):
            return b
    return min(BASES, key=lambda b: abs(units / b - round(units / b)))   # fallback


def simulate(pnl_per_base, months_per_trade, start, keep):
    eq, peak, maxdd, withdrawn, since = start, start, 0.0, 0.0, 0.0
    tpeak, tdd = start, 0.0                             # total value = balance + banked
    streak = worst_streak = 0
    eq_min = start
    for p in pnl_per_base:
        eq += p * tier_units(eq)
        since += months_per_trade
        streak = streak + 1 if p < 0 else 0
        worst_streak = max(worst_streak, streak)
        peak = max(peak, eq)
        maxdd = max(maxdd, (peak - eq) / peak if peak > 0 else 0)
        eq_min = min(eq_min, eq)
        tv = eq + withdrawn
        tpeak = max(tpeak, tv)
        tdd = max(tdd, (tpeak - tv) / tpeak)
        if since >= 1.0 and eq > keep:
            withdrawn += eq - keep
            eq, peak, since = keep, keep, 0.0
    return maxdd * 100, withdrawn, worst_streak, eq_min, tdd * 100


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default="data/mm_golden_full_p93_p99_trades.csv")
    ap.add_argument("--sims", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="data/monte_carlo_report.md")
    a = ap.parse_args()

    d = pd.read_csv(a.dump)
    d["t"] = pd.to_datetime(d.closed_at, utc=True)
    d = d.sort_values("t").reset_index(drop=True)
    d["base"] = d.units.map(infer_base)
    d["per_base"] = d.pnl / d.base                     # Rand per unit of tier base
    months = max((d.t.max() - d.t.min()).days / 30.44, 1)
    mpt = months / len(d)
    start, keep = float(config.STARTING_CASH), float(config.WITHDRAW_KEEP)
    x = d.per_base.to_numpy()

    orig = simulate(x, mpt, start, keep)
    rng = np.random.default_rng(a.seed)
    res = {}
    for mode in ("shuffle", "bootstrap"):
        out = []
        for _ in range(a.sims):
            s = rng.permutation(x) if mode == "shuffle" else rng.choice(x, size=len(x), replace=True)
            out.append(simulate(s, mpt, start, keep))
        res[mode] = np.array(out)

    L = ["# Monte Carlo drawdown study (P100)", "",
         f"Trades: {len(d)} from `{os.path.basename(a.dump)}` ({d.t.min():%Y-%m-%d} to {d.t.max():%Y-%m-%d}), "
         f"{a.sims:,} simulations per method, start R{start:,.0f}, working capital R{keep:,.0f}.", "",
         "## Calibration — the real order replayed by this simulator", "",
         f"Working-balance MaxDD {orig[0]:.2f}%, total-value MaxDD {orig[4]:.2f}%, withdrawn R{orig[1]:,.0f}, worst losing streak {orig[2]}, lowest balance R{orig[3]:,.0f}.",
         "Engine reported for the same run: working-balance MaxDD 31.59%, total-value MaxDD 15.66% (the headline figure), withdrawn R176,034.",
         "",
         "**Two drawdowns.** The engine's headline MaxDD is measured on TOTAL value (working balance + every rand already withdrawn), "
         "which grows as profit is banked, so a loss looks smaller against it. The working-balance figure is the fall of the money "
         "actually in the trading account, from its high. That is what you see in MT5.", ""]
    for mode, r in res.items():
        dd, wd, st, mn, td = r[:, 0], r[:, 1], r[:, 2], r[:, 3], r[:, 4]
        q = lambda v, p: np.percentile(v, p)
        L += [f"## {mode.capitalize()} — " + ("same trades, random order" if mode == "shuffle"
                                              else "random draw with replacement (a different 4 years)"), "",
              "| | median | 75th | 90th | 95th | 99th | worst |", "|---|---|---|---|---|---|---|",
              f"| Total-value drawdown % (headline measure) | {q(td,50):.1f} | {q(td,75):.1f} | {q(td,90):.1f} | {q(td,95):.1f} | {q(td,99):.1f} | {td.max():.1f} |",
              f"| Working-balance drawdown % (what MT5 shows) | {q(dd,50):.1f} | {q(dd,75):.1f} | {q(dd,90):.1f} | {q(dd,95):.1f} | {q(dd,99):.1f} | {dd.max():.1f} |",
              f"| Longest losing streak | {q(st,50):.0f} | {q(st,75):.0f} | {q(st,90):.0f} | {q(st,95):.0f} | {q(st,99):.0f} | {st.max():.0f} |",
              f"| Withdrawn R k (lower = worse; 50th / 25th / 10th / 5th / 1st / min) | {q(wd,50)/1e3:.1f} | {q(wd,25)/1e3:.1f} | {q(wd,10)/1e3:.1f} | {q(wd,5)/1e3:.1f} | {q(wd,1)/1e3:.1f} | {wd.min()/1e3:.1f} |",
              "",
              f"Total-value drawdown beyond 15.66% (worse than the backtest headline): **{(td>15.66).mean()*100:.1f}%**; beyond 20%: **{(td>20).mean()*100:.1f}%**; beyond 30%: **{(td>30).mean()*100:.1f}%**. "
              f"Working-balance drawdown beyond 15%: **{(dd>15).mean()*100:.1f}%**, 20%: **{(dd>20).mean()*100:.1f}%**, "
              f"30%: **{(dd>30).mean()*100:.1f}%**, 50%: **{(dd>50).mean()*100:.1f}%**. "
              f"Chance the balance ever falls below R500: **{(mn<500).mean()*100:.1f}%**. "
              f"Chance of withdrawing less than R100k: **{(wd<100_000).mean()*100:.1f}%**.", ""]
    txt = "\n".join(L) + "\n"
    open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()

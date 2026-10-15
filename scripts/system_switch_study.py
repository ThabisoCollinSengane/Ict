"""P105 — switching between the bot's sub-systems by their recent form.

    python scripts/system_switch_study.py [--group entry_model|pair]

The book already runs separate systems (judas, breakout, MM; weekly P&L correlation
~0, P103). Each has losing stretches. Question: does turning a system DOWN while it is
in a losing stretch, and back UP when it recovers, beat leaving everything on?

Every trade is put on a fixed size (the R6,000-tier base lot, multipliers kept) so the
answer is about the rule, not the compounding path. A paused system is still tracked
on paper ("shadow" results), exactly what a live bot could do, so it knows when to
come back. Rules, per system, judged on that system's own previous K trades:

  always        weight 1 (the current bot)
  pause_K       weight 0 while the last K trades summed < 0
  half_K        weight 0.5 while the last K trades summed < 0
  ma_K          weight 0.5 while the system's equity is below its K-trade average
  pf_K          weight 0.5 if trailing PF < 1, 1.25 if trailing PF > 3, else 1
  contra_K      weight 1.25 while the last K trades summed < 0 (back the system after a slump)

CONTROL (the test that matters): for every rule, the same number of trades is
down-weighted at RANDOM within each system, 500 times. A rule only has value if it
beats random de-weighting of the same size; otherwise it is just "trade less".
Also printed: does form persist? correlation of each system's last-K sum with its
next-K sum (if ~0, recent form cannot predict, and no switching rule can work).
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from monte_carlo import infer_base  # noqa: E402

TOP_UNITS = 9000


def load(paths):
    d = pd.concat([pd.read_csv(p) for p in paths if os.path.exists(p)], ignore_index=True)
    d["t"] = pd.to_datetime(d.closed_at, utc=True)
    d = d.sort_values("t").drop_duplicates(subset=["pair", "opened_at", "leg_idx"]).reset_index(drop=True)
    d["r"] = d.pnl / d.units.map(infer_base) * TOP_UNITS          # rand at the R6k tier
    d["half"] = np.select([d.t.dt.year <= 2023, d.t.dt.year <= 2025], ["IS 2022-23", "OOS 2024-25"],
                          "2026")
    return d


def weights(d, group, rule, k):
    w = np.ones(len(d))
    for _, idx in d.groupby(group).groups.items():
        idx = np.array(sorted(idx))
        r = d.r.to_numpy()[idx]
        eq = np.cumsum(r)
        for j in range(len(idx)):
            if j < k:
                continue
            past = r[j - k:j]
            if rule == "pause":
                w[idx[j]] = 0.0 if past.sum() < 0 else 1.0
            elif rule == "half":
                w[idx[j]] = 0.5 if past.sum() < 0 else 1.0
            elif rule == "ma":
                w[idx[j]] = 0.5 if eq[j - 1] < eq[j - k:j].mean() else 1.0
            elif rule == "contra":
                w[idx[j]] = 1.25 if past.sum() < 0 else 1.0
            elif rule == "pf":
                g, l = past[past > 0].sum(), -past[past < 0].sum()
                pf = g / l if l else 9.0
                w[idx[j]] = 0.5 if pf < 1 else (1.25 if pf > 3 else 1.0)
    return w


def stats(r):
    eq = np.cumsum(r)
    peak = np.maximum.accumulate(np.r_[0, eq])[1:]
    dd = (peak - eq).max() if len(r) else 0
    g, l = r[r > 0].sum(), -r[r < 0].sum()
    return r.sum(), dd, (g / l if l else np.nan)


def random_ctrl(d, group, w, rng, n=500):
    """Same per-system distribution of weights, shuffled within each system."""
    out = []
    groups = [np.array(sorted(ix)) for ix in d.groupby(group).groups.values()]
    for _ in range(n):
        wr = np.ones(len(d))
        for ix in groups:
            wr[ix] = rng.permutation(w[ix])
        out.append(wr)
    return out


def persistence(d, group, k):
    L = []
    for s, g in d.groupby(group):
        r = g.r.to_numpy()
        a = [r[j - k:j].sum() for j in range(k, len(r) - k)]
        b = [r[j:j + k].sum() for j in range(k, len(r) - k)]
        c = np.corrcoef(a, b)[0, 1] if len(a) > 3 else np.nan
        L.append(f"| {s} | {len(r)} | {c:+.2f} |")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--group", default="entry_model")
    ap.add_argument("--dumps", nargs="+", default=["data/mm_golden_full_p93_p99_trades.csv",
                                                   "data/mm_golden_y26_p93_p99_trades.csv"])
    ap.add_argument("--out", default="data/system_switch_report.md")
    a = ap.parse_args()
    d = load(a.dumps)
    rng = np.random.default_rng(5)
    L = [f"# System switching study (P105) — grouped by `{a.group}`", "",
         f"{len(d)} trades, fixed R6k-tier size, rand. Systems: "
         + ", ".join(f"{s} {n}" for s, n in d[a.group].value_counts().items()) + ".", "",
         "## Does recent form persist? (corr of a system's last-K sum with its next-K sum)", ""]
    for k in (10, 20):
        L += [f"K={k}", "", "| system | trades | corr |", "|---|---|---|"] + persistence(d, a.group, k) + [""]
    L += ["## Rules vs always-on vs random de-weighting of the same size", "",
          "| rule | half | total R | max DD R | PF | vs always | random ctrl (median) | beats random % |",
          "|---|---|---|---|---|---|---|---|"]
    base = {}
    for h, g in d.groupby("half"):
        base[h] = stats(g.r.to_numpy())
    for rule in ("pause", "half", "ma", "pf", "contra"):
        for k in (10, 20):
            w = weights(d, a.group, rule, k)
            ctrls = random_ctrl(d, a.group, w, rng)
            for h, g in d.groupby("half"):
                ix = g.index.to_numpy()
                tot, dd, pf = stats(d.r.to_numpy()[ix] * w[ix])
                ct = np.array([stats(d.r.to_numpy()[ix] * c[ix])[0] for c in ctrls])
                L.append(f"| {rule}_{k} | {h} | {tot:,.0f} | {dd:,.0f} | {pf:.2f} | "
                         f"{(tot / base[h][0] - 1) * 100:+.0f}% | {np.median(ct):,.0f} | "
                         f"{(tot > ct).mean() * 100:.0f}% |")
    L += ["", "Always-on per half: " + "; ".join(
        f"{h}: total {v[0]:,.0f}, DD {v[1]:,.0f}, PF {v[2]:.2f}" for h, v in base.items()), ""]
    txt = "\n".join(L) + "\n"
    open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()

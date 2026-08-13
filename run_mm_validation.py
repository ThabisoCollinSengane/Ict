#!/usr/bin/env python3
"""Market Maker IFVG-continuation — full-backtest A/B. Pure Python, no bash.

    python run_mm_validation.py

Three arms x {full 4yr, IS 2022-23, OOS 2024-25}, by shelling out to
`python run_backtest_histdata.py` with env overrides:

  1. baseline            MM_CONTINUATION_ENABLED=0                      (reference)
  2. MM adds             MM_CONTINUATION_ENABLED=1  MM_TARGET_OPPOSING=0
                         (IFVG re-entries, keep the normal nearest-draw target)
  3. MM adds + opp-tgt   MM_CONTINUATION_ENABLED=1  MM_TARGET_OPPOSING=1
                         (also escalate the target to the opposing liquidity pool)

Writes data/mm_validation.md. Arm 2 isolates the re-entries; arm 3 adds the
far-target change (the piece that has repeatedly failed on its own). Ships only if
an arm lifts equity with MaxDD held on the full 4yr AND both splits stay positive.

Options:
    --smt     also require H1 EU/GU SMT for MM adds (MM_HTF_SMT_REQUIRED=1)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))

SPLITS = (("Full 4yr", ["2022", "2023", "2024", "2025"]),
          ("IS 2022-23", ["2022", "2023"]),
          ("OOS 2024-25", ["2024", "2025"]))


def _run(env_over, years):
    env = dict(os.environ, **env_over)
    cmd = [sys.executable, "run_backtest_histdata.py", "--years", *years]
    p = subprocess.run(cmd, cwd=_ROOT, env=env, capture_output=True, text=True)
    return p.stdout + p.stderr


def _parse(txt):
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    add = re.search(r"mm_added\s+(\d+)", txt)
    esc = re.search(r"mm_target_escalated\s+(\d+)", txt)
    return {"trades": g("trades", int), "wr": g("win_rate_pct"),
            "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
            "eq": g("ending_equity_ZAR"),
            "adds": int(add.group(1)) if add else 0,
            "esc": int(esc.group(1)) if esc else 0}


def _fmt(d, k, suf=""):
    v = d.get(k)
    if v is None:
        return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smt", action="store_true")
    a = ap.parse_args()

    smt = {"MM_HTF_SMT_REQUIRED": "1"} if a.smt else {}
    arms = [
        ("baseline", {"MM_CONTINUATION_ENABLED": "0"}),
        ("MM adds", {"MM_CONTINUATION_ENABLED": "1", "MM_TARGET_OPPOSING": "0", **smt}),
        ("MM adds + opp-tgt", {"MM_CONTINUATION_ENABLED": "1", "MM_TARGET_OPPOSING": "1", **smt}),
    ]

    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=_ROOT,
                          capture_output=True, text=True).stdout.strip() or "unknown"
    cover2025 = os.path.exists(os.path.join(_ROOT, "data", "histdata", "UDXUSD_2025.csv"))

    res = {}   # (split, arm) -> parsed
    logs = {}
    for split, years in SPLITS:
        for arm, env in arms:
            print(f"=== {split} / {arm} ===")
            txt = _run(env, years)
            res[(split, arm)] = _parse(txt)
            logs[(split, arm)] = txt

    L = ["# Market Maker IFVG-continuation — full-backtest validation", "",
         "Arm 1 baseline (MM off) · Arm 2 IFVG re-entries only · Arm 3 re-entries + "
         "opposing-liquidity target. `adds` = MM legs added, `esc` = targets "
         "escalated to the opposing pool." + (" **H1 EU/GU SMT required.**" if a.smt else ""),
         "", f"_run commit: `{head}`_",
         ("_**TRUE 4yr** — 2025 M1 present._" if cover2025 else
          "_⚠️ **2025 M1 ABSENT** — 'Full' is 2022-2024 only._"), ""]

    crash = []
    for split, _years in SPLITS:
        b = res[(split, "baseline")]
        L += [f"## {split}", "",
              "| arm | trades | WR% | PF | MaxDD% | equity ZAR | adds | esc |",
              "|---|---|---|---|---|---|---|---|"]
        for arm, _env in arms:
            d = res[(split, arm)]
            L.append(f"| {arm} | {_fmt(d,'trades')} | {_fmt(d,'wr')} | {_fmt(d,'pf')} "
                     f"| {_fmt(d,'dd')} | {_fmt(d,'eq')} | {d.get('adds',0)} | {d.get('esc',0)} |")
            if d.get("pf") is None:
                tt = logs[(split, arm)]
                crash.append(f"### {split} / {arm} — NO SUMMARY\n\n```\n"
                             f"{chr(10).join(tt.splitlines()[-25:])}\n```\n")
        L.append("")

    # verdict per arm: full-4yr equity up + MaxDD not worse, both splits PF>1 and
    # MaxDD not worse by >1pp (OOS-restart tolerance, per CLAUDE.md).
    def judge(arm):
        f, i, o = (res[("Full 4yr", arm)], res[("IS 2022-23", arm)],
                   res[("OOS 2024-25", arm)])
        fb, ib, ob = (res[("Full 4yr", "baseline")], res[("IS 2022-23", "baseline")],
                      res[("OOS 2024-25", "baseline")])
        for d in (f, i, o, fb, ib, ob):
            if any(d.get(k) is None for k in ("pf", "eq", "dd")):
                return None, "a run crashed"
        fails = []
        if f["eq"] <= fb["eq"]:
            fails.append(f"full equity {f['eq']:,.0f}≤{fb['eq']:,.0f}")
        if f["dd"] < fb["dd"] - 0.10:
            fails.append(f"full MaxDD {f['dd']:.2f} worse than {fb['dd']:.2f}")
        for nm, d, base in (("IS", i, ib), ("OOS", o, ob)):
            if d["pf"] <= 1.0:
                fails.append(f"{nm} PF {d['pf']:.2f}≤1")
            if d["dd"] < base["dd"] - 1.0:
                fails.append(f"{nm} MaxDD {d['dd']:.2f} worse than {base['dd']:.2f} by >1pp")
        return (not fails), ("; ".join(fails) if fails else "ok")

    L += ["## Verdict", ""]
    any_green = False
    for arm, _env in arms[1:]:
        adds = sum(res[(s, arm)].get("adds", 0) for s, _y in SPLITS)
        v, why = judge(arm)
        if adds == 0:
            mark, why = "⚠️ inert", "0 MM adds fired — no setups matched (check IFVG/structure gates)"
        elif v is None:
            mark = "⚠️ crash"
        elif v:
            mark, any_green = "🟢 GREEN", True
        else:
            mark = "🔴 RED"
        L.append(f"- **{arm}: {mark}** — {why}")
    L += ["", ("_At least one arm passed — Claude reviews split magnitudes before shipping._"
               if any_green else
               "_No arm passed the full gate. Same measure-first discipline: nothing ships._")]
    if crash:
        L += ["", "## Crash diagnostics", ""] + crash

    out = os.path.join(_ROOT, "data", "mm_validation.md")
    text = "\n".join(L) + "\n"
    open(out, "w").write(text)
    print(text)
    print(f"[report → {os.path.relpath(out, _ROOT)}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

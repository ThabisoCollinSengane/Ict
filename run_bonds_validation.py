#!/usr/bin/env python3
"""Bonds/yields dollar-bias sizing lever — full-backtest A/B. Pure Python, no bash.

    python run_bonds_validation.py

Runs baseline (BONDS_SIZE_MULT=1.0) vs lever (1.25), BONDS_BIAS_ENABLED=1, on the
full 4yr and the IS (2022-23) / OOS (2024-25) splits by shelling out to
`python run_backtest_histdata.py` with env overrides (same way you run the
backtest — no bash script). Writes data/bonds_validation.md and prints the
verdict. Run this ONLY after run_bonds.py returns GREEN.

Ships only if full-4yr equity is up and MaxDD not worse, and both splits stay
positive with MaxDD not materially worse.

Options:
    --mult 1.25        lever multiplier to test against 1.0 baseline
    --skip-bias        don't regenerate data/bond_bias.json (use the existing file)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

RUNS = (("Full 4yr", "full", ["2022", "2023", "2024", "2025"]),
        ("IS 2022-23", "is", ["2022", "2023"]),
        ("OOS 2024-25", "oos", ["2024", "2025"]))


def _run(mult, years):
    env = dict(os.environ, BONDS_BIAS_ENABLED="1", BONDS_SIZE_MULT=str(mult))
    cmd = [sys.executable, "run_backtest_histdata.py", "--years", *years]
    p = subprocess.run(cmd, cwd=_ROOT, env=env, capture_output=True, text=True)
    return p.stdout + p.stderr


def _parse(txt):
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    sz = re.search(r"bond_bias_sized\s+(\d+)", txt)
    return {"trades": g("trades", int), "wr": g("win_rate_pct"),
            "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
            "eq": g("ending_equity_ZAR"), "sized": int(sz.group(1)) if sz else 0}


def _fmt(d, k, suf=""):
    v = d.get(k)
    if v is None:
        return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf


def _ok(b, m, eq_up_required, dd_tol):
    if any(m.get(k) is None or b.get(k) is None for k in ("pf", "eq", "dd")):
        return None, "run crashed"
    fails = []
    if eq_up_required and m["eq"] <= b["eq"]:
        fails.append(f"equity {m['eq']:,.0f}≤{b['eq']:,.0f}")
    elif not eq_up_required and m["eq"] < b["eq"]:
        fails.append(f"equity down {m['eq']:,.0f}<{b['eq']:,.0f}")
    if m["dd"] < b["dd"] - dd_tol:
        fails.append(f"MaxDD {m['dd']:.2f} worse than {b['dd']:.2f} by >{dd_tol}pp")
    if m["pf"] <= 1.0:
        fails.append(f"PF {m['pf']:.2f}≤1.0")
    return (not fails), ("; ".join(fails) if fails else "ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mult", type=float, default=1.25)
    ap.add_argument("--skip-bias", action="store_true")
    a = ap.parse_args()

    bias_path = os.path.join(_ROOT, "data", "bond_bias.json")
    if not a.skip_bias:
        print("=== regenerating data/bond_bias.json (from data/bonds_src/) ===")
        import bonds_analysis as ba
        ba.write_bond_bias(3, 20)
    if not os.path.exists(bias_path):
        print("ERROR: data/bond_bias.json missing. Run `python run_bonds.py` first "
              "(it fetches yields and emits the bias file).")
        return 1

    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=_ROOT,
                          capture_output=True, text=True).stdout.strip() or "unknown"
    cover2025 = os.path.exists(os.path.join(_ROOT, "data", "histdata", "UDXUSD_2025.csv"))

    res = {}
    crash_logs = []
    for label, _key, years in RUNS:
        print(f"=== {label}: baseline vs lever {a.mult}× ===")
        bt = _run(1.0, years)
        mt = _run(a.mult, years)
        res[label] = (_parse(bt), _parse(mt), bt, mt)

    L = ["# Bonds/yields dollar-bias sizing lever — full-backtest validation", "",
         f"Baseline (`BONDS_SIZE_MULT=1.0`) vs lever (`{a.mult}`), "
         "`BONDS_BIAS_ENABLED=1`, on the full 4yr and the IS/OOS splits. `sized` = "
         "trades the lever bumped (yields confirmed the dollar direction). **Ships "
         "only if full-4yr equity is up and MaxDD not worse, and both splits stay "
         "positive with MaxDD not materially worse.**", "", f"_run commit: `{head}`_",
         ("_**TRUE 4yr run** — 2025 M1 present._" if cover2025 else
          "_⚠️ **2025 M1 ABSENT** — 'Full' is 2022-2024 only (not the documented "
          "810-trade path)._"), ""]

    for label, (b, m, bt, mt) in ((lbl, res[lbl]) for lbl, _k, _y in RUNS):
        L += [f"## {label}", "", "| metric | baseline | lever | Δ |", "|---|---|---|---|"]
        for k, name, suf in (("trades", "trades", ""), ("wr", "win rate", "%"),
                             ("pf", "profit factor", ""), ("dd", "max drawdown", "%"),
                             ("eq", "ending equity ZAR", "")):
            bv, mv = b.get(k), m.get(k)
            if bv is None or mv is None:
                d = "—"
            elif k == "eq":
                d = f"{mv-bv:+,.0f}"
            else:
                d = f"{mv-bv:+.2f}"
            L.append(f"| {name} | {_fmt(b,k,suf)} | {_fmt(m,k,suf)} | {d} |")
        L += ["", f"_trades sized by lever: {m.get('sized',0)}_", ""]
        for tag, dd, tt in (("baseline", b, bt), ("lever", m, mt)):
            if dd.get("pf") is None:
                crash_logs.append(f"### {label} {tag} — NO SUMMARY (crash?)\n\n"
                                  f"```\n{chr(10).join(tt.splitlines()[-30:])}\n```\n")

    checks = {
        "Full 4yr": _ok(res["Full 4yr"][0], res["Full 4yr"][1], True, 0.10),
        "IS 2022-23": _ok(res["IS 2022-23"][0], res["IS 2022-23"][1], False, 1.0),
        "OOS 2024-25": _ok(res["OOS 2024-25"][0], res["OOS 2024-25"][1], False, 1.0),
    }
    sized_any = any(res[l][1].get("sized", 0) for l in res)
    crashed = any(v is None for v, _ in checks.values())
    green = (not crashed) and sized_any and all(v for v, _ in checks.values())
    if crashed:
        vhead = "⚠️ INCONCLUSIVE — a run crashed (see diagnostics)."
    elif not sized_any:
        vhead = ("⚠️ INERT — the lever sized 0 trades (no bond_bias.json match / no "
                 "confirmations). Not shippable; check coverage.")
    elif green:
        vhead = "🟢 GREEN — provisional ship. Full-4yr equity up + MaxDD held; both splits positive."
    else:
        vhead = "🔴 RED — do NOT ship. Stays OFF (BONDS_SIZE_MULT=1.0)."
    L += ["## Verdict", "", f"**{vhead}**", ""]
    for label, (v, why) in checks.items():
        mark = "🟢 pass" if v else ("⚠️ crash" if v is None else "🔴 fail")
        L.append(f"- **{label}: {mark}** — {why}")
    L += ["", "_Provisional — review the split magnitudes (IS/OOS same ballpark?) "
          "before final ship, per the 'what not curve-fit means' rule._"]
    if crash_logs:
        L += ["", "## Crash diagnostics", ""] + crash_logs

    out = os.path.join(_ROOT, "data", "bonds_validation.md")
    text = "\n".join(L) + "\n"
    open(out, "w").write(text)
    print(text)
    print(f"[report → {os.path.relpath(out, _ROOT)}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

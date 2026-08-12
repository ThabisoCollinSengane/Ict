#!/usr/bin/env bash
# Bonds/yields dollar-bias sizing lever — full-backtest validation (Codespaces).
#   bash run_bonds_validation.sh
# Baseline (BONDS_SIZE_MULT=1.0) vs lever (1.25) on the full 4yr AND the IS
# (2022-23) / OOS (2024-25) splits, with BONDS_BIAS_ENABLED=1. Run this ONLY after
# run_bonds.sh returns a GREEN verdict — this is the real ship gate.
# Ships only if full-4yr equity is up and MaxDD not worse, and both splits stay
# positive with MaxDD not materially worse.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring M1 data (all 4 years incl. UDXUSD — DXY gate) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD UDXUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y.csv MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ] || [ "${REFRESH_M1:-0}" = 1 ]; then
  echo "  fetching M1 from Drive + preparing…"
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  [ -z "$Z" ] && { echo "ERROR: M1 download failed"; exit 1; }
  python scripts/prepare_histdata.py "$(dirname "$Z")" || exit 1
fi
COVER2025="$(ls data/histdata/UDXUSD_2025.csv >/dev/null 2>&1 && echo yes || echo NO)"
echo "  -> UDXUSD_2025 present (true-4yr gate): $COVER2025"

echo "=== ensuring FRED yields + fresh bond_bias.json ==="
python scripts/fetch_fred.py --start 2020-01-01 --end 2025-12-31 \
  || echo "  ⚠️ FRED fetch failed — if data/bonds_src/DGS*.csv is absent the lever can't fire."
python scripts/bonds_analysis.py --emit-bias >/dev/null 2>&1
ls -la data/bond_bias.json 2>/dev/null || { echo "ERROR: bond_bias.json not written (no yield data)"; exit 1; }

run_one() {  # $1 = mult  $2 = label  $3.. = years
  local mult="$1" label="$2"; shift 2
  echo "  $label (BONDS_SIZE_MULT=$mult, years $*) ..."
  BONDS_BIAS_ENABLED=1 BONDS_SIZE_MULT="$mult" \
    python run_backtest_histdata.py --years "$@" > "/tmp/bond_$label.txt" 2>&1
}

echo "=== 6 runs: baseline vs lever x {full 4yr, IS 2022-23, OOS 2024-25} ==="
run_one 1.0  full_base 2022 2023 2024 2025
run_one 1.25 full_lev  2022 2023 2024 2025
run_one 1.0  is_base   2022 2023
run_one 1.25 is_lev    2022 2023
run_one 1.0  oos_base  2024 2025
run_one 1.25 oos_lev   2024 2025

echo "=== building comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" COVER2025="$COVER2025" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
C2025 = os.environ.get("COVER2025", "NO")
def grab(label):
    p = f"/tmp/bond_{label}.txt"
    if not os.path.exists(p):
        return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    sz = re.search(r"bond_bias_sized\s+(\d+)", txt)
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"),
         "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
         "eq": g("ending_equity_ZAR"), "sized": int(sz.group(1)) if sz else 0}
    return d, txt

L = ["# Bonds/yields dollar-bias sizing lever — full-backtest validation", "",
     "Baseline (`BONDS_SIZE_MULT=1.0`) vs lever (`1.25`), `BONDS_BIAS_ENABLED=1`, "
     "on the full 4yr and the IS/OOS splits. `sized` = trades the lever bumped "
     "(yields confirmed the dollar direction). **Ships only if full-4yr equity is "
     "up and MaxDD not worse, and both splits stay positive with MaxDD not "
     "materially worse.**", "", f"_run commit: `{HEAD}`_",
     ("_**TRUE 4yr run** — 2025 M1 present._" if C2025 == "yes" else
      "_⚠️ **2025 M1 ABSENT** — 'Full' is 2022-2024 only (not the documented 810-"
      "trade path). Load 2025 for a true 4yr confirm._"), ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    if v is None: return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf

crash_logs = []
res = {}
for split, base, lev in (("Full 4yr", "full_base", "full_lev"),
                         ("IS 2022-23", "is_base", "is_lev"),
                         ("OOS 2024-25", "oos_base", "oos_lev")):
    (b, bt), (m, mt) = grab(base), grab(lev)
    res[split] = (b, m)
    L += [f"## {split}", "",
          "| metric | baseline | lever 1.25× | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades", "trades", ""), ("wr", "win rate", "%"),
                        ("pf", "profit factor", ""), ("dd", "max drawdown", "%"),
                        ("eq", "ending equity ZAR", "")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None:      d = "—"
        elif k == "eq":                   d = f"{mv-bv:+,.0f}"
        else:                             d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_trades sized by lever: {m.get('sized',0)}_", ""]
    for tag, dd, tt in (("baseline", b, bt), ("lever", m, mt)):
        if dd.get("pf") is None:
            crash_logs.append(f"### {split} {tag} — NO SUMMARY (crash?)\n\n"
                              f"```\n{chr(10).join(tt.splitlines()[-30:])}\n```\n")

def ok(split, eq_up_required, dd_tol):
    b, m = res.get(split, ({}, {}))
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

checks = {"Full 4yr": ok("Full 4yr", True, 0.10),
          "IS 2022-23": ok("IS 2022-23", False, 1.0),
          "OOS 2024-25": ok("OOS 2024-25", False, 1.0)}
sized_any = any(res[s][1].get("sized", 0) for s in res)
crashed = any(v is None for v, _ in checks.values())
green = (not crashed) and sized_any and all(v for v, _ in checks.values())
if crashed:      head = "⚠️ INCONCLUSIVE — a run crashed (see diagnostics below)."
elif not sized_any: head = "⚠️ INERT — the lever sized 0 trades (no bond_bias.json match / no confirmations). Not shippable; investigate coverage."
elif green:      head = "🟢 GREEN — provisional ship. Full-4yr equity up + MaxDD held; both splits positive."
else:            head = "🔴 RED — do NOT ship. Stays OFF (BONDS_SIZE_MULT=1.0)."
L += ["## Verdict", "", f"**{head}**", ""]
for split, (v, why) in checks.items():
    mark = "🟢 pass" if v else ("⚠️ crash" if v is None else "🔴 fail")
    L.append(f"- **{split}: {mark}** — {why}")
L += ["", "_Provisional — Claude reviews the split magnitudes (IS/OOS same "
      "ballpark?) before final ship, per the 'what not curve-fit means' rule._"]
if crash_logs:
    L += ["", "## Crash diagnostics (auto-captured)", ""] + crash_logs
open("data/bonds_validation.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/bonds_validation.md 2>/dev/null
git commit -q -m "Bonds dollar-bias lever validation results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/bonds_validation.md"
else
  echo "(push failed — copy the comparison above to Claude)"
fi

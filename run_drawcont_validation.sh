#!/usr/bin/env bash
# Draw-to-liquidity continuation entry — full-backtest validation (Codespaces).
#   bash run_drawcont_validation.sh
# Baseline (DRAW_CONT_ENABLED=0) vs entry ON (=1) on the full 4yr AND IS/OOS.
# This ADDS trades (continuation entries toward unswept near PDH/PDL), so the
# critical gate is MaxDD — gate bypasses have a strong negative prior (P11 NY
# exempt, SOJ-draw bypass both blew MaxDD out). Ships only if: full-4yr equity up
# and MaxDD NOT worse, and both splits stay positive with MaxDD not materially
# worse. Price-based, so all pairs/years apply.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring M1 data (all 4 years) ==="
missing=0
for y in 2022 2023 2024 2025; do
  ls data/histdata/EURUSD_$y.csv >/dev/null 2>&1 || { echo "  EURUSD_$y.csv MISSING"; missing=1; }
done
if [ "$missing" = 1 ]; then
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  [ -z "$Z" ] && { echo "ERROR: M1 download failed"; exit 1; }
  python scripts/prepare_histdata.py "$(dirname "$Z")" || exit 1
fi
COVER2025="$(ls data/histdata/UDXUSD_2025.csv >/dev/null 2>&1 && echo yes || echo NO)"

run_one() {  # $1 = flag  $2 = label  $3.. = years
  local flag="$1" label="$2"; shift 2
  echo "  $label (DRAW_CONT_ENABLED=$flag, years $*) ..."
  DRAW_CONT_ENABLED="$flag" python run_backtest_histdata.py --years "$@" \
    > "/tmp/dc_$label.txt" 2>&1
}

echo "=== 6 runs: baseline vs draw-cont x {full 4yr, IS 2022-23, OOS 2024-25} ==="
run_one 0 full_base 2022 2023 2024 2025
run_one 1 full_on   2022 2023 2024 2025
run_one 0 is_base   2022 2023
run_one 1 is_on     2022 2023
run_one 0 oos_base  2024 2025
run_one 1 oos_on    2024 2025

echo "=== building comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" COVER2025="$COVER2025" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
C2025 = os.environ.get("COVER2025", "NO")
def grab(label):
    p = f"/tmp/dc_{label}.txt"
    if not os.path.exists(p):
        return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    dc = re.search(r"draw_cont_confirmed\s+(\d+)", txt)
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"),
         "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
         "eq": g("ending_equity_ZAR"), "added": int(dc.group(1)) if dc else 0}
    return d, txt

L = ["# Draw-to-liquidity continuation entry — full-backtest validation", "",
     "Baseline (`DRAW_CONT_ENABLED=0`) vs entry ON (`1`). This ADDS continuation "
     "trades toward unswept near PDH/PDL. `added` = draw-cont entries opened. "
     "**Ships only if full-4yr equity up and MaxDD NOT worse, and both splits stay "
     "positive with MaxDD not materially worse** (gate bypasses have blown MaxDD "
     "before — this must prove otherwise).", "", f"_run commit: `{HEAD}`_",
     ("_TRUE 4yr run — 2025 DXY present._" if C2025 == "yes" else
      "_⚠️ 2025 DXY (UDXUSD_2025) ABSENT — 'Full' is effectively 2022-2024; "
      "re-confirm once loaded._"), ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    if v is None: return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf

crash_logs = []
res = {}
for split, base, on in (("Full 4yr", "full_base", "full_on"),
                        ("IS 2022-23", "is_base", "is_on"),
                        ("OOS 2024-25", "oos_base", "oos_on")):
    (b, bt), (m, mt) = grab(base), grab(on)
    res[split] = (b, m)
    L += [f"## {split}", "",
          "| metric | baseline | draw-cont ON | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades", "trades", ""), ("wr", "win rate", "%"),
                        ("pf", "profit factor", ""), ("dd", "max drawdown", "%"),
                        ("eq", "ending equity ZAR", "")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None:      d = "—"
        elif k == "eq":                   d = f"{mv-bv:+,.0f}"
        else:                             d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_draw-cont entries added: {m.get('added',0)}_", ""]
    for tag, dd, tt in (("baseline", b, bt), ("draw-cont", m, mt)):
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
crashed = any(v is None for v, _ in checks.values())
green = (not crashed) and all(v for v, _ in checks.values())
if crashed:   head = "⚠️ INCONCLUSIVE — a run crashed (see diagnostics below)."
elif green:   head = "🟢 GREEN — provisional ship. Full-4yr equity up + MaxDD held; both splits positive."
else:         head = "🔴 RED — do NOT ship. Stays OFF (DRAW_CONT_ENABLED=0)."
L += ["## Verdict", "", f"**{head}**", ""]
for split, (v, why) in checks.items():
    mark = "🟢 pass" if v else ("⚠️ crash" if v is None else "🔴 fail")
    L.append(f"- **{split}: {mark}** — {why}")
L += ["", "_Provisional — Claude reviews split magnitudes + whether the added "
      "trades are net-positive (not just MaxDD-neutral) before final ship._"]
if crash_logs:
    L += ["", "## Crash diagnostics (auto-captured)", ""] + crash_logs
open("data/drawcont_validation.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/drawcont_validation.md 2>/dev/null
git commit -q -m "Draw-cont entry validation results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/drawcont_validation.md"
else
  echo "(push failed — copy the comparison above to Claude)"
fi

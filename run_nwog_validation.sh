#!/usr/bin/env bash
# NWOG (New Week Opening Gap) — full-backtest validation (Codespaces).
#   bash run_nwog_validation.sh
# Baseline (NWOG_ENABLED=0, byte-identical to pre-NWOG) vs NWOG (NWOG_ENABLED=1)
# on the full 4yr AND the IS (2022-23) / OOS (2024-25) splits. NWOG adds a +1
# conviction at the weekend-gap CE and a "nwog" confluence/target source (which
# can bump P18 score sizing). Price-based, so ALL pairs/years apply.
# Ships only if: full-4yr equity UP and MaxDD NOT worse, and both splits stay
# positive with MaxDD not materially worse. Otherwise defaults OFF (NWOG_ENABLED=0).
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring M1 data is prepared (all 4 years: 2022-2025) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD UDXUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y.csv MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ] || [ "${REFRESH_M1:-0}" = 1 ]; then
  echo "  fetching M1 from Drive + preparing (REFRESH_M1=${REFRESH_M1:-0})…"
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  [ -z "$Z" ] && { echo "ERROR: M1 download failed"; exit 1; }
  python scripts/prepare_histdata.py "$(dirname "$Z")" || exit 1
fi
COVER2025="$(ls data/histdata/UDXUSD_2025.csv >/dev/null 2>&1 && echo yes || echo NO)"
echo "  -> UDXUSD_2025 present (true-4yr gate): $COVER2025"

run_one() {  # $1 = enabled  $2 = label  $3.. = years
  local en="$1" label="$2"; shift 2
  echo "  $label (NWOG_ENABLED=$en, years $*) ..."
  NWOG_ENABLED="$en" python run_backtest_histdata.py --years "$@" \
    > "/tmp/nwog_$label.txt" 2>&1
}

echo "=== 6 runs: baseline vs NWOG x {full 4yr, IS 2022-23, OOS 2024-25} ==="
run_one 0 full_base 2022 2023 2024 2025
run_one 1 full_nwog 2022 2023 2024 2025
run_one 0 is_base   2022 2023
run_one 1 is_nwog   2022 2023
run_one 0 oos_base  2024 2025
run_one 1 oos_nwog  2024 2025

echo "=== building comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" COVER2025="$COVER2025" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
C2025 = os.environ.get("COVER2025", "NO")
def grab(label):
    p = f"/tmp/nwog_{label}.txt"
    if not os.path.exists(p):
        return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    hit = re.search(r"nwog_ce_hit\s+(\d+)", txt)
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"),
         "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
         "eq": g("ending_equity_ZAR"), "hit": int(hit.group(1)) if hit else 0}
    return d, txt

L = ["# NWOG (New Week Opening Gap) — full-backtest validation", "",
     "Baseline (`NWOG_ENABLED=0`, byte-identical to pre-NWOG) vs NWOG "
     "(`NWOG_ENABLED=1`) on the full 4yr and the IS/OOS splits. `hit` = trades "
     "where price sat at the NWOG CE aligned with the trade. **Ships only if "
     "full-4yr equity is up and MaxDD is not worse, and both splits stay positive "
     "with MaxDD not materially worse.**", "", f"_run commit: `{HEAD}`_",
     ("_**TRUE 4yr run** — 2025 M1 data present._" if C2025 == "yes" else
      "_⚠️ **2025 M1 data ABSENT** — 'Full' below is 2022-2024 only (not the "
      "documented 810-trade 4yr path)._"), ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    if v is None: return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf

crash_logs, res = [], {}
for split, base, nw in (("Full 4yr", "full_base", "full_nwog"),
                        ("IS 2022-23", "is_base", "is_nwog"),
                        ("OOS 2024-25", "oos_base", "oos_nwog")):
    (b, bt), (m, mt) = grab(base), grab(nw)
    res[split] = (b, m)
    L += [f"## {split}", "",
          "| metric | baseline | NWOG | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades", "trades", ""), ("wr", "win rate", "%"),
                        ("pf", "profit factor", ""), ("dd", "max drawdown", "%"),
                        ("eq", "ending equity ZAR", "")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None:      d = "—"
        elif k == "eq":                   d = f"{mv-bv:+,.0f}"
        else:                             d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_NWOG CE hits: {m.get('hit',0)}_", ""]
    for tag, dd, tt in (("baseline", b, bt), ("nwog", m, mt)):
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
else:         head = "🔴 RED — do NOT ship. Default NWOG_ENABLED=0."
L += ["## Verdict", "", f"**{head}**", ""]
for split, (v, why) in checks.items():
    mark = "🟢 pass" if v else ("⚠️ crash" if v is None else "🔴 fail")
    L.append(f"- **{split}: {mark}** — {why}")
L += ["", "_Provisional — review split magnitudes (IS/OOS same ballpark?) before "
      "final ship, per the 'what not curve-fit means' rule._"]
if crash_logs:
    L += ["", "## Crash diagnostics (auto-captured)", ""] + crash_logs
open("data/nwog_validation.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/nwog_validation.md 2>/dev/null
git commit -q -m "NWOG validation results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/nwog_validation.md"
else
  echo "(push failed — copy the comparison above to Claude)"
fi

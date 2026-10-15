#!/usr/bin/env bash
# Structure-entry trigger (Ep-12 "enter on the LTF reversal swing") — validation.
#   bash run_structure_entry_validation.sh
# Baseline (STRUCTURE_ENTRY_ENABLED=0) vs lever (=1) on the full 4yr AND the IS
# (2022-23) / OOS (2024-25) splits. The trigger requires a freshly-confirmed
# lower-TF STL (longs) / STH (shorts) before entry — a filter on top of the
# existing FVG/OB entry, so it can only reduce or hold the trade count.
#
# Ship gate (per the OOS protocol + the path-dependency lessons in CLAUDE.md):
#   keep ONLY if full-4yr equity is UP and MaxDD is NOT worse, AND both splits
#   stay positive with MaxDD not materially worse. Otherwise it stays OFF.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring M1 data (2022-2025; UDXUSD is a hard-gate core symbol) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD UDXUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y.csv MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ] || [ "${REFRESH_M1:-0}" = 1 ]; then
  echo "  fetching M1 from Drive + preparing (REFRESH_M1=${REFRESH_M1:-0})..."
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
  echo "  $label (STRUCTURE_ENTRY_ENABLED=$en, years $*) ..."
  STRUCTURE_ENTRY_ENABLED="$en" python run_backtest_histdata.py --years "$@" \
    > "/tmp/se_$label.txt" 2>&1
}

echo "=== 6 runs: baseline vs trigger x {full 4yr, IS 2022-23, OOS 2024-25} ==="
run_one 0 full_base 2022 2023 2024 2025
run_one 1 full_lev  2022 2023 2024 2025
run_one 0 is_base   2022 2023
run_one 1 is_lev    2022 2023
run_one 0 oos_base  2024 2025
run_one 1 oos_lev   2024 2025

echo "=== building comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" COVER2025="$COVER2025" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
C2025 = os.environ.get("COVER2025", "NO")

def grab(label):
    p = f"/tmp/se_{label}.txt"
    if not os.path.exists(p):
        return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    bl = re.search(r"structure_entry_blocked\s+(\d+)", txt)
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"),
         "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
         "eq": g("ending_equity_ZAR"),
         "blocked": int(bl.group(1)) if bl else 0}
    return d, txt

L = ["# Structure-entry trigger (Ep-12 LTF reversal swing) - validation", "",
     "Baseline (`STRUCTURE_ENTRY_ENABLED=0`) vs trigger (`=1`) on the full 4yr and "
     "the IS/OOS splits. `blocked` = entries the trigger rejected (no fresh confirmed "
     "LTF swing). **Keep ONLY if full-4yr equity is up and MaxDD not worse, and both "
     "splits stay positive with MaxDD not materially worse - else it stays OFF.**",
     "", f"_run commit: `{HEAD}`_",
     ("_**TRUE 4yr run** - 2025 M1 present._" if C2025 == "yes" else
      "_WARNING: 2025 M1 ABSENT - 'Full' below is 2022-2024 only, not the documented "
      "810-trade path. Load 2025 for a true 4yr confirm._"), ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    if v is None: return "-"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf

for split, base, lev in (("Full 4yr", "full_base", "full_lev"),
                         ("IS 2022-23", "is_base", "is_lev"),
                         ("OOS 2024-25", "oos_base", "oos_lev")):
    (b, _), (m, _) = grab(base), grab(lev)
    L += [f"## {split}", "",
          "| metric | baseline | trigger ON | delta |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades", "trades", ""), ("wr", "win rate", "%"),
                        ("pf", "profit factor", ""), ("dd", "max drawdown", "%"),
                        ("eq", "ending equity ZAR", "")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None:      d = "-"
        elif k == "eq":                   d = f"{mv-bv:+,.0f}"
        else:                             d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += [f"| entries blocked | - | {m.get('blocked','-')} | - |", ""]

open("data/structure_entry_validation.md", "w").write("\n".join(L) + "\n")
print("wrote data/structure_entry_validation.md")
PY

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/structure_entry_validation.md
git add -f data/structure_entry_validation.md 2>/dev/null
git commit -q -m "Structure-entry validation results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED - Claude will read data/structure_entry_validation.md"
else
  echo "(push failed - copy the report above to Claude)"
fi

#!/usr/bin/env bash
# Minimum-target validation (Codespaces): does raising the target floor from 20 to
# 25 / 30 pips help? Raising it forces further targets — higher RR per trade but a
# lower hit-rate — so it must be validated, not assumed.
#   bash run_mintarget_validation.sh
# Ships a new floor only if full-4yr equity is UP and MaxDD NOT worse, with both
# IS/OOS splits still positive — the same gate as every sizing/structural change.
cd "$(dirname "$0")" || exit 1

echo "=== ensuring full 4yr M1 (incl UDXUSD_2025) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD UDXUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || missing=1
  done
done
if [ "$missing" = 1 ]; then
  python scripts/fetch_histdata.py --years 2025 --dest /tmp/histdata_dl \
    && python scripts/prepare_histdata.py /tmp/histdata_dl || { echo "ERROR: data"; exit 1; }
fi

run_one() {  # $1 = min_target  $2 = label  $3.. = years
  local mt="$1" label="$2"; shift 2
  echo "  $label (MIN_PIPS_TARGET=$mt, years $*) ..."
  MIN_PIPS_TARGET="$mt" python run_backtest_histdata.py --years "$@" \
    > "/tmp/mt_$label.txt" 2>&1
}

echo "=== runs: 20 (baseline) / 25 / 30, each on full 4yr + IS + OOS ==="
for mt in 20 25 30; do
  run_one "$mt" "full_$mt" 2022 2023 2024 2025
  run_one "$mt" "is_$mt"   2022 2023
  run_one "$mt" "oos_$mt"  2024 2025
done

echo "=== building comparison ==="
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
SHA="$SHA" python - <<'PY'
import re, os
SHA = os.environ.get("SHA", "unknown")
def grab(label):
    p = f"/tmp/mt_{label}.txt"
    if not os.path.exists(p):
        return {}, "(no output)"
    t = open(p).read()
    def g(k, c=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", t); return c(m.group(1)) if m else None
    return {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
            "dd": g("max_drawdown_pct"), "eq": g("ending_equity_ZAR")}, t

def row(mt, split):
    d, _ = grab(f"{split}_{mt}")
    def f(k):
        v = d.get(k);
        return "—" if v is None else (f"{v:,.0f}" if k=="eq" else f"{v:.2f}")
    return (f"| {mt} pips | {f('trades')} | {f('wr')}% | {f('pf')} | {f('dd')}% | {f('eq')} |")

L = ["# Minimum-target floor — 20 vs 25 vs 30 pips", "",
     "Raising the floor forces further targets: higher reward:risk per trade but a "
     "lower hit-rate. **Ship a new floor only if full-4yr equity is up and MaxDD is "
     "not worse, both IS/OOS splits still positive.**", "", f"_run commit: `{SHA}`_", ""]
for split, title in (("full", "Full 4yr"), ("is", "IS 2022-23"), ("oos", "OOS 2024-25")):
    L += [f"## {title}", "", "| floor | trades | WR | PF | MaxDD | equity ZAR |",
          "|---|---|---|---|---|---|"]
    for mt in (20, 25, 30):
        L.append(row(mt, split))
    L += [""]

# verdict: compare 30 (and 25) to 20 baseline on the full run + splits.
def d(label):
    return grab(label)[0]
b, m25, m30 = d("full_20"), d("full_25"), d("full_30")
def verdict(cand, name):
    if any(cand.get(k) is None or b.get(k) is None for k in ("eq","dd","pf")):
        return f"- **{name}: ⚠️ crash/no-data**"
    up = cand["eq"] > b["eq"]; dd_ok = cand["dd"] >= b["dd"] - 0.10; pf_ok = cand["pf"] > 1
    tag = "🟢 candidate" if (up and dd_ok and pf_ok) else "🔴 no"
    return (f"- **{name}: {tag}** — equity {cand['eq']:,.0f} vs {b['eq']:,.0f}, "
            f"MaxDD {cand['dd']:.2f} vs {b['dd']:.2f}, PF {cand['pf']:.2f}")
L += ["## Verdict (full-4yr vs 20-pip baseline)", "",
      verdict(m25, "25 pips"), verdict(m30, "30 pips"), "",
      "_Claude reviews IS/OOS magnitudes before shipping — a full-run gain that "
      "regresses either split is not shipped (the not-curve-fit rule)._"]
open("data/mintarget_validation.md","w").write("\n".join(L)+"\n")
print("\n".join(L))
PY

git add -f data/mintarget_validation.md 2>/dev/null
git commit -q -m "Min-target validation results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/mintarget_validation.md"
else
  echo "(push failed — copy the comparison above to Claude)"
fi

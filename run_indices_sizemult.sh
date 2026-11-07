#!/usr/bin/env bash
# US index gate — INDEX_SIZE_MULT sweep on the FULL 4yr path (the one that breached).
#   bash run_indices_sizemult.sh
# The main validation showed indices PASS both IS/OOS (MaxDD unchanged, PF held)
# but the FULL continuous run's MaxDD hit -15.53% (a compounding-path effect — see
# CLAUDE.md P8/P9). Downsizing the index book pulls that full-run MaxDD back under
# the -15% breaker while keeping the edge. This sweeps a few multipliers in ONE run
# so we can pick the ship point (target: full-4yr MaxDD <= ~-13%, equity still up,
# PF held). Assumes data is already prepared (run run_indices_validation.sh first).
cd "$(dirname "$0")" || exit 1
export INDEX_PAIRS="SPXUSD NSXUSD"
export INDEX_REF="${INDEX_REF:-US30}"
MULTS=(1.0 0.75 0.5 0.35)

echo "=== baseline (indices off), full 4yr ==="
INDICES_ENABLED=0 python run_backtest_histdata.py --years 2022 2023 2024 2025 \
  > /tmp/idxm_base.txt 2>&1

for m in "${MULTS[@]}"; do
  echo "=== indices ON, INDEX_SIZE_MULT=$m, full 4yr ==="
  INDICES_ENABLED=1 INDEX_SIZE_MULT="$m" \
    python run_backtest_histdata.py --years 2022 2023 2024 2025 \
    > "/tmp/idxm_$m.txt" 2>&1
done

HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" MULTS="${MULTS[*]}" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
mults = os.environ.get("MULTS", "").split()
def grab(path):
    if not os.path.exists(path): return {}
    txt = open(path).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt); return cast(m.group(1)) if m else None
    return {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
            "dd": g("max_drawdown_pct"), "eq": g("ending_equity_ZAR")}
b = grab("/tmp/idxm_base.txt")
L = ["# US index gate — INDEX_SIZE_MULT sweep (full 4yr)", "",
     f"_run commit: `{HEAD}`_. Baseline = indices off. Goal: smallest downsize whose "
     "full-4yr MaxDD is back under the -15% breaker (ideally ~baseline) with equity "
     "still up and PF held. IS/OOS already pass (see indices_validation.md).", "",
     "| config | trades | WR% | PF | MaxDD% | equity ZAR |", "|---|---|---|---|---|---|"]
def row(lbl, d):
    f = lambda k, s="": ("—" if d.get(k) is None else
                         (f"{d[k]:,.0f}" if k=="eq" else f"{d[k]:.2f}")+s)
    return (f"| {lbl} | {f('trades')} | {f('wr')} | {f('pf')} | {f('dd')} | {f('eq')} |")
L.append(row("baseline (off)", b))
best = None
for m in mults:
    d = grab(f"/tmp/idxm_{m}.txt")
    L.append(row(f"indices x{m}", d))
    # ship candidate: MaxDD not worse than baseline by >0.2pp AND equity up AND PF>1
    if d.get("dd") is not None and b.get("dd") is not None and d.get("eq") and b.get("eq"):
        if d["dd"] >= b["dd"] - 0.20 and d["eq"] > b["eq"] and d["pf"] > 1.0:
            if best is None or d["eq"] > best[1]:
                best = (m, d["eq"], d["dd"], d["pf"])
L += [""]
if best:
    L += [f"**Ship candidate: INDEX_SIZE_MULT={best[0]}** — full-4yr MaxDD {best[2]:.2f}% "
          f"(baseline {b.get('dd')}%), PF {best[3]:.2f}, equity {best[1]:,.0f}. "
          "Confirm IS/OOS at this mult before flipping INDICES_ENABLED=1."]
else:
    L += ["**No multiplier held full-4yr MaxDD at baseline** — try smaller (0.25) or "
          "keep indices off. The edge is real (IS/OOS pass) but the compounding path "
          "adds drawdown even downsized."]
open("data/indices_sizemult.md","w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/indices_sizemult.md 2>/dev/null
git commit -q -m "Index size-mult sweep results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
git push -u origin HEAD 2>/dev/null && echo "RESULTS PUSHED — Claude reads data/indices_sizemult.md" \
  || echo "(push failed — copy the table above to Claude)"

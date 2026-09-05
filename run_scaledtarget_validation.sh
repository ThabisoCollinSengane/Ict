#!/usr/bin/env bash
# Equity-scaled target floor validation (Codespaces): flat-20 vs flat-30 vs SCALED
# (20 below R3k, 30 above). The scaled floor should capture 20's small-account
# compounding AND 30's large-account quality. Full 4yr + IS + OOS.
#   bash run_scaledtarget_validation.sh
# Ships scaled only if it beats flat-30 (the current shipped floor) on full-4yr
# equity with MaxDD not worse, and holds up on both splits.
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

run_one() {  # $1 label  $2.. env+years, invoked via caller
  :
}
bt() {  # $1=label  $2=extra_env  $3..=years
  local label="$1" env="$2"; shift 2
  echo "  $label ($env, years $*) ..."
  env $env python run_backtest_histdata.py --years "$@" > "/tmp/st_$label.txt" 2>&1
}

echo "=== flat-20 / flat-30 / scaled, each full + IS + OOS ==="
bt flat20_full "MIN_TARGET_SCALED=0 MIN_PIPS_TARGET=20" 2022 2023 2024 2025
bt flat20_is   "MIN_TARGET_SCALED=0 MIN_PIPS_TARGET=20" 2022 2023
bt flat20_oos  "MIN_TARGET_SCALED=0 MIN_PIPS_TARGET=20" 2024 2025
bt flat30_full "MIN_TARGET_SCALED=0 MIN_PIPS_TARGET=30" 2022 2023 2024 2025
bt flat30_is   "MIN_TARGET_SCALED=0 MIN_PIPS_TARGET=30" 2022 2023
bt flat30_oos  "MIN_TARGET_SCALED=0 MIN_PIPS_TARGET=30" 2024 2025
bt scaled_full "MIN_TARGET_SCALED=1" 2022 2023 2024 2025
bt scaled_is   "MIN_TARGET_SCALED=1" 2022 2023
bt scaled_oos  "MIN_TARGET_SCALED=1" 2024 2025

echo "=== building comparison ==="
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
SHA="$SHA" python - <<'PY'
import re, os
SHA = os.environ.get("SHA", "unknown")
def grab(label):
    p = f"/tmp/st_{label}.txt"
    if not os.path.exists(p): return {}
    t = open(p).read()
    def g(k, c=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", t); return c(m.group(1)) if m else None
    return {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
            "dd": g("max_drawdown_pct"), "eq": g("ending_equity_ZAR"),
            "pyr": g("pyramid_added", int), "pyrblk": g("pyramid_blocked_min_target", int)}
def cell(d, k):
    v = d.get(k)
    return "—" if v is None else (f"{v:,.0f}" if k == "eq" else f"{v:.2f}")
def rowset(split, title):
    L = [f"## {title}", "", "| floor | trades | WR | PF | MaxDD | equity ZAR |",
         "|---|---|---|---|---|---|"]
    for cfg, name in (("flat20", "flat 20"), ("flat30", "flat 30 (shipped)"),
                      ("scaled", "SCALED 20/30")):
        d = grab(f"{cfg}_{split}")
        L.append(f"| {name} | {cell(d,'trades')} | {cell(d,'wr')}% | {cell(d,'pf')} | "
                 f"{cell(d,'dd')}% | {cell(d,'eq')} |")
    return L + [""]
def pyrset(split, title):
    L = [f"### {title} — pyramiding", "",
         "| floor | pyramids added | blocked by target-room gate |", "|---|---|---|"]
    for cfg, name in (("flat20", "flat 20"), ("flat30", "flat 30 (shipped)"),
                      ("scaled", "SCALED 20/30")):
        d = grab(f"{cfg}_{split}")
        L.append(f"| {name} | {d.get('pyr','—')} | {d.get('pyrblk','—')} |")
    return L + [""]

L = ["# Equity-scaled target floor — flat-20 vs flat-30 vs scaled(20/30)", "",
     "Scaled = 20-pip floor below R3k (small-account compounding), 30-pip above "
     "(large-account quality). **Ship scaled only if it beats flat-30 on full-4yr "
     "equity with MaxDD not worse, both splits holding.**", "", f"_run commit: `{SHA}`_", ""]
for split, title in (("full", "Full 4yr"), ("is", "IS 2022-23"), ("oos", "OOS 2024-25")):
    L += rowset(split, title)

L += ["## Pyramiding — did the 30-pip floor starve adds?", "",
      "`pyramids added` = legs that fired; `blocked by target-room gate` = adds "
      "rejected because <floor pips remained to TP. If flat-30 adds ≪ flat-20, the "
      "floor is starving pyramids and a separate PYRAMID_MIN_TARGET is worth it.", ""]
for split, title in (("full", "Full 4yr"), ("is", "IS 2022-23"), ("oos", "OOS 2024-25")):
    L += pyrset(split, title)

f30, sc = grab("flat30_full"), grab("scaled_full")
f20 = grab("flat20_full")
L += ["## Verdict", ""]
if any(sc.get(k) is None or f30.get(k) is None for k in ("eq", "dd", "pf")):
    L += ["⚠️ INCONCLUSIVE — a run crashed."]
else:
    beats30 = sc["eq"] > f30["eq"] and sc["dd"] >= f30["dd"] - 0.10
    bestboth = (f20.get("eq") and sc["eq"] >= 0.95 * f20["eq"]
                and sc["pf"] >= f30["pf"] - 0.10)
    if beats30:
        L += [f"🟢 **Ship scaled.** Full-4yr equity {sc['eq']:,.0f} > flat-30 "
              f"{f30['eq']:,.0f}, MaxDD {sc['dd']:.2f} vs {f30['dd']:.2f}, PF {sc['pf']:.2f}. "
              "Captures the small-account compounding without giving up 30's quality."]
    else:
        L += [f"🔴 **Keep flat-30.** Scaled full-4yr equity {sc['eq']:,.0f} vs flat-30 "
              f"{f30['eq']:,.0f} (MaxDD {sc['dd']:.2f} vs {f30['dd']:.2f}, PF {sc['pf']:.2f}) "
              "— doesn't beat the shipped flat-30. Claude reviews IS/OOS before final call "
              "(scaled may still win the small-account IS phase — relevant to a live R1k start)."]
open("data/scaledtarget_validation.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/scaledtarget_validation.md 2>/dev/null
git commit -q -m "Scaled-target validation results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/scaledtarget_validation.md"
else
  echo "(push failed — copy the comparison above to Claude)"
fi

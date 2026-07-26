#!/usr/bin/env bash
# P40 conditional-volume modulator — full validation (Codespaces).
#   bash run_p40_validation.sh
# Runs the backtest baseline (modulator OFF) vs modulator ON, on the full
# continuous path AND the IS/OOS splits, and writes a side-by-side comparison.
# The modulator only fires where tick data exists (EU/GU 2022+2024); elsewhere
# neutral. Ships only if it improves PF/equity while holding MaxDD in BOTH splits.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring M1 data + tick aggregation ==="
if ! ls data/histdata/EURUSD_2022.csv >/dev/null 2>&1; then
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  [ -z "$Z" ] && { echo "ERROR: M1 download failed"; exit 1; }
  python scripts/prepare_histdata.py "$(dirname "$Z")" || exit 1
fi
if ! ls data/p39_agg/*_m5.csv >/dev/null 2>&1; then
  if ls /tmp/ticks/*.zip >/dev/null 2>&1; then
    python scripts/p39_volume_analysis.py aggregate /tmp/ticks || exit 1
  else
    echo "ERROR: no tick aggregation (data/p39_agg). Run run_p39_only.sh first."; exit 1
  fi
fi

run_one() {  # $1 = flag (0/1)  $2 = label  $3 = years
  echo "  running $2 (USE_CONDITIONAL_VOLUME=$1, years $3) ..."
  USE_CONDITIONAL_VOLUME="$1" python run_backtest_histdata.py --years $3 \
    > "/tmp/p40_$2.txt" 2>&1
}

echo "=== running 6 backtests (baseline vs modulator × full/IS/OOS) — ~40 min ==="
run_one 0 full_base "2022 2023 2024"
run_one 1 full_mod  "2022 2023 2024"
run_one 0 is_base   "2022 2023"
run_one 1 is_mod    "2022 2023"
run_one 0 oos_base  "2024"
run_one 1 oos_mod   "2024"

echo "=== building comparison ==="
python - <<'PY'
import re, os
def grab(label):
    p = f"/tmp/p40_{label}.txt"
    if not os.path.exists(p):
        return {}
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    vm = re.search(r"vol_mod_applied\s+(\d+)", txt)
    return {"trades": g("trades", int), "wr": g("win_rate_pct"),
            "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
            "eq": g("ending_equity_ZAR"), "vmod": int(vm.group(1)) if vm else 0}
rows = []
for split, base, mod in (("Full 2022-24", "full_base", "full_mod"),
                          ("IS 2022-23", "is_base", "is_mod"),
                          ("OOS 2024", "oos_base", "oos_mod")):
    b, m = grab(base), grab(mod)
    rows.append((split, b, m))
L = ["# P40 conditional-volume modulator — validation", "",
     "Baseline (modulator OFF) vs modulator ON. Modulator fires only on EU/GU "
     "2022+2024 FVG/OB entries with high tick volume (`vmod` = # trades sized). "
     "**Ships only if PF and equity improve while MaxDD holds — in BOTH IS and OOS.**",
     ""]
def fmt(d, k, suf=""):
    v = d.get(k)
    if v is None: return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf
for split, b, m in rows:
    L += [f"## {split}", "",
          "| metric | baseline | modulator | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades","trades",""),("wr","win rate","%"),
                        ("pf","profit factor",""),("dd","max drawdown","%"),
                        ("eq","ending equity ZAR","")):
        bv, mv = b.get(k), m.get(k)
        d = (f"{mv-bv:+.2f}" if (bv is not None and mv is not None and k!='eq')
             else (f"{mv-bv:+,.0f}" if (bv is not None and mv is not None) else "—"))
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_trades sized by modulator: {m.get('vmod',0)}_", ""]
L += ["## Verdict", "",
      "GREEN (ship) = PF and equity up, MaxDD not worse, in BOTH IS and OOS. "
      "Otherwise it stays OFF (USE_CONDITIONAL_VOLUME=0). Same bar as every "
      "P-feature."]
open("data/p40_validation.md","w").write("\n".join(L)+"\n")
print("\n".join(L))
PY

git add -f data/p40_validation.md 2>/dev/null
if git commit -q -m "P40 validation results (auto)" 2>/dev/null && git push -q 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/p40_validation.md"
else
  echo "(auto-push skipped — copy the comparison above to Claude)"
fi

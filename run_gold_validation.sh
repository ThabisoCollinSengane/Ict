#!/usr/bin/env bash
# Gold (XAUUSD) gate — validation (Codespaces / anywhere egress is open).
#   bash run_gold_validation.sh
# Baseline (GOLD_ENABLED=0, the shipped 3-pair engine) vs gold (GOLD_ENABLED=1,
# adds XAUUSD via the DXY+silver+AUDUSD gate) on the full 4yr + IS/OOS splits.
#
# Data: core FX (EURUSD/GBPUSD/EURGBP/UDXUSD) come from the prepared-M1 Drive
# folder (same as every other validation); the GOLD COMPLEX (XAUUSD/XAGUSD/AUDUSD)
# is self-served from HistData via scripts/fetch_histdata.py.
#
# READ THIS on the numbers: XAUUSD pip/contract sizing is PROVISIONAL (config
# GOLD_PIP=1.0), so absolute ZAR equity is NOT yet calibrated. PF / WR / MaxDD are
# scale-invariant, so THOSE are the gate's real edge signal. Ship gold ON only if
# adding it does not worsen the book's MaxDD and gold's own trades are PF-positive
# in BOTH splits.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"
YEARS=(2022 2023 2024 2025)

echo "=== 1. core FX M1 (Drive) ==="
missing=0
for y in "${YEARS[@]}"; do for p in EURUSD GBPUSD UDXUSD; do
  ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y MISSING"; missing=1; }
done; done
if [ "$missing" = 1 ] || [ "${REFRESH_M1:-0}" = 1 ]; then
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  [ -z "$Z" ] && { echo "ERROR: core M1 download failed"; exit 1; }
  python scripts/prepare_histdata.py "$(dirname "$Z")" || exit 1
fi

echo "=== 2. gold complex (HistData: XAUUSD, XAGUSD, AUDUSD) ==="
gmissing=0
for y in "${YEARS[@]}"; do for p in XAUUSD XAGUSD AUDUSD; do
  ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y MISSING"; gmissing=1; }
done; done
if [ "$gmissing" = 1 ] || [ "${REFRESH_GOLD:-0}" = 1 ]; then
  echo "  fetching gold complex from HistData…"
  rm -rf /tmp/golddl && mkdir -p /tmp/golddl
  python scripts/fetch_histdata.py --years "${YEARS[@]}" \
    --pairs XAUUSD XAGUSD AUDUSD --dest /tmp/golddl 2>&1 | tee /tmp/goldfetch.log
  if ! ls /tmp/golddl/HISTDATA_*.zip >/dev/null 2>&1; then
    echo "  ⚠️ gold fetch produced no zips — HistData may lack XAU/XAG coverage."
    echo "     See /tmp/goldfetch.log; you can also drop the CSVs into data/histdata/ manually."
  fi
  python scripts/prepare_histdata.py /tmp/golddl || true
fi
echo "  coverage:"
for y in "${YEARS[@]}"; do for p in XAUUSD XAGUSD AUDUSD; do
  f="data/histdata/${p}_$y.csv"
  if [ -f "$f" ]; then printf "    %s %s: %s rows\n" "$p" "$y" "$(wc -l < "$f")";
  else printf "    %s %s: MISSING\n" "$p" "$y"; fi
done; done

run_one() {  # $1=enabled $2=label $3..=years
  local en="$1" label="$2"; shift 2
  echo "  $label (GOLD_ENABLED=$en, years $*) ..."
  GOLD_ENABLED="$en" python run_backtest_histdata.py --years "$@" \
    > "/tmp/gold_$label.txt" 2>&1
}

echo "=== 3. 6 runs: baseline vs gold x {full, IS, OOS} ==="
run_one 0 full_base "${YEARS[@]}"
run_one 1 full_gold "${YEARS[@]}"
run_one 0 is_base   2022 2023
run_one 1 is_gold   2022 2023
run_one 0 oos_base  2024 2025
run_one 1 oos_gold  2024 2025

echo "=== 4. comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
def grab(label):
    p = f"/tmp/gold_{label}.txt"
    if not os.path.exists(p): return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt); return cast(m.group(1)) if m else None
    # gold trade count: count G-long/G-short scenario rows if the report prints them
    gld = len(re.findall(r"\bG-(?:long|short)\b", txt))
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
         "dd": g("max_drawdown_pct"), "eq": g("ending_equity_ZAR"), "gold": gld}
    return d, txt

L = ["# Gold (XAUUSD) gate — validation", "",
     "Baseline (`GOLD_ENABLED=0`) vs gold (`GOLD_ENABLED=1`, DXY+silver+AUDUSD "
     "gate). **XAUUSD sizing is provisional (GOLD_PIP=1.0) — absolute equity is "
     "NOT calibrated; PF/WR/MaxDD are scale-invariant and ARE the edge signal.** "
     "Ship gold ON only if the book's MaxDD is not worse and gold trades are "
     "PF-positive in both splits.", "", f"_run commit: `{HEAD}`_", ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    return "—" if v is None else ((f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf)

res = {}
for split, base, gld in (("Full 4yr","full_base","full_gold"),
                         ("IS 2022-23","is_base","is_gold"),
                         ("OOS 2024-25","oos_base","oos_gold")):
    (b, _), (m, mt) = grab(base), grab(gld)
    res[split] = (b, m)
    L += [f"## {split}", "", "| metric | baseline | +gold | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades","trades",""),("wr","win rate","%"),
                        ("pf","profit factor",""),("dd","max drawdown","%"),
                        ("eq","ending equity ZAR","")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None: d = "—"
        elif k == "eq":              d = f"{mv-bv:+,.0f}"
        else:                        d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_gold trades taken: {m.get('gold',0)}_", ""]

# Verdict: MaxDD not worse (dd is negative; not worse = gold dd >= base dd - tol),
# full-4yr book PF not degraded, and gold actually traded.
def ok(split, dd_tol):
    b, m = res.get(split, ({}, {}))
    if any(m.get(k) is None or b.get(k) is None for k in ("pf","dd")):
        return None, "run crashed"
    fails = []
    if m["dd"] < b["dd"] - dd_tol: fails.append(f"MaxDD {m['dd']:.2f} worse than {b['dd']:.2f}")
    if m["pf"] <= 1.0:             fails.append(f"book PF {m['pf']:.2f}≤1.0")
    if m.get("gold", 0) == 0:      fails.append("gold took 0 trades (data/gate issue)")
    return (not fails), ("; ".join(fails) if fails else "ok")
checks = {"Full 4yr": ok("Full 4yr", 0.10), "IS 2022-23": ok("IS 2022-23", 1.0),
          "OOS 2024-25": ok("OOS 2024-25", 1.0)}
crashed = any(v is None for v,_ in checks.values())
green = (not crashed) and all(v for v,_ in checks.values())
head = ("⚠️ INCONCLUSIVE — a run crashed / gold took no trades." if crashed else
        "🟢 GREEN — gold added without worsening the book (review gold's own PF/WR by split)."
        if green else "🔴 RED — do NOT ship gold ON (GOLD_ENABLED stays 0).")
L += ["## Verdict", "", f"**{head}**", ""]
for s,(v,why) in checks.items():
    L.append(f"- **{s}: {'🟢 pass' if v else ('⚠️ crash' if v is None else '🔴 fail')}** — {why}")
L += ["", "_Reminder: calibrate GOLD_PIP / gold contract before trusting absolute "
      "equity; then re-run. Also inspect gold-only WR/PF (report scenario table "
      "G-long/G-short) for the not-curve-fit IS/OOS ballpark check._"]
open("data/gold_validation.md","w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/gold_validation.md 2>/dev/null
git commit -q -m "Gold gate validation results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
git push -u origin HEAD 2>/dev/null && echo "RESULTS PUSHED — Claude reads data/gold_validation.md" \
  || echo "(push failed — copy the comparison above to Claude)"

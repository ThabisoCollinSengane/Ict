#!/usr/bin/env bash
# P40 conditional-volume modulator — focused TICK-VOLUME validation (Codespaces).
#   bash run_p40_validation.sh
# This is a tick-volume test, so it runs ONLY where tick data exists: EURUSD +
# GBPUSD, and 2022 and 2024 as TWO SEPARATE tests (no NZD, no 2023 — they have
# no ticks and would be identical in both arms). For each year: baseline
# (modulator OFF) vs modulator ON. Ships only if PF + equity improve while MaxDD
# holds in BOTH 2022 and 2024.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"
export TRADE_PAIRS="GBPUSD EURUSD"   # tick-covered pairs only

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

run_one() {  # $1 = flag (0/1)  $2 = label  $3 = year
  echo "  $2 (USE_CONDITIONAL_VOLUME=$1, EU+GU $3) ..."
  USE_CONDITIONAL_VOLUME="$1" python run_backtest_histdata.py --years "$3" \
    > "/tmp/p40_$2.txt" 2>&1
}

echo "=== 2 tick-volume tests (2022 & 2024), baseline vs modulator, EU+GU only ==="
run_one 0 y2022_base 2022
run_one 1 y2022_mod  2022
run_one 0 y2024_base 2024
run_one 1 y2024_mod  2024

echo "=== building comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
def grab(label):
    p = f"/tmp/p40_{label}.txt"
    if not os.path.exists(p):
        return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt)
        return cast(m.group(1)) if m else None
    vm = re.search(r"vol_mod_applied\s+(\d+)", txt)
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"),
         "pf": g("profit_factor"), "dd": g("max_drawdown_pct"),
         "eq": g("ending_equity_ZAR"), "vmod": int(vm.group(1)) if vm else 0}
    return d, txt

L = ["# P40 conditional-volume modulator — tick-volume validation", "",
     "**EURUSD + GBPUSD only; 2022 and 2024 as two separate tests** (the tick-"
     "covered set). Baseline (modulator OFF) vs modulator ON. `vmod` = trades the "
     "modulator actually sized. **Ships only if PF + equity improve while MaxDD "
     "holds in BOTH years.**", "",
     f"_run commit: `{HEAD}`_", ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    if v is None: return "—"
    return (f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf

crash_logs = []
per_year = {}   # yr -> (pass_bool_or_None, reason)
for yr, base, mod in (("2022", "y2022_base", "y2022_mod"),
                      ("2024", "y2024_base", "y2024_mod")):
    (b, bt), (m, mt) = grab(base), grab(mod)
    L += [f"## {yr}", "",
          "| metric | baseline | modulator | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades", "trades", ""), ("wr", "win rate", "%"),
                        ("pf", "profit factor", ""), ("dd", "max drawdown", "%"),
                        ("eq", "ending equity ZAR", "")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None:
            d = "—"
        elif k == "eq":
            d = f"{mv-bv:+,.0f}"
        else:
            d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_trades sized by modulator: {m.get('vmod',0)}_", ""]
    # Surface any run that produced NO summary (a crash) so it can't hide again.
    for tag, dd, tt in (("baseline", b, bt), ("modulator", m, mt)):
        if dd.get("pf") is None:
            tail = "\n".join(tt.splitlines()[-30:])
            crash_logs.append(f"### {yr} {tag} — NO SUMMARY (crash?)\n\n"
                              f"```\n{tail}\n```\n")
    # Per-year pass = PF up AND equity up AND MaxDD not worse. dd is negative
    # (e.g. -11.6) so "not worse" means modulator dd >= baseline dd.
    if any(b.get(k) is None or m.get(k) is None for k in ("pf", "eq", "dd")):
        per_year[yr] = (None, "run crashed — no summary")
    else:
        fails = []
        if m["pf"] <= b["pf"]:  fails.append(f"PF {m['pf']:.2f}≤{b['pf']:.2f}")
        if m["eq"] <= b["eq"]:  fails.append(f"equity {m['eq']:,.0f}≤{b['eq']:,.0f}")
        if m["dd"] <  b["dd"]:  fails.append(f"MaxDD {m['dd']:.2f}<{b['dd']:.2f} (worse)")
        per_year[yr] = (not fails, "; ".join(fails) if fails else "PF+equity up, MaxDD held")

# Computed verdict — an explicit RED/GREEN, not just the definition.
crashed = any(v is None for v, _ in per_year.values())
green = (not crashed) and all(v for v, _ in per_year.values())
if crashed:
    head = "⚠️ INCONCLUSIVE — a run crashed (see diagnostics below)."
elif green:
    head = "🟢 GREEN — ship. PF+equity up and MaxDD held in BOTH years."
else:
    head = "🔴 RED — do NOT ship. Stays OFF (USE_CONDITIONAL_VOLUME=0)."
L += ["## Verdict", "", f"**{head}**", ""]
for yr, (v, why) in per_year.items():
    mark = "🟢 pass" if v else ("⚠️ crash" if v is None else "🔴 fail")
    L.append(f"- **{yr}: {mark}** — {why}")
L += ["", "_Rule: GREEN only if PF **and** ending equity improve while MaxDD is "
      "not worse, in **both** 2022 and 2024. This line is the computed result, "
      "not a legend._"]
if crash_logs:
    L += ["", "## Crash diagnostics (auto-captured)", ""] + crash_logs
open("data/p40_validation.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/p40_validation.md 2>/dev/null
git commit -q -m "P40 tick-volume validation results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/p40_validation.md"
else
  echo "(push failed — copy the comparison above to Claude)"
fi

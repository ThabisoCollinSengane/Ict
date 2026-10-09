#!/usr/bin/env bash
# SMT detector A/B — is the reactive fractal SMT better than the block-half proxy,
# and does requiring SMT confirmation improve index trade quality?
#   bash run_smt_validation.sh
#
# Runs indices ON (with the frequency levers) and compares three arms on IS + OOS:
#   1. no SMT gate            (INDEX_SMT_REQUIRED=0)              — reference
#   2. proxy SMT gate         (SMT_MODE=proxy,   REQUIRED=1)
#   3. fractal SMT gate       (SMT_MODE=fractal, REQUIRED=1)      — reactive
# Reports trades / WR / PF / MaxDD per arm. SMT ships (as a gate) only if it lifts
# WR/PF without gutting the trade count; fractal wins if it beats proxy.
#
# 2yr splits keep it light so it can run alongside the main validation — but if the
# Codespace is tight on memory, run this AFTER the main run finishes.
cd "$(dirname "$0")" || exit 1

export INDICES_ENABLED=1
export INDEX_PAIRS="SPXUSD NSXUSD"
export INDEX_REF="${INDEX_REF:-US30}"
export INDEX_AMD_MAX_RANGE_PCT="${INDEX_AMD_MAX_RANGE_PCT:-0.8}"
export INDEX_MAX_TRADES_PER_DAY="${INDEX_MAX_TRADES_PER_DAY:-3}"
export INDEX_MIN_IMSCORE="${INDEX_MIN_IMSCORE:-0.75}"
# withdrawals OFF here — we're measuring SMT quality (PF/WR/MaxDD are scale-invariant)

echo "=== index data coverage (need SPXUSD/NSXUSD; US30 optional) ==="
for y in 2022 2023 2024 2025; do for p in SPXUSD NSXUSD US30; do
  f="data/histdata/${p}_$y.csv"
  [ -f "$f" ] && printf "  %s %s: %s rows\n" "$p" "$y" "$(wc -l < "$f")" || printf "  %s %s: MISSING\n" "$p" "$y"
done; done
if ! ls data/histdata/SPXUSD_2024.csv >/dev/null 2>&1; then
  echo "ERROR: index data missing — run run_indices_validation.sh first (it fetches it)."; exit 1
fi

run() {  # $1=label  $2=required  $3=mode  $4..=years
  local label="$1" req="$2" mode="$3"; shift 3
  echo "  $label (REQUIRED=$req MODE=$mode, years $*) ..."
  INDEX_SMT_REQUIRED="$req" SMT_MODE="$mode" \
    python run_backtest_histdata.py --years "$@" > "/tmp/smt_$label.txt" 2>&1
}

echo "=== 6 runs: {no-gate, proxy, fractal} x {IS, OOS} ==="
run is_none    0 proxy   2022 2023
run is_proxy   1 proxy   2022 2023
run is_fractal 1 fractal 2022 2023
run oos_none    0 proxy   2024 2025
run oos_proxy   1 proxy   2024 2025
run oos_fractal 1 fractal 2024 2025

echo "=== comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
def grab(label):
    p = f"/tmp/smt_{label}.txt"
    if not os.path.exists(p): return {}, ""
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt); return cast(m.group(1)) if m else None
    return {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
            "dd": g("max_drawdown_pct")}, txt
def fmt(d,k,s=""):
    v=d.get(k); return "—" if v is None else (f"{v:.2f}" if k!="trades" else f"{v}")+s

L=["# SMT detector A/B — proxy vs reactive fractal (as an index entry gate)","",
   "Indices ON + frequency levers. Three arms: no SMT gate / proxy-SMT-required / "
   "fractal-SMT-required. **A gate is worth it if it lifts WR/PF without gutting "
   "trades; fractal wins if it beats proxy.**","",f"_run commit: `{HEAD}`_",""]
crash=[]
for split, arms in (("IS 2022-23", ("is_none","is_proxy","is_fractal")),
                    ("OOS 2024-25", ("oos_none","oos_proxy","oos_fractal"))):
    L += [f"## {split}","","| arm | trades | WR% | PF | MaxDD% |","|---|---|---|---|---|"]
    for name,label in (("no SMT gate",arms[0]),("proxy SMT gate",arms[1]),("fractal SMT gate",arms[2])):
        d,txt=grab(label)
        L.append(f"| {name} | {fmt(d,'trades')} | {fmt(d,'wr')} | {fmt(d,'pf')} | {fmt(d,'dd')} |")
        if d.get("pf") is None:
            tail="\n".join(txt.splitlines()[-20:]) if txt else "(no output)"
            crash.append(f"### {label} — NO RESULTS\n\n```\n{tail}\n```\n")
    L.append("")
L += ["## How to read it","",
      "- proxy/fractal vs **no-gate**: does requiring SMT raise WR/PF? By how many trades does it cost?",
      "- **fractal vs proxy**: higher WR/PF at similar trade count = the reactive detector is the better filter.",
      "- Same-ballpark IS *and* OOS is the not-curve-fit check before shipping SMT as a gate."]
if crash: L += ["","## Diagnostics",""]+crash
open("data/smt_validation.md","w").write("\n".join(L)+"\n")
print("\n".join(L))
PY

git add -f data/smt_validation.md 2>/dev/null
git commit -q -m "SMT detector A/B results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
git push -u origin HEAD 2>/dev/null && echo "RESULTS PUSHED — Claude reads data/smt_validation.md" \
  || echo "(push failed — copy the table above to Claude)"

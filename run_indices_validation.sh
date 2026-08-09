#!/usr/bin/env bash
# US index gate — validation (Codespaces / anywhere egress is open).
#   bash run_indices_validation.sh
# Baseline (INDICES_ENABLED=0, the shipped 3-pair FX engine) vs indices
# (INDICES_ENABLED=1, adds US500+US100 via the DXY+sibling+US30 SMT-breadth gate)
# on the full 4yr + IS/OOS splits.
#
# Data: core FX (Drive, as every other validation) + US indices from HistData.
# HistData's ASCII index codes are SPXUSD (=US500) and NSXUSD (=US100); Dow/US30
# is NOT in HistData free ASCII, so US30 is used only if you supply US30 data
# (the gate degrades gracefully to DXY+sibling breadth without it). We therefore
# run the backtest with INDEX_PAIRS="SPXUSD NSXUSD".
#
# SIZING IS PROVISIONAL (INDEX_PIP/INDEX_LOT_UNITS): absolute ZAR equity is NOT
# calibrated. PF / WR / MaxDD are scale-invariant and ARE the edge signal. Ship
# indices ON only if the book's MaxDD is not worse and index trades are PF-positive
# in BOTH splits.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"
YEARS=(2022 2023 2024 2025)
IDX_SYMS=(SPXUSD NSXUSD)       # HistData codes for US500 / US100
export INDEX_PAIRS="SPXUSD NSXUSD"
export INDEX_REF="${INDEX_REF:-US30}"   # used only if US30 data is present

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

echo "=== 2. US indices (HistData: ${IDX_SYMS[*]}) ==="
imissing=0
for y in "${YEARS[@]}"; do for p in "${IDX_SYMS[@]}"; do
  ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y MISSING"; imissing=1; }
done; done
if [ "$imissing" = 1 ] || [ "${REFRESH_IDX:-0}" = 1 ]; then
  echo "  fetching indices from HistData…"
  rm -rf /tmp/idxdl && mkdir -p /tmp/idxdl
  python scripts/fetch_histdata.py --years "${YEARS[@]}" \
    --pairs "${IDX_SYMS[@]}" --dest /tmp/idxdl 2>&1 | tee /tmp/idxfetch.log
  if ! ls /tmp/idxdl/HISTDATA_*.zip >/dev/null 2>&1; then
    echo "  ⚠️ index fetch produced no zips — see /tmp/idxfetch.log. You can also"
    echo "     drop SPXUSD_YYYY.csv / NSXUSD_YYYY.csv into data/histdata/ manually."
  fi
  python scripts/prepare_histdata.py /tmp/idxdl || true
fi
echo "  coverage:"
for y in "${YEARS[@]}"; do for p in "${IDX_SYMS[@]}" "$INDEX_REF"; do
  f="data/histdata/${p}_$y.csv"
  if [ -f "$f" ]; then printf "    %s %s: %s rows\n" "$p" "$y" "$(wc -l < "$f")";
  else printf "    %s %s: MISSING\n" "$p" "$y"; fi
done; done

run_one() {  # $1=enabled $2=label $3..=years
  local en="$1" label="$2"; shift 2
  echo "  $label (INDICES_ENABLED=$en, years $*) ..."
  INDICES_ENABLED="$en" python run_backtest_histdata.py --years "$@" \
    > "/tmp/idx_$label.txt" 2>&1
}

echo "=== 3. 6 runs: baseline vs indices x {full, IS, OOS} ==="
run_one 0 full_base "${YEARS[@]}"
run_one 1 full_idx  "${YEARS[@]}"
run_one 0 is_base   2022 2023
run_one 1 is_idx    2022 2023
run_one 0 oos_base  2024 2025
run_one 1 oos_idx   2024 2025

echo "=== 4. comparison ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
def grab(label):
    p = f"/tmp/idx_{label}.txt"
    if not os.path.exists(p): return {}, "(no run output)"
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt); return cast(m.group(1)) if m else None
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
         "dd": g("max_drawdown_pct"), "eq": g("ending_equity_ZAR")}
    return d, txt

L = ["# US index gate — validation", "",
     "Baseline (`INDICES_ENABLED=0`) vs indices (`INDICES_ENABLED=1`, US500+US100 "
     "via DXY+sibling+US30 SMT-breadth gate). **Sizing is provisional — absolute "
     "equity is NOT calibrated; PF/WR/MaxDD are scale-invariant and ARE the edge "
     "signal.** Ship indices ON only if the book's MaxDD is not worse and index "
     "trades are PF-positive in both splits.", "", f"_run commit: `{HEAD}`_", ""]

def fmt(d, k, suf=""):
    v = d.get(k)
    return "—" if v is None else ((f"{v:,.0f}" if k == "eq" else f"{v:.2f}") + suf)

res = {}
for split, base, idx in (("Full 4yr","full_base","full_idx"),
                         ("IS 2022-23","is_base","is_idx"),
                         ("OOS 2024-25","oos_base","oos_idx")):
    (b, _), (m, mt) = grab(base), grab(idx)
    if b.get("trades") is not None and m.get("trades") is not None:
        m["idx"] = m["trades"] - b["trades"]
    else:
        m["idx"] = None
    res[split] = (b, m)
    L += [f"## {split}", "", "| metric | baseline | +indices | Δ |", "|---|---|---|---|"]
    for k, lbl, suf in (("trades","trades",""),("wr","win rate","%"),
                        ("pf","profit factor",""),("dd","max drawdown","%"),
                        ("eq","ending equity ZAR","")):
        bv, mv = b.get(k), m.get(k)
        if bv is None or mv is None: d = "—"
        elif k == "eq":              d = f"{mv-bv:+,.0f}"
        else:                        d = f"{mv-bv:+.2f}"
        L.append(f"| {lbl} | {fmt(b,k,suf)} | {fmt(m,k,suf)} | {d} |")
    L += ["", f"_index trades taken: {m.get('idx')}_", ""]

def ok(split, dd_tol):
    b, m = res.get(split, ({}, {}))
    if any(m.get(k) is None or b.get(k) is None for k in ("pf","dd")):
        return None, "run crashed"
    fails = []
    if not m.get("idx"):           fails.append("indices took 0 trades (data coverage/gate issue)")
    if m["dd"] < b["dd"] - dd_tol: fails.append(f"MaxDD {m['dd']:.2f} worse than {b['dd']:.2f}")
    if m["pf"] <= 1.0:             fails.append(f"book PF {m['pf']:.2f}≤1.0")
    return (not fails), ("; ".join(fails) if fails else "ok")
checks = {"Full 4yr": ok("Full 4yr", 0.10), "IS 2022-23": ok("IS 2022-23", 1.0),
          "OOS 2024-25": ok("OOS 2024-25", 1.0)}
crashed = any(v is None for v,_ in checks.values())
green = (not crashed) and all(v for v,_ in checks.values())
head = ("⚠️ INCONCLUSIVE — a run crashed / indices took no trades." if crashed else
        "🟢 GREEN — indices added without worsening the book (review index PF/WR by split)."
        if green else "🔴 RED — do NOT ship indices ON (INDICES_ENABLED stays 0).")
L += ["## Verdict", "", f"**{head}**", ""]
for s,(v,why) in checks.items():
    L.append(f"- **{s}: {'🟢 pass' if v else ('⚠️ crash' if v is None else '🔴 fail')}** — {why}")
L += ["", "_Reminder: calibrate INDEX_PIP / INDEX_LOT_UNITS before trusting absolute "
      "equity. If MaxDD breaches, tighten INDEX_MIN_IMSCORE=1.0 (all 3 agree) or set "
      "INDEX_SIZE_MULT<1 and re-run — same risk-fit path as gold._"]
open("data/indices_validation.md","w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/indices_validation.md 2>/dev/null
git commit -q -m "US index gate validation results (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
git push -u origin HEAD 2>/dev/null && echo "RESULTS PUSHED — Claude reads data/indices_validation.md" \
  || echo "(push failed — copy the comparison above to Claude)"

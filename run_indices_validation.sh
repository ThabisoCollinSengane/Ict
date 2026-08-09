#!/usr/bin/env bash
# REALISTIC full-basket validation — currencies + US indices + gold, judged on the
# scheduled-withdrawal income model (NOT fantasy compounding).
#   bash run_indices_validation.sh
#
# Withdrawal policy (env-overridable at the top): start withdrawing once the account
# reaches R10k, then every additional R10k BAND the account reaches makes the
# withdrawals more frequent (monthly -> biweekly -> weekly) AND larger. A fraction
# is banked as income each time; the rest compounds so the cadence can climb.
#
# Instruments: FX (currencies, always) + US indices (US500/US100 via SPXUSD/NSXUSD,
# US30 confirmer) + gold (XAUUSD, silver+AUD confirmers). Missing data for any leg
# is reported and that leg simply contributes no trades (graceful).
#
# Report (data/indices_validation.md): per-split PF / WR / working-MaxDD / total
# value, PLUS the per-year income table (amount + frequency + avg) and the TOTAL
# number of withdrawals over the test — currencies-only vs the full basket, so you
# can see how much indices+gold lift the income.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"
YEARS=(2022 2023 2024 2025)

# ── withdrawal policy (override by exporting before the run) ──────────────────
export WITHDRAW_SCHEDULE="${WITHDRAW_SCHEDULE:-1}"
export WITHDRAW_KEEP="${WITHDRAW_KEEP:-10000}"      # start withdrawing at R10k
export WITHDRAW_FRACTION="${WITHDRAW_FRACTION:-0.7}"# bank 70% income / compound 30%
export WITHDRAW_BAND="${WITHDRAW_BAND:-10000}"      # cadence steps up every R10k
export INDEX_PAIRS="SPXUSD NSXUSD"
export INDEX_REF="${INDEX_REF:-US30}"
export INDEX_MIN_IMSCORE="${INDEX_MIN_IMSCORE:-0.75}"

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

echo "=== 2. indices + gold complex (HistData) ==="
NEED=(SPXUSD NSXUSD XAUUSD XAGUSD AUDUSD)
gmissing=0
for y in "${YEARS[@]}"; do for p in "${NEED[@]}"; do
  ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || gmissing=1
done; done
if [ "$gmissing" = 1 ] || [ "${REFRESH_XTRA:-0}" = 1 ]; then
  echo "  fetching indices+gold from HistData…"
  rm -rf /tmp/xtradl && mkdir -p /tmp/xtradl
  python scripts/fetch_histdata.py --years "${YEARS[@]}" \
    --pairs "${NEED[@]}" --dest /tmp/xtradl 2>&1 | tail -5
  python scripts/prepare_histdata.py /tmp/xtradl || true
fi
echo "  coverage (US30 = Dow, import separately via scripts/import_index_csv.py):"
for y in "${YEARS[@]}"; do for p in "${NEED[@]}" US30; do
  f="data/histdata/${p}_$y.csv"
  if [ -f "$f" ]; then printf "    %s %s: %s rows\n" "$p" "$y" "$(wc -l < "$f")";
  else printf "    %s %s: MISSING\n" "$p" "$y"; fi
done; done

run() {  # $1=label  $2=indices(0/1)  $3=gold(0/1)  $4..=years
  local label="$1" idx="$2" gld="$3"; shift 3
  echo "  $label (indices=$idx gold=$gld, years $*) ..."
  INDICES_ENABLED="$idx" GOLD_ENABLED="$gld" \
    python run_backtest_histdata.py --years "$@" > "/tmp/rb_$label.txt" 2>&1
}

echo "=== 3. runs: currencies-only vs full basket (all under the withdrawal model) ==="
run fx_full   0 0 "${YEARS[@]}"
run all_full  1 1 "${YEARS[@]}"
run fx_is     0 0 2022 2023
run all_is    1 1 2022 2023
run fx_oos    0 0 2024 2025
run all_oos   1 1 2024 2025

echo "=== 4. building report ==="
HEAD_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
HEAD_SHA="$HEAD_SHA" python - <<'PY'
import re, os
HEAD = os.environ.get("HEAD_SHA", "unknown")
def grab(label):
    p = f"/tmp/rb_{label}.txt"
    if not os.path.exists(p):
        return {}, ""
    txt = open(p).read()
    def g(k, cast=float):
        m = re.search(rf"{k}\s+(-?[\d.]+)", txt); return cast(m.group(1)) if m else None
    d = {"trades": g("trades", int), "wr": g("win_rate_pct"), "pf": g("profit_factor"),
         "dd": g("max_drawdown_pct"), "wdd": g("working_max_drawdown_pct"),
         "total": g("ending_equity_ZAR"), "income": g("withdrawn_total_ZAR"),
         "wcount": g("withdrawal_count", int)}
    # extract the per-year income block
    blk = re.search(r"Withdrawals \(income\) per year.*?final working balance[^\n]*",
                    txt, re.S)
    return d, (blk.group(0) if blk else "")

def fmt(d, k, suf=""):
    v = d.get(k)
    return "—" if v is None else ((f"{v:,.0f}" if k in ("total","income") else f"{v:.2f}") + suf)

L = ["# Realistic full-basket validation — currencies + indices + gold", "",
     "Judged on the **scheduled-withdrawal income model** (start at R10k; every R10k "
     "band the account reaches makes withdrawals more frequent + larger; bank 70% / "
     "compound 30%). Sizing for indices/gold is provisional, so PF / WR / working-"
     "MaxDD and the **income schedule** are the signals, not fantasy equity.", "",
     f"_run commit: `{HEAD}`_", ""]

L += ["## Metrics — currencies-only vs full basket", "",
      "| split | book | trades | WR% | PF | MaxDD% | working-DD% | total value R | income R | withdrawals |",
      "|---|---|---|---|---|---|---|---|---|---|"]
for split, fx, allb in (("Full 4yr","fx_full","all_full"),
                        ("IS 2022-23","fx_is","all_is"),
                        ("OOS 2024-25","fx_oos","all_oos")):
    for lbl, label in (("FX only", fx), ("FX+idx+gold", allb)):
        d, _ = grab(label)
        L.append(f"| {split} | {lbl} | {fmt(d,'trades')} | {fmt(d,'wr')} | {fmt(d,'pf')} "
                 f"| {fmt(d,'dd')} | {fmt(d,'wdd')} | {fmt(d,'total')} | {fmt(d,'income')} "
                 f"| {d.get('wcount','—')} |")

# Income schedule (the headline) from the full-basket full-4yr run.
_, blk_all = grab("all_full")
_, blk_fx  = grab("fx_full")
L += ["", "## Income schedule — FULL basket (currencies + indices + gold), 4yr", "",
      "```", blk_all or "(no withdrawals — account never reached R10k)", "```",
      "", "## Income schedule — currencies only, 4yr (for comparison)", "",
      "```", blk_fx or "(no withdrawals — account never reached R10k)", "```"]

# Crash/exit diagnostics — surface the tail of any run that produced no PF.
crash = []
for label in ("fx_full","all_full","fx_is","all_is","fx_oos","all_oos"):
    d, _ = grab(label)
    if d.get("pf") is None:
        p = f"/tmp/rb_{label}.txt"
        tail = "\n".join(open(p).read().splitlines()[-25:]) if os.path.exists(p) else "(no output file)"
        crash.append(f"### {label} — NO RESULTS (crash/early-exit)\n\n```\n{tail}\n```\n")

da, _ = grab("all_full"); dfx, _ = grab("fx_full")
L += ["", "## Bottom line", ""]
if crash:
    L = (L[:1] + ["", "> ⚠️ Some runs produced no Results — diagnostics at the bottom.", ""]
         + L[1:])
if da.get("income") is not None and dfx.get("income") is not None:
    lift = da["income"] - dfx["income"]
    L += [f"- Full basket banked **R{da['income']:,.0f}** income across "
          f"**{da.get('wcount')}** withdrawals over 4yr; currencies-only banked "
          f"R{dfx['income']:,.0f} across {dfx.get('wcount')}. "
          f"Indices+gold added **R{lift:,.0f}** of income "
          f"({'+' if lift>=0 else ''}{(lift/dfx['income']*100 if dfx['income'] else 0):.0f}%)."]
L += ["- Working-account MaxDD is the realistic per-cycle drawdown; the total-value "
      "MaxDD is withdrawal-neutral. Ship the basket if working-DD stays tolerable and "
      "the income schedule is worth it — equity size is capped by design."]
if crash:
    L += ["", "## Diagnostics (why some runs had no Results)", ""] + crash
open("data/indices_validation.md","w").write("\n".join(L) + "\n")
print("\n".join(L))
PY

git add -f data/indices_validation.md 2>/dev/null
git commit -q -m "Realistic full-basket + income validation (auto, commit ${HEAD_SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
git push -u origin HEAD 2>/dev/null && echo "RESULTS PUSHED — Claude reads data/indices_validation.md" \
  || echo "(push failed — copy the report above to Claude)"

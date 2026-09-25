#!/usr/bin/env bash
# Draw-on-liquidity ladder study (Codespaces): how price reacts to each rung —
# previous session H/L, 3-day, weekly, 30-day, 60-day — as targets and as draws
# price delivers to. Measurement only; the instrumentation is analytics (logging
# + MFE), so it MUST leave the backtest numbers identical: the runner asserts
# 810 trades / PF 4.47 / MaxDD -12.95% and flags loudly if they moved.
#   bash run_draw_ladder.sh
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
    && python scripts/prepare_histdata.py /tmp/histdata_dl || {
      echo "ERROR: could not obtain full 4yr data"; exit 1; }
fi

echo "=== full 4yr backtest (writes trade dump with lad_* + mfe_pips) ==="
python run_backtest_histdata.py --years 2022 2023 2024 2025 > /tmp/ladder_bt.txt 2>&1
grep -E "trades |win_rate_pct|profit_factor|max_drawdown_pct|ending_equity" /tmp/ladder_bt.txt | head

echo "=== integrity check: analytics-only must NOT move the numbers ==="
python - <<'PY'
import re
t = open("/tmp/ladder_bt.txt").read()
def g(k):
    m = re.search(rf"{k}\s+(-?[\d.]+)", t); return m.group(1) if m else "?"
tr, pf, dd = g("trades"), g("profit_factor"), g("max_drawdown_pct")
print(f"  trades={tr}  PF={pf}  MaxDD={dd}%")
ok = (tr == "810" and pf in ("4.46","4.47") and dd == "-12.95")
print("  ✅ numbers unchanged — instrumentation is pure analytics"
      if ok else f"  ⚠️ NUMBERS MOVED — the logging changed behavior, investigate before trusting the study")
PY

if ! ls data/histdata/trades_dump.csv >/dev/null 2>&1; then
  echo "ERROR: no trade dump — see /tmp/ladder_bt.txt"; exit 1
fi

echo "=== draw-ladder analysis ==="
python scripts/draw_ladder_analysis.py || exit 1

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/draw_ladder_report.md
git add -f data/draw_ladder_report.md 2>/dev/null
git commit -q -m "Draw-ladder study results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/draw_ladder_report.md"
else
  echo "(push failed — copy the report above to Claude)"
fi

#!/usr/bin/env bash
# Inversion FVG (IFVG) backtest (Codespaces).
#   bash run_ifvg.sh
# Validates the full-body-close-outside inversion across D1/H4/H1/M15 (entry one
# TF lower), IS 2022 vs OOS 2024, on the HistData M1 already prepared. Pushes
# data/ifvg_report.md. Measurement only — nothing ships to the engine.
cd "$(dirname "$0")" || exit 1

echo "=== ensuring 2022-2025 M1 (EURUSD/GBPUSD/NZDUSD) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD NZDUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ]; then
  echo "  fetching missing years from HistData…"
  python scripts/fetch_histdata.py --years 2022 2023 2024 2025 --dest /tmp/ifvg_dl \
    && python scripts/prepare_histdata.py /tmp/ifvg_dl || {
      echo "ERROR: could not obtain M1"; exit 1; }
fi

echo "=== running IFVG backtest — SWING-structure entry, H1/H4, IS 22-23 vs OOS 24-25 ==="
RUN_IFVG_BACKTEST=1 python scripts/backtest_ifvg.py --years 2022 2023 2024 2025 \
  --entry swing --target 2r || {
  echo "run failed — copy the traceback to Claude"; exit 1; }

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/ifvg_report.md
git add -f data/ifvg_report.md data/ifvg_trades.csv 2>/dev/null
git commit -q -m "IFVG backtest results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/ifvg_report.md"
else
  echo "(push failed — copy the report above to Claude)"
fi

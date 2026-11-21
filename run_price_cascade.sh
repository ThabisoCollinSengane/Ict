#!/usr/bin/env bash
# Pure-price draw cascade (Codespaces): does price go daily -> 3d -> 30d -> 60d?
#   bash run_price_cascade.sh
# Raw M1 price only — no backtest, no trades. Fast. Measurement only.
cd "$(dirname "$0")" || exit 1

echo "=== ensuring M1 for EURUSD/GBPUSD/NZDUSD, all 4 years ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD NZDUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ]; then
  echo "  fetching 2025 direct from HistData…"
  python scripts/fetch_histdata.py --years 2025 --dest /tmp/histdata_dl \
    && python scripts/prepare_histdata.py /tmp/histdata_dl \
    || echo "  ⚠️ fetch/prepare incomplete — analysis will skip missing pairs/years and say so."
fi

echo "=== cascade analysis (horizon 2 trading days) ==="
python scripts/price_cascade.py --horizon-days 2 || exit 1

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/price_cascade_report.md
git add -f data/price_cascade_report.md 2>/dev/null
git commit -q -m "Price-cascade study results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/price_cascade_report.md"
else
  echo "(push failed — copy the report above to Claude)"
fi

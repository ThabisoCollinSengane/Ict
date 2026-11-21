#!/usr/bin/env bash
# PWH/PWL reaction study (Codespaces): run the full 4yr backtest to produce the
# trade dump, then measure how price reacts when the sweep ran a weekly pool.
#   bash run_pwliq_analysis.sh
# Measurement only — nothing ships. If the weekly-sweep bucket shows a both-year
# edge with adequate n, THEN we build + validate a PWH/PWL sizing lever (like P41).
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring M1 data (all 4 years, incl. UDXUSD) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD UDXUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y.csv MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ]; then
  echo "  fetching 2025 direct from HistData (fills the DXY + EUR/GBP gap)…"
  python scripts/fetch_histdata.py --years 2025 --dest /tmp/histdata_dl \
    && python scripts/prepare_histdata.py /tmp/histdata_dl || {
      echo "  fetch/prepare hit an issue — falling back to Drive pull…"
      pip install -q --upgrade "gdown>=5.2"
      rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
      Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
      [ -n "$Z" ] && python scripts/prepare_histdata.py "$(dirname "$Z")"
    }
fi

echo "=== running full 4yr backtest (writes data/histdata/trades_dump.csv) ==="
python run_backtest_histdata.py --years 2022 2023 2024 2025 > /tmp/pwliq_bt.txt 2>&1
tail -6 /tmp/pwliq_bt.txt
if ! ls data/histdata/trades_dump.csv >/dev/null 2>&1; then
  echo "ERROR: no trade dump produced — see /tmp/pwliq_bt.txt"; exit 1
fi

echo "=== PWH/PWL reaction analysis ==="
python scripts/pwliq_analysis.py || exit 1

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/pwliq_report.md
git add -f data/pwliq_report.md 2>/dev/null
git commit -q -m "PWH/PWL reaction study results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/pwliq_report.md"
else
  echo "(push failed — copy the report above to Claude)"
fi

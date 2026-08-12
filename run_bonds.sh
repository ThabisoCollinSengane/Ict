#!/usr/bin/env bash
# Bonds/yields × dollar — daily-bias measurement (Codespaces).
#   bash run_bonds.sh
# Fetches US Treasury yields (DGS2/5/10) from FRED + ensures pair M1, then runs
# scripts/bonds_analysis.py and pushes data/bonds_report.md. Measurement only —
# nothing ships to the engine. Read the report's GREEN/YELLOW/RED verdict; only a
# GREEN warrants run_bonds_validation.sh (the actual backtest A/B of the lever).
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== ensuring pair M1 (EURUSD/GBPUSD/NZDUSD, all 4 years) ==="
missing=0
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD NZDUSD; do
    ls data/histdata/${p}_$y.csv >/dev/null 2>&1 || { echo "  ${p}_$y MISSING"; missing=1; }
  done
done
if [ "$missing" = 1 ] || [ "${REFRESH_M1:-0}" = 1 ]; then
  echo "  fetching M1 from Drive + preparing (REFRESH_M1=${REFRESH_M1:-0})…"
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  if [ -n "$Z" ]; then
    python scripts/prepare_histdata.py "$(dirname "$Z")" \
      || echo "  ⚠️ prepare failed — analysis will skip missing pairs and say so."
  else
    echo "  ⚠️ Drive M1 download empty — trying direct HistData for 2025…"
    python scripts/fetch_histdata.py --years 2025 --dest /tmp/histdata_dl \
      && python scripts/prepare_histdata.py /tmp/histdata_dl \
      || echo "  ⚠️ fetch incomplete — analysis reports which pairs/years are missing."
  fi
fi

echo "=== fetching US Treasury yields from FRED (DGS2/DGS5/DGS10) ==="
python scripts/fetch_fred.py --start 2020-01-01 --end 2025-12-31 \
  || echo "  ⚠️ FRED fetch failed (proxy?). Drop DGS*.csv into data/bonds_src/ manually."

echo "=== bonds analysis (horizon 3 days, SMT lookback 20) + emit bond_bias.json ==="
python scripts/bonds_analysis.py --horizon-days 3 --lookback 20 --emit-bias || exit 1

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/bonds_report.md
git add -f data/bonds_report.md 2>/dev/null
git commit -q -m "Bonds/yields dollar-bias measurement (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/bonds_report.md"
else
  echo "(push failed — copy the report above to Claude)"
fi

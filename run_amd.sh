#!/usr/bin/env bash
# One-command AMD setup-quality study (Codespaces).
#   bash run_amd.sh
# Uses the M1 data already prepared in data/histdata/ (re-downloads only if
# missing). Runs the instrumented backtest (logs accumulation + stop-run details
# per trade), analyses which AMD conditions produce winners, and auto-pushes the
# report. No tick data — no Google rate-limit risk this time.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== [1/3] ensuring M1 data is prepared ==="
if ! ls data/histdata/EURUSD_2022.csv >/dev/null 2>&1; then
  echo "  M1 CSVs missing — downloading + preparing (small, should be quick)…"
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  M1_ZIP=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  if [ -z "$M1_ZIP" ]; then
    echo "  ERROR: M1 download failed (rate-limit?). Wait a bit and re-run."
    exit 1
  fi
  python scripts/prepare_histdata.py "$(dirname "$M1_ZIP")" || exit 1
else
  echo "  M1 CSVs already present — reusing them."
fi

echo "=== [2/3] running the instrumented backtest (logs AMD details) ==="
python run_backtest_histdata.py --years 2022 2023 2024 2025 > /tmp/amd_bt.txt 2>&1
echo "--- backtest tail ---"; tail -20 /tmp/amd_bt.txt
if ! ls data/histdata/trades_dump.csv >/dev/null 2>&1; then
  echo "ERROR: no trade dump produced — see /tmp/amd_bt.txt"; exit 1
fi

echo "=== [3/3] AMD setup-quality analysis ==="
python scripts/amd_analysis.py || exit 1

echo ""
echo "############################################################"
echo "#  AMD REPORT  (copy this to Claude)                        #"
echo "############################################################"
cat data/amd_report.md

git add -f data/amd_report.md 2>/dev/null
if git commit -q -m "AMD setup-quality results (auto)" 2>/dev/null && git push -q 2>/dev/null; then
  echo ""; echo "RESULTS PUSHED — Claude will read the report."
else
  echo ""; echo "(auto-push skipped — copy the AMD REPORT above to Claude)"
fi

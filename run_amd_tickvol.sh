#!/usr/bin/env bash
# One-command AMD × tick-volume study (Codespaces).
#   bash run_amd_tickvol.sh
# Profiles tick volume across accumulation / Judas sweep / distribution and at
# PD arrays. Reuses the M1 data + the P39 tick aggregation already in the
# Codespace (no new tick download). Re-runs the instrumented backtest, joins the
# AMD phase timestamps to the tick bins, and auto-pushes the report.
cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"

echo "=== [1/4] ensuring M1 data is prepared ==="
if ! ls data/histdata/EURUSD_2022.csv >/dev/null 2>&1; then
  echo "  M1 CSVs missing — downloading + preparing…"
  pip install -q --upgrade "gdown>=5.2"
  rm -rf /tmp/m1dl && gdown --folder -O /tmp/m1dl "$M1_URL"
  Z=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
  [ -z "$Z" ] && { echo "  ERROR: M1 download failed (rate-limit?). Wait + re-run."; exit 1; }
  python scripts/prepare_histdata.py "$(dirname "$Z")" || exit 1
else
  echo "  M1 CSVs present — reusing."
fi

echo "=== [2/4] ensuring tick aggregation is present ==="
if ! ls data/p39_agg/*_m5.csv >/dev/null 2>&1; then
  if ls /tmp/ticks/*.zip >/dev/null 2>&1; then
    echo "  aggregating ticks from /tmp/ticks…"
    python scripts/p39_volume_analysis.py aggregate /tmp/ticks || exit 1
  else
    echo "  ERROR: no tick aggregation (data/p39_agg) and no tick zips (/tmp/ticks)."
    echo "  Run 'bash run_p39_only.sh' first to fetch + aggregate the ticks, then re-run this."
    exit 1
  fi
else
  echo "  tick aggregation present — reusing."
fi

echo "=== [3/4] running the instrumented backtest (logs AMD phase timestamps) ==="
python run_backtest_histdata.py --years 2022 2023 2024 2025 > /tmp/amdtv_bt.txt 2>&1
echo "--- backtest tail ---"; tail -15 /tmp/amdtv_bt.txt
if ! ls data/histdata/trades_dump.csv >/dev/null 2>&1; then
  # Surface the crash into the report so it lands in the repo, not just /tmp.
  { echo "# AMD × tick-volume — RUN FAILED"; echo;
    echo "The instrumented backtest produced no trade dump. Tail of the run:"; echo;
    echo '```'; tail -40 /tmp/amdtv_bt.txt; echo '```'; } > data/amd_tickvol_report.md
  git add -f data/amd_tickvol_report.md 2>/dev/null
  git commit -q -m "AMD x tick-volume: backtest crash (auto)" 2>/dev/null
  git pull -q --no-rebase --no-edit 2>/dev/null; git push -u origin HEAD 2>/dev/null
  echo "ERROR: no trade dump — crash tail pushed to data/amd_tickvol_report.md"; exit 1
fi

echo "=== [4/4] AMD × tick-volume analysis ==="
python scripts/amd_tickvol_analysis.py || exit 1

# Stamp the run's commit sha so we can confirm which code produced the report.
SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/amd_tickvol_report.md

echo ""
echo "############################################################"
echo "#  AMD x TICK-VOLUME REPORT  (copy this to Claude)          #"
echo "############################################################"
cat data/amd_tickvol_report.md

git add -f data/amd_tickvol_report.md 2>/dev/null
git commit -q -m "AMD x tick-volume results (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo ""; echo "RESULTS PUSHED — Claude will read the report."
else
  echo ""; echo "(push failed — copy the report above to Claude)"
fi

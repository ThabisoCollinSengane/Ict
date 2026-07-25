#!/usr/bin/env bash
# One-command cloud runner (GitHub Codespaces or any Linux box with internet).
#   bash run_cloud.sh
# Pulls the public M1 + tick Drive folders, runs the full backtest, then P39,
# and prints both result blocks. No Drive login, no token, no notebook cells.
#
# Prerequisites: the repo + both Drive folders set to public / anyone-with-link.

cd "$(dirname "$0")" || exit 1
M1_URL="https://drive.google.com/drive/folders/1uN2c7QvNJg15CmVmNXUYR1CTiSsaB-d4"
TICK_URL="https://drive.google.com/drive/folders/1cXPxh_PqcNYIhHOnvZoV6JRI526tQIz-"

echo "=== [1/6] installing dependencies ==="
pip install -q -r requirements.txt || { echo "pip install failed"; exit 1; }
pip install -q --upgrade "gdown>=5.2" || { echo "gdown upgrade failed"; exit 1; }

echo "=== [2/6] downloading M1 data (public link) ==="
rm -rf /tmp/m1dl && gdown --folder --remaining-ok -O /tmp/m1dl "$M1_URL"
M1_ZIP=$(find /tmp/m1dl -name 'HISTDATA_*_M1????.zip' 2>/dev/null | head -1)
if [ -z "$M1_ZIP" ]; then
  echo "ERROR: no M1 zips downloaded — is the M1 folder set to 'Anyone with the link'?"
  exit 1
fi
M1_DIR=$(dirname "$M1_ZIP")
echo "M1_DIR=$M1_DIR"
python scripts/prepare_histdata.py "$M1_DIR" || { echo "prepare failed"; exit 1; }

echo "=== [3/6] running the full backtest (2022-2025) ==="
python run_backtest_histdata.py --years 2022 2023 2024 2025 > /tmp/backtest_out.txt 2>&1
echo "--- backtest summary (tail) ---"
tail -50 /tmp/backtest_out.txt

echo "=== [4/6] downloading tick data (slow, a few GB) ==="
rm -rf /tmp/tickdl && gdown --folder --remaining-ok -O /tmp/tickdl "$TICK_URL"
TICK_ZIP=$(find /tmp/tickdl -name 'HISTDATA_*_T*.zip' 2>/dev/null | head -1)
if [ -z "$TICK_ZIP" ]; then
  echo "ERROR: no tick zips downloaded — is the tick folder set to 'Anyone with the link'?"
  exit 1
fi
TICK_DIR=$(dirname "$TICK_ZIP")
echo "TICK_DIR=$TICK_DIR"

echo "=== [5/6] P39 aggregate + analyse ==="
python scripts/p39_volume_analysis.py aggregate "$TICK_DIR" || { echo "aggregate failed"; exit 1; }
python scripts/p39_volume_analysis.py analyse || { echo "analyse failed"; exit 1; }

echo ""
echo "############################################################"
echo "#  P39 REPORT  (copy everything below into the Claude chat) #"
echo "############################################################"
cat data/p39_volume_report.md
echo "############################################################"
echo "#  BACKTEST SUMMARY                                          #"
echo "############################################################"
tail -50 /tmp/backtest_out.txt
echo ""
echo "=== [6/6] DONE. Report also saved at data/p39_volume_report.md ==="

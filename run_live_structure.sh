#!/usr/bin/env bash
# Real classifier + real entries/gates on RECENT LIVE 5m data (Codespaces).
#   bash run_live_structure.sh [PAIR] [DAYS]
# Needs open internet (Codespace has it; the cloud chat session does not). Pulls
# recent 5m forex from yfinance, runs the actual market_structure classifier + the
# full strategy, and pushes the labelled swings + the entries the algo took + the
# gate funnel — so we can see EXACTLY how it reads/traded the window in your chart.
cd "$(dirname "$0")" || exit 1
PAIR="${1:-GBPUSD}"
DAYS="${2:-3}"

echo "=== ensuring yfinance ==="
python -c "import yfinance" 2>/dev/null || pip install -q yfinance

echo "=== running real classifier + entries/gates ($PAIR, last $DAYS days) ==="
python scripts/live_structure.py --pair "$PAIR" --days "$DAYS" || {
  echo "run failed — copy the traceback above to Claude"; exit 1; }

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
printf '\n_report generated on commit `%s`_\n' "$SHA" >> data/live_structure_report.md
git add -f data/live_structure_report.md 2>/dev/null
git commit -q -m "Live structure + entries report (auto, commit ${SHA})" 2>/dev/null
git pull -q --no-rebase --no-edit 2>/dev/null
if git push -u origin HEAD 2>/dev/null; then
  echo "RESULTS PUSHED — Claude will read data/live_structure_report.md"
else
  echo "(push failed — copy the report above to Claude)"
fi

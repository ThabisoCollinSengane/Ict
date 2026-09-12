#!/usr/bin/env bash
# Build seasonal tendencies from long-history daily FX (Dukascopy) — one command.
#   bash run_seasonal.sh                 # 2005..2025 by default
#   FROM=2010 bash run_seasonal.sh
#
# Fetches ~20yr DAILY bars per pair from Dukascopy (tiny, fast), imports them into
# a SEPARATE folder (data/seasonal_src/ - so the M1 backtest data is NOT touched),
# computes data/seasonal_bias.json, and pushes it. Run in the Codespace or the Ops
# VM (needs Node/npx + Python; the live bot doesn't need this).
set -u
cd "$(dirname "$0")" || exit 1
FROM="${FROM:-2005-01-01}"; TO="${TO:-2025-12-31}"
[ "${FROM}" = "${FROM%-*-*}" ] && FROM="${FROM}-01-01"   # allow FROM=2010
SRC="data/seasonal_src"
mkdir -p "$SRC" /tmp/seasdl

# pair -> dukascopy instrument id
declare -A DUKAS=( [EURUSD]=eurusd [GBPUSD]=gbpusd [NZDUSD]=nzdusd [EURGBP]=eurgbp )

echo "=== 1. fetch + import daily history ($FROM..$TO) ==="
for p in EURUSD GBPUSD NZDUSD EURGBP; do
  if ls "$SRC/${p}_"*.csv >/dev/null 2>&1 && [ "${REFRESH:-0}" != 1 ]; then
    echo "  $p: already imported (REFRESH=1 to refetch)"; continue
  fi
  echo "  $p: fetching ${DUKAS[$p]} d1 ..."
  rm -f /tmp/seasdl/${DUKAS[$p]}-*.csv
  npx --yes dukascopy-node -i "${DUKAS[$p]}" -from "$FROM" -to "$TO" \
      -t d1 -f csv -dir /tmp/seasdl >/tmp/seas_${p}.log 2>&1
  f=$(ls /tmp/seasdl/${DUKAS[$p]}-*.csv 2>/dev/null | head -1)
  if [ -z "$f" ]; then
    echo "    ! no file for $p — see /tmp/seas_${p}.log (skipping)"; continue
  fi
  python scripts/import_index_csv.py "$f" --symbol "$p" --out-dir "$SRC"
done

echo "=== 2. compute seasonal_bias.json ==="
python scripts/build_seasonal.py --src-dir "$SRC" --pairs EURUSD GBPUSD NZDUSD EURGBP

echo "=== 3. commit + push ==="
if [ -f data/seasonal_bias.json ]; then
  git add -f data/seasonal_bias.json
  git commit -q -m "Seasonal bias computed from long-history daily FX" 2>/dev/null
  git pull -q --no-rebase --no-edit 2>/dev/null
  git push -u origin HEAD 2>/dev/null && echo "PUSHED data/seasonal_bias.json" \
    || echo "(push failed — the file is in data/seasonal_bias.json)"
  echo; echo "Preview:"; python - <<'PY'
import json
d=json.load(open("data/seasonal_bias.json"))
for p,meta in d.get("_meta",{}).get("pairs",{}).items():
    print(f"  {p}: {meta['n_years']}yr {meta['span']}")
PY
else
  echo "ERROR: seasonal_bias.json not produced — check the fetch logs in /tmp/seas_*.log"
fi

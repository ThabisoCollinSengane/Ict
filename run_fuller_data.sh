#!/usr/bin/env bash
# Fuller-data run (Codespaces): fetch the missing 2025 M1 from HistData directly,
# prepare it, then run the TRUE 4yr (2022-2025) P41 validation.
#   bash run_fuller_data.sh
# The blocker was UDXUSD_2025 (real DXY feed) + EUR/GBP 2025 gaps → 2025 gated to
# ~0 trades (602 not 810). This self-serves that data instead of manual Drive
# uploads. Set FETCH_2026=1 to also pull 2026 H1 (Jan-Jun) for a later 2026 run.
cd "$(dirname "$0")" || exit 1
DL=/tmp/histdata_dl

echo "=== [1/3] fetching 2025 M1 (all pairs) from HistData ==="
python scripts/fetch_histdata.py --years 2025 --dest "$DL" || {
  echo "⚠️ some 2025 files failed — HistData may be rate-limiting or blocking the"
  echo "   Codespace IP. Re-run in a few minutes; partial files are cached + skipped."
}
if [ "${FETCH_2026:-0}" = 1 ]; then
  echo "=== fetching 2026 H1 (Jan-Jun), monthly ==="
  python scripts/fetch_histdata.py --years 2026 --months 1 2 3 4 5 6 --dest "$DL" \
    || echo "⚠️ some 2026 months failed (only completed months are published)."
fi

echo "=== [2/3] preparing downloaded zips into data/histdata ==="
if ! ls "$DL"/HISTDATA_*_M1*.zip >/dev/null 2>&1; then
  echo "ERROR: no zips downloaded — nothing to prepare. See fetch output above."; exit 1
fi
python scripts/prepare_histdata.py "$DL" || exit 1

echo "=== coverage after prepare (UDXUSD_2025 is the true-4yr gate) ==="
for y in 2022 2023 2024 2025; do
  for p in EURUSD GBPUSD NZDUSD UDXUSD; do
    f="data/histdata/${p}_$y.csv"
    if [ -f "$f" ]; then printf "  %s %s: %s rows\n" "$p" "$y" "$(wc -l < "$f")";
    else printf "  %s %s: MISSING\n" "$p" "$y"; fi
  done
done

echo "=== [3/3] running the TRUE 4yr P41 validation ==="
exec bash run_pdliq_validation.sh

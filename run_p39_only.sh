#!/usr/bin/env bash
# P39-only retry. Reuses the trades_dump.csv from a prior run_cloud.sh run, so
# it does NOT re-run the backtest. Downloads the needed tick files INDIVIDUALLY
# (2022 IS + 2024 OOS, EURUSD + GBPUSD) — robust vs gdown folder-mode, which
# aborts on the first bad/rate-limited file. Skips failures (partial coverage
# is fine for P39), sleeps between files to dodge Google's rate limiter.
cd "$(dirname "$0")" || exit 1
pip install -q --upgrade "gdown>=5.2" 2>/dev/null

if [ ! -f data/histdata/trades_dump.csv ]; then
  echo "No data/histdata/trades_dump.csv found."
  echo "Run 'bash run_cloud.sh' first (it produces the trade dump), then this script."
  exit 1
fi

mkdir -p /tmp/ticks
# id|filename  — EURUSD + GBPUSD tick zips for 2022 and 2024.
read -r -d '' TICKS <<'IDS'
1CI2b-YlbSf4diaQNhzmBYfn9nJZoIzBG|HISTDATA_COM_ASCII_EURUSD_T202201.zip
1UFbv5UyZfxha_bQ5TEH5ECX3O3QO3lCx|HISTDATA_COM_ASCII_EURUSD_T202202.zip
1qd3LSl5l6tWBD1Oi7UWqctJvY35xAVcx|HISTDATA_COM_ASCII_EURUSD_T202203.zip
1OpaWo-BYsgzLb5NTEeIEEM6qmJK8iiYD|HISTDATA_COM_ASCII_EURUSD_T202205.zip
1QfQuU0D5ZQtlsTGAgNsPgS9QyFbiktqd|HISTDATA_COM_ASCII_EURUSD_T202206.zip
1bbKuvlky-o9PGYq2wQ4i19sWPOzcdyQg|HISTDATA_COM_ASCII_EURUSD_T202207.zip
1BkBWh2uCDXf48xa_tf2waSskWqMWvXsZ|HISTDATA_COM_ASCII_EURUSD_T202208.zip
1yV6F22DYMoL-Qa8HAsFRgOpEuBALgwb_|HISTDATA_COM_ASCII_EURUSD_T202210.zip
1g_gWn-93Wp7-0Xdsp9XHydRgoj5gW7LW|HISTDATA_COM_ASCII_EURUSD_T202212.zip
1z6S9OFYtX-3SSy5vuw0rOT6B1B1kwBD6|HISTDATA_COM_ASCII_EURUSD_T202401.zip
1IK4PthJmJdMRXIRLGUrGFMRmwQD4s_GN|HISTDATA_COM_ASCII_EURUSD_T202402.zip
1I9-i8rfw6A39VwLNj6xkjXjPj9wqvSjr|HISTDATA_COM_ASCII_EURUSD_T202403.zip
1Kuu-iXLfOBfGMDZ-6uUt2QhOGkNr7mKa|HISTDATA_COM_ASCII_EURUSD_T202404.zip
1UtGZI0CxxC4i-dH8KkJecCI8vpG_uLOS|HISTDATA_COM_ASCII_EURUSD_T202405.zip
1KxV0H9QMKUy_HvZbjmO6ati71hOh-dyd|HISTDATA_COM_ASCII_EURUSD_T202406.zip
19M1RrfytoZt03X895ng6HgDOj52em7P5|HISTDATA_COM_ASCII_EURUSD_T202407.zip
1c3FTHI3ieV9nSmh9YNWcWaPOkgI4yuac|HISTDATA_COM_ASCII_EURUSD_T202408.zip
1XKFhEmj6TN2t3JBlsrAdKEQf1nPLNeYa|HISTDATA_COM_ASCII_EURUSD_T202409.zip
13aMKrBivQpIHq4zQ7rTS8yigMqbzcFim|HISTDATA_COM_ASCII_EURUSD_T202410.zip
1XmsZ8iLCfR4YNzao9tGLiFDm4tavpfhn|HISTDATA_COM_ASCII_EURUSD_T202411.zip
1CF4BvdgyxusYHYD1GFqcmiFswpC5Y4jF|HISTDATA_COM_ASCII_EURUSD_T202412.zip
1lR36UVSmU4O8Obv7bkKmgAoxRcogWhqz|HISTDATA_COM_ASCII_GBPUSD_T202201.zip
1b997Gx8O7yqLcz9ITR-5P0TrXoabvvKo|HISTDATA_COM_ASCII_GBPUSD_T202202.zip
1T3zT0b9ZckDiEwiDIMNK-x_E-HzbjPaV|HISTDATA_COM_ASCII_GBPUSD_T202204.zip
1gcGZAa05gd1JzEjGLTIET3WG-g_XVSww|HISTDATA_COM_ASCII_GBPUSD_T202205.zip
1vkuUqtP1cZr-e9ySxf_rfxPWPtWqldnX|HISTDATA_COM_ASCII_GBPUSD_T202206.zip
1nw6q_tzzrm_ksBzwmvAa9Hp2xnXAt5aG|HISTDATA_COM_ASCII_GBPUSD_T202207.zip
1s5ukzerI5YaAhxpJd918Q7SHc_nTOvAz|HISTDATA_COM_ASCII_GBPUSD_T202208.zip
1K-cUbZSOtIqNHxXN3I9rkhVWKkB_kWN0|HISTDATA_COM_ASCII_GBPUSD_T202209.zip
14Rcnurbpf_c70VwSlGj67N2BchLwD6Mx|HISTDATA_COM_ASCII_GBPUSD_T202211.zip
1M4I3gbdZS3IDfv3Vegy0keDECQR7_5Ec|HISTDATA_COM_ASCII_GBPUSD_T202212.zip
1QSNgqfEz7rDA-4A3aFGQ1UbnyJH6ae-b|HISTDATA_COM_ASCII_GBPUSD_T202401.zip
1zG2q7PN6_zpXG9nu64bAwzPad10rADqt|HISTDATA_COM_ASCII_GBPUSD_T202402.zip
1Vw1_fniV7RpZ3IEsS_aAiICBG4ueIUlM|HISTDATA_COM_ASCII_GBPUSD_T202403.zip
1FaNMBHG_pcMpcHiCujvC7Wu4EyKI1iGw|HISTDATA_COM_ASCII_GBPUSD_T202404.zip
1cEWadxZNlzNHhWh0syKJTWCJkozMNSbP|HISTDATA_COM_ASCII_GBPUSD_T202405.zip
1tWwwd55LqiCL3Pq-MoN_xPrcKiswy0WB|HISTDATA_COM_ASCII_GBPUSD_T202406.zip
1Nv_UNVI3fZfX8Phj3bdFqjSTVg9O_eme|HISTDATA_COM_ASCII_GBPUSD_T202407.zip
1-CZvmH7UEJp9CNhh71cZO4fQeZmCgt4u|HISTDATA_COM_ASCII_GBPUSD_T202408.zip
1bMe_tQgBLWSXdPbpvAJ-BjWER6wvabXo|HISTDATA_COM_ASCII_GBPUSD_T202409.zip
1eTOFajPlK0Ow-WQfxT0ms6o_Ozh5OTRe|HISTDATA_COM_ASCII_GBPUSD_T202410.zip
105yllx8gKmk9nEYn_VjJcU92YL1T_YKS|HISTDATA_COM_ASCII_GBPUSD_T202411.zip
1-Z7MipEcy2m0FmDNwHeN7D0bVcMFu7bJ|HISTDATA_COM_ASCII_GBPUSD_T202412.zip
IDS

echo "=== downloading tick files individually (skips failures) ==="
while IFS='|' read -r id name; do
  [ -z "$id" ] && continue
  [ -s "/tmp/ticks/$name" ] && { echo "have $name"; continue; }
  gdown "$id" -O "/tmp/ticks/$name" >/dev/null 2>&1 && echo "ok  $name" || echo "SKIP $name"
  sleep 1
done <<< "$TICKS"

N=$(ls /tmp/ticks/*.zip 2>/dev/null | wc -l)
echo "=== downloaded $N tick zips ==="
if [ "$N" -eq 0 ]; then
  echo "None downloaded — Google is rate-limiting the account. Wait ~20-30 min, then re-run this script."
  exit 1
fi

echo "=== P39 aggregate + analyse ==="
python scripts/p39_volume_analysis.py aggregate /tmp/ticks || exit 1
python scripts/p39_volume_analysis.py analyse || exit 1

echo ""
echo "############################################################"
echo "#  P39 REPORT  (copy this to Claude)                        #"
echo "############################################################"
cat data/p39_volume_report.md

git add -f data/p39_volume_report.md 2>/dev/null
if git commit -q -m "P39 results (auto)" 2>/dev/null && git push -q 2>/dev/null; then
  echo ""; echo "RESULTS PUSHED — Claude will pick them up."
else
  echo ""; echo "(auto-push skipped — copy the report above to Claude)"
fi

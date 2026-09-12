# How to run — command cheat-sheet

All of these run in the **Codespace** (it has internet + the data). Always start
with `git pull` so you have the latest code. Reports auto-push back to the repo.

---

## 1 · The main strategy backtest (the headline numbers)

```bash
python run_backtest_histdata.py --years 2022 2023 2024 2025
```

Prints the full result — trades, win rate, profit factor, max drawdown, ending
equity — plus the gate funnel and per-scenario breakdown. This is the 810-trade
/ PF 4.47 / MaxDD −12.95% run. Splits:

```bash
python run_backtest_histdata.py --years 2022 2023      # in-sample
python run_backtest_histdata.py --years 2024 2025      # out-of-sample
```

If it complains about missing data, fetch it first:

```bash
python scripts/fetch_histdata.py --years 2025 --dest /tmp/dl && python scripts/prepare_histdata.py /tmp/dl
```

---

## 2 · Live structure + entries + gates (recent real data, via Yahoo)

The tool that shows how the algo reads/labels/trades a recent window.

```bash
# last 3 days: structure labels + entries + cumulative gate funnel
bash run_live_structure.sh --pair GBPUSD --days 3

# one specific day: structure + entries + gate funnel scoped to THAT DAY
bash run_live_structure.sh --pair GBPUSD --date 2026-07-30

# every trade over the last ~60 days + a per-day tally (find trending days ⭐)
bash run_live_structure.sh --pair GBPUSD --list
```

Swap `GBPUSD` for `EURUSD` etc. Reads `data/live_structure_report.md`.

---

## 3 · Validation runners (already-tested levers — for reference)

```bash
bash run_pdliq_validation.sh          # P41 PDH/PDL-sweep sizing (SHIPPED)
bash run_mintarget_validation.sh      # 20 vs 25 vs 30 target floor (30 SHIPPED)
bash run_scaledtarget_validation.sh   # equity-scaled floor + pyramid counts (RED)
```

Each runs baseline-vs-lever across full + IS + OOS and pushes a verdict report to
`data/<name>_validation.md`.

---

## 4 · Measurement studies (analytics only — nothing ships)

```bash
bash run_price_cascade.sh             # daily→3d→30d→60d draw cascade
bash run_draw_ladder.sh               # how price reacts to each liquidity rung
bash run_pwliq_analysis.sh            # previous-week high/low reaction
```

---

## Reading results
Every runner pushes its `data/*.md` report back to the repo, so after a run
finishes just tell Claude "done" and it reads the pushed report. The main
strategy backtest (#1) prints to the terminal — copy the summary block.

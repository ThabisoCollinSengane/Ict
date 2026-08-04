#!/usr/bin/env python3
"""Real classifier + real entries/gates on recent LIVE 5m data (yfinance).

Codespace only — needs open internet (this cloud session's proxy blocks data
hosts). Fetches recent 5m forex via yfinance, then:
  1. Runs the actual ict.market_structure.classify() on the pair's 5m + 15m bars
     for the target window → exact ITH/ITL/STH/STL swings with timestamps.
  2. Runs the full Backtester over the fetched data → the actual entries the algo
     took in that window (with the gate outcomes recorded on each trade) + the
     cumulative gate funnel.

Run:  python scripts/live_structure.py --pair GBPUSD --days 3
"""
from __future__ import annotations

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backtest as bt                       # noqa: E402
from ict import market_structure as ms      # noqa: E402

REPORT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      "data", "live_structure_report.md")


def _classify_window(df, start, end):
    bars = bt.df_to_bars(df)
    res = ms.classify(bars)
    rows = []
    for tier in ("ith", "itl", "sth", "stl"):
        for s in res[tier]:
            if 0 <= s.bar_index < len(df.index):
                ts = df.index[s.bar_index]
                if start <= ts <= end:
                    rows.append((ts, s.tier, s.price, s.swept))
    rows.sort(key=lambda r: r[0])
    return rows, ms.structure_direction(res), ms.last_intact(res, "ITH"), ms.last_intact(res, "ITL")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", default="GBPUSD")
    ap.add_argument("--days", type=float, default=3.0, help="window = last N days of data")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD — window = just that UTC day")
    ap.add_argument("--period", default="60d")
    a = ap.parse_args()

    L = [f"# Live structure + entries — {a.pair}", ""]
    print("fetching live 5m data via yfinance…")
    data = bt.fetch_data(period=a.period, interval="5m")
    if a.pair not in data or data[a.pair].empty:
        L.append(f"ERROR: no data for {a.pair} from yfinance.")
        _write(L); return 1

    if a.date:
        start = pd.Timestamp(a.date, tz="UTC")
        end = start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    else:
        end = data[a.pair].index.max()
        start = end - pd.Timedelta(days=a.days)
    L += [f"_data window: {start} → {end} (UTC) · classifier + gates are the real code_", ""]

    # Build + run the full strategy on the fetched data (entries + gate funnel).
    trades, gate, run_err = [], {}, None
    try:
        b = bt.Backtester(data)
        b.run()
        gate = dict(b.gate)
        trades = [t for t in b.trades
                  if start <= pd.Timestamp(t["opened_at"]).tz_convert("UTC") <= end]
    except Exception as e:  # noqa: BLE001
        run_err = f"{type(e).__name__}: {e}"
        # fall back to a fresh Backtester purely for the resampled dfs (structure still works)
        b = bt.Backtester(data)

    # 1 · Structure labels (real classify) on 5m and 15m.
    for tf, name in (("15T", "15-minute"), ("5T", "5-minute")):
        df = b.tf_dfs[(a.pair, tf)]
        rows, direction, li_ith, li_itl = _classify_window(df, start, end)
        dtxt = {1: "bullish (higher ITHs/ITLs)", -1: "bearish (lower ITHs/ITLs)",
                0: "indeterminate"}[direction]
        L += [f"## {name} structure", "",
              f"**Intermediate trend read: {dtxt}.**"]
        if li_ith:
            L.append(f"- last intact **ITH** {li_ith.price:.5f} (buy-side draw above)")
        if li_itl:
            L.append(f"- last intact **ITL** {li_itl.price:.5f} (sell-side pool below)")
        L += ["", "| time (UTC) | tier | price | swept? |", "|---|---|---|---|"]
        for ts, tier, price, swept in rows:
            mark = "✓ taken" if swept else "intact"
            L.append(f"| {ts:%m-%d %H:%M} | **{tier}** | {price:.5f} | {mark} |")
        if not rows:
            L.append("| — | — | (no confirmed swings in window) | — |")
        L += [""]

    # 2 · Entries the algo actually took in the window.
    L += ["## Entries the algorithm took (this window)", ""]
    if run_err:
        L += [f"⚠️ the full run raised `{run_err}` — structure above is still valid; "
              "entries/gates need the run to complete. Paste this and I'll fix.", ""]
    elif not trades:
        L += ["No entries — every candidate was rejected by a gate (see the funnel "
              "below). That's the algo being selective, not a bug.", ""]
    else:
        L += ["| opened (UTC) | dir | model | scenario | draw | target_type | swept PDH/PDL | result |",
              "|---|---|---|---|---|---|---|---|"]
        for t in trades:
            d = "long" if t["direction"] > 0 else "short"
            L.append(f"| {pd.Timestamp(t['opened_at']):%m-%d %H:%M} | {d} | "
                     f"{t.get('entry_model','?')} | {t.get('im_scenario','?')} | "
                     f"{t.get('draw_score','?')} | {t.get('target_type','?')} | "
                     f"{t.get('amd_swept_pdliq','?')} | {t.get('reason','open')} "
                     f"({t.get('pnl',0):+.0f}) |")
        L += [""]

    # 3 · Gate funnel — pipeline order first, then EVERY reject counter so the
    # exact gate that killed the setups is visible (cumulative over the period).
    order = ["checks", "in_killzone", "news_clear", "nfp_fomc_ok", "intermarket_signal",
             "pair_matches", "mss_h1_m15_m5_ok", "daily_bias_ok", "h1_bias_ok",
             "h4_bias_ok", "dealing_range_ok", "htf_draw_partial", "htf_draw_full_cascade",
             "htf_draw_counter", "consolidation_found", "manipulation_correct_dir",
             "m5_fvg_correct_dir", "target_found", "entry_blocked_min_target", "rr_ok",
             "risk_cap_ok", "risk_cap_skip", "units_nonzero", "limit_placed", "pyramid_added"]
    L += ["## Gate funnel — where setups die (cumulative over the fetched period)", "",
          "Pipeline order, then every reject counter. `htf_draw_counter` = killed by the "
          "0/3 draw gate; `entry_blocked_min_target` = target < the 30-pip floor; "
          "`risk_cap_skip` = stop too big for equity. The reject counter with the big "
          "number is the real bottleneck.", "", "```"]
    for k in order:
        if k in gate:
            L.append(f"  {k:28s} {gate[k]}")
    # anything else non-zero we didn't list explicitly
    extra = sorted(k for k, v in gate.items() if k not in order and v)
    if extra:
        L.append("  --- other non-zero counters ---")
        for k in extra:
            L.append(f"  {k:28s} {gate[k]}")
    L += ["```", ""]

    _write(L)
    print("\n".join(L))
    return 0


def _write(lines):
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())

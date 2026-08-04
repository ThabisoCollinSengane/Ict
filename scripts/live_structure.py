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


def _reject_section(rejects, title):
    """Markdown for the 'trades that couldn't be taken'. Splits the common
    no-MSS (structure never confirmed) from the post-MSS 'close calls' — real
    setups that formed and then hit a later gate."""
    from collections import Counter
    L = [f"## {title}", ""]
    if not rejects:
        return L + ["_None recorded._", ""]
    by_reason = Counter(r["reason"] for r in rejects)
    L += ["Why setups did **not** become trades (counts):", "",
          "| reason | count |", "|---|---|"]
    for reason, n in by_reason.most_common():
        L.append(f"| {reason} | {n} |")
    close = [r for r in rejects if not r["reason"].startswith("no MSS")]
    L += ["", f"**Close calls — {len(close)} setups that passed the structure shift "
          "but were blocked by a later gate:**", ""]
    if close:
        L += ["| time (UTC) | pair | dir | blocked by |", "|---|---|---|---|"]
        for r in sorted(close, key=lambda x: pd.Timestamp(x["t"]))[:60]:
            d = "long" if r["direction"] > 0 else "short"
            L.append(f"| {pd.Timestamp(r['t']):%m-%d %H:%M} | {r['pair']} | {d} | {r['reason']} |")
        if len(close) > 60:
            L.append(f"| … | | | (+{len(close) - 60} more) |")
    else:
        L.append("_None — every structure-confirmed setup that formed became a trade._")
    return L + [""]


def _list_trades(a, data, L):
    """Dump every trade over the fetched period + a per-day tally so the trending
    days (2+ entries) stand out. Then run --date on the best one for full detail."""
    pipsz = 0.01 if a.pair.endswith("JPY") else 0.0001
    try:
        b = bt.Backtester(data)
        b.run()
    except Exception as e:  # noqa: BLE001
        L += [f"ERROR: run failed — `{type(e).__name__}: {e}`"]; _write(L); print("\n".join(L)); return 1
    # entries on THIS pair only (not pyramid legs, not other pairs' trades)
    trades = [t for t in b.trades
              if t.get("pair") == a.pair and t.get("leg_idx", 1) == 1]
    L += [f"_all {len(trades)} {a.pair} entries over {a.period} · pips lot-independent · "
          f"ZAR shown at the run's lot; ×3 for 0.03 lots, ÷2 for 0.01_", "",
          "## Every entry (chronological)", "",
          "| opened (UTC) | dir | model | scenario | draw | lot | pips | ZAR | result |",
          "|---|---|---|---|---|---|---|---|---|"]
    per_day = {}
    for t in sorted(trades, key=lambda x: pd.Timestamp(x["opened_at"])):
        ts = pd.Timestamp(t["opened_at"]).tz_convert("UTC")
        d = "long" if t["direction"] > 0 else "short"
        pips = (t["exit"] - t["entry"]) * t["direction"] / pipsz
        lot = t.get("units", 0) / 100000.0
        day = ts.strftime("%Y-%m-%d")
        agg = per_day.setdefault(day, [0, 0.0, 0.0])
        agg[0] += 1; agg[1] += pips; agg[2] += t.get("pnl", 0)
        L.append(f"| {ts:%m-%d %H:%M} | {d} | {t.get('entry_model','?')} | "
                 f"{t.get('im_scenario','?')} | {t.get('draw_score','?')} | {lot:.2f} | "
                 f"{pips:+.1f} | {t.get('pnl',0):+.0f} | {t.get('reason','open')} |")
    L += ["", "## Per-day tally — the trending days (2+ entries) stand out", "",
          "| day | entries | net pips | net ZAR | at 0.03 lots |", "|---|---|---|---|---|"]
    for day in sorted(per_day):
        n, pp, zz = per_day[day]
        star = " ⭐" if n >= 2 else ""
        L.append(f"| {day}{star} | {n} | {pp:+.1f} | {zz:+.0f} | {pp*5.55:+.0f} |")
    L += ["", "_⭐ = multi-entry (trending) day. Run "
          "`bash run_live_structure.sh --pair " + a.pair + " --date <YYYY-MM-DD>` on one "
          "to see its structure + the gate funnel passing all the way to entry._", ""]
    L += _reject_section([r for r in getattr(b, "reject_log", []) if r.get("pair") == a.pair],
                         "Setups that couldn't be taken (whole period)")
    _write(L)
    print("\n".join(L))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", default="GBPUSD")
    ap.add_argument("--days", type=float, default=3.0, help="window = last N days of data")
    ap.add_argument("--date", default=None, help="YYYY-MM-DD — window = just that UTC day")
    ap.add_argument("--period", default="60d")
    ap.add_argument("--list", action="store_true",
                    help="dump EVERY trade over the period + per-day tally (find trending days)")
    a = ap.parse_args()

    L = [f"# Live structure + entries — {a.pair}", ""]
    print("fetching live 5m data via yfinance…")
    data = bt.fetch_data(period=a.period, interval="5m")
    if a.pair not in data or data[a.pair].empty:
        L.append(f"ERROR: no data for {a.pair} from yfinance.")
        _write(L); return 1

    if a.list:
        return _list_trades(a, data, L)

    if a.date:
        start = pd.Timestamp(a.date, tz="UTC")
        end = start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    else:
        end = data[a.pair].index.max()
        start = end - pd.Timedelta(days=a.days)
    L += [f"_data window: {start} → {end} (UTC) · classifier + gates are the real code_", ""]

    def _run(dslice):
        bb = bt.Backtester(dslice)
        bb.run()
        return bb

    # Build + run the full strategy. For --date, the funnel is scoped to THAT DAY
    # by diffing the cumulative gate at day-end minus day-start (counters only grow).
    trades, gate, run_err, b = [], {}, None, None
    funnel_scope = "cumulative over the fetched period"
    try:
        if a.date:
            b = _run({s: df[df.index <= end] for s, df in data.items()})
            g_end = dict(b.gate)
            b0 = _run({s: df[df.index < start] for s, df in data.items()})
            gate = {k: g_end.get(k, 0) - b0.gate.get(k, 0) for k in g_end}
            funnel_scope = f"**this day only** ({a.date}) — day-end minus day-start"
        else:
            b = _run(data)
            gate = dict(b.gate)
        trades = [t for t in b.trades if t.get("pair") == a.pair
                  and start <= pd.Timestamp(t["opened_at"]).tz_convert("UTC") <= end]
    except Exception as e:  # noqa: BLE001
        run_err = f"{type(e).__name__}: {e}"
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
        pipsz = 0.01 if a.pair.endswith("JPY") else 0.0001
        L += ["| opened (UTC) | dir | model | scenario | draw | lot | **pips** | **ZAR** | exit reason |",
              "|---|---|---|---|---|---|---|---|---|"]
        tot_pips = tot_zar = 0.0
        for t in trades:
            d = "long" if t["direction"] > 0 else "short"
            pips = (t["exit"] - t["entry"]) * t["direction"] / pipsz
            lot = t.get("units", 0) / 100000.0
            tot_pips += pips
            tot_zar += t.get("pnl", 0)
            L.append(f"| {pd.Timestamp(t['opened_at']):%m-%d %H:%M} | {d} | "
                     f"{t.get('entry_model','?')} | {t.get('im_scenario','?')} | "
                     f"{t.get('draw_score','?')} | {lot:.2f} | {pips:+.1f} | "
                     f"{t.get('pnl',0):+.0f} | {t.get('reason','open')} |")
        L += ["", f"_totals: {tot_pips:+.1f} pips · {tot_zar:+.0f} ZAR at the shown lot. "
              f"Pips are lot-independent — at **0.03 lots** (R5.55/pip) the day would be "
              f"**{tot_pips * 5.55:+.0f} ZAR**; at 0.01 lots (R1.85/pip) **{tot_pips * 1.85:+.0f} "
              f"ZAR**. 'exit reason' = stop covers both the −10-pip stop AND a trailing-stop "
              f"exit in profit._", ""]

    # 2b · Missed setups — the trades that couldn't be taken (this window).
    if not run_err and b is not None:
        rj = [r for r in getattr(b, "reject_log", []) if r.get("pair") == a.pair
              and start <= pd.Timestamp(r["t"]).tz_convert("UTC") <= end]
        L += _reject_section(rj, "Setups that couldn't be taken (this window)")

    # 3 · Gate funnel — pipeline order, then EVERY reject counter so the exact gate
    # that killed the setups is visible (cumulative over the period).
    order = ["checks", "in_killzone", "news_clear", "nfp_fomc_ok", "intermarket_signal",
             "pair_matches", "mss_h1_m15_m5_ok", "daily_bias_ok", "h1_bias_ok",
             "h4_bias_ok", "dealing_range_ok", "htf_draw_partial", "htf_draw_full_cascade",
             "htf_draw_counter", "consolidation_found", "manipulation_correct_dir",
             "m5_fvg_correct_dir", "target_found", "entry_blocked_min_target", "rr_ok",
             "risk_cap_ok", "risk_cap_skip", "units_nonzero", "entry_opened", "pyramid_added"]
    L += [f"## Gate funnel — where setups die ({funnel_scope})", "",
          "Pipeline order, then reject counters. `entry_opened` = trades actually opened "
          "(the real count — the old `limit_placed` was a dead counter). `htf_draw_counter` "
          "= killed by the 0/3 draw gate; `entry_blocked_min_target` = target < the 30-pip "
          "floor; `risk_cap_skip` = stop too big for equity. The reject counter with the big "
          "number is the real bottleneck.", "", "```"]
    for k in order:
        if k in gate:
            L.append(f"  {k:28s} {gate[k]}")
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

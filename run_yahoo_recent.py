#!/usr/bin/env python3
"""Replay the LAST FEW DAYS on Yahoo 5m data through the real strategy gates — to
see WHAT BLOCKED entries, and A/B the consolidation-range gate (current vs loosened)
so we can tell whether loosening it revives the Judas reversal frequency.

    python run_yahoo_recent.py [period]      # default 7d (~5 trading days)

Runs the base Backtester (same _maybe_open gate stack the live engine uses) TWICE on
the same data: once with the shipped consolidation gate, once loosened
(AMD_MIN_RANGE_BARS 8→4, AMD_MAX_RANGE_PIPS 35→50, AMD_MIN_TOUCHES 2→1). Reports both
funnels + trades side by side. Auto-pushes data/yahoo_recent_report.md.
Synthetic DXY is built from the real constituents so it's never falsely flat.
"""
from __future__ import annotations

import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)

FUNNEL = ["checks", "in_killzone", "drawdown_halt", "nfp_fomc_ok", "news_clear",
          "consolidation_found", "mss_h1_m15_m5_ok", "breakout_confirmed",
          "target_found", "units_nonzero", "risk_cap_ok", "risk_cap_skip",
          "entry_opened"]

LOOSE = {"AMD_MIN_RANGE_BARS": 4, "AMD_MAX_RANGE_PIPS": 50.0, "AMD_MIN_TOUCHES": 1}


def _publish(path, msg):
    def _git(*a):
        return subprocess.run(["git", *a], cwd=_ROOT, capture_output=True, text=True)
    _git("add", "-f", path)
    _git("commit", "-q", "-m", msg)
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    if _git("push", "origin", "HEAD").returncode == 0:
        print("RESULTS PUSHED — Claude can read", os.path.relpath(path, _ROOT))
    else:
        print("(auto-push failed — paste the report above to Claude)")


def _register_m1(bt, b, config):
    """Fetch Yahoo 1m for tradeable pairs → register as '1T' for faithful M1 stops."""
    try:
        import yfinance as yf
        import pandas as pd
        for sym in [p for p in config.PAIRS if p in bt.YF_TICKERS]:
            m1 = yf.download(bt.YF_TICKERS[sym], period="7d", interval="1m",
                             progress=False, auto_adjust=False)
            if m1 is None or m1.empty:
                continue
            if isinstance(m1.columns, pd.MultiIndex):
                m1.columns = m1.columns.get_level_values(0)
            m1 = m1[["Open", "High", "Low", "Close"]].dropna()
            m1.index = (m1.index.tz_localize("UTC") if m1.index.tz is None
                        else m1.index.tz_convert("UTC"))
            b.tf_dfs[(sym, "1T")] = m1
            b.tf_bars[(sym, "1T")] = bt.df_to_bars(m1)
            b.tf_index[(sym, "1T")] = m1.index
    except Exception as exc:
        print(f"  (1m fetch skipped: {exc})")


def _run_once(bt, config, data, label):
    b = bt.Backtester(data)
    _register_m1(bt, b, config)
    print(f"  replaying [{label}] ...")
    b.run()
    return b.gate, list(b.trades)


def _funnel_block(gate):
    L, prev = ["```"], None
    for k in FUNNEL:
        if k in gate:
            v = gate[k]
            L.append(f"{k:22s} {v:6d}" + ("" if prev is None else f"  ({v-prev:+d})"))
            prev = v
    L.append("```")
    return L


def _trades_block(trades):
    if not trades:
        return ["_(no trades)_"]
    import pandas as pd
    df = pd.DataFrame(trades)
    cols = [c for c in ["opened_at", "pair", "direction", "entry", "exit", "pnl",
                        "entry_model", "reason"] if c in df.columns]
    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    return [f"_{len(trades)} trades, {wins} wins, net "
            f"{sum(t.get('pnl',0) for t in trades):+.1f} ZAR_", "",
            "```", df[cols].to_string(index=False), "```"]


def _entry_breakdown(trades):
    """Group trades by model family (base judas/breakout vs MM) with count+P&L."""
    fam = {}
    for t in trades:
        et = str(t.get("entry_type", ""))
        em = str(t.get("entry_model", ""))
        if em == "mm_standalone" or et.startswith(("mm_", "mmstd_")):
            key = "MM standalone/adds"
        else:
            key = f"base {em or '?'}"
        d = fam.setdefault(key, {"n": 0, "w": 0, "pnl": 0.0})
        d["n"] += 1
        d["w"] += 1 if t.get("pnl", 0) > 0 else 0
        d["pnl"] += t.get("pnl", 0)
    L = ["| model | trades | wins | net ZAR |", "|---|---|---|---|"]
    for k, d in sorted(fam.items()):
        L.append(f"| {k} | {d['n']} | {d['w']} | {d['pnl']:+.1f} |")
    return L


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("period", nargs="?", default="7d")
    ap.add_argument("--full", action="store_true",
                    help="single run of the WHOLE algo as configured by env (base + "
                         "MM if MM_*_ENABLED set), instead of the consolidation A/B")
    a = ap.parse_args()
    period = a.period
    import backtest as bt
    import config

    print(f"=== fetching Yahoo 5m ({period}) — all symbols ===")
    data = bt.fetch_data(period=period, interval="5m")
    if "EURUSD" not in data or "GBPUSD" not in data:
        print("ERROR: primary pairs missing from Yahoo (rate-limited? retry).")
        return 1

    if a.full:
        gate, trades = _run_once(bt, config, data, "full algo (base + MM)")
        span = ""
        try:
            idx = data["EURUSD"].index
            span = f"{idx.min()} → {idx.max()} ({len(idx)} 5m bars)"
        except Exception:
            pass
        wd = getattr(config, "WITHDRAW_SCHEDULE", False) or getattr(config, "WITHDRAW_AT", 0)
        flags = (f"STARTING_CASH={config.STARTING_CASH} · "
                 f"MM_standalone={int(config.MM_STANDALONE_ENABLED)} · "
                 f"MM_continuation={int(config.MM_CONTINUATION_ENABLED)} · "
                 f"SMT_req={int(config.MM_HTF_SMT_REQUIRED)} · withdraw={int(bool(wd))}")
        L = [f"# Yahoo replay — WHOLE algo (base + MM), last {period}", "",
             f"_data span: {span}_", f"_{flags}_", "",
             "## Trades by model", ""] + _entry_breakdown(trades)
        L += ["", "## Gate funnel", ""] + _funnel_block(gate)
        # MM-specific counters
        mm = sorted(((k, v) for k, v in gate.items()
                     if k.startswith("mm_") and v), key=lambda kv: kv[1], reverse=True)
        if mm:
            L += ["", "## MM counters", "", "```"] + [f"{k:26s} {v}" for k, v in mm] + ["```"]
        L += ["", "## All trades", ""] + _trades_block(trades)
        text = "\n".join(L) + "\n"
        out = os.path.join(_ROOT, "data", "yahoo_recent_report.md")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w").write(text)
        print(text)
        _publish(out, f"Yahoo full-algo replay ({period}, cash={config.STARTING_CASH})")
        return 0

    # arm 1: shipped consolidation gate
    gate_cur, tr_cur = _run_once(bt, config, data, "current gate")
    # arm 2: loosened consolidation gate (mutate config in-process; detect_amd reads it live)
    for k, v in LOOSE.items():
        setattr(config, k, v)
    gate_loose, tr_loose = _run_once(bt, config, data, "loosened gate")

    span = ""
    try:
        idx = data["EURUSD"].index
        span = f"{idx.min()} → {idx.max()} ({len(idx)} 5m bars)"
    except Exception:
        pass

    L = [f"# Yahoo replay — consolidation gate A/B (last {period})", "",
         f"_data span: {span}_", "",
         "Same live gate stack, run twice: shipped gate vs loosened "
         "(MIN_RANGE_BARS 8→4, MAX_RANGE_PIPS 35→50, MIN_TOUCHES 2→1). More "
         "`consolidation_found` = more Judas-reversal opportunities.", "",
         "## Current (shipped) gate", ""]
    L += _funnel_block(gate_cur) + [""] + _trades_block(tr_cur)
    L += ["", "## Loosened consolidation gate", ""]
    L += _funnel_block(gate_loose) + [""] + _trades_block(tr_loose)
    L += ["", "## Read", "",
          f"- consolidation_found: **{gate_cur.get('consolidation_found',0)} → "
          f"{gate_loose.get('consolidation_found',0)}**  "
          f"(entries: {gate_cur.get('entry_opened',0)} → {gate_loose.get('entry_opened',0)})",
          "- More entries with comparable win-quality = loosen it live. More entries "
          "but the new ones lose = the tight coil was doing real work."]

    text = "\n".join(L) + "\n"
    out = os.path.join(_ROOT, "data", "yahoo_recent_report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(text)
    print(text)
    _publish(out, f"Yahoo consolidation-gate A/B ({period})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

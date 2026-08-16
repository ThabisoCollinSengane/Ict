#!/usr/bin/env python3
"""Replay the LAST FEW DAYS on Yahoo 5m data through the real strategy gates — to
see exactly WHAT BLOCKED entries (the "algo hasn't traded in N days" diagnosis).

    python run_yahoo_recent.py [period]      # default 7d (covers ~5 trading days)

Yahoo intraday history is ~60d max at 5m and ~7d at 1m. This fetches 5m for every
symbol (primary pairs + the DXY constituents, so synthetic DXY is real, not flat)
and 1m for the tradeable pairs (faithful M1 stops), runs the base Backtester (same
_maybe_open gate stack the live engine uses), and prints + pushes the gate funnel.
The gate where the count COLLAPSES is the blocker. Auto-pushes data/yahoo_recent_report.md.
"""
from __future__ import annotations

import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)

# pipeline order — the count drop-off between adjacent stages = the bottleneck gate
FUNNEL = ["checks", "in_killzone", "drawdown_halt", "daily_loss_halt",
          "consec_loss_pause", "nfp_fomc_ok", "news_clear", "consolidation_found",
          "mss_h1_m15_m5_ok", "draw_cascade_ok", "target_found", "units_nonzero",
          "risk_cap_ok", "entry_opened"]


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


def main():
    period = sys.argv[1] if len(sys.argv) > 1 else "7d"
    import backtest as bt
    import config

    print(f"=== fetching Yahoo 5m ({period}) — all symbols ===")
    data = bt.fetch_data(period=period, interval="5m")
    if "EURUSD" not in data or "GBPUSD" not in data:
        print("ERROR: primary pairs missing from Yahoo (rate-limited? try again).")
        return 1

    b = bt.Backtester(data)

    # faithful M1 stops: fetch 1m for the tradeable pairs and register as "1T"
    try:
        import yfinance as yf
        for sym in [p for p in config.PAIRS if p in bt.YF_TICKERS]:
            m1 = yf.download(bt.YF_TICKERS[sym], period="7d", interval="1m",
                             progress=False, auto_adjust=False)
            if m1 is None or m1.empty:
                continue
            import pandas as pd
            if isinstance(m1.columns, pd.MultiIndex):
                m1.columns = m1.columns.get_level_values(0)
            m1 = m1[["Open", "High", "Low", "Close"]].dropna()
            m1.index = (m1.index.tz_localize("UTC") if m1.index.tz is None
                        else m1.index.tz_convert("UTC"))
            b.tf_dfs[(sym, "1T")] = m1
            b.tf_bars[(sym, "1T")] = bt.df_to_bars(m1)
            b.tf_index[(sym, "1T")] = m1.index
        print("  1m registered for M1 stops")
    except Exception as exc:
        print(f"  (1m fetch skipped: {exc} — M1 stops fall back)")

    print("=== replaying through the live gate stack ===")
    b.run()

    g = b.gate
    span = ""
    try:
        idx = data["EURUSD"].index
        span = f"{idx.min()} → {idx.max()}  ({len(idx)} 5m bars)"
    except Exception:
        pass

    L = [f"# Yahoo recent replay — what blocked (last {period})", "",
         f"_data span: {span}_", "",
         "Same `_maybe_open` gate stack as the live engine. The gate where the count "
         "COLLAPSES to ~0 is what's blocking entries.", "",
         "## Gate funnel (pipeline order)", "", "```"]
    prev = None
    for k in FUNNEL:
        if k in g:
            v = g[k]
            drop = "" if prev is None else f"   ({v - prev:+d})"
            L.append(f"{k:24s} {v:6d}{drop}")
            prev = v
    L.append("```")
    # any counters not in the pipeline list (extra gates), largest first
    extra = sorted(((k, v) for k, v in g.items() if k not in FUNNEL and v),
                   key=lambda kv: kv[1], reverse=True)
    if extra:
        L += ["", "## Other gate counters", "", "```"]
        L += [f"{k:28s} {v}" for k, v in extra]
        L.append("```")
    L += ["", f"## Trades opened: {len(b.trades)}"]
    if b.trades:
        import pandas as pd
        df = pd.DataFrame(b.trades)
        cols = [c for c in ["opened_at", "pair", "direction", "entry", "exit",
                            "pnl", "entry_model", "reason"] if c in df.columns]
        L += ["", "```", df[cols].to_string(index=False), "```"]
    else:
        # find the bottleneck: last stage with count, first that dropped to 0
        block = None
        prev = None
        for k in FUNNEL:
            if k in g:
                if g[k] == 0 and prev is not None:
                    block = k
                    break
                prev = k
        L += ["", f"**No trades. Bottleneck gate: `{block or 'see funnel'}`** — the "
              "stage right before the count hits 0 is passing; this one isn't. If "
              "`checks` itself is 0, the window had no killzone bars / no data."]

    text = "\n".join(L) + "\n"
    out = os.path.join(_ROOT, "data", "yahoo_recent_report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(text)
    print(text)
    _publish(out, f"Yahoo recent replay ({period}) — what blocked")
    return 0


if __name__ == "__main__":
    sys.exit(main())

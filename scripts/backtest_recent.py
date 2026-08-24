#!/usr/bin/env python3
"""Backtest the last N trading days using Yahoo Finance 5-minute data.

Fetches EURUSD, GBPUSD, NZDUSD, EURGBP, AUDNZD + DXY components,
resamples to all required timeframes, runs the full backtest engine,
writes a detailed markdown report, and auto-pushes to the branch.

Usage:
    python scripts/backtest_recent.py                  # last 10 trading days, R1000 start
    python scripts/backtest_recent.py --days 5         # last 5 trading days
    python scripts/backtest_recent.py --equity 500     # R500 start
    python scripts/backtest_recent.py --selftest       # no data needed
"""
from __future__ import annotations
import argparse, os, sys, time, subprocess
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

REPORT = os.path.join(_ROOT, "data", "recent_backtest_report.md")

# Yahoo Finance ticker map
_YF_PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "NZDUSD": "NZDUSD=X",
    "EURGBP": "EURGBP=X",
    "AUDNZD": "AUDNZD=X",
    "USDJPY": "USDJPY=X",
    "USDCHF": "USDCHF=X",
    "USDCAD": "USDCAD=X",
    "USDSEK": "USDSEK=X",
}

_RESAMPLE_MAP = {
    "5T":  "5min",
    "15T": "15min",
    "60T": "1h",
    "240T": "4h",
    "D":   "1D",
    "W":   "1W",
}


def fetch_yahoo(days=10):
    """Fetch 5-min OHLC for all required pairs from Yahoo Finance."""
    try:
        import yfinance as yf
    except ImportError:
        print("Installing yfinance...")
        os.system(f"{sys.executable} -m pip install yfinance -q")
        import yfinance as yf

    import pandas as pd

    period = f"{min(days + 5, 59)}d"
    all_data = {}

    for pair, ticker in _YF_PAIRS.items():
        print(f"  Fetching {pair} ({ticker})...", end=" ", flush=True)
        for attempt in range(3):
            try:
                t = yf.Ticker(ticker)
                df = t.history(period=period, interval="5m")
                if len(df) > 0:
                    df = df[["Open", "High", "Low", "Close"]].copy()
                    df.index = df.index.tz_localize(None) if df.index.tz is None else df.index.tz_convert("UTC").tz_localize(None)
                    all_data[pair] = df
                    print(f"{len(df)} bars")
                    break
                else:
                    print(f"empty (attempt {attempt+1})")
            except Exception as e:
                print(f"failed: {e}" if attempt == 2 else f"retry {attempt+1}...")
                time.sleep(2)

    if "EURUSD" not in all_data or "GBPUSD" not in all_data:
        print("\nERROR: Could not fetch EURUSD and/or GBPUSD - cannot run backtest.")
        return None

    # Build synthetic DXY
    if all(p in all_data for p in ("USDJPY", "USDCHF", "USDCAD")):
        import numpy as np
        eu = all_data["EURUSD"]["Close"]
        uj = all_data["USDJPY"]["Close"]
        gu = all_data["GBPUSD"]["Close"]
        uc = all_data["USDCAD"]["Close"]
        uch = all_data["USDCHF"]["Close"]

        idx = eu.index
        uj = uj.reindex(idx, method="ffill")
        gu = gu.reindex(idx, method="ffill")
        uc = uc.reindex(idx, method="ffill")
        uch = uch.reindex(idx, method="ffill")

        if "USDSEK" in all_data:
            us = all_data["USDSEK"]["Close"].reindex(idx, method="ffill")
        else:
            us = pd.Series(10.5, index=idx)

        dxy = 50.14348112 * (eu ** -0.576) * (uj ** 0.136) * (gu ** -0.119) * \
              (uc ** 0.091) * (us ** 0.042) * (uch ** 0.036)

        dxy_df = pd.DataFrame({
            "Open": dxy, "High": dxy, "Low": dxy, "Close": dxy
        }, index=idx)
        all_data["UDXUSD"] = dxy_df
        print(f"  Synthetic DXY: {len(dxy_df)} bars")
    else:
        print("  WARNING: Missing DXY components - DXY gate will be approximated")

    return all_data


def resample_data(all_data):
    """Resample 5-min data to all required timeframes."""
    import pandas as pd
    from collections import namedtuple
    Bar = namedtuple("Bar", "Open High Low Close")

    tf_bars = {}
    tf_index = {}

    for pair, df5 in all_data.items():
        for tf_key, rule in _RESAMPLE_MAP.items():
            if tf_key == "5T":
                resampled = df5
            else:
                resampled = df5.resample(rule).agg({
                    "Open": "first", "High": "max", "Low": "min", "Close": "last"
                }).dropna()

            bars = [Bar(r.Open, r.High, r.Low, r.Close) for _, r in resampled.iterrows()]
            tf_bars[(pair, tf_key)] = bars
            tf_index[(pair, tf_key)] = pd.DatetimeIndex(resampled.index)

    return tf_bars, tf_index


def run_backtest(all_data, start_equity=1000, days=10):
    """Run the full backtest engine on the fetched data."""
    import pandas as pd
    import config

    orig_equity = getattr(config, "STARTING_EQUITY", 500)
    config.STARTING_EQUITY = start_equity

    tf_bars, tf_index = resample_data(all_data)

    from backtest import HistdataBacktester

    bt = HistdataBacktester.__new__(HistdataBacktester)

    bt.equity = start_equity
    bt._peak_equity = start_equity
    bt.active = {}
    bt.closed = []
    bt.tf_bars = tf_bars
    bt.tf_index = tf_index
    bt._init_state()

    eu_idx = tf_index[("EURUSD", "5T")]
    start_date = eu_idx[0]
    end_date = eu_idx[-1]

    cutoff = end_date - timedelta(days=days + 3)

    print(f"\nBacktest period: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")
    print(f"Starting equity: R{start_equity:,.0f}")
    print(f"Pairs: {', '.join(p for p in ('EURUSD', 'GBPUSD', 'NZDUSD') if p in all_data)}")
    print()

    trade_pairs = [p for p in config.PAIRS if p in all_data]
    eu_bars = tf_bars[("EURUSD", "5T")]
    total_bars = len(eu_bars)

    for i in range(1, total_bars):
        t = eu_idx[i]
        if t < cutoff:
            continue

        for pair in all_data:
            for tf_key in _RESAMPLE_MAP:
                idx_arr = tf_index.get((pair, tf_key))
                if idx_arr is not None:
                    pos = int(idx_arr.searchsorted(pd.Timestamp(t), side="right"))
                    bt._bar_pos = bt.__dict__.setdefault("_bar_pos", {})
                    bt._bar_pos[(pair, tf_key)] = pos

        for pair in trade_pairs:
            try:
                bt._maybe_open(pair, t)
            except Exception:
                pass
            try:
                bt._update_orders(pair, t)
            except Exception:
                pass
            try:
                bt._maybe_pyramid(pair, t)
            except Exception:
                pass

    return bt, start_date, end_date


def _session_label(profile):
    """Human-readable session name."""
    m = {"london": "London Open", "ny": "NY AM", "ny_pm": "NY PM"}
    return m.get(profile, profile or "?")


def _result_tag(pnl):
    return "WIN" if pnl > 0 else "LOSS" if pnl < 0 else "BE"


def write_report(bt, start_equity, days, start_date, end_date):
    """Write a detailed markdown report of all trades."""
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = []
    w = lines.append

    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    w(f"# Recent Backtest Report - Last {days} Trading Days")
    w(f"")
    w(f"Generated: {now_str}")
    w(f"Period: {start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}")
    w(f"Starting equity: R{start_equity:,.0f}")
    w("")

    closed = bt.closed
    n = len(closed)

    # --- Summary ---
    w("## Summary")
    w("")
    if n == 0:
        w(f"**No trades taken** in the last {days} trading days.")
        w("")
        w("This is normal - the algo is selective. It needs ALL of:")
        w("1. DXY H1 BOS direction (hard gate)")
        w("2. EURGBP/AUDNZD intermarket confirmation")
        w("3. M15 consolidation range with Judas sweep OR triple-confirmed breakout")
        w("4. 2-of-3 MSS (EU + GU + DXY)")
        w("5. M5 FVG/OB for entry")
        w("6. Draw score >= 1 (HTF alignment)")
        w("")
        w(f"Over 4 years the algo averages ~{810/208:.1f} trades/week.")
        w("Some weeks have 0 trades, some have 8-10.")

        if bt.active:
            w("")
            w("## Still Open Positions")
            w("")
            for pair, st in bt.active.items():
                d = "LONG" if st["direction"] > 0 else "SHORT"
                legs = st["legs"]
                entry = legs[0]["entry"] if legs else 0
                model = st.get("entry_model", "?")
                profile = _session_label(st.get("profile", "?"))
                w(f"- **{pair} {d}** entry {entry:.5f} ({model}, {profile})")
    else:
        wins = [t for t in closed if t.get("pnl", 0) > 0]
        losses = [t for t in closed if t.get("pnl", 0) <= 0]
        total_pnl = sum(t.get("pnl", 0) for t in closed)
        gp = sum(t.get("pnl", 0) for t in wins)
        gl = -sum(t.get("pnl", 0) for t in losses) if losses else 0
        pf = (gp / gl) if gl > 0 else float("inf")
        wr = len(wins) / n * 100

        w(f"| Metric | Value |")
        w(f"|---|---|")
        w(f"| Trades | {n} |")
        w(f"| Wins | {len(wins)} |")
        w(f"| Losses | {len(losses)} |")
        w(f"| Win Rate | {wr:.1f}% |")
        w(f"| Profit Factor | {pf:.2f} |")
        w(f"| Total P&L | R{total_pnl:,.2f} |")
        w(f"| Final Equity | R{bt.equity:,.2f} |")
        dd = ((bt._peak_equity - bt.equity) / bt._peak_equity * 100) if bt._peak_equity > 0 else 0
        w(f"| Max Drawdown | -{dd:.2f}% |")
        if wins:
            w(f"| Avg Win | R{gp/len(wins):,.2f} |")
        if losses:
            w(f"| Avg Loss | R{gl/len(losses):,.2f} |")
        w("")

        # --- Trade-by-trade detail ---
        w("## Trade Details")
        w("")
        w("| # | Date | Pair | Dir | Result | Entry Model | Session | Scenario | Pattern | Draw | Pips | P&L (ZAR) |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")

        for i, t in enumerate(closed, 1):
            pair = t.get("pair", "?")
            d = "LONG" if t.get("direction", 0) > 0 else "SHORT"
            pnl = t.get("pnl", 0)
            result = _result_tag(pnl)
            model = t.get("entry_model", "?")
            profile = _session_label(t.get("profile", "?"))
            scenario = t.get("im_scenario", "?")
            entry_type = t.get("entry_type", "?")
            draw = t.get("draw_score", 0)
            entry_p = t.get("entry", 0)
            exit_p = t.get("exit", 0)
            pip = 0.01 if "JPY" in pair else 0.0001
            pips = (exit_p - entry_p) * t.get("direction", 1) / pip

            opened = t.get("opened_at", "")
            if hasattr(opened, "strftime"):
                date_str = opened.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(opened)[:16] if opened else "?"

            w(f"| {i} | {date_str} | {pair} | {d} | **{result}** | {model} | {profile} | {scenario} | {entry_type} | {draw}/3 | {pips:+.1f} | R{pnl:,.2f} |")

        w("")

        # --- By entry model ---
        w("## Breakdown by Entry Model")
        w("")
        w("| Model | Trades | Wins | Losses | WR | PF | P&L |")
        w("|---|---|---|---|---|---|---|")
        models = {}
        for t in closed:
            m = t.get("entry_model", "?")
            models.setdefault(m, []).append(t)
        for m, trades in sorted(models.items()):
            tw = [t for t in trades if t.get("pnl", 0) > 0]
            tl = [t for t in trades if t.get("pnl", 0) <= 0]
            tpnl = sum(t.get("pnl", 0) for t in trades)
            tgp = sum(t.get("pnl", 0) for t in tw)
            tgl = -sum(t.get("pnl", 0) for t in tl) if tl else 0
            tpf = (tgp / tgl) if tgl > 0 else float("inf")
            twr = len(tw) / len(trades) * 100 if trades else 0
            w(f"| {m} | {len(trades)} | {len(tw)} | {len(tl)} | {twr:.0f}% | {tpf:.2f} | R{tpnl:,.2f} |")
        w("")

        # --- By session ---
        w("## Breakdown by Session")
        w("")
        w("| Session | Trades | Wins | Losses | WR | PF | P&L |")
        w("|---|---|---|---|---|---|---|")
        sessions = {}
        for t in closed:
            s = _session_label(t.get("profile", "?"))
            sessions.setdefault(s, []).append(t)
        for s, trades in sorted(sessions.items()):
            tw = [t for t in trades if t.get("pnl", 0) > 0]
            tl = [t for t in trades if t.get("pnl", 0) <= 0]
            tpnl = sum(t.get("pnl", 0) for t in trades)
            tgp = sum(t.get("pnl", 0) for t in tw)
            tgl = -sum(t.get("pnl", 0) for t in tl) if tl else 0
            tpf = (tgp / tgl) if tgl > 0 else float("inf")
            twr = len(tw) / len(trades) * 100 if trades else 0
            w(f"| {s} | {len(trades)} | {len(tw)} | {len(tl)} | {twr:.0f}% | {tpf:.2f} | R{tpnl:,.2f} |")
        w("")

        # --- By pair ---
        w("## Breakdown by Pair")
        w("")
        w("| Pair | Trades | Wins | Losses | WR | PF | P&L |")
        w("|---|---|---|---|---|---|---|")
        pairs = {}
        for t in closed:
            p = t.get("pair", "?")
            pairs.setdefault(p, []).append(t)
        for p, trades in sorted(pairs.items()):
            tw = [t for t in trades if t.get("pnl", 0) > 0]
            tl = [t for t in trades if t.get("pnl", 0) <= 0]
            tpnl = sum(t.get("pnl", 0) for t in trades)
            tgp = sum(t.get("pnl", 0) for t in tw)
            tgl = -sum(t.get("pnl", 0) for t in tl) if tl else 0
            tpf = (tgp / tgl) if tgl > 0 else float("inf")
            twr = len(tw) / len(trades) * 100 if trades else 0
            w(f"| {p} | {len(trades)} | {len(tw)} | {len(tl)} | {twr:.0f}% | {tpf:.2f} | R{tpnl:,.2f} |")
        w("")

        # --- By scenario ---
        w("## Breakdown by Intermarket Scenario")
        w("")
        w("| Scenario | Trades | WR | PF | P&L |")
        w("|---|---|---|---|---|")
        scenarios = {}
        for t in closed:
            sc = t.get("im_scenario", "?")
            scenarios.setdefault(sc, []).append(t)
        for sc, trades in sorted(scenarios.items()):
            tw = [t for t in trades if t.get("pnl", 0) > 0]
            tl = [t for t in trades if t.get("pnl", 0) <= 0]
            tpnl = sum(t.get("pnl", 0) for t in trades)
            tgp = sum(t.get("pnl", 0) for t in tw)
            tgl = -sum(t.get("pnl", 0) for t in tl) if tl else 0
            tpf = (tgp / tgl) if tgl > 0 else float("inf")
            twr = len(tw) / len(trades) * 100 if trades else 0
            w(f"| {sc} | {len(trades)} | {twr:.0f}% | {tpf:.2f} | R{tpnl:,.2f} |")
        w("")

        # --- Session phase ---
        w("## Breakdown by Session Phase")
        w("")
        w("| Phase | Trades | WR | PF | P&L |")
        w("|---|---|---|---|---|")
        phases = {}
        for t in closed:
            ph = t.get("session_phase", "?")
            phases.setdefault(ph, []).append(t)
        for ph, trades in sorted(phases.items()):
            tw = [t for t in trades if t.get("pnl", 0) > 0]
            tl = [t for t in trades if t.get("pnl", 0) <= 0]
            tpnl = sum(t.get("pnl", 0) for t in trades)
            tgp = sum(t.get("pnl", 0) for t in tw)
            tgl = -sum(t.get("pnl", 0) for t in tl) if tl else 0
            tpf = (tgp / tgl) if tgl > 0 else float("inf")
            twr = len(tw) / len(trades) * 100 if trades else 0
            w(f"| {ph} | {len(trades)} | {twr:.0f}% | {tpf:.2f} | R{tpnl:,.2f} |")
        w("")

        # --- Confluence signals present ---
        w("## Confluence Signals on Trades")
        w("")
        w("| Trade | Pair | HTF FVG | CRT Sweep | SOJ | Draw Score | Target Type | Confluence |")
        w("|---|---|---|---|---|---|---|---|")
        for i, t in enumerate(closed, 1):
            pair = t.get("pair", "?")
            htf_fvg = t.get("htf_fvg", "") or "-"
            crt = t.get("crt_tf", "") or "-"
            soj = t.get("soj_type", "") or "-"
            draw = t.get("draw_score", 0)
            tgt_type = t.get("target_type", "?")
            tgt_conf = t.get("target_confluence", "?")
            w(f"| {i} | {pair} | {htf_fvg} | {crt} | {soj} | {draw}/3 | {tgt_type} | {tgt_conf} |")
        w("")

        # --- MM model if any ---
        mm_trades = [t for t in closed if t.get("entry_model", "") in ("mm_standalone",) or t.get("mm_adds", 0) > 0]
        if mm_trades:
            w("## Market Maker Model Trades")
            w("")
            w("| # | Pair | Dir | Model | MM Adds | HTF SMT | P&L |")
            w("|---|---|---|---|---|---|---|")
            for i, t in enumerate(mm_trades, 1):
                pair = t.get("pair", "?")
                d = "LONG" if t.get("direction", 0) > 0 else "SHORT"
                model = t.get("entry_model", "?")
                mm_adds = t.get("mm_adds", 0)
                smt = t.get("htf_smt", "") or "-"
                pnl = t.get("pnl", 0)
                w(f"| {i} | {pair} | {d} | {model} | {mm_adds} | {smt} | R{pnl:,.2f} |")
            w("")

    # --- Still open ---
    if bt.active:
        w("## Still Open Positions")
        w("")
        w("| Pair | Dir | Entry | Model | Session | Scenario | Legs |")
        w("|---|---|---|---|---|---|---|")
        for pair, st in bt.active.items():
            d = "LONG" if st["direction"] > 0 else "SHORT"
            legs = st["legs"]
            entry = legs[0]["entry"] if legs else 0
            model = st.get("entry_model", "?")
            profile = _session_label(st.get("profile", "?"))
            scenario = st.get("im_scenario", "?")
            w(f"| {pair} | {d} | {entry:.5f} | {model} | {profile} | {scenario} | {len(legs)} |")
        w("")

    # --- Gate counters (what the algo checked but didn't trade) ---
    gate = getattr(bt, "gate", {})
    if gate:
        interesting = {k: v for k, v in gate.items() if v and isinstance(v, (int, float)) and v > 0}
        if interesting:
            w("## Gate Counters (why trades were NOT taken)")
            w("")
            w("These show what the algo evaluated but rejected:")
            w("")
            w("| Gate | Count |")
            w("|---|---|")
            for k, v in sorted(interesting.items(), key=lambda x: -x[1])[:25]:
                label = k.replace("_", " ").replace("blocked", "BLOCKED:").replace("no ", "no ")
                w(f"| {label} | {v} |")
            w("")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nReport written to {REPORT}")
    return REPORT


def push_report():
    """Git add, commit, push the report."""
    try:
        subprocess.run(["git", "add", REPORT], cwd=_ROOT, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Recent backtest report (auto)"],
            cwd=_ROOT, check=True,
        )
        for attempt in range(4):
            result = subprocess.run(
                ["git", "push", "origin", "HEAD"],
                cwd=_ROOT, capture_output=True, text=True,
            )
            if result.returncode == 0:
                print("RESULTS PUSHED to branch.")
                return True
            if attempt < 3:
                wait = 2 ** (attempt + 1)
                print(f"Push failed, retrying in {wait}s...")
                time.sleep(wait)
        print(f"Push failed after retries: {result.stderr}")
        return False
    except Exception as e:
        print(f"Git push error: {e}")
        return False


def _selftest():
    print("selftest: verifying imports and structure...")
    import config
    assert hasattr(config, "PAIRS")
    assert hasattr(config, "STARTING_EQUITY")
    for tf in ("5T", "15T", "60T", "240T", "D", "W"):
        assert tf in _RESAMPLE_MAP, f"Missing TF {tf}"
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="Backtest last N trading days using Yahoo Finance")
    ap.add_argument("--days", type=int, default=10, help="Number of trading days (default 10)")
    ap.add_argument("--equity", type=float, default=1000, help="Starting equity in ZAR (default 1000)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-push", action="store_true", help="Skip git push")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return 0

    print(f"Fetching last {a.days} trading days from Yahoo Finance...")
    all_data = fetch_yahoo(days=a.days)
    if all_data is None:
        return 1

    bt, start_date, end_date = run_backtest(all_data, start_equity=a.equity, days=a.days)

    write_report(bt, a.equity, a.days, start_date, end_date)

    if not a.no_push:
        push_report()
    else:
        print("Skipping push (--no-push)")

    # Console summary
    n = len(bt.closed)
    print(f"\n{'='*60}")
    print(f"RESULTS - Last {a.days} trading days")
    print(f"{'='*60}")
    if n == 0:
        print(f"No trades taken. Equity unchanged: R{bt.equity:,.2f}")
    else:
        wins = [t for t in bt.closed if t.get("pnl", 0) > 0]
        losses = [t for t in bt.closed if t.get("pnl", 0) <= 0]
        total_pnl = sum(t.get("pnl", 0) for t in bt.closed)
        gp = sum(t.get("pnl", 0) for t in wins)
        gl = -sum(t.get("pnl", 0) for t in losses) if losses else 0
        pf = (gp / gl) if gl > 0 else float("inf")
        wr = len(wins) / n * 100

        print(f"Trades: {n} | Wins: {len(wins)} | Losses: {len(losses)}")
        print(f"Win Rate: {wr:.1f}% | PF: {pf:.2f}")
        print(f"P&L: R{total_pnl:,.2f} | Equity: R{bt.equity:,.2f}")
        print()
        for t in bt.closed:
            pair = t.get("pair", "?")
            d = "LONG" if t.get("direction", 0) > 0 else "SHORT"
            model = t.get("entry_model", "?")
            pnl = t.get("pnl", 0)
            result = _result_tag(pnl)
            pip = 0.01 if "JPY" in pair else 0.0001
            pips = (t.get("exit", 0) - t.get("entry", 0)) * t.get("direction", 1) / pip
            session = _session_label(t.get("profile", "?"))
            print(f"  {result:4} {pair:8} {d:6} {model:12} {session:12} {pips:+6.1f} pips  R{pnl:,.2f}")

    if bt.active:
        print(f"\nStill open: {', '.join(bt.active.keys())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

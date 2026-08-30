#!/usr/bin/env python3
"""Backtest study: MM standalone filtered to user's preferred directions.

SELL GBPUSD (dollar UP) + BUY EURUSD (dollar DOWN) only.
Measures WR/PF/MaxDD on the 4-year histdata to validate the directional
filter before going semi-auto live.

Usage (from repo root):
    python scripts/mm_directional_study.py --years 2022 2023 2024 2025
    python scripts/mm_directional_study.py --years 2022 2023           # IS only
    python scripts/mm_directional_study.py --years 2024 2025           # OOS only

Requires histdata CSVs in data/histdata/.
Writes report to data/mm_directional_report.md and auto-pushes.
"""
from __future__ import annotations
import argparse, os, sys, time, subprocess

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

REPORT = os.path.join(_ROOT, "data", "mm_directional_report.md")

PREFERRED = {
    "GBPUSD": -1,  # SELL only
    "EURUSD": +1,  # BUY only
}


def run_study(years):
    """Run 3 backtests: baseline (no MM), MM all-directions, MM filtered."""
    import config

    # Save original config
    orig_mm_standalone = os.environ.get("MM_STANDALONE_ENABLED")
    orig_mm_cont = os.environ.get("MM_CONTINUATION_ENABLED")

    results = {}

    # --- ARM 1: Baseline (MM OFF) ---
    print("\n=== ARM 1: Baseline (MM OFF) ===")
    os.environ["MM_STANDALONE_ENABLED"] = "0"
    os.environ["MM_CONTINUATION_ENABLED"] = "0"
    import importlib
    importlib.reload(config)
    from run_backtest_histdata import run as run_bt
    bt_base = run_bt(years)
    results["baseline"] = _extract(bt_base, "baseline")

    # --- ARM 2: MM standalone ON, all directions ---
    print("\n=== ARM 2: MM standalone ON (all directions) ===")
    os.environ["MM_STANDALONE_ENABLED"] = "1"
    os.environ["MM_CONTINUATION_ENABLED"] = "0"
    importlib.reload(config)
    bt_all = run_bt(years)
    results["mm_all"] = _extract(bt_all, "mm_all")

    # --- ARM 3: MM standalone ON, filtered to preferred directions ---
    # We can't directly filter in the engine without modifying it,
    # so we'll analyse the trades from ARM 2 post-hoc
    all_trades = getattr(bt_all, "trades", [])
    mm_trades = [t for t in all_trades if t.get("entry_model") == "mm_standalone"]

    # Split into preferred vs non-preferred
    pref_trades = []
    nonpref_trades = []
    for t in mm_trades:
        pair = t.get("pair", "")
        d = t.get("direction", 0)
        if PREFERRED.get(pair) == d:
            pref_trades.append(t)
        else:
            nonpref_trades.append(t)

    results["mm_preferred"] = _trade_stats(pref_trades, "mm_preferred")
    results["mm_nonpreferred"] = _trade_stats(nonpref_trades, "mm_nonpreferred")
    results["mm_all_trades"] = _trade_stats(mm_trades, "mm_all_trades")

    # Per-pair per-direction breakdown
    pair_dir = {}
    for t in mm_trades:
        key = (t.get("pair", "?"), "BUY" if t.get("direction", 0) > 0 else "SELL")
        pair_dir.setdefault(key, []).append(t)
    results["pair_dir_breakdown"] = {
        k: _trade_stats(v, f"{k[1]} {k[0]}") for k, v in sorted(pair_dir.items())
    }

    # Per-confirmation breakdown
    confirm_buckets = {}
    for t in mm_trades:
        tag = t.get("entry_type", "")
        confirm_buckets.setdefault(tag, []).append(t)

    # Restore
    if orig_mm_standalone is not None:
        os.environ["MM_STANDALONE_ENABLED"] = orig_mm_standalone
    else:
        os.environ.pop("MM_STANDALONE_ENABLED", None)
    if orig_mm_cont is not None:
        os.environ["MM_CONTINUATION_ENABLED"] = orig_mm_cont
    else:
        os.environ.pop("MM_CONTINUATION_ENABLED", None)

    return results, bt_all, years


def _extract(bt, label):
    """Extract summary stats from a backtester."""
    trades = getattr(bt, "trades", [])
    return _trade_stats(trades, label, equity=bt.equity,
                        max_dd=getattr(bt, "_max_drawdown_pct", 0))


def _trade_stats(trades, label, equity=None, max_dd=None):
    wins = [t for t in trades if t.get("pnl", 0) > 0]
    losses = [t for t in trades if t.get("pnl", 0) <= 0]
    gp = sum(t.get("pnl", 0) for t in wins)
    gl = -sum(t.get("pnl", 0) for t in losses) if losses else 0
    pf = (gp / gl) if gl > 0 else float("inf")
    wr = len(wins) / len(trades) * 100 if trades else 0
    total_pnl = sum(t.get("pnl", 0) for t in trades)
    avg_r = None
    rs = []
    for t in trades:
        entry = t.get("entry", 0)
        stop = t.get("stop", 0)
        exit_p = t.get("exit", 0)
        risk = abs(entry - stop) if stop else 0
        if risk > 0:
            r = (exit_p - entry) * t.get("direction", 1) / risk
            rs.append(r)
    if rs:
        avg_r = sum(rs) / len(rs)
    return {
        "label": label, "n": len(trades), "wins": len(wins), "losses": len(losses),
        "wr": wr, "pf": pf, "pnl": total_pnl, "gp": gp, "gl": gl,
        "equity": equity, "max_dd": max_dd, "avg_r": avg_r,
    }


def write_report(results, years):
    """Write the study report."""
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = []
    w = lines.append

    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    w("# MM Directional Study: SELL GBPUSD + BUY EURUSD")
    w("")
    w(f"Generated: {now}")
    w(f"Years: {', '.join(str(y) for y in years)}")
    w(f"Filter: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)")
    w("")

    # Summary table
    w("## Summary")
    w("")
    w("| Arm | Trades | WR | PF | P&L | MaxDD | Avg R |")
    w("|---|---|---|---|---|---|---|")
    for key in ("baseline", "mm_all", "mm_all_trades", "mm_preferred", "mm_nonpreferred"):
        s = results.get(key)
        if s is None:
            continue
        dd = f"{s['max_dd']:.2f}%" if s["max_dd"] is not None else "—"
        eq = f"R{s['equity']:,.0f}" if s["equity"] is not None else "—"
        ar = f"{s['avg_r']:+.2f}R" if s["avg_r"] is not None else "—"
        w(f"| {s['label']} | {s['n']} | {s['wr']:.1f}% | {s['pf']:.2f} | R{s['pnl']:,.0f} | {dd} | {ar} |")
    w("")

    # Pair x Direction breakdown
    w("## Pair x Direction Breakdown (MM standalone trades only)")
    w("")
    w("| Setup | Trades | WR | PF | P&L | Avg R | Preferred? |")
    w("|---|---|---|---|---|---|---|")
    for (pair, d_label), s in sorted(results.get("pair_dir_breakdown", {}).items()):
        pref = PREFERRED.get(pair)
        is_pref = (pref == 1 and d_label == "BUY") or (pref == -1 and d_label == "SELL")
        pref_tag = "YES" if is_pref else "no"
        ar = f"{s['avg_r']:+.2f}R" if s["avg_r"] is not None else "—"
        w(f"| {d_label} {pair} | {s['n']} | {s['wr']:.1f}% | {s['pf']:.2f} | R{s['pnl']:,.0f} | {ar} | {pref_tag} |")
    w("")

    w("## Interpretation")
    w("")
    pref = results.get("mm_preferred", {})
    nonpref = results.get("mm_nonpreferred", {})
    if pref.get("n", 0) > 0 and nonpref.get("n", 0) > 0:
        w(f"- **Preferred** (SELL GU + BUY EU): {pref['n']} trades, WR {pref['wr']:.1f}%, PF {pref['pf']:.2f}")
        w(f"- **Non-preferred** (other combos): {nonpref['n']} trades, WR {nonpref['wr']:.1f}%, PF {nonpref['pf']:.2f}")
        if pref["pf"] > nonpref["pf"] and pref["wr"] > nonpref["wr"]:
            w("- **The directional filter IMPROVES the edge** — preferred combos outperform")
        elif pref["pf"] > 1.0:
            w("- **Preferred combos are profitable** (PF > 1) — directional filter is viable")
        else:
            w("- **WARNING:** preferred combos have PF < 1 — the directional filter may hurt")
    w("")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport written to {REPORT}")


def push_report():
    """Git add, commit, push."""
    try:
        subprocess.run(["git", "add", "-f", REPORT], cwd=_ROOT, check=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"],
                           cwd=_ROOT, capture_output=True)
        if r.returncode == 0:
            print("No changes to commit.")
            return
        subprocess.run(
            ["git", "commit", "-m", "MM directional study report (auto)"],
            cwd=_ROOT, check=True)
        for attempt in range(4):
            r = subprocess.run(["git", "push", "origin", "HEAD"],
                               cwd=_ROOT, capture_output=True, text=True)
            if r.returncode == 0:
                print("REPORT PUSHED.")
                return
            if attempt < 3:
                wait = 2 ** (attempt + 1)
                subprocess.run(["git", "pull", "origin", "HEAD", "--no-rebase", "--no-edit"],
                               cwd=_ROOT, capture_output=True)
                time.sleep(wait)
        print(f"Push failed: {r.stderr}")
    except Exception as e:
        print(f"Git error: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", type=int, nargs="+", default=[2022, 2023, 2024, 2025])
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    results, bt, years = run_study(a.years)
    write_report(results, years)

    if not a.no_push:
        push_report()

    # Console summary
    print(f"\n{'='*60}")
    print("MM DIRECTIONAL STUDY RESULTS")
    print(f"{'='*60}")
    for key in ("baseline", "mm_all_trades", "mm_preferred", "mm_nonpreferred"):
        s = results.get(key)
        if s:
            print(f"  {s['label']:20} {s['n']:4} trades  WR {s['wr']:.1f}%  PF {s['pf']:.2f}  P&L R{s['pnl']:,.0f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

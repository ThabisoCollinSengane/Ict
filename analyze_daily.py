"""Analyse per-day and per-week trade distribution from a backtest run."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from collections import defaultdict, Counter

import config
import run_backtest_histdata as rbt
import backtest as bt_module


# ── Re-run backtest to collect trade records ──────────────────────────────────
def run():
    years = ["2022", "2023", "2024", "2025"]
    DATA_DIR = rbt.DATA_DIR
    core_syms     = ["GBPUSD", "EURUSD", "EURGBP", "UDXUSD"]
    optional_syms = ["AUDUSD", "NZDUSD", "AUDNZD"]

    data_5m = {}
    dxy_5m  = None
    syms = core_syms + [s for s in optional_syms
                        if all(os.path.exists(os.path.join(DATA_DIR, f"{s}_{yr}.csv"))
                               for yr in years)]
    for sym in syms:
        frames = [rbt.load_m1(os.path.join(DATA_DIR, f"{sym}_{yr}.csv")) for yr in years
                  if os.path.exists(os.path.join(DATA_DIR, f"{sym}_{yr}.csv"))]
        if not frames:
            continue
        import pandas as _pd
        m1 = _pd.concat(frames).sort_index()
        m1 = m1[~m1.index.duplicated(keep='first')]
        m5 = rbt._resample(m1, "5min")
        if sym == "UDXUSD":
            dxy_5m = m5
        else:
            data_5m[sym] = m5

    bt = rbt.HistdataBacktester(data_5m, dxy_5m)
    bt.run()
    return bt


def analyse(bt):
    if not bt.trades:
        print("No trades.")
        return

    df = pd.DataFrame(bt.trades)
    df["open_date"] = pd.to_datetime(df["opened_at"]).dt.date
    df["open_week"] = pd.to_datetime(df["opened_at"]).dt.to_period("W")
    df["year"]      = pd.to_datetime(df["opened_at"]).dt.year

    # ── Overall summary ───────────────────────────────────────────────────────
    print("=" * 60)
    print("OVERALL RESULTS")
    print("=" * 60)
    print(f"  Total trades      : {len(df)}")
    print(f"  Win rate          : {(df.pnl > 0).mean()*100:.1f}%")
    pf_val = df[df.pnl > 0].pnl.sum() / abs(df[df.pnl < 0].pnl.sum())
    print(f"  Profit factor     : {pf_val:.2f}")
    print()

    # ── Per-pair ──────────────────────────────────────────────────────────────
    print("PER-PAIR BREAKDOWN")
    print("-" * 40)
    for pair, grp in df.groupby("pair"):
        w = (grp.pnl > 0).sum()
        print(f"  {pair}: {len(grp):4d} trades  "
              f"WR={w/len(grp)*100:.1f}%  P&L=R{grp.pnl.sum():,.0f}")
    print()

    # ── Per-day analysis ─────────────────────────────────────────────────────
    daily = df.groupby("open_date")
    day_trade_counts   = daily.size()
    day_pair_counts    = daily["pair"].nunique()

    print("PER-DAY TRADE DISTRIBUTION")
    print("-" * 40)
    total_trading_days = len(day_trade_counts)
    print(f"  Trading days with ≥1 trade : {total_trading_days}")
    print(f"  Avg trades per trading day : {day_trade_counts.mean():.2f}")
    print(f"  Avg pairs per trading day  : {day_pair_counts.mean():.2f}")
    print()
    print("  Days by number of pairs traded:")
    for n, cnt in sorted(day_pair_counts.value_counts().items()):
        pct = cnt / total_trading_days * 100
        bar = "█" * (cnt * 30 // total_trading_days)
        print(f"    {n} pair(s)  : {cnt:4d} days ({pct:5.1f}%)  {bar}")
    print()
    print("  Days by total trades entered:")
    for n, cnt in sorted(day_trade_counts.value_counts().items()):
        pct = cnt / total_trading_days * 100
        bar = "█" * (cnt * 30 // total_trading_days)
        print(f"    {n} trade(s) : {cnt:4d} days ({pct:5.1f}%)  {bar}")
    print()

    # ── Weekly frequency (3-of-5 pattern) ────────────────────────────────────
    # Count only leg_idx==1 entries as "a trade" (pyramid adds don't count)
    df1 = df[df["leg_idx"] == 1] if "leg_idx" in df.columns else df
    df1 = df1.copy()
    df1["open_week"] = pd.to_datetime(df1["opened_at"]).dt.to_period("W")
    df1["open_date"] = pd.to_datetime(df1["opened_at"]).dt.date

    weekly1 = df1.groupby("open_week")
    week_trade_counts = weekly1.size()
    week_day_counts   = weekly1["open_date"].nunique()

    print("WEEKLY TRADE BUDGET (target 3–5 per week)")
    print("-" * 40)
    total_weeks = len(week_trade_counts)
    print(f"  Weeks with ≥1 trade     : {total_weeks}")
    print(f"  Avg trades/week         : {week_trade_counts.mean():.2f}")
    print(f"  Avg pairs/week          : {weekly1['pair'].nunique().mean():.2f}")
    print()
    print("  Week distribution (total initial entries):")
    for n, cnt in sorted(week_trade_counts.value_counts().items()):
        pct = cnt / total_weeks * 100
        bar = "█" * (cnt * 30 // max(total_weeks, 1))
        print(f"    {n:2d} trade(s)/week : {cnt:4d} weeks ({pct:5.1f}%)  {bar}")
    print()
    print("  Pair share per week (avg initial entries):")
    for pair, grp in df1.groupby("pair"):
        wkly = grp.groupby("open_week").size()
        print(f"    {pair}: avg {wkly.mean():.2f}/week  "
              f"max {wkly.max()}/week  "
              f"weeks active {len(wkly)}/{total_weeks} ({len(wkly)/total_weeks*100:.0f}%)")
    print()
    print("  Week distribution (trading days per week):")
    for n, cnt in sorted(week_day_counts.value_counts().items()):
        pct = cnt / total_weeks * 100
        bar = "█" * (cnt * 30 // max(total_weeks, 1))
        print(f"    {n} day(s)/week : {cnt:4d} weeks ({pct:5.1f}%)  {bar}")
    print()

    # ── Session breakdown ─────────────────────────────────────────────────────
    df["hour_et"] = pd.to_datetime(df["opened_at"]).dt.tz_convert("America/New_York").dt.hour
    def session(h):
        if 3 <= h < 5:   return "London Open (03-05 ET)"
        if 7 <= h < 10:  return "New York AM (07-10 ET)"
        if 20 <= h < 22: return "Asian Open  (20-22 ET)"
        if h >= 23 or h < 1: return "Tokyo Kill  (23-01 ET)"
        return "Other"
    df["session"] = df["hour_et"].apply(session)
    print("PER-SESSION BREAKDOWN")
    print("-" * 40)
    for sess, grp in df.groupby("session"):
        w = (grp.pnl > 0).sum()
        print(f"  {sess:<28s}: {len(grp):4d} trades  WR={w/len(grp)*100:.1f}%")
    print()

    # ── Multi-pair day examples (most recent 10) ──────────────────────────────
    multi_pair_days = day_pair_counts[day_pair_counts >= 2].index
    print(f"MULTI-PAIR DAYS: {len(multi_pair_days)} days with 2+ pairs")
    print("-" * 40)
    recent = df[df["open_date"].isin(multi_pair_days)].sort_values("opened_at").tail(30)
    for date, grp in recent.groupby("open_date"):
        pairs = " + ".join(sorted(grp["pair"].unique()))
        wins  = (grp.pnl > 0).sum()
        print(f"  {date}  {pairs:<30s}  {len(grp)} trades  {wins}W/{len(grp)-wins}L")


if __name__ == "__main__":
    import backtest as bt_module
    print("Running backtest...")
    bt = run()
    analyse(bt)

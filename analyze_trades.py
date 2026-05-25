"""Post-backtest trade analysis: sessions, pip movements, repeating patterns."""

import os, sys
import pandas as pd
import pytz
from collections import defaultdict

# Re-use the same data loading and backtest machinery.
sys.path.insert(0, os.path.dirname(__file__))
from run_backtest_histdata import load_m1, _resample, df_to_bars, HistdataBacktester

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "histdata")
NY = pytz.timezone("America/New_York")

# Kill zones in ET
SESSIONS = [
    ("Asia",         19, 0,  21, 0),
    ("London Open",   2, 0,   5, 0),
    ("New York AM",   7, 0,  10, 0),
    ("London Close", 10, 0,  12, 0),
]

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def session_of(utc_dt):
    ny_dt = utc_dt.astimezone(NY)
    h, m = ny_dt.hour, ny_dt.minute
    mins = h * 60 + m
    for name, sh, sm, eh, em in SESSIONS:
        start = sh * 60 + sm
        end   = eh * 60 + em
        if start <= mins < end:
            return name
    return "Off-Hours"

def pip_move(pair, entry, exit_price):
    factor = 100 if "JPY" in pair else 10000
    return round(abs(exit_price - entry) * factor, 1)

def direction_label(d):
    return "LONG" if d > 0 else "SHORT"


def main():
    years = ["2022", "2023", "2024", "2025"]
    syms  = ["GBPUSD", "EURUSD", "EURGBP", "UDXUSD"]

    available = [y for y in years
                 if all(os.path.exists(os.path.join(DATA_DIR, f"{s}_{y}.csv")) for s in syms)]
    print(f"Loading {available} ...")

    data_5m = {}
    dxy_5m  = None
    for sym in syms:
        frames = [load_m1(os.path.join(DATA_DIR, f"{sym}_{y}.csv")) for y in available]
        m1 = pd.concat(frames).sort_index()
        m1 = m1[~m1.index.duplicated(keep="first")]
        m5 = _resample(m1, "5min")
        if sym == "UDXUSD":
            dxy_5m = m5
        else:
            data_5m[sym] = m5

    print("Running backtest ...")
    bt = HistdataBacktester(data_5m, dxy_5m)
    bt.run()

    if not bt.trades:
        print("No trades.")
        return

    df = pd.DataFrame(bt.trades)
    df["opened_at"] = pd.to_datetime(df["opened_at"], utc=True)
    df["closed_at"] = pd.to_datetime(df["closed_at"], utc=True)

    df["session"]   = df["opened_at"].apply(session_of)
    df["dow"]       = df["opened_at"].dt.dayofweek.map(lambda x: DAYS[x])
    df["hour_et"]   = df["opened_at"].apply(lambda t: t.astimezone(NY).hour)
    df["dir_label"] = df["direction"].map(direction_label)
    df["pips"]      = df.apply(lambda r: pip_move(r["pair"], r["entry"], r["exit"]), axis=1)
    df["win"]       = df["pnl"] > 0

    total = len(df)
    wins  = df["win"].sum()
    print(f"\n{'='*60}")
    print(f"TOTAL  {total} trades  |  {wins}W {total-wins}L  |  "
          f"WR {wins/total*100:.1f}%  |  PF {df[df.win].pnl.sum() / abs(df[~df.win].pnl.sum()):.2f}")
    print(f"{'='*60}")

    # ------------------------------------------------------------------ #
    # 1. Session breakdown
    # ------------------------------------------------------------------ #
    print("\n--- SESSION BREAKDOWN ---")
    for sess, grp in df.groupby("session", sort=False):
        w = grp["win"].sum()
        n = len(grp)
        pnl = grp["pnl"].sum()
        avg_pip_w = grp[grp.win]["pips"].mean() if w else 0
        avg_pip_l = grp[~grp.win]["pips"].mean() if (n - w) else 0
        print(f"  {sess:14s}  {n:3d} trades  {w}W/{n-w}L  WR {w/n*100:.0f}%  "
              f"P&L ${pnl:+,.0f}  avg pip W={avg_pip_w:.1f} L={avg_pip_l:.1f}")

    # ------------------------------------------------------------------ #
    # 2. Session × Pair × Direction (most common winning patterns)
    # ------------------------------------------------------------------ #
    print("\n--- TOP WINNING PATTERNS (session × pair × direction) ---")
    combos = df.groupby(["session", "pair", "dir_label"]).apply(
        lambda g: pd.Series({
            "n": len(g),
            "wins": g.win.sum(),
            "losses": len(g) - g.win.sum(),
            "wr_pct": g.win.mean() * 100,
            "pnl": g.pnl.sum(),
            "avg_pip_win":  g[g.win]["pips"].mean() if g.win.sum() else 0,
            "avg_pip_loss": g[~g.win]["pips"].mean() if (~g.win).sum() else 0,
        })
    ).reset_index().sort_values("pnl", ascending=False)

    for _, r in combos.iterrows():
        flag = "WIN PATTERN" if r.pnl > 0 and r.wins >= 2 else ("LOSS DRAIN" if r.pnl < -200 else "")
        print(f"  {r.session:14s} {r.pair} {r.dir_label:5s}  "
              f"{int(r.n):3d} trades  {int(r.wins)}W/{int(r.losses)}L  "
              f"WR {r.wr_pct:.0f}%  P&L ${r.pnl:+,.0f}  "
              f"avg pip: W={r.avg_pip_win:.1f} L={r.avg_pip_loss:.1f}  {flag}")

    # ------------------------------------------------------------------ #
    # 3. Day of week
    # ------------------------------------------------------------------ #
    print("\n--- DAY OF WEEK ---")
    for day in ["Mon", "Tue", "Wed", "Thu", "Fri"]:
        grp = df[df.dow == day]
        if grp.empty:
            continue
        w = grp.win.sum()
        n = len(grp)
        print(f"  {day}  {n:3d} trades  {w}W/{n-w}L  WR {w/n*100:.0f}%  P&L ${grp.pnl.sum():+,.0f}")

    # ------------------------------------------------------------------ #
    # 4. Pip distribution — winners vs losers
    # ------------------------------------------------------------------ #
    print("\n--- PIP DISTRIBUTION ---")
    buckets = [(0,5),(5,10),(10,20),(20,40),(40,80),(80,999)]
    w_pips = df[df.win]["pips"]
    l_pips = df[~df.win]["pips"]
    print(f"  {'Range':10s}  {'Winners':>8s}  {'Losers':>8s}")
    for lo, hi in buckets:
        wc = ((w_pips >= lo) & (w_pips < hi)).sum()
        lc = ((l_pips >= lo) & (l_pips < hi)).sum()
        print(f"  {lo:>3d}–{hi:<4d} pip  {wc:8d}  {lc:8d}")

    # ------------------------------------------------------------------ #
    # 5. Repeated loss patterns — trades that keep losing in same session+dir
    # ------------------------------------------------------------------ #
    print("\n--- REPEATED LOSS DRAINS (same session+pair+dir, ≥3 losses) ---")
    for _, r in combos[combos.losses >= 3].sort_values("losses", ascending=False).iterrows():
        if r.pnl < 0 or r.wr_pct < 45:
            print(f"  {r.session:14s} {r.pair} {r.dir_label:5s}  "
                  f"{int(r.losses)} losses / {int(r.n)} trades  "
                  f"WR {r.wr_pct:.0f}%  P&L ${r.pnl:+,.0f}")

    # ------------------------------------------------------------------ #
    # 6. Best individual trades
    # ------------------------------------------------------------------ #
    print("\n--- TOP 5 WINS (by P&L) ---")
    for _, r in df[df.win].nlargest(5, "pnl").iterrows():
        dur = (r.closed_at - r.opened_at).total_seconds() / 60
        print(f"  {str(r.opened_at)[:16]}  {r.pair} {r.dir_label}  "
              f"session={r.session}  pips={r.pips}  P&L=${r.pnl:+,.0f}  dur={dur:.0f}min")

    print("\n--- TOP 5 LOSSES (by P&L) ---")
    for _, r in df[~df.win].nsmallest(5, "pnl").iterrows():
        dur = (r.closed_at - r.opened_at).total_seconds() / 60
        print(f"  {str(r.opened_at)[:16]}  {r.pair} {r.dir_label}  "
              f"session={r.session}  pips={r.pips}  P&L=${r.pnl:+,.0f}  dur={dur:.0f}min")

    # ------------------------------------------------------------------ #
    # 7. Duration analysis
    # ------------------------------------------------------------------ #
    print("\n--- TRADE DURATION (minutes) ---")
    df["duration_min"] = (df.closed_at - df.opened_at).dt.total_seconds() / 60
    w_dur = df[df.win]["duration_min"]
    l_dur = df[~df.win]["duration_min"]
    print(f"  Winners: median={w_dur.median():.0f}m  mean={w_dur.mean():.0f}m  "
          f"min={w_dur.min():.0f}m  max={w_dur.max():.0f}m")
    print(f"  Losers:  median={l_dur.median():.0f}m  mean={l_dur.mean():.0f}m  "
          f"min={l_dur.min():.0f}m  max={l_dur.max():.0f}m")

    # ------------------------------------------------------------------ #
    # 8. Yearly breakdown
    # ------------------------------------------------------------------ #
    print("\n--- YEARLY BREAKDOWN ---")
    df["year"] = df["opened_at"].dt.year
    for yr, grp in df.groupby("year"):
        w = grp.win.sum()
        n = len(grp)
        print(f"  {yr}  {n:3d} trades  {w}W/{n-w}L  WR {w/n*100:.0f}%  P&L ${grp.pnl.sum():+,.0f}")


if __name__ == "__main__":
    main()

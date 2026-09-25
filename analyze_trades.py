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
    core_syms     = ["GBPUSD", "EURUSD", "EURGBP", "UDXUSD"]
    optional_syms = ["AUDUSD", "NZDUSD", "AUDNZD"]

    available = [y for y in years
                 if all(os.path.exists(os.path.join(DATA_DIR, f"{s}_{y}.csv")) for s in core_syms)]
    print(f"Loading {available} ...")

    data_5m = {}
    dxy_5m  = None
    all_syms = core_syms + [s for s in optional_syms
                            if all(os.path.exists(os.path.join(DATA_DIR, f"{s}_{y}.csv"))
                                   for y in available)]
    for sym in all_syms:
        frames = [load_m1(os.path.join(DATA_DIR, f"{sym}_{y}.csv")) for y in available
                  if os.path.exists(os.path.join(DATA_DIR, f"{sym}_{y}.csv"))]
        if not frames:
            continue
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
          f"WR {wins/total*100:.1f}%  |  PF {df[df.win].pnl.sum() / abs(df[~df.win].pnl.sum()):.2f}  "
          f"|  P&L R{df.pnl.sum():.2f} ZAR")
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
              f"P&L R{pnl:+,.0f}  avg pip W={avg_pip_w:.1f} L={avg_pip_l:.1f}")

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
              f"WR {r.wr_pct:.0f}%  P&L R{r.pnl:+,.0f}  "
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
        print(f"  {day}  {n:3d} trades  {w}W/{n-w}L  WR {w/n*100:.0f}%  P&L R{grp.pnl.sum():+,.0f}")

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
                  f"WR {r.wr_pct:.0f}%  P&L R{r.pnl:+,.0f}")

    # ------------------------------------------------------------------ #
    # 6. Best individual trades
    # ------------------------------------------------------------------ #
    print("\n--- TOP 5 WINS (by P&L) ---")
    for _, r in df[df.win].nlargest(5, "pnl").iterrows():
        dur = (r.closed_at - r.opened_at).total_seconds() / 60
        print(f"  {str(r.opened_at)[:16]}  {r.pair} {r.dir_label}  "
              f"session={r.session}  pips={r.pips}  P&L=R{r.pnl:+,.0f}  dur={dur:.0f}min")

    print("\n--- TOP 5 LOSSES (by P&L) ---")
    for _, r in df[~df.win].nsmallest(5, "pnl").iterrows():
        dur = (r.closed_at - r.opened_at).total_seconds() / 60
        print(f"  {str(r.opened_at)[:16]}  {r.pair} {r.dir_label}  "
              f"session={r.session}  pips={r.pips}  P&L=R{r.pnl:+,.0f}  dur={dur:.0f}min")

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
    # 8. Monthly breakdown (fixed lot equivalent — strips compounding)
    # ------------------------------------------------------------------ #
    import config
    from risk import pip_size
    base_lots = config.PYRAMID_LOTS[0]
    print(f"\n--- MONTHLY P&L ({base_lots} lots fixed — no compounding, single leg) ---")

    BASE_UNITS = int(config.PYRAMID_LOTS[0] * config.LOT_UNITS)  # 5000 units

    def fixed_pnl(row):
        """Recalculate P&L at fixed 0.05 lots regardless of account size."""
        p = pip_size(row["pair"])
        pips = (row["exit"] - row["entry"]) * row["direction"] / p
        return pips * BASE_UNITS * p * config.USD_ZAR

    df["fixed_pnl"] = df.apply(fixed_pnl, axis=1)
    df["ym"] = df["opened_at"].dt.to_period("M")

    monthly = df.groupby("ym").apply(lambda g: pd.Series({
        "trades": len(g),
        "wins":   (g.fixed_pnl > 0).sum(),
        "losses": (g.fixed_pnl <= 0).sum(),
        "pnl":    g.fixed_pnl.sum(),
        "wr":     (g.fixed_pnl > 0).mean() * 100,
    })).reset_index()

    running = config.STARTING_CASH
    print(f"  {'Month':<10} {'Trades':>6}  {'W/L':>7}  {'WR':>5}  "
          f"{'Monthly P&L':>12}  {'Balance':>10}  {'Status'}")
    print(f"  {'-'*75}")
    for _, r in monthly.iterrows():
        running += r.pnl
        status = "✓ PROFIT" if r.pnl > 0 else "✗ loss"
        print(f"  {str(r.ym):<10} {int(r.trades):>6}  "
              f"{int(r.wins)}W/{int(r.losses)}L  {r.wr:>4.0f}%  "
              f"R{r.pnl:>+10,.0f}  R{running:>9,.0f}  {status}")

    profitable_months = (monthly.pnl > 0).sum()
    total_months = len(monthly)
    print(f"\n  Profitable months: {profitable_months}/{total_months} "
          f"({profitable_months/total_months*100:.0f}%)")
    print(f"  Avg monthly P&L:   R{monthly.pnl.mean():+,.0f}")
    print(f"  Best month:        R{monthly.pnl.max():+,.0f}  ({monthly.loc[monthly.pnl.idxmax(),'ym']})")
    print(f"  Worst month:       R{monthly.pnl.min():+,.0f}  ({monthly.loc[monthly.pnl.idxmin(),'ym']})")

    # ------------------------------------------------------------------ #
    # 9. Entry type breakdown
    # ------------------------------------------------------------------ #
    print("\n--- ENTRY TYPE BREAKDOWN ---")
    if "entry_type" in df.columns:
        et = df.groupby("entry_type").apply(lambda g: pd.Series({
            "n":      len(g),
            "wins":   (g.pnl > 0).sum(),
            "wr_pct": (g.pnl > 0).mean() * 100,
            "pnl":    g.pnl.sum(),
            "avg_pnl": g.pnl.mean(),
        })).reset_index().sort_values("n", ascending=False)

        initial = df[df.leg_idx == 1]
        pyramid = df[df.leg_idx > 1]
        print(f"  Initial entries : {len(initial)} ({len(initial)/len(df)*100:.0f}%)")
        print(f"  Pyramid adds    : {len(pyramid)} ({len(pyramid)/len(df)*100:.0f}%)")
        print()
        for _, r in et.iterrows():
            print(f"  {r.entry_type:20s}  {int(r.n):4d} trades  "
                  f"{int(r.wins)}W/{int(r.n-r.wins)}L  "
                  f"WR {r.wr_pct:.0f}%  "
                  f"avg R{r.avg_pnl:+,.0f}  total R{r.pnl:+,.0f}")
    else:
        print("  entry_type column not found in trade log")

    # ------------------------------------------------------------------ #
    # 9b. Entry PATTERN breakdown (fvg/ob/breaker × timeframe × W/L)
    # ------------------------------------------------------------------ #
    print("\n--- ENTRY PATTERN BREAKDOWN (fvg/ob/breaker × timeframe) ---")
    if "entry_type" in df.columns:
        # Parse pattern tag from entry_type: "amd_fvg_m15" → "fvg_m15"
        def _pattern(et):
            parts = str(et).split("_", 1)  # split on first _ only (amd/mss prefix)
            return parts[1] if len(parts) > 1 else et

        df["pattern"] = df["entry_type"].apply(_pattern)
        PATTERN_ORDER = ["fvg_m5", "fvg_m15", "fvg_h1",
                         "ob_m5", "ob_m15",
                         "breaker_m5", "breaker_m15", "breaker_h1"]

        pt = df.groupby("pattern").apply(
            lambda g: pd.Series({
                "n":       len(g),
                "wins":    int((g.pnl > 0).sum()),
                "losses":  int((g.pnl <= 0).sum()),
                "wr_pct":  (g.pnl > 0).mean() * 100,
                "pnl":     g.pnl.sum(),
                "avg_w":   g[g.pnl > 0].pnl.mean() if (g.pnl > 0).any() else 0,
                "avg_l":   g[g.pnl <= 0].pnl.mean() if (g.pnl <= 0).any() else 0,
            })
        ).reset_index()

        print(f"  {'Pattern':<14}  {'N':>4}  {'W/L':>8}  {'WR':>5}  "
              f"{'Total P&L':>12}  {'avg_W':>9}  {'avg_L':>9}  Status")
        print(f"  {'-'*80}")
        for pat in PATTERN_ORDER:
            row = pt[pt.pattern == pat]
            if row.empty:
                continue
            r = row.iloc[0]
            flag = ""
            if r.wr_pct >= 55 and r.pnl > 0:
                flag = "★ BEST"
            elif r.wr_pct < 40 or r.pnl < 0:
                flag = "✗ AVOID"
            print(f"  {pat:<14}  {int(r.n):>4}  "
                  f"{int(r.wins)}W/{int(r.losses)}L  {r.wr_pct:>4.0f}%  "
                  f"R{r.pnl:>+11,.0f}  R{r.avg_w:>+8,.0f}  R{r.avg_l:>+8,.0f}  {flag}")

        # Detailed: pattern × session × pair (winners)
        print(f"\n  TOP WIN PATTERNS (pattern × session × pair, ≥3 wins):")
        print(f"  {'-'*85}")
        detail_w = df.groupby(["pattern", "session", "pair"]).apply(
            lambda g: pd.Series({
                "n":      len(g),
                "wins":   int((g.pnl > 0).sum()),
                "losses": int((g.pnl <= 0).sum()),
                "wr_pct": (g.pnl > 0).mean() * 100,
                "pnl":    g.pnl.sum(),
                "avg_w":  g[g.pnl > 0].pnl.mean() if (g.pnl > 0).any() else 0,
            })
        ).reset_index()
        winners_detail = detail_w[detail_w.wins >= 3].sort_values(
            ["wins", "wr_pct"], ascending=False).head(20)
        for _, r in winners_detail.iterrows():
            flag = "★★" if r.wr_pct >= 60 else ("★" if r.wr_pct >= 50 else "")
            print(f"  {r.pattern:<14}  {r.session:<18}  {r.pair}  "
                  f"{int(r.wins)}W/{int(r.losses)}L  WR {r.wr_pct:.0f}%  "
                  f"P&L R{r.pnl:+,.0f}  avg_W R{r.avg_w:+,.0f}  {flag}")

        # Detailed: pattern × session × pair (losers / avoid)
        print(f"\n  LOSS DRAINS TO AVOID (pattern × session × pair, ≥3 losses, WR<50%):")
        print(f"  {'-'*85}")
        losers_detail = detail_w[
            (detail_w.losses >= 3) & (detail_w.wr_pct < 50)
        ].sort_values(["losses", "wr_pct"], ascending=[False, True]).head(20)
        for _, r in losers_detail.iterrows():
            drain = " *** BLOCK" if r.pnl < -200 else ""
            print(f"  {r.pattern:<14}  {r.session:<18}  {r.pair}  "
                  f"{int(r.wins)}W/{int(r.losses)}L  WR {r.wr_pct:.0f}%  "
                  f"P&L R{r.pnl:+,.0f}{drain}")
    else:
        print("  entry_type column not found — re-run backtest to generate pattern tags")

    # ------------------------------------------------------------------ #
    # 10. Weekly trade distribution (initial entries only)
    # ------------------------------------------------------------------ #
    print("\n--- WEEKLY TRADE DISTRIBUTION (initial entries, leg_idx=1) ---")
    df1 = df[df.leg_idx == 1].copy()
    df1["open_week"] = df1["opened_at"].dt.to_period("W")
    week_counts = df1.groupby("open_week").size()
    total_weeks  = len(week_counts)
    print(f"  Active weeks    : {total_weeks}")
    print(f"  Avg trades/week : {week_counts.mean():.2f}  "
          f"(target 3–5)")
    print(f"  Weeks at 3–5    : {((week_counts >= 3) & (week_counts <= 5)).sum()} "
          f"({((week_counts >= 3) & (week_counts <= 5)).sum()/total_weeks*100:.0f}%)")
    print(f"  Weeks < 3       : {(week_counts < 3).sum()} "
          f"({(week_counts < 3).sum()/total_weeks*100:.0f}%)")
    print(f"  Weeks > 5       : {(week_counts > 5).sum()} "
          f"({(week_counts > 5).sum()/total_weeks*100:.0f}%)")
    print()
    for n, cnt in sorted(week_counts.value_counts().items()):
        pct = cnt / total_weeks * 100
        bar = "█" * int(cnt * 40 // total_weeks)
        print(f"    {n:2d} trade(s)/week : {cnt:4d} ({pct:5.1f}%)  {bar}")

    print()
    print("  Per-pair weekly share (initial entries):")
    for pair, grp in df1.groupby("pair"):
        wkly = grp.groupby("open_week").size()
        print(f"    {pair}: {len(grp):3d} total  avg {wkly.mean():.2f}/week  "
              f"max {int(wkly.max())}/week  "
              f"active {len(wkly)}/{total_weeks} weeks ({len(wkly)/total_weeks*100:.0f}%)")

    # ------------------------------------------------------------------ #
    # 11. Top repeating WIN patterns (ranked by frequency then WR)
    # ------------------------------------------------------------------ #
    print("\n--- TOP REPEATING WIN PATTERNS (session × pair × direction × entry_type) ---")
    grp_cols = ["session", "pair", "dir_label"]
    if "entry_type" in df.columns:
        df["entry_cat"] = df["entry_type"].str.split("_").str[:2].str.join("_")
        grp_cols = ["session", "pair", "dir_label", "entry_cat"]

    combos2 = df.groupby(grp_cols).apply(
        lambda g: pd.Series({
            "n":      len(g),
            "wins":   int(g.win.sum()),
            "losses": int((~g.win).sum()),
            "wr_pct": g.win.mean() * 100,
            "pnl":    g.pnl.sum(),
            "avg_pnl_w": g[g.win].pnl.mean() if g.win.any() else 0,
            "avg_pnl_l": g[~g.win].pnl.mean() if (~g.win).any() else 0,
        })
    ).reset_index()

    winners = combos2[(combos2.wins >= 3) & (combos2.pnl > 0)].sort_values(
        ["wins", "wr_pct"], ascending=False).head(15)
    for _, r in winners.iterrows():
        label = " | ".join(str(r[c]) for c in grp_cols)
        print(f"  {label:<55s}  "
              f"{int(r.wins):3d}W/{int(r.losses):3d}L  WR {r.wr_pct:.0f}%  "
              f"P&L R{r.pnl:+,.0f}  avg_W R{r.avg_pnl_w:+,.0f}")

    # ------------------------------------------------------------------ #
    # 12. Top repeating LOSS patterns (ranked by frequency then losses)
    # ------------------------------------------------------------------ #
    print("\n--- TOP REPEATING LOSS PATTERNS (session × pair × direction × entry_type) ---")
    losers = combos2[(combos2.losses >= 3)].sort_values(
        ["losses", "wr_pct"], ascending=[False, True]).head(15)
    for _, r in losers.iterrows():
        label = " | ".join(str(r[c]) for c in grp_cols)
        flag = " *** DRAIN" if r.pnl < -500 else ""
        print(f"  {label:<55s}  "
              f"{int(r.wins):3d}W/{int(r.losses):3d}L  WR {r.wr_pct:.0f}%  "
              f"P&L R{r.pnl:+,.0f}  avg_L R{r.avg_pnl_l:+,.0f}{flag}")

    # ------------------------------------------------------------------ #
    # 13. Exit reason breakdown
    # ------------------------------------------------------------------ #
    print("\n--- EXIT REASON BREAKDOWN ---")
    if "reason" in df.columns:
        for reason, grp in df.groupby("reason"):
            w = grp.win.sum()
            n = len(grp)
            print(f"  {reason:12s}: {n:4d} trades  {w}W/{n-w}L  WR {w/n*100:.0f}%  "
                  f"P&L R{grp.pnl.sum():+,.0f}")
    else:
        print("  reason column not found")

    # ------------------------------------------------------------------ #
    # 14. Pyramid analytics (level distribution, entry patterns, SD targets)
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 60)
    print("PYRAMID ANALYTICS")
    print("=" * 60)

    from risk import pip_size as _pip_size

    # ── 14a. Leg level distribution ───────────────────────────────────────
    print("\n--- LEG LEVEL DISTRIBUTION ---")
    for leg_n, grp in df.groupby("leg_idx"):
        w = grp.win.sum()
        n = len(grp)
        label = {1: "L1 Initial", 2: "L2 Add", 3: "L3 Add"}.get(int(leg_n), f"L{leg_n}")
        print(f"  {label}: {n:4d} trades  {w}W/{n-w}L  WR {w/n*100:.0f}%  "
              f"P&L R{grp.pnl.sum():+,.0f}")

    # Positions that actually pyramided (reached L2 or L3)
    pyr_l2 = df[df.leg_idx == 2]
    pyr_l3 = df[df.leg_idx == 3]
    initial = df[df.leg_idx == 1]
    print(f"\n  Positions that added L2 : {len(pyr_l2):3d}  "
          f"({len(pyr_l2)/len(initial)*100:.1f}% of initial entries)")
    print(f"  Positions that added L3 : {len(pyr_l3):3d}  "
          f"({len(pyr_l3)/len(initial)*100:.1f}% of initial entries)")

    # ── 14b. Pyramid entry patterns ───────────────────────────────────────
    print("\n--- PYRAMID ENTRY PATTERNS (L2/L3 legs) ---")
    pyr_legs = df[df.leg_idx > 1].copy()
    if not pyr_legs.empty:
        def _pyr_pattern(et):
            # "pyramid_im1.0_fvg_m5" → "fvg_m5"
            parts = str(et).split("_", 2)  # ["pyramid", "im1.0", "fvg_m5"]
            return parts[2] if len(parts) > 2 else et

        pyr_legs["pyr_pat"] = pyr_legs["entry_type"].apply(_pyr_pattern)
        for pat, grp in pyr_legs.groupby("pyr_pat"):
            w = grp.win.sum()
            n = len(grp)
            print(f"  {pat:<14}  {n:3d} pyramid legs  {w}W/{n-w}L  "
                  f"WR {w/n*100:.0f}%  P&L R{grp.pnl.sum():+,.0f}")
    else:
        print("  No pyramid legs in dataset")

    # ── 14c. ICT Standard Deviation target classification ─────────────────
    # Stop = 10 pips fixed. SD levels = multiples of initial risk:
    #   1st SD = 1R  = 10 pips  (minimum viable / trail to BE)
    #   2nd SD = 2R  = 20 pips  (MIN_PIPS_TARGET — standard first target)
    #   3rd SD = 3R  = 30 pips  (127.2% extension)
    #   4th SD = 4R+ = 40+ pips (161.8%+ full distribution)
    print("\n--- ICT STANDARD DEVIATION TARGET HITS (winning trades, all legs) ---")
    winners = df[df.win].copy()
    winners["pips_profit"] = winners.apply(
        lambda r: (r["exit"] - r["entry"]) * r["direction"] / _pip_size(r["pair"]),
        axis=1
    )
    winners["sd_level"] = pd.cut(
        winners["pips_profit"],
        bins=[0, 10, 20, 30, 40, 9999],
        labels=["<1st SD (<10pip)", "1st SD (10-19pip)",
                "2nd SD (20-29pip)", "3rd SD (30-39pip)", "4th SD (40+pip)"]
    )
    sd_counts = winners["sd_level"].value_counts().sort_index()
    total_wins = len(winners)
    print(f"  {'SD Level':<22}  {'Count':>6}  {'%':>6}  {'Avg P&L':>10}")
    print(f"  {'-'*52}")
    for sd, cnt in sd_counts.items():
        grp = winners[winners.sd_level == sd]
        avg_pnl = grp.pnl.mean()
        pct = cnt / total_wins * 100
        bar = "█" * int(cnt * 30 // total_wins)
        print(f"  {str(sd):<22}  {cnt:>6}  {pct:>5.1f}%  R{avg_pnl:>+9,.0f}  {bar}")

    # SD by leg level
    print(f"\n  SD target by leg level:")
    for leg_n, grp in winners.groupby("leg_idx"):
        label = {1: "L1", 2: "L2", 3: "L3"}.get(int(leg_n), f"L{leg_n}")
        avg_pips = grp["pips_profit"].mean()
        avg_sd = avg_pips / 10  # express as SD multiples (10-pip stop = 1 SD)
        print(f"    {label}: {len(grp):3d} wins  avg {avg_pips:.1f} pips  "
              f"≈ {avg_sd:.1f}R  (avg P&L R{grp.pnl.mean():+,.0f})")

    # SD per pair
    print(f"\n  SD target distribution per pair (winners only):")
    for pair, grp in winners.groupby("pair"):
        avg_pips = grp["pips_profit"].mean()
        top_sd = grp["sd_level"].mode().iloc[0] if not grp.empty else "—"
        print(f"    {pair}: {len(grp):3d} wins  avg {avg_pips:.1f} pips  "
              f"most common target: {top_sd}")

    # ── 14d. Full position view (grouped by close time)  ──────────────────
    print("\n--- FULL POSITION VIEW (grouped positions with ≥2 legs) ---")
    df["closed_at_str"] = df["closed_at"].astype(str).str[:16]
    multi_leg = df.groupby(["pair", "closed_at_str"]).filter(lambda g: len(g) > 1)
    pos_groups = multi_leg.groupby(["pair", "closed_at_str"])

    pos_rows = []
    for (pair, close_str), grp in pos_groups:
        legs_sorted = grp.sort_values("leg_idx")
        n_legs = len(legs_sorted)
        patterns = " → ".join(legs_sorted["entry_type"].apply(
            lambda et: str(et).split("_", 1)[1] if "_" in str(et) else et
        ).tolist())
        total_pnl = legs_sorted.pnl.sum()
        l1_pips = ((legs_sorted.iloc[0]["exit"] - legs_sorted.iloc[0]["entry"])
                   * legs_sorted.iloc[0]["direction"]
                   / _pip_size(pair))
        opened_str = str(legs_sorted.iloc[0]["opened_at"])[:16]
        pos_rows.append({
            "pair": pair, "legs": n_legs, "opened": opened_str, "closed": close_str,
            "patterns": patterns, "pips_l1": round(l1_pips, 1),
            "total_pnl": total_pnl, "won": total_pnl > 0,
        })

    if pos_rows:
        pos_df = pd.DataFrame(pos_rows)
        wins_pos = pos_df.won.sum()
        print(f"  Multi-leg positions: {len(pos_df)} total  "
              f"{wins_pos}W/{len(pos_df)-wins_pos}L  "
              f"WR {wins_pos/len(pos_df)*100:.0f}%  "
              f"P&L R{pos_df.total_pnl.sum():+,.0f}")
        print()
        print(f"  {'Opened':<17}  {'Pair':<7}  {'Legs':>4}  {'PnL':>9}  Pattern chain")
        print(f"  {'-'*80}")
        for _, r in pos_df.sort_values("total_pnl", ascending=False).iterrows():
            flag = "★" if r.total_pnl > 0 else " "
            print(f"  {flag} {r.opened:<16}  {r.pair:<7}  {int(r.legs):>4}  "
                  f"R{r.total_pnl:>+8,.0f}  {r.patterns}")
    else:
        print("  No multi-leg positions found in this run")


if __name__ == "__main__":
    main()

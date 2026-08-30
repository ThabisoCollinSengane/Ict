#!/usr/bin/env python3
"""MM Weekly Historical Replay — day-by-day setup detection + simulated outcomes.

Replays the past week's 5-min Yahoo data bar-by-bar through each killzone,
detects MM setups (IFVG zone + MSS + SMT + FBC) at each session boundary,
and simulates whether the trade would have won or lost using the stop/target.

Outputs a day-by-day breakdown: how many setups, which pair/direction,
signal strength, and simulated P&L (win/loss with pip result).

Usage (from repo root on the Windows VM):
    python scripts/mm_weekly_replay.py                   # last 5 trading days
    python scripts/mm_weekly_replay.py --days 10         # last 10 days
    python scripts/mm_weekly_replay.py --no-push         # skip git push
    python scripts/mm_weekly_replay.py --selftest        # imports only
"""
from __future__ import annotations
import argparse, os, sys, time, subprocess
from datetime import datetime, timedelta, timezone
from collections import namedtuple, defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

REPORT = os.path.join(_ROOT, "data", "mm_weekly_replay.md")

PREFERRED_SETUPS = {
    "GBPUSD": -1,
    "EURUSD": +1,
}

KILLZONES_ET = [
    {"name": "London Open",       "start_h": 3,  "start_m": 0,  "end_h": 5,  "end_m": 0},
    {"name": "London→NY Overlap", "start_h": 5,  "start_m": 0,  "end_h": 7,  "end_m": 0},
    {"name": "NY AM",             "start_h": 7,  "start_m": 0,  "end_h": 10, "end_m": 0},
    {"name": "NY PM",             "start_h": 13, "start_m": 0,  "end_h": 16, "end_m": 0},
]

Bar = namedtuple("Bar", ["Open", "High", "Low", "Close"])

_YF_PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "EURGBP": "EURGBP=X",
}


def _pip(pair):
    return 0.01 if "JPY" in pair else 0.0001


def fetch_yahoo(days=8):
    """Fetch 5-min OHLC for required pairs."""
    try:
        import yfinance as yf
    except ImportError:
        print("Installing yfinance...")
        os.system(f"{sys.executable} -m pip install yfinance -q")
        import yfinance as yf
    import pandas as pd

    period = f"{min(days + 3, 59)}d"
    all_data = {}

    for pair, ticker in _YF_PAIRS.items():
        print(f"  Fetching {pair} ({ticker})...", end=" ", flush=True)
        for attempt in range(3):
            try:
                t = yf.Ticker(ticker)
                df = t.history(period=period, interval="5m")
                if len(df) > 0:
                    df = df[["Open", "High", "Low", "Close"]].copy()
                    if df.index.tz is not None:
                        df.index = df.index.tz_convert("UTC")
                    else:
                        df.index = df.index.tz_localize("UTC")
                    all_data[pair] = df
                    print(f"{len(df)} bars")
                    break
                else:
                    print(f"empty (attempt {attempt+1})")
            except Exception as e:
                print(f"failed: {e}" if attempt == 2 else f"retry {attempt+1}...")
                time.sleep(2)

    return all_data


def _to_et(ts):
    """Convert UTC timestamp to ET (New York) datetime."""
    try:
        import pytz
        ny = pytz.timezone("America/New_York")
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        if ts.tzinfo is None:
            ts = pytz.utc.localize(ts)
        return ts.astimezone(ny)
    except ImportError:
        return ts


def _df_to_bars(df):
    return [Bar(r.Open, r.High, r.Low, r.Close) for _, r in df.iterrows()]


def _resample(df_5m, tf_str):
    return df_5m.resample(tf_str).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last"
    }).dropna()


def _get_trading_days(all_data):
    """Extract unique trading dates (ET) from the data."""
    import pytz
    ny = pytz.timezone("America/New_York")
    dates = set()
    for pair, df in all_data.items():
        if pair not in PREFERRED_SETUPS:
            continue
        for ts in df.index:
            if hasattr(ts, "to_pydatetime"):
                ts = ts.to_pydatetime()
            if ts.tzinfo is None:
                ts = pytz.utc.localize(ts)
            et = ts.astimezone(ny)
            if et.weekday() < 5:
                dates.add(et.date())
    return sorted(dates)


def _detect_setup_at_point(df_5m_slice, pair, pref_dir, partner_slice=None):
    """Run MM detection on a slice of data ending at a specific point.

    Returns a setup dict with confirmations, or None if no data.
    """
    from ict.ifvg import _fvgs, latest_inversion
    from ict import market_structure as mstruct
    from ict.smt import smt_divergence
    from ict.bias import htf_bias

    if df_5m_slice is None or len(df_5m_slice) < 10:
        return None

    pip = _pip(pair)
    cur_price = df_5m_slice["Close"].iloc[-1]
    cur_time = df_5m_slice.index[-1]

    tfs = {}
    tfs["5T"] = _df_to_bars(df_5m_slice)
    for tf_str, tf_key in [("15min", "15T"), ("30min", "30T"), ("1h", "60T")]:
        df_tf = _resample(df_5m_slice, tf_str)
        if len(df_tf) > 3:
            tfs[tf_key] = _df_to_bars(df_tf)

    # 1. IFVG zone
    ifvg_found = False
    ifvg_cascade = ("60T", "30T", "15T", "5T")
    for tf in ifvg_cascade:
        bars = tfs.get(tf)
        if not bars or len(bars) < 3:
            continue
        boxes = _fvgs(bars)
        for (bi, lo, hi) in reversed(boxes):
            if not (lo <= cur_price <= hi):
                continue
            idir = latest_inversion(bars[bi:], lo, hi)
            if idir == 0:
                lower_idx = ifvg_cascade.index(tf) + 1 if tf in ifvg_cascade else -1
                if lower_idx < len(ifvg_cascade):
                    lower_bars = tfs.get(ifvg_cascade[lower_idx])
                    if lower_bars:
                        idir = latest_inversion(lower_bars, lo, hi)
            if idir == pref_dir:
                ifvg_found = True
                break
        if ifvg_found:
            break

    # 2. MSS
    mss_confirmed = False
    for tf in ("5T", "15T"):
        bars = tfs.get(tf)
        if not bars or len(bars) < 6:
            continue
        res = mstruct.classify(bars)
        swings = res.get("stl" if pref_dir < 0 else "sth", [])
        if swings:
            last_sw = swings[-1]
            age = (len(bars) - 1) - last_sw.bar_index
            if last_sw.swept and age <= 40:
                mss_confirmed = True
                break

    # 3. SMT
    smt_confirmed = False
    if partner_slice is not None and len(partner_slice) >= 20:
        for tf_str, tf_key in [("1h", "60T"), ("15min", "15T")]:
            p_bars = tfs.get(tf_key)
            r_df = _resample(partner_slice, tf_str)
            if p_bars is None or len(r_df) < 20:
                continue
            r_bars = _df_to_bars(r_df)
            if len(p_bars) < 20 or len(r_bars) < 20:
                continue
            if (smt_divergence(p_bars, r_bars, pref_dir, inverse=False, lookback=20) or
                    smt_divergence(r_bars, p_bars, pref_dir, inverse=False, lookback=20)):
                smt_confirmed = True
                break

    # 4. FBC (full body close through any IFVG in the last few bars)
    fbc_confirmed = False
    for tf in ifvg_cascade:
        bars = tfs.get(tf)
        if not bars or len(bars) < 4:
            continue
        boxes = _fvgs(bars[:-1])
        if not boxes:
            continue
        last_bar = bars[-1]
        for (bi, lo, hi) in reversed(boxes[-5:]):
            if pref_dir > 0 and last_bar.Open > hi and last_bar.Close > hi:
                fbc_confirmed = True
                break
            elif pref_dir < 0 and last_bar.Open < lo and last_bar.Close < lo:
                fbc_confirmed = True
                break
        if fbc_confirmed:
            break

    # Build confirmations
    confirmations = []
    if ifvg_found:
        confirmations.append("IFVG")
    if mss_confirmed:
        confirmations.append("MSS")
    if smt_confirmed:
        confirmations.append("SMT")
    if fbc_confirmed:
        confirmations.append("FBC")

    if not confirmations:
        return None

    # Stop (structural, capped at 10 pips)
    m5_bars = tfs.get("5T", [])
    stop = None
    if m5_bars and len(m5_bars) >= 5:
        res = mstruct.classify(m5_bars)
        if pref_dir > 0:
            itls = [s for s in res.get("itl", []) if not s.swept]
            if itls:
                stop = itls[-1].price - 1.5 * pip
            else:
                stls = [s for s in res.get("stl", []) if not s.swept]
                if stls:
                    stop = stls[-1].price - 1.5 * pip
        else:
            iths = [s for s in res.get("ith", []) if not s.swept]
            if iths:
                stop = iths[-1].price + 1.5 * pip
            else:
                sths = [s for s in res.get("sth", []) if not s.swept]
                if sths:
                    stop = sths[-1].price + 1.5 * pip

    if stop is not None:
        stop_pips = abs(cur_price - stop) / pip
        if stop_pips > 10:
            stop = cur_price - pref_dir * 10 * pip
            stop_pips = 10
        elif stop_pips < 3:
            stop = cur_price - pref_dir * 3 * pip
            stop_pips = 3
    else:
        stop_pips = 10
        stop = cur_price - pref_dir * 10 * pip

    target = cur_price + pref_dir * 30 * pip
    target_pips = 30

    n = len(confirmations)
    if n >= 3:
        signal = "STRONG"
    elif n >= 2:
        signal = "MODERATE"
    else:
        signal = "WATCH"

    return {
        "pair": pair,
        "direction": pref_dir,
        "dir_label": "BUY" if pref_dir > 0 else "SELL",
        "price": cur_price,
        "time": cur_time,
        "confirmations": confirmations,
        "n_confirms": n,
        "signal": signal,
        "stop": stop,
        "stop_pips": stop_pips,
        "target": target,
        "target_pips": target_pips,
    }


def _simulate_outcome(setup, df_5m_after):
    """Walk forward from entry to see if target or stop was hit first.

    Returns dict with outcome, exit_price, exit_time, pips.
    """
    pip = _pip(setup["pair"])
    entry = setup["price"]
    stop = setup["stop"]
    target = setup["target"]
    d = setup["direction"]

    if df_5m_after is None or len(df_5m_after) == 0:
        return {"outcome": "OPEN", "pips": 0, "exit_price": entry, "exit_time": setup["time"]}

    for ts, row in df_5m_after.iterrows():
        if d > 0:
            if row["Low"] <= stop:
                return {"outcome": "LOSS", "pips": -(entry - stop) / pip,
                        "exit_price": stop, "exit_time": ts}
            if row["High"] >= target:
                return {"outcome": "WIN", "pips": (target - entry) / pip,
                        "exit_price": target, "exit_time": ts}
        else:
            if row["High"] >= stop:
                return {"outcome": "LOSS", "pips": -(stop - entry) / pip,
                        "exit_price": stop, "exit_time": ts}
            if row["Low"] <= target:
                return {"outcome": "WIN", "pips": (entry - target) / pip,
                        "exit_price": target, "exit_time": ts}

    last_price = df_5m_after["Close"].iloc[-1]
    unrealized = (last_price - entry) * d / pip
    return {"outcome": "OPEN", "pips": unrealized, "exit_price": last_price,
            "exit_time": df_5m_after.index[-1]}


def replay_week(all_data, days=5):
    """Replay MM setups day by day through each killzone.

    For each trading day, at the end of each killzone, runs the detection
    pipeline on data up to that point. If a setup fires (>= 2 confirmations),
    simulates the outcome using subsequent bars.

    Returns list of trade dicts with full details.
    """
    import pytz
    import pandas as pd

    ny = pytz.timezone("America/New_York")
    trading_days = _get_trading_days(all_data)

    if len(trading_days) > days:
        trading_days = trading_days[-days:]

    print(f"\nReplaying {len(trading_days)} trading days: {trading_days[0]} to {trading_days[-1]}")

    all_trades = []
    cooldown = {}

    for day in trading_days:
        day_trades = []

        for kz in KILLZONES_ET:
            kz_end_h, kz_end_m = kz["end_h"], kz["end_m"]
            kz_start_h, kz_start_m = kz["start_h"], kz["start_m"]

            for pair, pref_dir in PREFERRED_SETUPS.items():
                if pair not in all_data:
                    continue

                df = all_data[pair]

                kz_end_et = ny.localize(datetime(day.year, day.month, day.day,
                                                  kz_end_h, kz_end_m))
                kz_start_et = ny.localize(datetime(day.year, day.month, day.day,
                                                    kz_start_h, kz_start_m))
                kz_end_utc = kz_end_et.astimezone(pytz.utc)
                kz_start_utc = kz_start_et.astimezone(pytz.utc)

                # Also check mid-session (halfway through) for setups that form and resolve within the KZ
                check_points = [kz_start_utc + (kz_end_utc - kz_start_utc) / 2, kz_end_utc]

                for check_time in check_points:
                    # Cooldown: skip if we already alerted this pair in the last 30 min
                    cd_key = (pair, day)
                    last_alert = cooldown.get(cd_key)
                    if last_alert and (check_time - last_alert).total_seconds() < 1800:
                        continue

                    # Data up to this point (at least 2 hours of lookback)
                    lookback_start = check_time - timedelta(hours=6)
                    mask = (df.index >= lookback_start) & (df.index <= check_time)
                    df_slice = df.loc[mask]

                    if len(df_slice) < 10:
                        continue

                    # Partner data for SMT
                    partner = {"EURUSD": "GBPUSD", "GBPUSD": "EURUSD"}.get(pair)
                    partner_slice = None
                    if partner and partner in all_data:
                        pdf = all_data[partner]
                        partner_slice = pdf.loc[(pdf.index >= lookback_start) & (pdf.index <= check_time)]

                    setup = _detect_setup_at_point(df_slice, pair, pref_dir, partner_slice)

                    if setup is None or setup["n_confirms"] < 2:
                        continue

                    # Deduplicate: don't double-count if same setup fires at both checkpoints
                    dupe = False
                    for prev in day_trades:
                        if (prev["pair"] == pair and
                            abs((setup["time"] - prev["time"]).total_seconds()) < 3600 and
                            prev["confirmations"] == setup["confirmations"]):
                            dupe = True
                            break
                    if dupe:
                        continue

                    cooldown[cd_key] = check_time

                    # Forward data for outcome simulation (next 8 hours)
                    fwd_end = check_time + timedelta(hours=8)
                    fwd_mask = (df.index > check_time) & (df.index <= fwd_end)
                    df_fwd = df.loc[fwd_mask]

                    outcome = _simulate_outcome(setup, df_fwd)

                    trade = {
                        **setup,
                        "date": day,
                        "session": kz["name"],
                        "time_et": _to_et(setup["time"]),
                        **outcome,
                    }
                    day_trades.append(trade)

        all_trades.extend(day_trades)
        n = len(day_trades)
        wins = sum(1 for t in day_trades if t["outcome"] == "WIN")
        losses = sum(1 for t in day_trades if t["outcome"] == "LOSS")
        opens = sum(1 for t in day_trades if t["outcome"] == "OPEN")
        pips = sum(t["pips"] for t in day_trades)
        day_str = day.strftime("%a %d %b")
        if n > 0:
            print(f"  {day_str}: {n} setups — {wins}W / {losses}L / {opens}O — {pips:+.1f} pips")
        else:
            print(f"  {day_str}: no setups")

    return all_trades


def write_report(trades, trading_days):
    """Write the weekly replay report."""
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = []
    w = lines.append

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    w("# MM Weekly Replay — Day-by-Day Breakdown")
    w("")
    w(f"Generated: {now_str}")
    w(f"Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)")
    w(f"Detectors: IFVG zone + MSS + SMT + Full Body Close")
    w(f"Min confirmations: 2 (MODERATE+)")
    w(f"Stop: structural M5, capped 10 pips | Target: 30 pips")
    w("")

    # Overall summary
    total = len(trades)
    wins = [t for t in trades if t["outcome"] == "WIN"]
    losses = [t for t in trades if t["outcome"] == "LOSS"]
    opens = [t for t in trades if t["outcome"] == "OPEN"]
    total_pips = sum(t["pips"] for t in trades)
    wr = len(wins) / total * 100 if total > 0 else 0

    w("## Weekly Summary")
    w("")
    w(f"| Metric | Value |")
    w(f"|---|---|")
    w(f"| Total setups | **{total}** |")
    w(f"| Wins | **{len(wins)}** |")
    w(f"| Losses | **{len(losses)}** |")
    w(f"| Still open | {len(opens)} |")
    w(f"| Win rate | **{wr:.0f}%** |")
    w(f"| Total pips | **{total_pips:+.1f}** |")
    w(f"| Avg pips/trade | {total_pips/total:.1f} |" if total > 0 else "| Avg pips/trade | — |")
    w("")

    # Per-pair summary
    w("## Per-Pair Summary")
    w("")
    w("| Pair | Direction | Trades | W | L | WR | Pips |")
    w("|---|---|---|---|---|---|---|")
    for pair in ("GBPUSD", "EURUSD"):
        pt = [t for t in trades if t["pair"] == pair]
        pw = [t for t in pt if t["outcome"] == "WIN"]
        pl = [t for t in pt if t["outcome"] == "LOSS"]
        pp = sum(t["pips"] for t in pt)
        pwr = len(pw) / len(pt) * 100 if pt else 0
        d = "SELL" if PREFERRED_SETUPS.get(pair, 0) < 0 else "BUY"
        w(f"| {pair} | {d} | {len(pt)} | {len(pw)} | {len(pl)} | {pwr:.0f}% | {pp:+.1f} |")
    w("")

    # Day-by-day breakdown
    w("## Day-by-Day Breakdown")
    w("")

    by_day = defaultdict(list)
    for t in trades:
        by_day[t["date"]].append(t)

    for day in trading_days:
        day_str = day.strftime("%A %d %b %Y")
        day_trades = by_day.get(day, [])

        if not day_trades:
            w(f"### {day_str} — No setups")
            w("")
            w("No MM setups met the 2-confirmation threshold during any killzone.")
            w("")
            continue

        day_wins = sum(1 for t in day_trades if t["outcome"] == "WIN")
        day_losses = sum(1 for t in day_trades if t["outcome"] == "LOSS")
        day_pips = sum(t["pips"] for t in day_trades)
        day_emoji = "+" if day_pips > 0 else "-" if day_pips < 0 else "~"

        w(f"### {day_str} — {len(day_trades)} setups ({day_wins}W/{day_losses}L, {day_pips:+.1f} pips)")
        w("")
        w("| # | Time (ET) | Pair | Dir | Signal | Confirms | Entry | Stop | Target | Result | Pips |")
        w("|---|---|---|---|---|---|---|---|---|---|---|")

        for i, t in enumerate(sorted(day_trades, key=lambda x: x["time"]), 1):
            et_str = _to_et(t["time"]).strftime("%H:%M") if hasattr(t["time"], "strftime") else str(t["time"])[-8:-3]
            confirms = "+".join(t["confirmations"])
            result = t["outcome"]
            if result == "WIN":
                result_str = "WIN"
            elif result == "LOSS":
                result_str = "LOSS"
            else:
                result_str = "OPEN"

            w(f"| {i} | {et_str} | {t['pair']} | {t['dir_label']} | {t['signal']} | "
              f"{confirms} | {t['price']:.5f} | {t['stop']:.5f} | {t['target']:.5f} | "
              f"**{result_str}** | {t['pips']:+.1f} |")
        w("")

    # Session breakdown
    w("## Session Breakdown")
    w("")
    w("| Session | Trades | W | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    for kz in KILLZONES_ET:
        st = [t for t in trades if t["session"] == kz["name"]]
        sw = [t for t in st if t["outcome"] == "WIN"]
        sl = [t for t in st if t["outcome"] == "LOSS"]
        sp = sum(t["pips"] for t in st)
        swr = len(sw) / len(st) * 100 if st else 0
        w(f"| {kz['name']} | {len(st)} | {len(sw)} | {len(sl)} | {swr:.0f}% | {sp:+.1f} |")
    w("")

    # Signal strength breakdown
    w("## Signal Strength")
    w("")
    w("| Strength | Trades | W | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    for sig in ("STRONG", "MODERATE"):
        st = [t for t in trades if t["signal"] == sig]
        sw = [t for t in st if t["outcome"] == "WIN"]
        sl = [t for t in st if t["outcome"] == "LOSS"]
        sp = sum(t["pips"] for t in st)
        swr = len(sw) / len(st) * 100 if st else 0
        w(f"| {sig} (>={'3' if sig == 'STRONG' else '2'} confirms) | {len(st)} | {len(sw)} | {len(sl)} | {swr:.0f}% | {sp:+.1f} |")
    w("")

    # Detailed trade list
    w("## All Trades (detailed)")
    w("")
    for i, t in enumerate(sorted(trades, key=lambda x: x["time"]), 1):
        day_str = t["date"].strftime("%a %d")
        et_str = _to_et(t["time"]).strftime("%H:%M") if hasattr(t["time"], "strftime") else ""
        result = t["outcome"]
        w(f"{i}. **{result}** {t['dir_label']} {t['pair']} — {day_str} {et_str} ET "
          f"({t['session']}) — {t['signal']} [{'+'.join(t['confirmations'])}] — "
          f"Entry {t['price']:.5f}, Stop {t['stop']:.5f}, Target {t['target']:.5f} — "
          f"**{t['pips']:+.1f} pips**")
    w("")

    w("---")
    w("")
    w("*Simulated outcomes use 10-pip structural stop + 30-pip target on Yahoo 5-min data.*")
    w("*Real entries would use the live bot's structural stop + nearest qualifying fib/liquidity target.*")
    w("")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nReport written to {REPORT}")
    return REPORT


def push_report():
    """Git add, commit, push the report."""
    try:
        subprocess.run(["git", "add", "-f", REPORT], cwd=_ROOT, check=True)
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=_ROOT, capture_output=True,
        )
        if result.returncode == 0:
            print("No changes to commit.")
            return True
        subprocess.run(
            ["git", "commit", "-m", "MM weekly replay report (auto)"],
            cwd=_ROOT, check=True,
        )
        for attempt in range(4):
            r = subprocess.run(
                ["git", "push", "origin", "HEAD"],
                cwd=_ROOT, capture_output=True, text=True,
            )
            if r.returncode == 0:
                print("REPORT PUSHED.")
                return True
            if attempt < 3:
                wait = 2 ** (attempt + 1)
                print(f"Push failed, retrying in {wait}s...")
                subprocess.run(
                    ["git", "pull", "origin", "HEAD", "--no-rebase", "--no-edit"],
                    cwd=_ROOT, capture_output=True,
                )
                time.sleep(wait)
        print(f"Push failed: {r.stderr}")
        return False
    except Exception as e:
        print(f"Git error: {e}")
        return False


def _selftest():
    print("selftest: verifying imports...")
    from ict.ifvg import _fvgs, latest_inversion
    print("  IFVG OK")
    from ict import market_structure as mstruct
    print("  Market structure OK")
    from ict.smt import smt_divergence
    print("  SMT OK")
    from ict.bias import htf_bias
    print("  Bias OK")
    print("selftest OK — all detectors available")


def main():
    ap = argparse.ArgumentParser(description="MM weekly historical replay")
    ap.add_argument("--days", type=int, default=5, help="Trading days to replay (default 5)")
    ap.add_argument("--no-push", action="store_true", help="Skip git push")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return 0

    print(f"Fetching {a.days + 3} days of Yahoo data for historical replay...")
    all_data = fetch_yahoo(days=a.days + 3)

    if "EURUSD" not in all_data or "GBPUSD" not in all_data:
        print("ERROR: Could not fetch EURUSD and/or GBPUSD")
        return 1

    trading_days = _get_trading_days(all_data)
    if len(trading_days) > a.days:
        trading_days = trading_days[-a.days:]

    print(f"\nReplaying MM setups through {len(trading_days)} trading days...")
    trades = replay_week(all_data, days=a.days)

    write_report(trades, trading_days)

    if not a.no_push:
        push_report()

    # Console summary
    total = len(trades)
    wins = sum(1 for t in trades if t["outcome"] == "WIN")
    losses = sum(1 for t in trades if t["outcome"] == "LOSS")
    total_pips = sum(t["pips"] for t in trades)

    print(f"\n{'='*60}")
    print("MM WEEKLY REPLAY SUMMARY")
    print(f"{'='*60}")
    print(f"  Total setups:  {total}")
    print(f"  Wins:          {wins}")
    print(f"  Losses:        {losses}")
    print(f"  Win rate:      {wins/total*100:.0f}%" if total > 0 else "  Win rate:      —")
    print(f"  Total pips:    {total_pips:+.1f}")
    print(f"\n  Day-by-day:")
    by_day = defaultdict(list)
    for t in trades:
        by_day[t["date"]].append(t)
    for day in trading_days:
        dt = by_day.get(day, [])
        dw = sum(1 for t in dt if t["outcome"] == "WIN")
        dl = sum(1 for t in dt if t["outcome"] == "LOSS")
        dp = sum(t["pips"] for t in dt)
        day_str = day.strftime("%a %d %b")
        if dt:
            print(f"    {day_str}: {len(dt)} trades — {dw}W/{dl}L — {dp:+.1f} pips")
        else:
            print(f"    {day_str}: no setups")

    return 0


if __name__ == "__main__":
    sys.exit(main())

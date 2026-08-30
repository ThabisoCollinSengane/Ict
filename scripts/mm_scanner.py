#!/usr/bin/env python3
"""Semi-auto Market Maker entry scanner.

Fetches recent Yahoo Finance data, runs the MM detection pipeline
(IFVG zone + MSS/SMT/full-body-close confirmations) filtered to the
user's preferred directions:

    Dollar UP   → SELL GBPUSD  (GBP weaker)
    Dollar DOWN → BUY EURUSD   (EUR stronger)

Outputs detected setups with entry, stop, target, and which
confirmations fired.  Auto-pushes an alert report to the branch.

Usage (from the repo root on the Windows VM):
    python scripts/mm_scanner.py                  # scan now
    python scripts/mm_scanner.py --pair GBPUSD    # single pair
    python scripts/mm_scanner.py --no-push        # skip git push
    python scripts/mm_scanner.py --selftest       # imports only
"""
from __future__ import annotations
import argparse, os, sys, time, subprocess
from datetime import datetime, timedelta
from collections import namedtuple

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

REPORT = os.path.join(_ROOT, "data", "mm_scan_alerts.md")

# The user's directional preference
PREFERRED_SETUPS = {
    "GBPUSD": -1,   # SELL GBPUSD when dollar is strong
    "EURUSD": +1,    # BUY EURUSD when dollar is weak
}

# All sessions to scan — including the London→NY overlap/handover
# Times in ET (New York time)
MM_SESSIONS = [
    {"name": "London Open",      "start": (3, 0),   "end": (5, 0)},
    {"name": "London→NY Overlap", "start": (5, 0),   "end": (7, 0)},
    {"name": "NY AM",            "start": (7, 0),   "end": (10, 0)},
    {"name": "NY Noon Block",    "start": (12, 0),  "end": (13, 0), "blocked": True},
    {"name": "NY PM",            "start": (13, 0),  "end": (16, 0)},
]

# ICT Macros — the institutional delivery windows (XX:50–XX:10)
MACRO_WINDOWS_NY = [
    ("London Macro 1", "01:50", "02:10"),
    ("London Macro 2", "02:50", "03:10"),
    ("London Macro 3", "03:50", "04:10"),
    ("London Macro 4", "04:50", "05:10"),
    ("NY Macro 1",     "08:50", "09:10"),
    ("NY Macro 2",     "09:50", "10:10"),
    ("NY Macro 3",     "10:50", "11:10"),
    ("NY Macro 4",     "11:50", "12:10"),
]

Bar = namedtuple("Bar", ["Open", "High", "Low", "Close"])

# Yahoo Finance tickers
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


def fetch_yahoo(days=5):
    """Fetch 5-min OHLC for all required pairs."""
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


def _resample(df_5m, tf_str):
    """Resample 5-min DataFrame to a higher timeframe."""
    import pandas as pd
    return df_5m.resample(tf_str).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last"
    }).dropna()


def _df_to_bars(df):
    """Convert DataFrame rows to namedtuple bars."""
    return [Bar(r.Open, r.High, r.Low, r.Close) for _, r in df.iterrows()]


def _pip(pair):
    return 0.01 if "JPY" in pair else 0.0001


def _get_et_time(ts):
    """Convert a timestamp to ET (New York) hour/minute."""
    import pytz
    ny = pytz.timezone("America/New_York")
    if hasattr(ts, "to_pydatetime"):
        ts = ts.to_pydatetime()
    if ts.tzinfo is None:
        import pytz as _p
        ts = _p.utc.localize(ts)
    et = ts.astimezone(ny)
    return et.hour, et.minute


def _current_session(ts):
    """Identify which session the current time falls in."""
    h, m = _get_et_time(ts)
    t_min = h * 60 + m
    for sess in MM_SESSIONS:
        s_min = sess["start"][0] * 60 + sess["start"][1]
        e_min = sess["end"][0] * 60 + sess["end"][1]
        if s_min <= t_min < e_min:
            return sess
    return None


def _current_macro(ts):
    """Check if we're inside an ICT macro window (XX:50-XX:10)."""
    h, m = _get_et_time(ts)
    for name, s, e in MACRO_WINDOWS_NY:
        sh, sm = int(s.split(":")[0]), int(s.split(":")[1])
        eh, em = int(e.split(":")[0]), int(e.split(":")[1])
        s_min = sh * 60 + sm
        e_min = eh * 60 + em
        t_min = h * 60 + m
        if s_min <= t_min < e_min:
            return name
    return None


def _detect_london_consolidation(df_5m, pair):
    """Detect if London session formed a consolidation range.

    Returns (high, low, width_pips) of the London range or None.
    Used to detect London→NY overlap breakout setups.
    """
    import pytz
    ny = pytz.timezone("America/New_York")
    pip = _pip(pair)

    # Filter to London session bars (03:00-05:00 ET)
    london_bars = []
    for ts, row in df_5m.iterrows():
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        if ts.tzinfo is None:
            ts = pytz.utc.localize(ts)
        et = ts.astimezone(ny)
        if et.hour >= 3 and et.hour < 5:
            # Only today's London
            london_bars.append(row)

    if len(london_bars) < 8:  # need at least 8 bars (40 min)
        return None

    hi = max(b["High"] for b in london_bars)
    lo = min(b["Low"] for b in london_bars)
    width = (hi - lo) / pip

    # A consolidation is a tight range (< 35 pips per AMD config)
    if width <= 35:
        return {"high": hi, "low": lo, "width_pips": width}
    return None


def scan_mm_setups(all_data, pairs=None):
    """Scan for MM setups on the preferred pairs/directions.

    Scans ALL sessions: London, London→NY overlap, NY AM, NY PM.
    Detects London consolidation → NY breakout pattern.
    Returns a list of setup dicts with all details.
    """
    import pandas as pd
    import config
    from ict.ifvg import _fvgs, latest_inversion, find_inversion_fvgs
    from ict.smt import smt_divergence
    from ict import market_structure as mstruct
    from ict.bias import htf_bias

    if pairs is None:
        pairs = list(PREFERRED_SETUPS.keys())

    setups = []

    for pair in pairs:
        if pair not in all_data:
            print(f"  {pair}: no data, skipping")
            continue

        pref_dir = PREFERRED_SETUPS.get(pair)
        if pref_dir is None:
            continue

        df_5m = all_data[pair]
        pip = _pip(pair)
        cur_price = df_5m["Close"].iloc[-1]
        cur_time = df_5m.index[-1]

        # Session context
        session = _current_session(cur_time)
        macro = _current_macro(cur_time)
        london_range = _detect_london_consolidation(df_5m, pair)

        session_name = session["name"] if session else "Outside KZ"
        blocked = session.get("blocked", False) if session else False

        print(f"\n  Scanning {pair} for {'BUY' if pref_dir > 0 else 'SELL'} setups...")
        print(f"    Current: {cur_price:.5f} at {cur_time}")
        print(f"    Session: {session_name}" + (f" | Macro: {macro}" if macro else ""))
        if london_range:
            print(f"    London consolidation: {london_range['high']:.5f}-{london_range['low']:.5f} ({london_range['width_pips']:.0f} pips)")
        if blocked:
            print(f"    ** NY NOON BLOCK — no entries **")

        # Build multi-TF bars
        tfs = {}
        tfs["5T"] = _df_to_bars(df_5m)
        for tf_str in ("15min", "30min", "1h", "4h"):
            tf_key = {"15min": "15T", "30min": "30T", "1h": "60T", "4h": "240T"}[tf_str]
            df_tf = _resample(df_5m, tf_str)
            if len(df_tf) > 3:
                tfs[tf_key] = _df_to_bars(df_tf)

        # --- 1. IFVG ZONE DETECTION ---
        # Cascade highest→lowest TF looking for an inverted FVG price is inside
        ifvg_zones = []
        ifvg_cascade = ("240T", "60T", "30T", "15T", "5T")
        for tf in ifvg_cascade:
            bars = tfs.get(tf)
            if not bars or len(bars) < 3:
                continue
            boxes = _fvgs(bars)
            if not boxes:
                continue
            # Check each box (most recent first) for inversion + price inside
            for (bi, lo, hi) in reversed(boxes):
                if not (lo <= cur_price <= hi):
                    continue
                idir = latest_inversion(bars[bi:], lo, hi)
                if idir == 0:
                    # Check one TF lower
                    lower_idx = ifvg_cascade.index(tf) + 1 if tf in ifvg_cascade else -1
                    if lower_idx < len(ifvg_cascade):
                        lower_bars = tfs.get(ifvg_cascade[lower_idx])
                        if lower_bars:
                            idir = latest_inversion(lower_bars, lo, hi)
                if idir == pref_dir:
                    ifvg_zones.append({
                        "tf": tf, "lo": lo, "hi": hi, "mid": (lo + hi) / 2,
                        "idir": idir
                    })
                    break  # take the first valid zone on this TF

        # Also scan for recent IFVGs not necessarily containing current price
        # (approaching zones the user should watch)
        watch_zones = []
        for tf in ifvg_cascade:
            bars = tfs.get(tf)
            if not bars or len(bars) < 3:
                continue
            invs = find_inversion_fvgs(bars, direction=pref_dir, scan=60, max_zones=3)
            for inv in invs:
                dist = (inv["lo"] - cur_price) * pref_dir if pref_dir > 0 else (cur_price - inv["hi"]) * pref_dir
                dist_pips = dist / pip
                if 0 < dist_pips < 50:
                    watch_zones.append({
                        "tf": tf, "lo": inv["lo"], "hi": inv["hi"],
                        "mid": inv["mid"], "dist_pips": dist_pips
                    })

        # --- 2. MARKET STRUCTURE SHIFT (MSS) ---
        mss_confirmed = False
        mss_tf = None
        mss_detail = ""
        for tf in ("5T", "15T"):
            bars = tfs.get(tf)
            if not bars or len(bars) < 6:
                continue
            res = mstruct.classify(bars)
            # For a sell: look for a recent STL being swept (lower low = downside MSS)
            # For a buy: look for a recent STH being swept (higher high = upside MSS)
            swings = res.get("stl" if pref_dir < 0 else "sth", [])
            if not swings:
                continue
            last_sw = swings[-1]
            age = (len(bars) - 1) - last_sw.bar_index
            if last_sw.swept and age <= 40:
                mss_confirmed = True
                mss_tf = tf
                mss_detail = f"{tf} {'STL' if pref_dir < 0 else 'STH'} swept at {last_sw.price:.5f} ({age} bars ago)"
                break

        # --- 3. SMT DIVERGENCE (EU vs GU) ---
        smt_confirmed = False
        smt_detail = ""
        partner = {"EURUSD": "GBPUSD", "GBPUSD": "EURUSD"}.get(pair)
        if partner and partner in all_data:
            for tf_str, tf_key in [("1h", "60T"), ("4h", "240T"), ("15min", "15T")]:
                p_bars = tfs.get(tf_key)
                r_bars_df = _resample(all_data[partner], tf_str) if partner in all_data else None
                if p_bars is None or r_bars_df is None or len(r_bars_df) < 20:
                    continue
                r_bars = _df_to_bars(r_bars_df)
                if len(p_bars) < 20 or len(r_bars) < 20:
                    continue
                # Check both ways (either pair as primary)
                if (smt_divergence(p_bars, r_bars, pref_dir, inverse=False, lookback=20) or
                        smt_divergence(r_bars, p_bars, pref_dir, inverse=False, lookback=20)):
                    smt_confirmed = True
                    smt_detail = f"{tf_key} EU/GU SMT divergence confirmed"
                    break

        # --- 4. FULL BODY CLOSE ABOVE/BELOW IFVG ---
        fbc_confirmed = False
        fbc_detail = ""
        for zone in ifvg_zones:
            bars = tfs.get(zone["tf"])
            if not bars:
                continue
            last_bar = bars[-1]
            # Full body close: both Open and Close on the correct side
            if pref_dir > 0:
                # Buy: full body close above the IFVG zone = demand confirmed
                if last_bar.Open > zone["hi"] and last_bar.Close > zone["hi"]:
                    fbc_confirmed = True
                    fbc_detail = f"{zone['tf']} full body close above IFVG ({zone['hi']:.5f})"
            else:
                # Sell: full body close below the IFVG zone = supply confirmed
                if last_bar.Open < zone["lo"] and last_bar.Close < zone["lo"]:
                    fbc_confirmed = True
                    fbc_detail = f"{zone['tf']} full body close below IFVG ({zone['lo']:.5f})"

        # --- 5. STRUCTURAL BIAS (H1/H4) ---
        h1_bias = 0
        h4_bias = 0
        for tf, attr in [("60T", "h1_bias"), ("240T", "h4_bias")]:
            bars = tfs.get(tf)
            if bars and len(bars) >= 10:
                b = htf_bias(bars, lookback=10)
                if attr == "h1_bias":
                    h1_bias = b
                else:
                    h4_bias = b

        # --- 6. DEALING RANGE + PREMIUM/DISCOUNT ---
        dr_info = None
        try:
            from ict.dealing_range import detect_dealing_range, premium_discount
            h1_bars = tfs.get("60T")
            if h1_bars and len(h1_bars) >= 20:
                dr = detect_dealing_range(h1_bars, lookback=100)
                if dr and dr.width > 0:
                    pd_zone = premium_discount(cur_price, dr.high, dr.low)
                    correct_zone = (pref_dir > 0 and pd_zone == "DISCOUNT") or \
                                   (pref_dir < 0 and pd_zone == "PREMIUM")
                    dr_info = {
                        "high": dr.high, "low": dr.low, "eq": dr.equilibrium,
                        "pd": pd_zone, "correct_zone": correct_zone,
                        "width_pips": dr.width / pip
                    }
        except ImportError:
            pass

        # --- 7. ENTRY PATTERN (FVG/OB in the IFVG zone) ---
        entry_patterns = []
        for zone in ifvg_zones:
            for etf in ("15T", "5T"):
                bars = tfs.get(etf)
                if not bars or len(bars) < 5:
                    continue
                # Use the IFVG module's _fvgs to scan for 3-candle gaps
                boxes = _fvgs(bars[-24:])
                for (bi, fvg_lo, fvg_hi) in boxes:
                    fvg_mid = (fvg_lo + fvg_hi) / 2
                    # FVG must be inside the IFVG zone
                    if fvg_lo >= zone["lo"] and fvg_hi <= zone["hi"]:
                        # And on the retracement side
                        if (pref_dir < 0 and fvg_mid >= cur_price) or \
                           (pref_dir > 0 and fvg_mid <= cur_price):
                            entry_patterns.append({
                                "tf": etf, "type": "FVG",
                                "entry": fvg_mid, "lo": fvg_lo, "hi": fvg_hi,
                                "ifvg_tf": zone["tf"]
                            })

        # --- 8. LONDON CONSOLIDATION → NY BREAKOUT ---
        london_breakout = None
        if london_range:
            lr = london_range
            if pref_dir > 0 and cur_price > lr["high"]:
                london_breakout = {
                    "type": "breakout_above",
                    "range_high": lr["high"], "range_low": lr["low"],
                    "break_pips": (cur_price - lr["high"]) / pip,
                    "detail": f"Price broke above London consolidation high {lr['high']:.5f} by {(cur_price - lr['high'])/pip:.1f} pips"
                }
            elif pref_dir < 0 and cur_price < lr["low"]:
                london_breakout = {
                    "type": "breakout_below",
                    "range_high": lr["high"], "range_low": lr["low"],
                    "break_pips": (lr["low"] - cur_price) / pip,
                    "detail": f"Price broke below London consolidation low {lr['low']:.5f} by {(lr['low'] - cur_price)/pip:.1f} pips"
                }
            elif lr["low"] <= cur_price <= lr["high"]:
                london_breakout = {
                    "type": "inside_range",
                    "range_high": lr["high"], "range_low": lr["low"],
                    "break_pips": 0,
                    "detail": f"Price still inside London range {lr['low']:.5f}-{lr['high']:.5f} — watch for sweep + reversal or breakout"
                }

        # --- BUILD SETUP ---
        confirmations = []
        if ifvg_zones:
            confirmations.append("IFVG_ZONE")
        if mss_confirmed:
            confirmations.append("MSS")
        if smt_confirmed:
            confirmations.append("SMT")
        if fbc_confirmed:
            confirmations.append("FBC")
        if london_breakout and london_breakout["type"] in ("breakout_above", "breakout_below"):
            confirmations.append("LONDON_BREAK")

        # Compute stop from M5 structure
        stop = None
        m5_bars = tfs.get("5T", [])
        if m5_bars and len(m5_bars) >= 5:
            res = mstruct.classify(m5_bars)
            # Stop beyond the last intact opposing swing
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
            # Cap at 10 pips
            if stop_pips > 10:
                stop = cur_price - pref_dir * 10 * pip
                stop_pips = 10
        else:
            stop_pips = 10
            stop = cur_price - pref_dir * 10 * pip

        # Target: nearest fib extension or PDH/PDL
        target = cur_price + pref_dir * 30 * pip  # default 30 pip target
        target_type = "default_30pip"

        setup = {
            "pair": pair,
            "direction": pref_dir,
            "dir_label": "BUY" if pref_dir > 0 else "SELL",
            "price": cur_price,
            "time": str(cur_time),
            "session": session_name,
            "session_blocked": blocked,
            "macro": macro,
            "london_range": london_range,
            "london_breakout": london_breakout,
            "ifvg_zones": ifvg_zones,
            "watch_zones": watch_zones,
            "mss": {"confirmed": mss_confirmed, "tf": mss_tf, "detail": mss_detail},
            "smt": {"confirmed": smt_confirmed, "detail": smt_detail},
            "fbc": {"confirmed": fbc_confirmed, "detail": fbc_detail},
            "h1_bias": h1_bias,
            "h4_bias": h4_bias,
            "dr": dr_info,
            "entry_patterns": entry_patterns,
            "confirmations": confirmations,
            "n_confirmations": len(confirmations),
            "stop": stop,
            "stop_pips": stop_pips,
            "target": target,
            "target_type": target_type,
        }

        # Signal strength
        if len(confirmations) >= 3:
            setup["signal"] = "STRONG"
        elif len(confirmations) >= 2:
            setup["signal"] = "MODERATE"
        elif len(confirmations) >= 1:
            setup["signal"] = "WATCH"
        else:
            setup["signal"] = "NO_SETUP"

        setups.append(setup)

    return setups


def write_report(setups, all_data):
    """Write alert report."""
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = []
    w = lines.append

    try:
        from datetime import timezone
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    w("# MM Semi-Auto Scanner Alerts")
    w("")
    w(f"Generated: {now_str}")
    w(f"Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)")
    w(f"Detectors: IFVG zone + MSS + SMT + Full Body Close + London→NY Breakout")
    w(f"Sessions: London Open | London→NY Overlap | NY AM | NY PM (all killzones)")
    w("")

    # Quick summary
    active = [s for s in setups if s["signal"] in ("STRONG", "MODERATE")]
    watching = [s for s in setups if s["signal"] == "WATCH"]

    if active:
        w("## ACTIVE SETUPS")
        w("")
        for s in active:
            strength = s["signal"]
            w(f"### {strength}: {s['dir_label']} {s['pair']} @ {s['price']:.5f}")
            w("")
            w(f"| Detail | Value |")
            w(f"|---|---|")
            w(f"| Signal | **{strength}** ({s['n_confirmations']} confirmations) |")
            w(f"| Direction | {s['dir_label']} |")
            w(f"| Current Price | {s['price']:.5f} |")
            w(f"| Time | {s['time']} |")
            w(f"| Session | **{s['session']}** |")
            if s.get("macro"):
                w(f"| ICT Macro | **{s['macro']}** (institutional delivery window) |")
            w(f"| Confirmations | {', '.join(s['confirmations'])} |")
            w(f"| Stop | {s['stop']:.5f} ({s['stop_pips']:.1f} pips) |")
            w(f"| H1 Bias | {'Bullish' if s['h1_bias'] > 0 else 'Bearish' if s['h1_bias'] < 0 else 'Flat'} |")
            w(f"| H4 Bias | {'Bullish' if s['h4_bias'] > 0 else 'Bearish' if s['h4_bias'] < 0 else 'Flat'} |")
            w("")

            # London consolidation → NY breakout context
            if s.get("london_breakout"):
                lb = s["london_breakout"]
                w(f"**London→NY Context:** {lb['detail']}")
                if lb["type"] in ("breakout_above", "breakout_below"):
                    w(f"  Break confirmed: {lb['break_pips']:.1f} pips beyond London range — look for IFVG retrace entry")
                elif lb["type"] == "inside_range":
                    w(f"  Still consolidating — watch for sweep of {s['london_range']['high']:.5f} or {s['london_range']['low']:.5f}")
                w("")

            # Dealing range context
            if s["dr"]:
                dr = s["dr"]
                w(f"**Dealing Range:** {dr['high']:.5f} - {dr['low']:.5f} (eq {dr['eq']:.5f}, {dr['width_pips']:.0f} pips)")
                w(f"  Price in **{dr['pd']}** zone — {'CORRECT for entry' if dr['correct_zone'] else 'WRONG zone — wait for retrace'}")
                w("")

            # IFVG zones price is IN
            if s["ifvg_zones"]:
                w("**IFVG Zones (price inside):**")
                w("")
                w("| TF | Low | High | Mid | Dir |")
                w("|---|---|---|---|---|")
                for z in s["ifvg_zones"]:
                    d = "Demand (+1)" if z["idir"] > 0 else "Supply (-1)"
                    w(f"| {z['tf']} | {z['lo']:.5f} | {z['hi']:.5f} | {z['mid']:.5f} | {d} |")
                w("")

            # Entry patterns
            if s["entry_patterns"]:
                w("**Entry Patterns (FVG/OB inside IFVG):**")
                w("")
                w("| TF | Type | Entry | Range | IFVG TF |")
                w("|---|---|---|---|---|")
                for ep in s["entry_patterns"]:
                    w(f"| {ep['tf']} | {ep['type']} | {ep['entry']:.5f} | {ep['lo']:.5f}-{ep['hi']:.5f} | {ep['ifvg_tf']} |")
                w("")

            # Confirmation details
            w("**Confirmation Details:**")
            w("")
            if s["mss"]["confirmed"]:
                w(f"- MSS: {s['mss']['detail']}")
            else:
                w("- MSS: Not confirmed (no recent structure shift)")
            if s["smt"]["confirmed"]:
                w(f"- SMT: {s['smt']['detail']}")
            else:
                w("- SMT: Not confirmed (EU/GU not diverging)")
            if s["fbc"]["confirmed"]:
                w(f"- FBC: {s['fbc']['detail']}")
            else:
                w("- FBC: No full body close through IFVG yet")
            w("")
    else:
        w("## No Active Setups")
        w("")
        w("No setups meet the minimum 2-confirmation threshold right now.")
        w("")

    # Watch list (1 confirmation — building)
    if watching:
        w("## WATCHLIST (1 confirmation — building)")
        w("")
        for s in watching:
            w(f"### {s['dir_label']} {s['pair']} @ {s['price']:.5f}")
            w("")
            w(f"- Confirmations: {', '.join(s['confirmations'])}")
            if s["mss"]["confirmed"]:
                w(f"- MSS: {s['mss']['detail']}")
            if s["smt"]["confirmed"]:
                w(f"- SMT: {s['smt']['detail']}")
            if s["fbc"]["confirmed"]:
                w(f"- FBC: {s['fbc']['detail']}")
            w("")

            # Watch zones — IFVGs price is approaching
            if s["watch_zones"]:
                w("  **Approaching IFVG zones (watch for retrace into):**")
                w("")
                w("  | TF | Low | High | Distance |")
                w("  |---|---|---|---|")
                for wz in s["watch_zones"][:5]:
                    w(f"  | {wz['tf']} | {wz['lo']:.5f} | {wz['hi']:.5f} | {wz['dist_pips']:.1f} pips |")
                w("")

    # No setup at all
    no_setup = [s for s in setups if s["signal"] == "NO_SETUP"]
    if no_setup:
        w("## NO SETUP")
        w("")
        for s in no_setup:
            w(f"- {s['dir_label']} {s['pair']}: no confirmations firing — flat/unclear structure")
            if s["dr"]:
                w(f"  DR: {s['dr']['high']:.5f}-{s['dr']['low']:.5f}, price in {s['dr']['pd']}")
        w("")

    # News check
    w("## News Check")
    w("")
    try:
        from news_filter import NewsCalendar
        nc = NewsCalendar()
        csv_path = os.path.join(_ROOT, "data", "news_events.csv")
        if os.path.exists(csv_path):
            with open(csv_path) as f:
                nc.load_csv(f.read())
            from datetime import timezone
            now = datetime.now(timezone.utc)
            impact = nc.nearest_impact(now)
            pre = nc.pre_release_impact(now)
            if impact:
                w(f"**BLOCKED: {impact}-impact event active NOW** — do not enter")
            elif pre:
                w(f"**WARNING: {pre}-impact event in next 16-90 minutes** — caution")
            else:
                w("Clear — no high-impact events in the immediate window")
            if nc.is_nfp_week(now):
                w("**NFP WEEK** — reduced probability Wed-Fri NY")
        else:
            w("news_events.csv not found — news filter inactive")
    except Exception as e:
        w(f"News check failed: {e}")
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
            print("No changes to commit (report unchanged).")
            return True

        subprocess.run(
            ["git", "commit", "-m", "MM scanner alerts (auto)"],
            cwd=_ROOT, check=True,
        )
        for attempt in range(4):
            r = subprocess.run(
                ["git", "push", "origin", "HEAD"],
                cwd=_ROOT, capture_output=True, text=True,
            )
            if r.returncode == 0:
                print("ALERTS PUSHED to branch.")
                return True
            if attempt < 3:
                wait = 2 ** (attempt + 1)
                print(f"Push failed, retrying in {wait}s...")
                subprocess.run(
                    ["git", "pull", "origin", "HEAD", "--no-rebase", "--no-edit"],
                    cwd=_ROOT, capture_output=True,
                )
                time.sleep(wait)
        print(f"Push failed after retries: {r.stderr}")
        return False
    except Exception as e:
        print(f"Git push error: {e}")
        return False


def _selftest():
    print("selftest: verifying imports...")
    from ict.ifvg import _fvgs, latest_inversion, find_inversion_fvgs
    print("  IFVG module OK")
    from ict.smt import smt_divergence
    print("  SMT module OK")
    from ict import market_structure as mstruct
    print("  Market structure OK")
    from ict.bias import htf_bias
    print("  Bias module OK")
    from ict.dealing_range import detect_dealing_range, premium_discount
    print("  Dealing range OK")
    from ict.fvg import find_fvg
    print("  FVG module OK")
    from news_filter import NewsCalendar
    print("  News filter OK")
    print("selftest OK — all detectors available")


def main():
    ap = argparse.ArgumentParser(description="MM semi-auto entry scanner")
    ap.add_argument("--days", type=int, default=5, help="Days of data to fetch (default 5)")
    ap.add_argument("--pair", type=str, default=None, help="Scan single pair (EURUSD or GBPUSD)")
    ap.add_argument("--no-push", action="store_true", help="Skip git push")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return 0

    pairs = [a.pair.upper()] if a.pair else None

    print(f"Fetching {a.days} days of data from Yahoo Finance...")
    all_data = fetch_yahoo(days=a.days)
    if "EURUSD" not in all_data or "GBPUSD" not in all_data:
        print("ERROR: Could not fetch EURUSD and/or GBPUSD")
        return 1

    print("\nScanning for MM setups...")
    setups = scan_mm_setups(all_data, pairs=pairs)

    write_report(setups, all_data)

    # Console summary
    print(f"\n{'='*60}")
    print(f"MM SCANNER RESULTS")
    print(f"{'='*60}")
    for s in setups:
        sig = s["signal"]
        icon = {"STRONG": "[!!!]", "MODERATE": "[!!]", "WATCH": "[.]", "NO_SETUP": "[-]"}[sig]
        print(f"  {icon} {s['dir_label']:5} {s['pair']:8} {sig:10} confirmations: {', '.join(s['confirmations']) or 'none'}")
        if s["ifvg_zones"]:
            z = s["ifvg_zones"][0]
            print(f"        IFVG {z['tf']}: {z['lo']:.5f}-{z['hi']:.5f}")
        if s["mss"]["confirmed"]:
            print(f"        {s['mss']['detail']}")
        if s["smt"]["confirmed"]:
            print(f"        {s['smt']['detail']}")
        if s["dr"]:
            print(f"        DR: {s['dr']['pd']} zone ({'correct' if s['dr']['correct_zone'] else 'wrong — wait'})")

    if not a.no_push:
        push_report()
    else:
        print("\nSkipping push (--no-push)")

    return 0


if __name__ == "__main__":
    sys.exit(main())

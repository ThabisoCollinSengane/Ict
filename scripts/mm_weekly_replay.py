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
_SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

from intermarket_cascade import intermarket_cascade

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
    "T5":     "^FVX",
    "T10":    "^TNX",
    "T30":    "^TYX",
    "DXY":    "DX-Y.NYB",
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

    period = f"{min(int(days * 1.6) + 5, 59)}d"
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
    for tf_str, tf_key in [("15min", "15T"), ("30min", "30T"), ("1h", "60T"), ("4h", "240T")]:
        df_tf = _resample(df_5m_slice, tf_str)
        if len(df_tf) > 3:
            tfs[tf_key] = _df_to_bars(df_tf)

    # 1. IFVG zone — top-down TF cascade (H4 → H1 → M30 → M15 → M5)
    ifvg_found = False
    ifvg_zones = []
    ifvg_cascade = ("240T", "60T", "30T", "15T", "5T")
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
                ifvg_zones.append({"tf": tf, "lo": lo, "hi": hi})
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

    # 4. FBC — full body close through a confirmed IFVG zone only
    fbc_confirmed = False
    for zone in ifvg_zones:
        bars = tfs.get(zone["tf"])
        if not bars or len(bars) < 2:
            continue
        last_bar = bars[-1]
        if pref_dir > 0 and last_bar.Open > zone["hi"] and last_bar.Close > zone["hi"]:
            fbc_confirmed = True
            break
        elif pref_dir < 0 and last_bar.Open < zone["lo"] and last_bar.Close < zone["lo"]:
            fbc_confirmed = True
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


def _detect_amd_at_point(df_5m_slice, pair, pref_dir, partner_slice=None, dxy_slice=None):
    """Run the base algorithm's AMD detection (Judas reversal + breakout).

    Uses ict/amd.py detect_amd_setup (Judas reversal) and detect_breakout
    (continuation). These are the 'normal' algorithm entries — the M15
    consolidation range + sweep that the backtester uses.

    Returns a setup dict or None.
    """
    from ict.amd import detect_amd_setup, detect_breakout
    from ict import market_structure as mstruct
    from ict.smt import smt_divergence

    if df_5m_slice is None or len(df_5m_slice) < 30:
        return None

    pip = _pip(pair)
    cur_price = df_5m_slice["Close"].iloc[-1]
    cur_time = df_5m_slice.index[-1]

    # Resample to M15 for range detection
    df_15m = _resample(df_5m_slice, "15min")
    if len(df_15m) < 12:
        return None
    m15_bars = _df_to_bars(df_15m)
    m5_bars = _df_to_bars(df_5m_slice)

    # Try Judas reversal first, then breakout
    entry_model = None
    amd_dir = None

    result = detect_amd_setup(m15_bars, pair)
    if result is not None:
        _rng, amd_dir = result
        entry_model = "judas"

    if entry_model is None:
        result = detect_breakout(m15_bars, pair)
        if result is not None:
            _rng, amd_dir = result
            entry_model = "breakout"

    if entry_model is None:
        return None

    # Direction must match preferred direction
    if amd_dir != pref_dir:
        return None

    # 2-of-3 MSS check: pair + partner + DXY inverse
    mss_count = 0
    confirmations = []

    # Check pair structure
    res_pair = mstruct.classify(m5_bars[-90:] if len(m5_bars) > 90 else m5_bars)
    if pref_dir > 0:
        swings = res_pair.get("stl", [])
    else:
        swings = res_pair.get("sth", [])
    if swings and swings[-1].swept:
        mss_count += 1

    # Check partner structure
    if partner_slice is not None and len(partner_slice) >= 30:
        p_m5 = _df_to_bars(partner_slice)
        res_p = mstruct.classify(p_m5[-90:] if len(p_m5) > 90 else p_m5)
        if pref_dir > 0:
            p_sw = res_p.get("stl", [])
        else:
            p_sw = res_p.get("sth", [])
        if p_sw and p_sw[-1].swept:
            mss_count += 1

    # Check DXY inverse (dollar down = pair up for BUY, dollar up = pair down for SELL)
    if dxy_slice is not None and len(dxy_slice) >= 30:
        d_m5 = _df_to_bars(dxy_slice)
        res_d = mstruct.classify(d_m5[-90:] if len(d_m5) > 90 else d_m5)
        dxy_dir = -pref_dir  # inverse
        if dxy_dir > 0:
            d_sw = res_d.get("stl", [])
        else:
            d_sw = res_d.get("sth", [])
        if d_sw and d_sw[-1].swept:
            mss_count += 1

    if entry_model == "judas":
        confirmations.append("JUDAS")
    else:
        confirmations.append("BREAKOUT")

    if mss_count >= 2:
        confirmations.append("MSS-2/3")
    elif mss_count >= 1:
        confirmations.append("MSS-1/3")

    # SMT between pair and partner
    smt_confirmed = False
    if partner_slice is not None and len(partner_slice) >= 20:
        p_h1 = _df_to_bars(_resample(partner_slice, "1h"))
        pair_h1 = _df_to_bars(_resample(df_5m_slice, "1h"))
        if len(p_h1) >= 20 and len(pair_h1) >= 20:
            if (smt_divergence(pair_h1, p_h1, pref_dir, inverse=False, lookback=20) or
                    smt_divergence(p_h1, pair_h1, pref_dir, inverse=False, lookback=20)):
                smt_confirmed = True
                confirmations.append("SMT")

    # Need at least the AMD detection + one confirmation
    if len(confirmations) < 2:
        return None

    # Stop — structural M5
    stop = None
    if len(m5_bars) >= 5:
        res = mstruct.classify(m5_bars[-90:] if len(m5_bars) > 90 else m5_bars)
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
        "entry_model": entry_model,
        "model": "AMD",
    }


def _simulate_outcome(setup, df_5m_after):
    """Walk forward from entry with trailing BE + session-end close.

    Exit logic:
    - Stop hit (original or trailed) → LOSS / BE / TRAIL
    - Target hit (30 pips) → WIN
    - At +10 pips MFE: stop moves to breakeven (entry price)
    - At +20 pips MFE: stop locks to entry + 10 pips
    - Session end (8h window): close at last price → CLOSE

    No more "OPEN" — every trade resolves.
    """
    pip = _pip(setup["pair"])
    entry = setup["price"]
    orig_stop = setup["stop"]
    target = setup["target"]
    d = setup["direction"]

    if df_5m_after is None or len(df_5m_after) == 0:
        return {"outcome": "CLOSE", "pips": 0, "exit_price": entry, "exit_time": setup["time"]}

    current_stop = orig_stop
    mfe = 0.0

    for ts, row in df_5m_after.iterrows():
        # Track max favorable excursion
        if d > 0:
            excursion = (row["High"] - entry) / pip
        else:
            excursion = (entry - row["Low"]) / pip
        if excursion > mfe:
            mfe = excursion

        # Trail stop based on MFE
        if mfe >= 20:
            new_stop = entry + d * 10 * pip
            if d > 0 and new_stop > current_stop:
                current_stop = new_stop
            elif d < 0 and new_stop < current_stop:
                current_stop = new_stop
        elif mfe >= 10:
            if d > 0 and entry > current_stop:
                current_stop = entry
            elif d < 0 and entry < current_stop:
                current_stop = entry

        # Check stop hit
        if d > 0:
            if row["Low"] <= current_stop:
                pips = (current_stop - entry) / pip
                if abs(pips) < 0.5:
                    outcome = "BE"
                elif pips > 0:
                    outcome = "TRAIL"
                else:
                    outcome = "LOSS"
                return {"outcome": outcome, "pips": round(pips, 1),
                        "exit_price": current_stop, "exit_time": ts}
            if row["High"] >= target:
                return {"outcome": "WIN", "pips": round((target - entry) / pip, 1),
                        "exit_price": target, "exit_time": ts}
        else:
            if row["High"] >= current_stop:
                pips = (entry - current_stop) / pip
                if abs(pips) < 0.5:
                    outcome = "BE"
                elif pips > 0:
                    outcome = "TRAIL"
                else:
                    outcome = "LOSS"
                return {"outcome": outcome, "pips": round(pips, 1),
                        "exit_price": current_stop, "exit_time": ts}
            if row["Low"] <= target:
                return {"outcome": "WIN", "pips": round((entry - target) / pip, 1),
                        "exit_price": target, "exit_time": ts}

    # Session end — close at last available price
    last_price = df_5m_after["Close"].iloc[-1]
    pips = round((last_price - entry) * d / pip, 1)
    return {"outcome": "CLOSE", "pips": pips, "exit_price": last_price,
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
    session_counts = defaultdict(int)
    cascade_log = {}

    for day in trading_days:
        day_trades = []

        for kz in KILLZONES_ET:
            kz_end_h, kz_end_m = kz["end_h"], kz["end_m"]
            kz_start_h, kz_start_m = kz["start_h"], kz["start_m"]

            kz_end_et = ny.localize(datetime(day.year, day.month, day.day,
                                              kz_end_h, kz_end_m))
            kz_start_et = ny.localize(datetime(day.year, day.month, day.day,
                                                kz_start_h, kz_start_m))
            kz_end_utc = kz_end_et.astimezone(pytz.utc)
            kz_start_utc = kz_start_et.astimezone(pytz.utc)

            # --- Intermarket cascade (yields → DXY → EURGBP → pairs) ---
            cascade = None
            has_yield = any(k in all_data for k in ("T5", "T10", "T30", "TNX"))
            if has_yield and "DXY" in all_data:
                cascade_slice = {}
                for key in ("T5", "T10", "T30", "TNX", "DXY", "EURGBP", "EURUSD", "GBPUSD"):
                    if key in all_data:
                        cascade_slice[key] = all_data[key].loc[:kz_start_utc]
                cascade = intermarket_cascade(cascade_slice, check_time=kz_start_utc)
                cascade_log[(day, kz["name"])] = cascade

            for pair, pref_dir in PREFERRED_SETUPS.items():
                if pair not in all_data:
                    continue

                # Max 2 alerts per pair per killzone session
                session_key = (pair, day, kz["name"])
                if session_counts[session_key] >= 2:
                    continue

                df = all_data[pair]

                check_points = [kz_start_utc + (kz_end_utc - kz_start_utc) / 2, kz_end_utc]

                for check_time in check_points:
                    if session_counts[session_key] >= 2:
                        break

                    # Data up to this point (48h lookback for H4 IFVG detection)
                    lookback_start = check_time - timedelta(hours=48)
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

                    # BUY EURUSD gate: require STRONG (3+) with IFVG mandatory
                    if pair == "EURUSD" and pref_dir > 0:
                        if setup["n_confirms"] < 3 or "IFVG" not in setup["confirmations"]:
                            continue

                    # IFVG mandatory for all setups (pure MSS+FBC is noise)
                    if "IFVG" not in setup["confirmations"]:
                        continue

                    session_counts[session_key] += 1

                    # Forward data for outcome simulation (next 8 hours)
                    fwd_end = check_time + timedelta(hours=8)
                    fwd_mask = (df.index > check_time) & (df.index <= fwd_end)
                    df_fwd = df.loc[fwd_mask]

                    outcome = _simulate_outcome(setup, df_fwd)

                    # Attach cascade confirmation tag
                    c_info = {"cascade_tag": "no_data", "cascade_summary": ""}
                    if cascade:
                        db = cascade["dollar_bias"]
                        if db == 0:
                            tag = "flat"
                        elif (db > 0 and pref_dir < 0) or (db < 0 and pref_dir > 0):
                            tag = "confirmed"
                        else:
                            tag = "against"
                        yc = cascade.get("yield_curve") or {}
                        c_info = {
                            "dollar_bias": db,
                            "dollar_source": cascade["dollar_source"],
                            "bonds_dxy_agreement": cascade.get("bonds_dxy_agreement", False),
                            "bonds_dxy_smt": cascade.get("bonds_dxy_smt", False),
                            "entry_smt": cascade.get("entry_smt", False),
                            "cascade_summary": cascade.get("summary", ""),
                            "cascade_tag": tag,
                            "yield_agreement": yc.get("agreement", 0),
                            "curve_stress": yc.get("curve_stress", ""),
                        }

                    trade = {
                        **setup,
                        "model": "MM",
                        "date": day,
                        "session": kz["name"],
                        "time_et": _to_et(setup["time"]),
                        **outcome,
                        **c_info,
                    }
                    day_trades.append(trade)

            # --- AMD / Judas / Breakout detection (base algorithm) ---
            for pair, pref_dir in PREFERRED_SETUPS.items():
                if pair not in all_data:
                    continue

                amd_key = ("AMD", pair, day, kz["name"])
                if session_counts.get(amd_key, 0) >= 2:
                    continue

                df = all_data[pair]
                check_points = [kz_start_utc + (kz_end_utc - kz_start_utc) / 2, kz_end_utc]

                for check_time in check_points:
                    if session_counts.get(amd_key, 0) >= 2:
                        break

                    lookback_start = check_time - timedelta(hours=48)
                    mask = (df.index >= lookback_start) & (df.index <= check_time)
                    df_slice = df.loc[mask]

                    if len(df_slice) < 30:
                        continue

                    partner = {"EURUSD": "GBPUSD", "GBPUSD": "EURUSD"}.get(pair)
                    partner_slice = None
                    if partner and partner in all_data:
                        pdf = all_data[partner]
                        partner_slice = pdf.loc[(pdf.index >= lookback_start) & (pdf.index <= check_time)]

                    dxy_slice = None
                    if "DXY" in all_data:
                        ddf = all_data["DXY"]
                        dxy_slice = ddf.loc[(ddf.index >= lookback_start) & (ddf.index <= check_time)]

                    try:
                        amd_setup = _detect_amd_at_point(df_slice, pair, pref_dir, partner_slice, dxy_slice)
                    except Exception:
                        amd_setup = None

                    if amd_setup is None:
                        continue

                    session_counts[amd_key] = session_counts.get(amd_key, 0) + 1

                    fwd_end = check_time + timedelta(hours=8)
                    fwd_mask = (df.index > check_time) & (df.index <= fwd_end)
                    df_fwd = df.loc[fwd_mask]

                    outcome = _simulate_outcome(amd_setup, df_fwd)

                    c_info = {"cascade_tag": "no_data", "cascade_summary": ""}
                    if cascade:
                        db = cascade["dollar_bias"]
                        if db == 0:
                            tag = "flat"
                        elif (db > 0 and pref_dir < 0) or (db < 0 and pref_dir > 0):
                            tag = "confirmed"
                        else:
                            tag = "against"
                        c_info = {"cascade_tag": tag, "cascade_summary": cascade.get("summary", "")}

                    trade = {
                        **amd_setup,
                        "date": day,
                        "session": kz["name"],
                        "time_et": _to_et(amd_setup["time"]),
                        **outcome,
                        **c_info,
                    }
                    day_trades.append(trade)

        all_trades.extend(day_trades)
        n = len(day_trades)
        d_prof = sum(1 for t in day_trades if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0))
        d_loss = sum(1 for t in day_trades if t["outcome"] == "LOSS")
        d_be = sum(1 for t in day_trades if t["outcome"] == "BE")
        pips = sum(t["pips"] for t in day_trades)
        day_str = day.strftime("%a %d %b")
        if n > 0:
            print(f"  {day_str}: {n} setups — {d_prof}P / {d_loss}L / {d_be}BE — {pips:+.1f} pips")
        else:
            print(f"  {day_str}: no setups")

    return all_trades


def write_report(trades, trading_days):
    """Write the weekly replay report."""
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    lines = []
    w = lines.append

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    w("# Weekly Replay — Day-by-Day Breakdown")
    w("")
    w(f"Generated: {now_str}")
    w(f"Strategy: SELL GBPUSD (dollar UP) | BUY EURUSD (dollar DOWN)")
    w(f"Gate: Bonds/Yields → DXY → EURGBP → pair selection (intermarket cascade)")
    w(f"Models: **MM** (IFVG zone + MSS + SMT + FBC) | **AMD** (Judas reversal + breakout)")
    w(f"Min confirmations: 2 (MODERATE+)")
    w(f"Stop: structural M5, capped 10 pips | Trail: BE at +10, lock +10 at +20 | Target: 30 pips")
    w("")

    # Overall summary
    total = len(trades)
    wins = [t for t in trades if t["outcome"] == "WIN"]
    losses = [t for t in trades if t["outcome"] == "LOSS"]
    be_trades = [t for t in trades if t["outcome"] == "BE"]
    trail_trades = [t for t in trades if t["outcome"] == "TRAIL"]
    closes = [t for t in trades if t["outcome"] == "CLOSE"]
    close_pos = [t for t in closes if t["pips"] > 0]
    close_neg = [t for t in closes if t["pips"] <= 0]
    profitable = len(wins) + len(trail_trades) + len(close_pos)
    total_pips = sum(t["pips"] for t in trades)
    wr = profitable / total * 100 if total > 0 else 0

    w("## Weekly Summary")
    w("")
    w(f"| Metric | Value |")
    w(f"|---|---|")
    w(f"| Total setups | **{total}** |")
    w(f"| Wins (hit 30-pip target) | **{len(wins)}** |")
    w(f"| Trail exits (+10 lock) | {len(trail_trades)} |")
    w(f"| Session-end close (positive) | {len(close_pos)} |")
    w(f"| Breakeven | {len(be_trades)} |")
    w(f"| Session-end close (negative) | {len(close_neg)} |")
    w(f"| Losses (stop hit) | **{len(losses)}** |")
    w(f"| Profitable trades | **{profitable}** ({wr:.0f}%) |")
    w(f"| Total pips | **{total_pips:+.1f}** |")
    w(f"| Avg pips/trade | {total_pips/total:.1f} |" if total > 0 else "| Avg pips/trade | — |")
    w("")

    # Per-pair summary
    w("## Per-Pair Summary")
    w("")
    w("| Pair | Direction | Trades | Prof | L | WR | Pips |")
    w("|---|---|---|---|---|---|---|")
    for pair in ("GBPUSD", "EURUSD"):
        pt = [t for t in trades if t["pair"] == pair]
        pw = [t for t in pt if t["outcome"] == "WIN"]
        pl = [t for t in pt if t["outcome"] == "LOSS"]
        p_prof = [t for t in pt if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        pp = sum(t["pips"] for t in pt)
        pwr = len(p_prof) / len(pt) * 100 if pt else 0
        d = "SELL" if PREFERRED_SETUPS.get(pair, 0) < 0 else "BUY"
        w(f"| {pair} | {d} | {len(pt)} | {len(p_prof)} | {len(pl)} | {pwr:.0f}% | {pp:+.1f} |")
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
            w("No setups (MM or AMD) met the 2-confirmation threshold during any killzone.")
            w("")
            continue

        day_prof = sum(1 for t in day_trades if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0))
        day_losses = sum(1 for t in day_trades if t["outcome"] == "LOSS")
        day_pips = sum(t["pips"] for t in day_trades)

        w(f"### {day_str} — {len(day_trades)} setups ({day_prof}P/{day_losses}L, {day_pips:+.1f} pips)")
        w("")
        w("| # | Time (ET) | Model | Pair | Dir | Signal | Confirms | Cascade | Result | Pips |")
        w("|---|---|---|---|---|---|---|---|---|---|")

        for i, t in enumerate(sorted(day_trades, key=lambda x: x["time"]), 1):
            et_str = _to_et(t["time"]).strftime("%H:%M") if hasattr(t["time"], "strftime") else str(t["time"])[-8:-3]
            confirms = "+".join(t["confirmations"])
            ctag = t.get("cascade_tag", "—")
            if ctag == "confirmed":
                ctag_str = "Y"
            elif ctag == "against":
                ctag_str = "X"
            elif ctag == "flat":
                ctag_str = "—"
            else:
                ctag_str = "?"

            model_label = t.get("model", "MM")
            w(f"| {i} | {et_str} | {model_label} | {t['pair']} | {t['dir_label']} | {t['signal']} | "
              f"{confirms} | {ctag_str} | "
              f"**{t['outcome']}** | {t['pips']:+.1f} |")
        w("")

    # Session breakdown
    w("## Session Breakdown")
    w("")
    w("| Session | Trades | Prof | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    for kz in KILLZONES_ET:
        st = [t for t in trades if t["session"] == kz["name"]]
        sw = [t for t in st if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        sl = [t for t in st if t["outcome"] == "LOSS"]
        sp = sum(t["pips"] for t in st)
        swr = len(sw) / len(st) * 100 if st else 0
        w(f"| {kz['name']} | {len(st)} | {len(sw)} | {len(sl)} | {swr:.0f}% | {sp:+.1f} |")
    w("")

    # Signal strength breakdown
    w("## Signal Strength")
    w("")
    w("| Strength | Trades | Prof | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    for sig in ("STRONG", "MODERATE"):
        st = [t for t in trades if t["signal"] == sig]
        sw = [t for t in st if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
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
        model_label = t.get("model", "MM")
        w(f"{i}. **{result}** [{model_label}] {t['dir_label']} {t['pair']} — {day_str} {et_str} ET "
          f"({t['session']}) — {t['signal']} [{'+'.join(t['confirmations'])}] — "
          f"Entry {t['price']:.5f}, Stop {t['stop']:.5f}, Target {t['target']:.5f} — "
          f"**{t['pips']:+.1f} pips**")
    w("")

    w("## Outcome Breakdown")
    w("")
    w("| Outcome | Count | Total Pips | Avg Pips |")
    w("|---|---|---|---|")
    for oc_label, oc_list in [("WIN (target hit)", wins), ("TRAIL (+10 lock)", trail_trades),
                               ("CLOSE (session end +)", close_pos), ("BE (breakeven)", be_trades),
                               ("CLOSE (session end -)", close_neg), ("LOSS (stop hit)", losses)]:
        oc_pips = sum(t["pips"] for t in oc_list)
        oc_avg = oc_pips / len(oc_list) if oc_list else 0
        w(f"| {oc_label} | {len(oc_list)} | {oc_pips:+.1f} | {oc_avg:+.1f} |")
    w("")

    # Model breakdown (MM vs AMD)
    w("## Model Breakdown (MM vs AMD)")
    w("")
    w("| Model | Trades | Prof | L | WR | Pips | Avg |")
    w("|---|---|---|---|---|---|---|")
    for model_name in ("MM", "AMD"):
        mt = [t for t in trades if t.get("model", "MM") == model_name]
        if not mt:
            continue
        mp = [t for t in mt if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        ml = [t for t in mt if t["outcome"] == "LOSS"]
        m_pips = sum(t["pips"] for t in mt)
        m_avg = m_pips / len(mt) if mt else 0
        m_wr = len(mp) / len(mt) * 100 if mt else 0
        sub = ""
        if model_name == "AMD":
            judas = [t for t in mt if t.get("entry_model") == "judas"]
            brk = [t for t in mt if t.get("entry_model") == "breakout"]
            if judas or brk:
                sub = f" (J:{len(judas)} B:{len(brk)})"
        w(f"| {model_name}{sub} | {len(mt)} | {len(mp)} | {len(ml)} | {m_wr:.0f}% | {m_pips:+.1f} | {m_avg:+.1f} |")
    w("")

    # Winner vs Loser analysis
    w("## Winner / Loser Analysis")
    w("")
    w("### By Session")
    w("")
    w("| Session | Trades | Prof | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    for kz in KILLZONES_ET:
        st = [t for t in trades if t["session"] == kz["name"]]
        if not st:
            continue
        sw = [t for t in st if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        sl = [t for t in st if t["outcome"] == "LOSS"]
        sp = sum(t["pips"] for t in st)
        swr = len(sw) / len(st) * 100 if st else 0
        w(f"| {kz['name']} | {len(st)} | {len(sw)} | {len(sl)} | {swr:.0f}% | {sp:+.1f} |")
    w("")

    w("### By Confirmation Combo")
    w("")
    w("| Confirmations | Trades | Prof | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    combo_set = sorted(set("+".join(t["confirmations"]) for t in trades))
    for combo in combo_set:
        ct = [t for t in trades if "+".join(t["confirmations"]) == combo]
        if not ct:
            continue
        cp = [t for t in ct if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        cl = [t for t in ct if t["outcome"] == "LOSS"]
        c_pips = sum(t["pips"] for t in ct)
        c_wr = len(cp) / len(ct) * 100 if ct else 0
        w(f"| {combo} | {len(ct)} | {len(cp)} | {len(cl)} | {c_wr:.0f}% | {c_pips:+.1f} |")
    w("")

    w("### By Time of Day (ET)")
    w("")
    w("| Time | Trades | Prof | L | WR | Pips |")
    w("|---|---|---|---|---|---|")
    time_set = sorted(set(
        (_to_et(t["time"]).strftime("%H:%M") if hasattr(t["time"], "strftime") else "")
        for t in trades
    ))
    for tm in time_set:
        tt = [t for t in trades if (_to_et(t["time"]).strftime("%H:%M") if hasattr(t["time"], "strftime") else "") == tm]
        if not tt:
            continue
        tw = [t for t in tt if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        tl = [t for t in tt if t["outcome"] == "LOSS"]
        t_pips = sum(t["pips"] for t in tt)
        t_wr = len(tw) / len(tt) * 100 if tt else 0
        w(f"| {tm} | {len(tt)} | {len(tw)} | {len(tl)} | {t_wr:.0f}% | {t_pips:+.1f} |")
    w("")

    # Cascade confirmation breakdown
    w("## Intermarket Cascade (Bonds/DXY)")
    w("")
    w("| Cascade | Trades | Prof | L | WR | Pips | Avg |")
    w("|---|---|---|---|---|---|---|")
    for tag_label, tag_key in [("Confirmed (bonds+DXY agree)", "confirmed"),
                                ("Flat (no dollar signal)", "flat"),
                                ("Against (dollar opposes)", "against"),
                                ("No data", "no_data")]:
        ct = [t for t in trades if t.get("cascade_tag") == tag_key]
        if not ct:
            continue
        cp = [t for t in ct if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0)]
        cl = [t for t in ct if t["outcome"] == "LOSS"]
        c_pips = sum(t["pips"] for t in ct)
        c_avg = c_pips / len(ct) if ct else 0
        c_wr = len(cp) / len(ct) * 100 if ct else 0
        w(f"| {tag_label} | {len(ct)} | {len(cp)} | {len(cl)} | {c_wr:.0f}% | {c_pips:+.1f} | {c_avg:+.1f} |")
    w("")

    w("---")
    w("")
    w("*Intermarket cascade: Bonds/Yields (T5/T10/T30) → DXY → EURGBP → pair selection.*")
    w("*Simulation: structural M5 stop (capped 10 pips), trail BE at +10, lock +10 at +20, target 30 pips.*")
    w("*Session-end close resolves all trades — no \"OPEN\" status.*")
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
    from intermarket_cascade import intermarket_cascade as _ic
    print("  Intermarket cascade OK")
    assert callable(_ic), "intermarket_cascade not callable"
    print("selftest OK — all detectors + cascade available")


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
    trails = sum(1 for t in trades if t["outcome"] == "TRAIL")
    be_c = sum(1 for t in trades if t["outcome"] == "BE")
    close_p = sum(1 for t in trades if t["outcome"] == "CLOSE" and t["pips"] > 0)
    close_n = sum(1 for t in trades if t["outcome"] == "CLOSE" and t["pips"] <= 0)
    losses = sum(1 for t in trades if t["outcome"] == "LOSS")
    profitable = wins + trails + close_p
    total_pips = sum(t["pips"] for t in trades)

    print(f"\n{'='*60}")
    print("MM WEEKLY REPLAY SUMMARY")
    print(f"{'='*60}")
    print(f"  Total setups:  {total}")
    print(f"  Wins (target): {wins}")
    print(f"  Trail exits:   {trails}")
    print(f"  Close (+):     {close_p}")
    print(f"  Breakeven:     {be_c}")
    print(f"  Close (-):     {close_n}")
    print(f"  Losses (stop): {losses}")
    print(f"  Profitable:    {profitable} ({profitable/total*100:.0f}%)" if total > 0 else "  Profitable:    —")
    print(f"  Total pips:    {total_pips:+.1f}")
    print(f"\n  Day-by-day:")
    by_day = defaultdict(list)
    for t in trades:
        by_day[t["date"]].append(t)
    for day in trading_days:
        dt = by_day.get(day, [])
        dp_c = sum(1 for t in dt if t["outcome"] in ("WIN", "TRAIL") or (t["outcome"] == "CLOSE" and t["pips"] > 0))
        dl = sum(1 for t in dt if t["outcome"] == "LOSS")
        dp = sum(t["pips"] for t in dt)
        day_str = day.strftime("%a %d %b")
        if dt:
            print(f"    {day_str}: {len(dt)} trades — {dp_c}P/{dl}L — {dp:+.1f} pips")
        else:
            print(f"    {day_str}: no setups")

    return 0


if __name__ == "__main__":
    sys.exit(main())

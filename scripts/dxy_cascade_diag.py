#!/usr/bin/env python3
"""Diagnose why DXY cascade is inverted — confirmed trades lose, against trades win.

Hypothesis: daily BOS is backward-looking (yesterday's breakout), so by the time
we trade, the move is already done and reverting. Tests this + an alternative
approach: DXY price vs daily/weekly open (real-time institutional read).
"""
import os, sys, time
from collections import namedtuple
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

from ict.bias import htf_bias

Bar = namedtuple("Bar", ["Open", "High", "Low", "Close"])


def _resample(df, tf):
    return df.resample(tf).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
    }).dropna()


def _df_to_bars(df):
    return [Bar(r.Open, r.High, r.Low, r.Close) for _, r in df.iterrows()]


def fetch(days=30):
    try:
        import yfinance as yf
    except ImportError:
        os.system(f"{sys.executable} -m pip install yfinance -q")
        import yfinance as yf
    import pandas as pd

    period = f"{min(int(days * 1.6) + 5, 59)}d"
    tickers = {
        "DXY": "DX-Y.NYB",
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
    }
    data = {}
    for name, ticker in tickers.items():
        print(f"  Fetching {name}...", end=" ", flush=True)
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
                    data[name] = df
                    print(f"{len(df)} bars")
                    break
            except Exception as e:
                if attempt == 2:
                    print(f"FAILED: {e}")
                else:
                    time.sleep(2)
    return data


def main():
    import pytz
    ny = pytz.timezone("US/Eastern")

    print("Fetching data...")
    data = fetch(days=30)

    if "DXY" not in data:
        print("ERROR: no DXY data")
        return

    dxy_5m = data["DXY"]
    eu_5m = data.get("EURUSD")
    gu_5m = data.get("GBPUSD")

    # Daily bars
    dxy_daily = _resample(dxy_5m, "1D")
    dxy_h4 = _resample(dxy_5m, "4h")
    dxy_h1 = _resample(dxy_5m, "1h")

    print(f"\nDXY: {len(dxy_5m)} 5m bars, {len(dxy_daily)} daily bars, {len(dxy_h4)} H4 bars")
    print(f"DXY range: {dxy_5m['Low'].min():.3f} - {dxy_5m['High'].max():.3f}")
    print()

    # Get trading days
    import pandas as pd
    trading_days = sorted(set(
        ts.astimezone(ny).date()
        for ts in dxy_5m.index
        if ts.astimezone(ny).weekday() < 5
    ))

    # For each trading day, compute DXY bias at London open (03:00 ET = ~07:00-08:00 UTC)
    print("=" * 100)
    print(f"{'Date':12} | {'D1 bias':8} | {'H4 bias':8} | {'H1(20)':8} | {'vs DOpen':10} | {'vs WOpen':10} | {'DXY@LO':9} | {'EU chg':8} | {'GU chg':8} | Notes")
    print("-" * 100)

    weekly_open = None
    last_weekday = None

    for day in trading_days:
        # London open: 03:00 ET
        lo_et = ny.localize(datetime(day.year, day.month, day.day, 3, 0))
        lo_utc = lo_et.astimezone(pytz.utc)

        # Session end: 10:00 ET
        se_et = ny.localize(datetime(day.year, day.month, day.day, 10, 0))
        se_utc = se_et.astimezone(pytz.utc)

        # DXY price at London open
        dxy_at_lo = dxy_5m.loc[:lo_utc]
        if len(dxy_at_lo) < 20:
            continue
        dxy_price = dxy_at_lo.iloc[-1].Close

        # DXY daily open (00:00 UTC today)
        today_start = pd.Timestamp(day, tz="UTC")
        today_bars = dxy_5m.loc[today_start:lo_utc]
        if len(today_bars) > 0:
            daily_open = today_bars.iloc[0].Open
        else:
            daily_open = dxy_price

        # Weekly open (Monday 00:00 UTC)
        if last_weekday is None or day.weekday() == 0:
            mon_bars = dxy_5m.loc[today_start:]
            if len(mon_bars) > 0:
                weekly_open = mon_bars.iloc[0].Open
        last_weekday = day.weekday()

        if weekly_open is None:
            weekly_open = daily_open

        # DXY daily bias (htf_bias on daily bars up to London open)
        dxy_d_slice = _df_to_bars(_resample(dxy_at_lo, "1D"))
        d1_bias = htf_bias(dxy_d_slice, lookback=5) if len(dxy_d_slice) >= 7 else None

        # DXY H4 bias
        dxy_h4_slice = _df_to_bars(_resample(dxy_at_lo, "4h"))
        h4_bias = htf_bias(dxy_h4_slice, lookback=6) if len(dxy_h4_slice) >= 8 else None

        # DXY H1 bias (longer lookback)
        dxy_h1_slice = _df_to_bars(_resample(dxy_at_lo, "1h"))
        h1_bias_20 = htf_bias(dxy_h1_slice, lookback=20) if len(dxy_h1_slice) >= 22 else None

        # DXY vs daily open
        vs_dopen = dxy_price - daily_open
        dopen_dir = "+1 bid" if vs_dopen > 0.02 else ("-1 ofr" if vs_dopen < -0.02 else " 0 flat")

        # DXY vs weekly open
        vs_wopen = dxy_price - weekly_open
        wopen_dir = "+1 bid" if vs_wopen > 0.05 else ("-1 ofr" if vs_wopen < -0.05 else " 0 flat")

        # What EURUSD/GBPUSD actually did from London open to session end
        eu_chg = ""
        gu_chg = ""
        if eu_5m is not None:
            eu_lo = eu_5m.loc[:lo_utc]
            eu_se = eu_5m.loc[:se_utc]
            if len(eu_lo) > 0 and len(eu_se) > 0:
                eu_start = eu_lo.iloc[-1].Close
                eu_end = eu_se.iloc[-1].Close
                eu_pips = (eu_end - eu_start) * 10000
                eu_chg = f"{eu_pips:+.0f}p"

        if gu_5m is not None:
            gu_lo = gu_5m.loc[:lo_utc]
            gu_se = gu_5m.loc[:se_utc]
            if len(gu_lo) > 0 and len(gu_se) > 0:
                gu_start = gu_lo.iloc[-1].Close
                gu_end = gu_se.iloc[-1].Close
                gu_pips = (gu_end - gu_start) * 10000
                gu_chg = f"{gu_pips:+.0f}p"

        # Notes
        notes = []
        if d1_bias is not None and d1_bias != 0:
            # Check if EURUSD moved WITH or AGAINST the D1 signal
            if eu_chg:
                eu_val = float(eu_chg.replace("p", ""))
                expected = "down" if d1_bias > 0 else "up"
                actual = "up" if eu_val > 5 else ("down" if eu_val < -5 else "flat")
                if (d1_bias > 0 and eu_val > 5) or (d1_bias < 0 and eu_val < -5):
                    notes.append("D1 WRONG")
                elif (d1_bias > 0 and eu_val < -5) or (d1_bias < 0 and eu_val > 5):
                    notes.append("D1 right")

        def _b(v):
            if v is None:
                return "   —   "
            return {1: " bull  ", -1: " bear  ", 0: " flat  "}[v]

        print(f"{str(day):12} | {_b(d1_bias)} | {_b(h4_bias)} | {_b(h1_bias_20)} | {dopen_dir:10} | {wopen_dir:10} | {dxy_price:9.3f} | {eu_chg:8} | {gu_chg:8} | {' '.join(notes)}")

    print()
    print("=" * 80)
    print("LEGEND:")
    print("  D1 bias  = htf_bias(daily bars, lookback=5) — the current cascade read")
    print("  H4 bias  = htf_bias(H4 bars, lookback=6) — ~1 day of structure")
    print("  H1(20)   = htf_bias(H1 bars, lookback=20) — ~1 day of hourly structure")
    print("  vs DOpen  = DXY price vs daily open (>+0.02 = bid, <-0.02 = offer)")
    print("  vs WOpen  = DXY price vs weekly open (>+0.05 = bid, <-0.05 = offer)")
    print("  EU/GU chg = pip change from London open to 10:00 ET (the trading session)")
    print("  D1 WRONG  = D1 bias predicted pairs DOWN but they went UP, or vice versa")
    print("  D1 right  = D1 bias prediction matched pair movement")
    print()
    print("If D1 is mostly WRONG → daily BOS is stale (yesterday's breakout = today's reversion)")
    print("Compare vs DOpen/WOpen columns to see if open-relative reads are more accurate")


if __name__ == "__main__":
    main()

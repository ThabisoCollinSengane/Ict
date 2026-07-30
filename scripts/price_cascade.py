#!/usr/bin/env python3
"""Pure-price draw cascade — when daily liquidity is taken, where does price go?

Independent of the strategy's entries/exits. On the raw M1 price of each pair it:
  1. Detects every DAILY-liquidity sweep — price trades beyond the previous day's
     high (buy-side taken → up) or low (sell-side taken → down).
  2. From that moment follows the forward price for a horizon and records which
     higher/lower pools it reaches, in order: 3-day → 30-day → 60-day extreme
     (weekly PWH/PWL reported alongside).
  3. Reports reach rates + the conditional cascade P(reach next | reached prior),
     split IS (2022-23) vs OOS (2024-25), per pair and combined.

This tests the ICT hypothesis directly: daily taken → 3-day → 30-day → 60-day.
The pools 3d<=30d<=60d are ascending by construction, so a monotonic run reaches
them in order — the reach rates ARE the cascade. Measurement only; nothing ships.

Run:  python scripts/price_cascade.py [--horizon-days 2]
      python scripts/price_cascade.py --selftest        # no data needed
"""
from __future__ import annotations

import argparse
import os
import sys

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "histdata")
REPORT = os.path.join(os.path.dirname(DATA), "price_cascade_report.md")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
RUNGS = ("3-day", "30-day", "60-day")


def cascade_reach(fwd_extreme, levels, direction):
    """levels ascending by distance from the sweep (3d,30d,60d); each strictly
    beyond the sweep in the trade direction. Returns a bool per level: did the
    forward extreme reach it? Monotonic by construction (reaching far ⇒ near)."""
    if direction > 0:
        return [fwd_extreme >= lv for lv in levels]
    return [fwd_extreme <= lv for lv in levels]


def _pct(a, b):
    return (100.0 * a / b) if b else None


def _fmt(v):
    return "—" if v is None else f"{v:.0f}%"


# ---- data + event detection (pandas; only the walk logic above is pure) ----

def _load(pair):
    import pandas as pd
    frames = []
    for y in (2022, 2023, 2024, 2025):
        p = os.path.join(DATA, f"{pair}_{y}.csv")
        if os.path.exists(p):
            df = pd.read_csv(p, sep=";", header=None,
                             names=["dt", "o", "h", "l", "c", "v"])
            frames.append(df)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    return df


def _events(pair, horizon_days):
    """List of (year, direction, reached_bools, n_pools, wk_reach, wk_avail) per
    daily sweep. Named rungs are kept per-slot (3d/30d/60d) so reach rates are
    always aligned to the same pool, not to a variable-length compacted list."""
    import numpy as np
    import pandas as pd
    m1 = _load(pair)
    if m1 is None or len(m1) < 5000:
        return []
    m5 = m1.resample("5min").agg({"h": "max", "l": "min"}).dropna()
    d = m1.resample("1D").agg({"h": "max", "l": "min"}).dropna()
    w = m1.resample("1W").agg({"h": "max", "l": "min"}).dropna()

    def align(series):
        # Prior-period value carried forward onto the M5 index (no lookahead:
        # a period's value is only visible strictly after it, via shift(1)).
        return series.reindex(m5.index, method="ffill").to_numpy()

    lv = {  # aligned numpy arrays over the M5 index
        "pdh": align(d["h"].shift(1)),          "pdl": align(d["l"].shift(1)),
        "d3h": align(d["h"].shift(1).rolling(3).max()),
        "d3l": align(d["l"].shift(1).rolling(3).min()),
        "d30h": align(d["h"].shift(1).rolling(30).max()),
        "d30l": align(d["l"].shift(1).rolling(30).min()),
        "d60h": align(d["h"].shift(1).rolling(60).max()),
        "d60l": align(d["l"].shift(1).rolling(60).min()),
        "pwh": align(w["h"].shift(1)),          "pwl": align(w["l"].shift(1)),
    }
    hz = int(horizon_days * 288)
    highs = m5["h"].to_numpy()
    lows = m5["l"].to_numpy()
    years = m5.index.year.to_numpy()
    days = m5.index.normalize().view("int64")   # fast day key
    n = len(m5)
    tol = 1e-5
    out = []
    seen_up = set()
    seen_dn = set()

    def _rec(i, direction, lvl, pool_hi, pool_mid, pool_lo, wk):
        if direction > 0:
            fwd = highs[i:i + hz].max()
            pools = [p for p in (pool_hi, pool_mid, pool_lo)]  # 3d,30d,60d
            reached = [(not np.isnan(p)) and p > lvl + tol and fwd >= p for p in pools]
            avail = [(not np.isnan(p)) and p > lvl + tol for p in pools]
            wk_av = (not np.isnan(wk)) and wk > lvl + tol
            wk_re = wk_av and fwd >= wk
        else:
            fwd = lows[i:i + hz].min()
            pools = [pool_hi, pool_mid, pool_lo]  # 3d,30d,60d (lows)
            reached = [(not np.isnan(p)) and p < lvl - tol and fwd <= p for p in pools]
            avail = [(not np.isnan(p)) and p < lvl - tol for p in pools]
            wk_av = (not np.isnan(wk)) and wk < lvl - tol
            wk_re = wk_av and fwd <= wk
        out.append((int(years[i]), direction, reached, avail, wk_re, wk_av))

    for i in range(1, n):
        pdh_v, pdl_v = lv["pdh"][i], lv["pdl"][i]
        dk = days[i]
        if not np.isnan(pdh_v) and dk not in seen_up and highs[i] >= pdh_v > highs[i - 1]:
            seen_up.add(dk)
            _rec(i, 1, pdh_v, lv["d3h"][i], lv["d30h"][i], lv["d60h"][i], lv["pwh"][i])
        if not np.isnan(pdl_v) and dk not in seen_dn and lows[i] <= pdl_v < lows[i - 1]:
            seen_dn.add(dk)
            _rec(i, -1, pdl_v, lv["d3l"][i], lv["d30l"][i], lv["d60l"][i], lv["pwl"][i])
    return out


def _agg(events):
    """Return dict: n, per-slot avail/reach counts (3d/30d/60d), weekly."""
    avail = [0, 0, 0]
    reach = [0, 0, 0]
    wk_avail = wk_reach = 0
    for (_yr, _dir, reached, av, wkr, wka) in events:
        for k in range(3):
            if av[k]:
                avail[k] += 1
                if reached[k]:
                    reach[k] += 1
        if wka:
            wk_avail += 1
            if wkr:
                wk_reach += 1
    return {"n": len(events), "avail": avail, "reach": reach,
            "wk_avail": wk_avail, "wk_reach": wk_reach}


def _split(events, yrs):
    return [e for e in events if e[0] in yrs]


def _table(title, events):
    a = _agg(events)
    L = [f"**{title}** — {a['n']} sweep events", "",
         "| next pool | events with it ahead | reached it |",
         "|---|---|---|"]
    for k, name in enumerate(RUNGS):
        L.append(f"| {name} | {a['avail'][k]} | {_fmt(_pct(a['reach'][k], a['avail'][k]))} |")
    L.append(f"| weekly | {a['wk_avail']} | {_fmt(_pct(a['wk_reach'], a['wk_avail']))} |")
    # conditional cascade
    L += ["", "_Conditional cascade (of those that reached the prior rung):_", ""]
    prev = a["avail"][0]
    steps = []
    for k, name in enumerate(RUNGS):
        r = a["reach"][k]
        cond = _pct(a["reach"][k], a["reach"][k - 1]) if k > 0 and a["reach"][k - 1] else None
        if k == 0:
            steps.append(f"take daily → **{name}** { _fmt(_pct(r, a['avail'][k])) }")
        else:
            steps.append(f"→ **{name}** {_fmt(cond)}")
    L.append("· ".join(steps))
    return L


def analyse(horizon_days):
    all_events = []
    per_pair = {}
    missing = []
    for pair in PAIRS:
        ev = _events(pair, horizon_days)
        if not ev:
            missing.append(pair)
            continue
        per_pair[pair] = ev
        all_events += ev

    L = ["# Pure-price draw cascade — daily taken → 3-day → 30-day → 60-day", "",
         f"Raw M1 price, independent of the strategy. Horizon after each sweep: "
         f"**{horizon_days} trading day(s)**. A daily sweep = price trades beyond the "
         "prior day's high/low; then we follow price and see which higher/lower pools "
         "it reaches. Pools 3d≤30d≤60d are ascending, so reach rates ARE the cascade. "
         "IS = 2022-23, OOS = 2024-25.", ""]
    if missing:
        L += [f"_⚠️ no data for: {', '.join(missing)} — those pairs skipped._", ""]
    if not all_events:
        return L + ["ERROR: no price data found in data/histdata — run the backtest "
                    "data prep first (fetch_histdata / prepare_histdata)."]

    L += ["## All pairs combined", ""]
    L += _table("In-sample 2022-23", _split(all_events, (2022, 2023)))
    L += [""]
    L += _table("Out-of-sample 2024-25", _split(all_events, (2024, 2025)))
    L += ["", "## Per pair (full 4yr)", ""]
    for pair, ev in per_pair.items():
        L += _table(pair, ev) + [""]

    # verdict
    isa = _agg(_split(all_events, (2022, 2023)))
    oosa = _agg(_split(all_events, (2024, 2025)))
    def rr(a, k): return _pct(a["reach"][k], a["avail"][k])
    L += ["## Read", "",
          "The cascade is REAL if reach rates step DOWN monotonically (near pools "
          "reached more than far) and IS/OOS agree. Compare the two splits above: "
          f"3-day {_fmt(rr(isa,0))}/{_fmt(rr(oosa,0))}, 30-day {_fmt(rr(isa,1))}/"
          f"{_fmt(rr(oosa,1))}, 60-day {_fmt(rr(isa,2))}/{_fmt(rr(oosa,2))} (IS/OOS). "
          "A steep drop from 3-day to 60-day means price usually stops at the nearer "
          "draw — the strategy's exit-at-nearest design is correct, and the far pools "
          "are genuinely the NEXT cycle's target, not this move's."]
    return L


def _selftest():
    # up: sweep level 100, pools [102,105,110]; forward high 106 → reach 102,105 not 110
    r = cascade_reach(106.0, [102.0, 105.0, 110.0], 1)
    assert r == [True, True, False], r
    # down: sweep 100, pools [98,95,90]; forward low 94 → reach 98,95 not 90
    r = cascade_reach(94.0, [98.0, 95.0, 90.0], -1)
    assert r == [True, True, False], r
    # aggregation monotonicity (tuple: year,dir,reached[3],avail[3],wk_re,wk_av)
    ev = [(2022, 1, [True, True, False], [True, True, True], False, True),
          (2022, 1, [True, False, False], [True, True, True], False, True)]
    a = _agg(ev)
    assert a["reach"] == [2, 1, 0] and a["avail"] == [2, 2, 2], a
    print("selftest OK — cascade walk, monotonicity, aggregation pass")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon-days", type=float, default=2.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    text = "\n".join(analyse(a.horizon_days)) + "\n"
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)
    print(f"[report → {REPORT}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

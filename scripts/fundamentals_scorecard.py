#!/usr/bin/env python3
"""P79 — fundamentals scorecard: what did COT, interest rates and the news
actually do to EURUSD / GBPUSD / NZDUSD — and what would the OPPOSITE have done?

    python scripts/fundamentals_scorecard.py            # needs internet (Yahoo, CFTC)
    python scripts/fundamentals_scorecard.py --null     # stand-in random walks: must read nothing
    python scripts/fundamentals_scorecard.py --selftest

Measurement only. Nothing here touches the engine.

§A COT — CFTC legacy futures report, non-commercial (speculator) net position
   as % of open interest, z-scored against the PRIOR 52 weeks only. Positions
   are as of Tuesday and released Friday 15:30 ET, so the return is measured
   from the following MONDAY close to the Monday after — no lookahead. FOLLOW =
   trade with the specs, OPPOSITE = fade them. Both reported.
§B RATES — US yields from Yahoo (^IRX 3m, ^FVX 5y, ^TNX 10y). (1) Same day: do
   yields and the pairs move opposite, as the rate story says? (2) Next day:
   does yesterday's yield move predict today's pair move? (3) The brief's own
   rule: 5-day yield change > 5bp -> lean the pairs the other way. FOLLOW and
   OPPOSITE both reported.
§C NEWS — every High/Medium event in data/news_events.csv over Yahoo's hourly
   history (~2 years). IMPACT = size of the move in the 2h from the event's hour
   vs the SAME clock hour on no-news days. FOLLOW-THROUGH = does the next 3h
   continue the first move? Compared with the same clock hours on no-news days,
   because markets drift or revert a little at every hour anyway. FADE (the
   opposite) is reported alongside.

THE GATE (same as every study here): an effect counts only if it has the same
sign in BOTH halves and pooled t >= 2. Everything else is "nothing".
"""
from __future__ import annotations

import argparse
import io
import math
import os
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
REPORT = os.path.join(ROOT, "data", "fundamentals_scorecard.md")
PAIRS = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "NZDUSD": "NZDUSD=X"}
COT_MARKETS = {  # name prefixes used by CFTC over the years
    "EURUSD": ("EURO FX - ",),
    "GBPUSD": ("BRITISH POUND - ", "BRITISH POUND STERLING - "),
    "NZDUSD": ("NZ DOLLAR - ", "NEW ZEALAND DOLLAR - "),
}
YIELDS = {"3m": "^IRX", "5y": "^FVX", "10y": "^TNX"}
NEWS_PAIRS = {"USD": ("EURUSD", "GBPUSD", "NZDUSD"), "EUR": ("EURUSD",),
              "GBP": ("GBPUSD",), "NZD": ("NZDUSD",)}
CRITICAL = {"NFP", "CPI", "FOMC"}
H1_RULE = "60min"           # pandas 3.x: no "T"/"H" aliases (P77)


# ───────────────────────────── pure logic ──────────────────────────────────────
def mean_se(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    n = len(xs)
    if n == 0:
        return float("nan"), float("nan"), 0
    m = sum(xs) / n
    if n < 2:
        return m, float("nan"), n
    v = sum((x - m) ** 2 for x in xs) / (n - 1)
    return m, math.sqrt(v / n), n


def tstat(ms):
    m, se, _ = ms
    return m / se if se and not math.isnan(se) and se > 0 else float("nan")


def corr_t(x, y):
    """Pearson r and its t-stat over paired non-missing values."""
    pts = [(a, b) for a, b in zip(x, y) if a is not None and b is not None
           and not math.isnan(a) and not math.isnan(b)]
    n = len(pts)
    if n < 5:
        return float("nan"), float("nan"), n
    mx = sum(a for a, _ in pts) / n
    my = sum(b for _, b in pts) / n
    sxx = sum((a - mx) ** 2 for a, _ in pts)
    syy = sum((b - my) ** 2 for _, b in pts)
    if sxx == 0 or syy == 0:
        return float("nan"), float("nan"), n
    r = sum((a - mx) * (b - my) for a, b in pts) / math.sqrt(sxx * syy)
    r = max(min(r, 0.999999), -0.999999)
    return r, r * math.sqrt((n - 2) / (1 - r * r)), n


def zscore_prior(values, window=52, min_n=26):
    """z of each value against the PRIOR `window` values only (never itself)."""
    out = []
    for i, v in enumerate(values):
        prior = [x for x in values[max(0, i - window):i] if x is not None]
        if v is None or len(prior) < min_n:
            out.append(None)
            continue
        m = sum(prior) / len(prior)
        sd = math.sqrt(sum((x - m) ** 2 for x in prior) / (len(prior) - 1))
        out.append(None if sd == 0 else (v - m) / sd)
    return out


T_BAR = 2.5


def verdict(m_a, m_b, t_pool, bar=None):
    """Same sign in both halves and pooled |t| >= T_BAR.

    The bar is 2.5, not the project's usual 2: on 12 random-walk datasets x 12
    tests, |t| >= 2 passed 11 of 144 (7.6%) — about double what a fair gate
    should let through. A threshold the null clears is not a threshold (P77)."""
    bar = T_BAR if bar is None else bar
    if any(x is None or math.isnan(x) for x in (m_a, m_b, t_pool)):
        return "no data"
    if m_a > 0 and m_b > 0 and t_pool >= bar:
        return "WORKS"
    if m_a < 0 and m_b < 0 and t_pool <= -bar:
        return "OPPOSITE WORKS"
    return "nothing"


def cot_column(cols, *need, avoid=()):
    """Find a CFTC column by lowercase substrings (header text changed over years)."""
    # CFTC has shipped both "Noncommercial Positions-Long (All)" and
    # "NonComm_Positions_Long_All": normalise underscores and match "noncomm".
    low = {c: c.lower().replace("_", " ") for c in cols}
    for c, lc in low.items():
        if all(n in lc for n in need) and not any(a in lc for a in avoid):
            return c
    return None


def parse_cot_table(df):
    """CFTC legacy annual file -> rows of (pair, report_date, net_pct)."""
    import pandas as pd
    cols = list(df.columns)
    c_name = cot_column(cols, "market", "exchange")
    c_date = (cot_column(cols, "yyyy-mm-dd") or cot_column(cols, "report", "date")
              or cot_column(cols, "yymmdd"))
    c_long = cot_column(cols, "noncomm", "long", "all", avoid=("spread", "%", "pct", "old", "other"))
    c_short = cot_column(cols, "noncomm", "short", "all", avoid=("spread", "%", "pct", "old", "other"))
    c_oi = cot_column(cols, "open interest", "all", avoid=("%", "pct", "old", "other"))
    missing = [k for k, v in (("name", c_name), ("date", c_date), ("long", c_long),
                              ("short", c_short), ("oi", c_oi)) if v is None]
    if missing:
        raise ValueError(f"COT columns not found {missing}; headers: {cols[:12]}...")
    out = []
    for _, r in df.iterrows():
        name = str(r[c_name]).upper().strip()
        pair = next((p for p, pre in COT_MARKETS.items() if any(name.startswith(x) for x in pre)), None)
        if pair is None:
            continue
        ds = str(r[c_date]).strip()
        try:
            d = (pd.Timestamp(ds) if "-" in ds else
                 pd.Timestamp(datetime.strptime(ds.zfill(6), "%y%m%d"))).date()
        except Exception:
            continue
        try:
            oi = float(r[c_oi])
            net = (float(r[c_long]) - float(r[c_short])) / oi * 100.0 if oi else None
        except (TypeError, ValueError):
            net = None
        out.append((pair, d, net))
    return out


def next_trading_on_or_after(dates_sorted, d):
    import bisect
    i = bisect.bisect_left(dates_sorted, d)
    return dates_sorted[i] if i < len(dates_sorted) else None


def follow_through(p0, p2, p5):
    """First 2h move vs the next 3h. Returns (impact_bp, continuation_bp)."""
    if None in (p0, p2, p5) or any(math.isnan(x) for x in (p0, p2, p5)):
        return None, None
    first = math.log(p2 / p0) * 1e4
    nxt = math.log(p5 / p2) * 1e4
    if first == 0:
        return abs(first), None
    return abs(first), math.copysign(1.0, first) * nxt


def half_of(d, cut):
    return "A" if d < cut else "B"


# ───────────────────────────── data ────────────────────────────────────────────
def _yf(ticker, **kw):
    import pandas as pd
    import yfinance as yf
    df = yf.download(ticker, progress=False, auto_adjust=False, **kw)
    if df is None or df.empty:
        return None
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df["Close"].dropna()


def load_daily(start="2021-01-01"):
    out = {}
    for p, t in PAIRS.items():
        s = _yf(t, start=start, interval="1d")
        if s is not None:
            s.index = s.index.tz_localize(None) if s.index.tz is not None else s.index
            out[p] = s
    return out


def load_yields(start="2021-01-01"):
    out = {}
    for k, t in YIELDS.items():
        s = _yf(t, start=start, interval="1d")
        if s is None:
            continue
        s.index = s.index.tz_localize(None) if s.index.tz is not None else s.index
        if s.median() > 20:          # some feeds quote yield x10
            s = s / 10.0
        out[k] = s
    return out


def load_hourly():
    import pandas as pd
    out = {}
    for p, t in PAIRS.items():
        s = _yf(t, period="729d", interval="1h")
        if s is None:
            continue
        s.index = (s.index.tz_localize("UTC") if s.index.tz is None
                   else s.index.tz_convert("UTC")) + pd.Timedelta(H1_RULE)   # price AS OF label
        out[p] = s
    return out


def load_cot(years):
    import pandas as pd
    import urllib.request
    rows, notes = [], []
    for y in years:
        url = f"https://www.cftc.gov/files/dea/history/deacot{y}.zip"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=120).read()
            z = zipfile.ZipFile(io.BytesIO(raw))
            name = next(n for n in z.namelist() if n.lower().endswith(".txt"))
            df = pd.read_csv(z.open(name), low_memory=False)
            got = parse_cot_table(df)
            rows += got
            notes.append(f"{y}: {len(got)} rows")
        except Exception as exc:
            notes.append(f"{y}: FAILED ({type(exc).__name__}: {str(exc)[:120]})")
    return rows, notes


def load_news():
    from news_filter import NewsCalendar
    cal = NewsCalendar()
    cal.load_csv(open(os.path.join(ROOT, "data", "news_events.csv")).read())
    return cal.events          # (utc_dt, ccy, impact, name)


# ───────────────────────────── sections ────────────────────────────────────────
def _f(x, nd=1):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{nd}f}"


def section_cot(cot_rows, daily, notes):
    L = ["## §A COT — do speculators' positions predict next week?", "",
         "_" + " · ".join(notes) + "_", "",
         "Signal = specs' net position (% of open interest), z-scored against the "
         "prior 52 weeks. Return = Monday after release → following Monday, bp. "
         "IS 2022-23 / OOS 2024-26.", "",
         "| pair | split | weeks | corr z→return (t) | extreme weeks |z|≥1.5 | FOLLOW bp/wk (hit%) | OPPOSITE bp/wk (hit%) |",
         "|---|---|---|---|---|---|---|"]
    verdicts = []
    for pair in PAIRS:
        rows = sorted((d, n) for p, d, n in cot_rows if p == pair)
        if not rows or pair not in daily:
            L.append(f"| {pair} | — | 0 | — | — | — | — |")
            continue
        dates = [d for d, _ in rows]
        z = zscore_prior([n for _, n in rows])
        px = daily[pair]
        pdates = sorted(x.date() for x in px.index)
        close = {x.date(): float(v) for x, v in px.items()}
        obs = []
        for d, zz in zip(dates, z):
            if zz is None:
                continue
            a = next_trading_on_or_after(pdates, d + timedelta(days=6))     # Monday after release
            b = next_trading_on_or_after(pdates, d + timedelta(days=13))
            if a is None or b is None:
                continue
            obs.append((d, zz, math.log(close[b] / close[a]) * 1e4))
        fol = {}
        for split, yrs in (("IS", (2022, 2023)), ("OOS", (2024, 2025, 2026))):
            sub = [o for o in obs if o[0].year in yrs]
            r, t, n = corr_t([o[1] for o in sub], [o[2] for o in sub])
            ext = [o for o in sub if abs(o[1]) >= 1.5]
            f_ = [math.copysign(1, o[1]) * o[2] for o in ext]
            ms = mean_se(f_)
            hit = 100 * sum(1 for x in f_ if x > 0) / len(f_) if f_ else float("nan")
            fol[split] = ms
            L.append(f"| {pair} | {split} | {n} | {_f(r,2)} ({_f(t)}) | {len(ext)} | "
                     f"{_f(ms[0])} ({hit:.0f}%) | {_f(-ms[0] if not math.isnan(ms[0]) else ms[0])} "
                     f"({(100-hit):.0f}%) |")
        pooled = mean_se([math.copysign(1, o[1]) * o[2] for o in obs if abs(o[1]) >= 1.5])
        verdicts.append((pair, verdict(fol["IS"][0], fol["OOS"][0], tstat(pooled)), tstat(pooled)))
    L += ["", "**Verdict (extreme weeks, FOLLOW the specs):** " +
          " · ".join(f"{p} {v} (pooled t {_f(t)})" for p, v, t in verdicts) +
          ". `OPPOSITE WORKS` means fading the crowd paid in both halves.", ""]
    return L


def section_rates(yields, daily):
    import pandas as pd
    L = ["## §B Interest rates — do US yields move or predict the pairs?", "",
         "Daily yield change in bp vs daily pair return in bp. The rate story says "
         "yields UP → dollar UP → pairs DOWN, i.e. a NEGATIVE same-day correlation. "
         "Halves: 2022-23 / 2024-26.", "",
         "| pair | yield | same-day corr IS / OOS | next-day corr IS / OOS (t) |",
         "|---|---|---|---|"]
    for pair, px in daily.items():
        pr = (px.apply(math.log).diff() * 1e4).rename("p")
        for k, y in yields.items():
            dy = (y.diff() * 100).rename("y")             # yield points -> bp
            df = pd.concat([pr, dy], axis=1).dropna()
            df["y_lag"] = df["y"].shift(1)
            cells = []
            for yrs in ((2022, 2023), (2024, 2025, 2026)):
                sub = df[df.index.year.isin(yrs)]
                r0, t0, _ = corr_t(list(sub.y), list(sub.p))
                r1, t1, _ = corr_t(list(sub.y_lag), list(sub.p))
                cells.append((r0, t0, r1, t1))
            L.append(f"| {pair} | {k} | {_f(cells[0][0],2)} / {_f(cells[1][0],2)} | "
                     f"{_f(cells[0][2],2)} ({_f(cells[0][3])}) / {_f(cells[1][2],2)} ({_f(cells[1][3])}) |")
    # the brief's lean rule on the 5y
    L += ["", "**The brief's own rule** (5-day US yield change beyond ±5bp → lean the "
          "pairs the OTHER way), scored on the next day and the next 5 days:", "",
          "| pair | horizon | split | signals | FOLLOW bp (hit%) | OPPOSITE bp (hit%) |",
          "|---|---|---|---|---|---|"]
    y5 = yields.get("5y")
    rule_v = []
    for pair, px in daily.items():
        if y5 is None:
            break
        df = pd.concat([px.rename("px"), y5.rename("y")], axis=1).dropna()
        df["chg5"] = (df["y"] - df["y"].shift(5)) * 100
        df["lean"] = [(-1 if c > 5 else (1 if c < -5 else 0)) if not math.isnan(c) else 0
                      for c in df["chg5"]]
        for h in (1, 5):
            df[f"f{h}"] = (df["px"].shift(-h).apply(math.log) - df["px"].apply(math.log)) * 1e4
            # NON-overlapping: one observation per h-day block. Overlapping 5-day
            # windows (plus a lean that persists for days) inflated t enough that
            # the random-walk null read "OPPOSITE WORKS" on two pairs.
            dh = df.iloc[::h]
            per = {}
            for split, yrs in (("IS", (2022, 2023)), ("OOS", (2024, 2025, 2026))):
                sub = dh[(dh.index.year.isin(yrs)) & (dh.lean != 0)].dropna(subset=[f"f{h}"])
                gains = list(sub.lean * sub[f"f{h}"])
                ms = mean_se(gains)
                hit = 100 * sum(1 for g in gains if g > 0) / len(gains) if gains else float("nan")
                per[split] = ms
                L.append(f"| {pair} | +{h}d | {split} | {len(gains)} | {_f(ms[0])} ({hit:.0f}%) | "
                         f"{_f(-ms[0] if not math.isnan(ms[0]) else ms[0])} ({100-hit:.0f}%) |")
            allg = list((dh[dh.lean != 0].lean * dh[dh.lean != 0][f"f{h}"]).dropna())
            rule_v.append((pair, h, verdict(per["IS"][0], per["OOS"][0], tstat(mean_se(allg)))))
    L += ["", "**Verdict (brief's yield lean):** " +
          " · ".join(f"{p} +{h}d {v}" for p, h, v in rule_v) +
          ". +5d uses non-overlapping 5-day blocks.", ""]
    return L


def section_news(events, hourly):
    import pandas as pd
    if not hourly:
        return ["## §C News", "", "_no hourly data_", ""]
    any_s = next(iter(hourly.values()))
    lo, hi = any_s.index.min(), any_s.index.max()
    cut = (lo + (hi - lo) / 2).date()
    L = ["## §C High / Medium news — how big is the move, and does it follow through?", "",
         f"_hourly data {lo:%Y-%m-%d} → {hi:%Y-%m-%d}; halves split at {cut}. "
         "IMPACT = |move| in the 2h from the event's hour, as a multiple of the same "
         "clock hour on no-news days. FOLLOW = next 3h in the direction of that first "
         "move (bp); FADE = the opposite. CONTROL = the same measures at the same "
         "clock hours on no-news days._", ""]

    def px_at(s, t):
        v = s.reindex([t], method="ffill", tolerance=pd.Timedelta("90min")).iloc[0]
        return None if pd.isna(v) else float(v)

    # events -> (pair, floored hour) observations, deduped
    ev_obs = {}
    for ev_dt, ccy, imp, name in events:
        t = pd.Timestamp(ev_dt).tz_convert("UTC").floor(H1_RULE)
        if not (lo <= t <= hi):
            continue
        cls = "Critical" if (imp == "High" and (name or "").upper() in CRITICAL) else imp
        for pair in NEWS_PAIRS.get(ccy, ()):
            key = (pair, t)
            rank = {"Critical": 3, "High": 2, "Medium": 1}[cls]
            if key not in ev_obs or rank > ev_obs[key][1]:
                ev_obs[key] = (cls, rank, ccy)
    news_hours = {(p, t + pd.Timedelta(hours=k)) for (p, t) in ev_obs for k in range(-3, 6)}

    def measure(pair, t):
        s = hourly.get(pair)
        if s is None:
            return None
        return follow_through(px_at(s, t), px_at(s, t + pd.Timedelta(hours=2)),
                              px_at(s, t + pd.Timedelta(hours=5)))

    # control by (pair, UTC hour, half): same clock hour, weekdays, no news within window
    ctrl = {}
    for pair, s in hourly.items():
        hrs = sorted({h for (_, t) in ev_obs for h in [t.hour]})
        for t in s.index:
            if t.dayofweek >= 5 or t.hour not in hrs or (pair, t) in news_hours:
                continue
            imp_, cont = measure(pair, t)
            if imp_ is None:
                continue
            ctrl.setdefault((pair, t.hour, half_of(t.date(), cut)), []).append((imp_, cont))

    rows = {}
    for (pair, t), (cls, _, _) in ev_obs.items():
        imp_, cont = measure(pair, t)
        if imp_ is None:
            continue
        c = ctrl.get((pair, t.hour, half_of(t.date(), cut)), [])
        if not c:
            continue
        c_imp = sum(x for x, _ in c) / len(c)
        c_cont = mean_se([y for _, y in c])[0]
        rows.setdefault((cls, half_of(t.date(), cut)), []).append(
            (imp_, imp_ / c_imp if c_imp else None, cont, None if cont is None else cont - c_cont))

    L += ["| class | half | events | avg 2h move bp | × normal hour | FOLLOW next 3h bp (t) | vs no-news (t) | FADE bp |",
          "|---|---|---|---|---|---|---|---|"]
    verd = []
    for cls in ("Critical", "High", "Medium"):
        per = {}
        for half in ("A", "B"):
            r = rows.get((cls, half), [])
            mi = mean_se([x[0] for x in r])
            mr = mean_se([x[1] for x in r])
            mc = mean_se([x[2] for x in r])
            md = mean_se([x[3] for x in r])
            per[half] = md
            L.append(f"| {cls} | {half} | {len(r)} | {mi[0]:.1f} | {mr[0]:.1f}× | "
                     f"{_f(mc[0])} ({_f(tstat(mc))}) | {_f(md[0])} ({_f(tstat(md))}) | "
                     f"{_f(-mc[0] if not math.isnan(mc[0]) else mc[0])} |")
        alld = mean_se([x[3] for h in ("A", "B") for x in rows.get((cls, h), [])])
        verd.append((cls, verdict(per["A"][0], per["B"][0], tstat(alld)), tstat(alld)))
    L += ["", "**Verdict (follow-through beyond a normal hour):** " +
          " · ".join(f"{c} {v} (pooled t {_f(t)})" for c, v, t in verd) +
          ". `OPPOSITE WORKS` here means fading the first news move paid.", "",
          "_No NZD events exist in the calendar, so NZDUSD only appears via USD news. "
          "USD events are High only (NFP/CPI/FOMC are 'Critical')._", ""]
    return L


# ───────────────────────────── main ────────────────────────────────────────────
def build(cot_rows, notes, daily, yields, hourly, events, label):
    L = [f"# P79 — fundamentals scorecard ({label})", "",
         "_Measurement only. Every effect must hold in BOTH halves with pooled |t| ≥ 2.5 "
         "to count. 'OPPOSITE' = what fading the signal would have done._", "",
         "_coverage: daily " + ", ".join(f"{p} {s.index.min():%Y-%m-%d}→{s.index.max():%Y-%m-%d}"
                                         for p, s in daily.items()) +
         "; yields " + ", ".join(yields) + f"; COT rows {len(cot_rows)}; hourly pairs "
         f"{len(hourly)}; news events {len(events)}_", ""]
    L += section_cot(cot_rows, daily, notes)
    L += section_rates(yields, daily)
    L += section_news(events, hourly)
    return "\n".join(L) + "\n"


def _synthetic(seed=3):
    """Random walks for every input: the scorecard must find nothing."""
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    days = pd.bdate_range("2021-01-04", "2026-10-02")
    daily = {p: pd.Series(np.exp(np.cumsum(rng.normal(0, 50, len(days)) / 1e4)) * b, index=days)
             for p, b in (("EURUSD", 1.1), ("GBPUSD", 1.3), ("NZDUSD", 0.6))}
    yields = {k: pd.Series(4 + np.cumsum(rng.normal(0, 0.06, len(days))), index=days)
              for k in YIELDS}
    tues = [d.date() for d in days if d.weekday() == 1]
    cot = [(p, d, float(v)) for p in PAIRS
           for d, v in zip(tues, np.cumsum(rng.normal(0, 3, len(tues))))]
    hidx = pd.date_range("2024-10-07", "2026-10-02", freq=H1_RULE, tz="UTC")
    hidx = hidx[hidx.dayofweek < 5]
    hourly = {p: pd.Series(np.exp(np.cumsum(rng.normal(0, 10, len(hidx)) / 1e4)) * 1.1, index=hidx)
              for p in PAIRS}
    return cot, ["synthetic"], daily, yields, hourly, load_news()


def _publish(path):
    if os.environ.get("NO_PUSH") == "1":
        return
    def _git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    _git("add", "-f", path)
    if _git("diff", "--cached", "--quiet", "--", path).returncode == 0:
        print("report unchanged — nothing pushed")
        return
    _git("commit", "-q", "-m", "fundamentals scorecard (auto)")
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    print("PUSHED" if _git("push", "origin", "HEAD").returncode == 0 else "(push failed)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.null:
        text = build(*_synthetic(), "RANDOM-WALK NULL")
        print(text)
        return 0
    daily = load_daily()
    yields = load_yields()
    hourly = load_hourly()
    cot, notes = load_cot(range(2021, datetime.utcnow().year + 1))
    text = build(cot, notes, daily, yields, hourly, load_news(), "real data")
    print(text)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8").write(text)
    _publish(REPORT)
    return 0


def selftest():
    import pandas as pd
    from datetime import date
    pd.Timedelta(H1_RULE)
    assert abs(mean_se([1, 2, 3])[0] - 2) < 1e-12 and mean_se([])[2] == 0
    r, t, n = corr_t([1, 2, 3, 4, 5, 6], [2, 4, 6, 8, 10, 12.1])
    assert r > 0.99 and t > 10 and n == 6
    assert math.isnan(corr_t([1, 2], [1, 2])[0])
    z = zscore_prior([0.0] * 30 + [1.0, 0.0, 10.0], window=52, min_n=26)
    assert z[29] is None                                   # all-equal prior: sd 0
    assert z[31] is not None and z[32] > z[31]            # uses prior only
    assert zscore_prior([1.0, 2.0])[1] is None             # too little history
    assert verdict(1, 1, 2.6) == "WORKS" and verdict(-1, -1, -2.6) == "OPPOSITE WORKS"
    assert verdict(1, -1, 2.6) == "nothing" and verdict(1, 1, 2.2) == "nothing"
    assert verdict(float("nan"), 1, 3) == "no data"
    imp, cont = follow_through(1.0, 1.001, 1.002)
    assert imp > 9 and cont > 0                            # continued up
    imp, cont = follow_through(1.0, 1.001, 1.0)
    assert cont < 0                                        # reversed
    imp, cont = follow_through(1.0, 0.999, 0.998)
    assert cont > 0                                        # continued down
    assert follow_through(None, 1, 1) == (None, None)
    assert half_of(date(2025, 1, 1), date(2025, 6, 1)) == "A"
    d = [date(2024, 1, 1), date(2024, 1, 3), date(2024, 1, 8)]
    assert next_trading_on_or_after(d, date(2024, 1, 2)) == date(2024, 1, 3)
    assert next_trading_on_or_after(d, date(2024, 1, 9)) is None
    # COT parser, two header vintages
    v1 = pd.DataFrame({"Market and Exchange Names": ["EURO FX - CHICAGO MERCANTILE EXCHANGE",
                                                     "EURO FX/BRITISH POUND XRATE - CME",
                                                     "BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE"],
                       "As of Date in Form YYYY-MM-DD": ["2024-01-02", "2024-01-02", "2024-01-02"],
                       "Open Interest (All)": [100, 50, 200],
                       "Noncommercial Positions-Long (All)": [60, 10, 50],
                       "Noncommercial Positions-Short (All)": [20, 10, 150],
                       "Noncommercial Positions-Spreading (All)": [5, 5, 5]})
    got = parse_cot_table(v1)
    assert ("EURUSD", date(2024, 1, 2), 40.0) in got
    assert ("GBPUSD", date(2024, 1, 2), -50.0) in got
    assert len(got) == 2                                   # cross-rate excluded
    v2 = pd.DataFrame({"Market_and_Exchange_Names": ["NZ DOLLAR - CHICAGO MERCANTILE EXCHANGE"],
                       "As_of_Date_In_Form_YYMMDD": ["240102"],
                       "Open_Interest_All": [10],
                       "NonComm_Positions_Long_All": [2],
                       "NonComm_Positions_Short_All": [7]})
    got2 = parse_cot_table(v2)
    assert got2 == [("NZDUSD", date(2024, 1, 2), -50.0)], got2
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

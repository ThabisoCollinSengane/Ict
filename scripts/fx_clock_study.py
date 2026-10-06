#!/usr/bin/env python3
"""P78 — the institutional FX clock, measured on OUR M1 data.

    python scripts/fx_clock_study.py                 # real data, auto-pushes
    python scripts/fx_clock_study.py --null          # random walk: must read RED
    python scripts/fx_clock_study.py --null --plant 3  # planted fix effect: must read GREEN
    python scripts/fx_clock_study.py --selftest

THE CLAIM UNDER TEST (Krohn, Mueller & Whelan, J. Finance 2024): the dollar
APPRECIATES into each benchmark fix and DEPRECIATES after it, every day, for
20+ years. Fixes: ECB 14:15 Frankfurt, WMR 16:00 London, Tokyo 09:55. Plus the
home-hours effect (Ranaldo; Breedon & Ranaldo): a currency tends to fall during
its own working hours.

None of it has been measured on EURUSD/GBPUSD/NZDUSD 2022-2025. This does.

SECTIONS
  §1  average move by ET hour (USD basket and per pair), both halves
  §2  the fix reversal: dollar move in the W hours before vs after each fix.
      R = pre - post (bp). Positive R = dollar up into the fix, down after.
      CONTROL: the same R at 96 placebo clock times (every 15 min ET, minus a
      band around the real fixes). The real fix must beat ~all of them. A fix
      that merely reads positive is not evidence — P68b/P69 both looked
      positive until the mirror was put next to them.
  §3  daylight-saving natural experiment. ~3-4 weeks a year Europe is 5h ahead
      of New York instead of 6, so the ECB fix moves 08:15 -> 09:15 ET and the
      WMR fix 11:00 -> 12:00 ET. On those days, measure R at the European clock
      time AND at the usual ET time. Whichever carries the effect is the clock
      that drives it. Small n — the minimum detectable effect is printed next
      to every number so an underpowered null cannot read as a finding.
  §4  our trades WITH vs AGAINST the clock flow. Descriptive unless §2 is GREEN.
      Prints the n each comparison would need, per the P76b lesson.

NO LOOKAHEAD: 5-min closes are labelled at the END of their bar
(label="right"), so price "at" T is the last trade at or before T.
HistData is fixed EST: UTC = EST + 5h always (same as run_backtest_histdata).
"""
from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
DATA = os.path.join(ROOT, "data", "histdata")
REPORT = os.path.join(ROOT, "data", "fx_clock_report.md")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
# pandas 3.x removed the "T" minute alias — use "min" (triple_sweep_study._freq,
# P77's crash). Pinned here and asserted in the selftest.
BAR_RULE = "5min"
H1_RULE = "60min"
ET_TZ = "America/New_York"

# (local tz, hour, minute) — the published benchmark times
FIXES = {
    "ECB":   ("Europe/Berlin", 14, 15),
    "WMR":   ("Europe/London", 16, 0),
    "TOKYO": ("Asia/Tokyo",     9, 55),
}
# ET clock times near which a placebo anchor would overlap a real fix
# (normal-week AND mismatch-week positions; Tokyo has no DST)
REAL_FIX_ET = ("08:15", "09:15", "11:00", "12:00", "19:55", "20:55")
PLACEBO_EXCLUDE_MIN = 90


# ─────────────────────────── pure logic (unit-tested) ───────────────────────────
def split_of(year: int):
    if year in IS_YEARS:
        return "IS"
    if year in OOS_YEARS:
        return "OOS"
    return None


def fix_utc(day, tzname: str, hh: int, mm: int):
    """Local clock time on calendar `day` -> UTC pandas Timestamp (DST-aware)."""
    import pandas as pd
    return (pd.Timestamp(year=day.year, month=day.month, day=day.day, hour=hh, minute=mm)
            .tz_localize(tzname).tz_convert("UTC"))


def europe_ny_offset_h(day) -> float:
    """Berlin minus New York, in hours, at noon UTC on `day` (6 normally, 5 in
    the spring/autumn mismatch weeks)."""
    import pandas as pd
    t = pd.Timestamp(year=day.year, month=day.month, day=day.day, hour=12, tz="UTC")
    b = t.tz_convert("Europe/Berlin").utcoffset().total_seconds()
    n = t.tz_convert(ET_TZ).utcoffset().total_seconds()
    return (b - n) / 3600.0


def is_mismatch(day) -> bool:
    return abs(europe_ny_offset_h(day) - 6.0) > 1e-9


def dollar_bp(p0: float, p1: float) -> float:
    """Dollar return in bp for an X/USD pair moving p0 -> p1 (pair up = dollar down)."""
    return -math.log(p1 / p0) * 1e4


def reversal(p_pre: float, p_fix: float, p_post: float):
    """(dollar_pre, dollar_post, R). R > 0 = dollar up into the fix, down after."""
    pre = dollar_bp(p_pre, p_fix)
    post = dollar_bp(p_fix, p_post)
    return pre, post, pre - post


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


def fix_verdict(r_is, t_pool, pct_is, r_oos, pct_oos, pct_bar=95.0):
    """GREEN : R > 0 in BOTH halves, pooled t >= 2, AND beats >= pct_bar % of the
              placebo clock times in BOTH halves — real, and specific to the fix.
    YELLOW: R > 0 both halves and pooled t >= 2, but the placebo bar is not met —
            a real time-of-day move that is NOT special to the fix minute.
    RED   : anything else.
    The first version made YELLOW "right sign in both halves" alone. A coin flip
    does that 25% of the time per fix, so the random-walk null read YELLOW.
    A threshold the null clears is not a threshold (P77)."""
    def ok(x):
        return x is not None and not math.isnan(x)
    if not (ok(r_is) and ok(r_oos)):
        return "NO DATA"
    if r_is > 0 and r_oos > 0 and ok(t_pool) and t_pool >= 2.0:
        if pct_is >= pct_bar and pct_oos >= pct_bar:
            return "GREEN"
        return "YELLOW"
    return "RED"


def percentile_rank(value: float, others) -> float:
    others = [o for o in others if not math.isnan(o)]
    if not others or math.isnan(value):
        return float("nan")
    return 100.0 * sum(1 for o in others if o < value) / len(others)


def clock_flow_dir(t_utc, window_h: float, fixes=("ECB", "WMR")) -> int:
    """Expected PAIR direction from the fix clock at t (X/USD pairs):
    -1 in the W hours BEFORE a fix (dollar bid -> pair down),
    +1 in the W hours AFTER (dollar offered -> pair up), 0 otherwise.
    Uses that calendar day's DST-correct fix times."""
    import pandas as pd
    t = pd.Timestamp(t_utc)
    t = t.tz_localize("UTC") if t.tzinfo is None else t.tz_convert("UTC")
    w = pd.Timedelta(hours=window_h)
    for name in fixes:
        tz, hh, mm = FIXES[name]
        day = t.tz_convert(tz).date()
        f = fix_utc(day, tz, hh, mm)
        if f - w <= t < f:
            return -1
        if f <= t < f + w:
            return +1
    return 0


def mde(se: float) -> float:
    """Minimum detectable effect at 2 standard errors."""
    return 2.0 * se if not math.isnan(se) else float("nan")


def n_needed(p: float, diff: float) -> int:
    """Per-bucket n for a win-rate difference `diff` to reach 2 SE."""
    if diff == 0 or p <= 0 or p >= 1:
        return 0
    return int(math.ceil(8.0 * p * (1 - p) / diff ** 2))


# ─────────────────────────────── data ───────────────────────────────────────────
def _find_dump():
    """Same candidate list as the six existing analysis scripts (P73 lesson)."""
    for p in (os.path.join(ROOT, "data", "histdata", "trades_dump.csv"),
              os.path.join(ROOT, "data", "trades_dump.csv")):
        if os.path.exists(p):
            return p
    return None


def _load_closes(sym):
    """HistData M1 -> 5-min closes labelled at bar END, UTC index."""
    import pandas as pd
    frames = []
    for y in IS_YEARS + OOS_YEARS:
        p = os.path.join(DATA, f"{sym}_{y}.csv")
        if os.path.exists(p):
            frames.append(pd.read_csv(p, sep=";", header=None,
                                      names=["dt", "o", "h", "l", "c", "v"]))
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S")
    df = df.drop_duplicates("dt").sort_values("dt").set_index("dt")
    df.index = (df.index + pd.Timedelta(hours=5)).tz_localize("UTC")
    return df["c"].resample(BAR_RULE, label="right", closed="left").last().dropna()


def _synthetic(plant_bp: float, seed: int = 11):
    """Random-walk 5-min closes for 3 pairs, 2022-2025 weekdays. With plant>0,
    injects a dollar W around the ECB fix: dollar +plant bp over the 2h before
    the fix and -plant bp over the 2h after (pairs move the other way)."""
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-03", "2025-12-31", freq=BAR_RULE, tz="UTC")
    idx = idx[idx.tz_convert(ET_TZ).dayofweek < 5]
    out = {}
    base = {"EURUSD": 1.10, "GBPUSD": 1.27, "NZDUSD": 0.62}
    common = rng.normal(0, 2.0, len(idx))                  # shared dollar noise, bp
    plant = np.zeros(len(idx))
    if plant_bp:
        days = sorted(set(idx.tz_convert(ET_TZ).date))
        per_bar = plant_bp / 24.0                          # 24 five-minute bars in 2h
        pos = pd.Series(np.arange(len(idx)), index=idx)
        for d in days:
            f = fix_utc(d, "Europe/Berlin", 14, 15)
            pre = pos[(pos.index > f - pd.Timedelta(hours=2)) & (pos.index <= f)]
            post = pos[(pos.index > f) & (pos.index <= f + pd.Timedelta(hours=2))]
            plant[pre.values] -= per_bar                   # pair DOWN = dollar up
            plant[post.values] += per_bar
    for i, p in enumerate(PAIRS):
        own = rng.normal(0, 2.0, len(idx))
        logp = math.log(base[p]) + np.cumsum((common + own + plant) / 1e4)
        out[p] = pd.Series(np.exp(logp), index=idx)
    return out


def _px_at(closes, times):
    """Last close at or before each time (tolerance 15 min), as a numpy array."""
    import pandas as pd
    return closes.reindex(pd.DatetimeIndex(times), method="ffill",
                          tolerance=pd.Timedelta("15min")).to_numpy()


# ─────────────────────────────── analysis ───────────────────────────────────────
def _days(closes):
    import pandas as pd
    et = closes.index.tz_convert(ET_TZ)
    d = pd.Series(1, index=et.date).groupby(level=0).size()
    return sorted(x for x, n in d.items() if n >= 200 and x.weekday() < 5)


def hourly_profile(series):
    """{split: {hour: (mean USD bp, se, n)}} from the USD basket of hourly returns."""
    import numpy as np
    import pandas as pd
    rets = []
    for p, c in series.items():
        h = c.resample(H1_RULE, label="right", closed="left").last().dropna()
        r = -np.log(h / h.shift(1)) * 1e4                  # dollar bp
        gap = h.index.to_series().diff() > pd.Timedelta(H1_RULE)
        rets.append(r[~gap].rename(p))
    basket = pd.concat(rets, axis=1).mean(axis=1).dropna()
    start_et = (basket.index - pd.Timedelta(H1_RULE)).tz_convert(ET_TZ)
    df = pd.DataFrame({"r": basket.values, "hour": start_et.hour,
                       "year": start_et.year, "dow": start_et.dayofweek})
    df = df[df.dow < 5]
    out = {}
    for split, years in (("IS", IS_YEARS), ("OOS", OOS_YEARS)):
        sub = df[df.year.isin(years)]
        out[split] = {h: mean_se(list(g.r)) for h, g in sub.groupby("hour")}
    return out


def _reversal_by_day(series, days, anchor_fn, window_h):
    """Per-day USD-basket reversal R at the anchor returned by anchor_fn(day)."""
    import numpy as np
    import pandas as pd
    w = pd.Timedelta(hours=window_h)
    anchors = [anchor_fn(d) for d in days]
    per_pair = []
    for c in series.values():
        a = _px_at(c, [x - w for x in anchors])
        b = _px_at(c, anchors)
        e = _px_at(c, [x + w for x in anchors])
        with np.errstate(invalid="ignore", divide="ignore"):
            pre = -np.log(b / a) * 1e4
            post = -np.log(e / b) * 1e4
        per_pair.append(pre - post)
    R = np.nanmean(np.vstack(per_pair), axis=0)
    return {d: (None if np.isnan(r) else float(r)) for d, r in zip(days, R)}


def _by_split(day_vals):
    out = {}
    for split in ("IS", "OOS"):
        out[split] = mean_se([v for d, v in day_vals.items() if split_of(d.year) == split])
    out["ALL"] = mean_se(list(day_vals.values()))
    return out


def _placebo_anchors():
    keep = []
    real = [int(s[:2]) * 60 + int(s[3:]) for s in REAL_FIX_ET]
    for m in range(0, 24 * 60, 15):
        dist = min(min(abs(m - r), 1440 - abs(m - r)) for r in real)
        if dist > PLACEBO_EXCLUDE_MIN:
            keep.append(m)
    return keep


def fix_study(series, days, window_h):
    """§2 — real fix R per split, against placebo ET clock times."""
    res = {}
    for name, (tz, hh, mm) in FIXES.items():
        vals = _reversal_by_day(series, days, lambda d: fix_utc(d, tz, hh, mm), window_h)
        res[name] = _by_split(vals)
    plac = {"IS": [], "OOS": []}
    for m in _placebo_anchors():
        vals = _reversal_by_day(series, days,
                                lambda d, m=m: fix_utc(d, ET_TZ, m // 60, m % 60), window_h)
        s = _by_split(vals)
        for split in ("IS", "OOS"):
            plac[split].append(s[split][0])
    return res, plac


def dst_study(series, days, window_h):
    """§3 — on mismatch days, R at the European clock vs the usual ET clock."""
    mism = [d for d in days if is_mismatch(d)]
    norm = [d for d in days if not is_mismatch(d)]
    rows = []
    for name, usual_et in (("ECB", (8, 15)), ("WMR", (11, 0))):
        tz, hh, mm = FIXES[name]
        euro = _reversal_by_day(series, mism, lambda d: fix_utc(d, tz, hh, mm), window_h)
        etc = _reversal_by_day(series, mism, lambda d: fix_utc(d, ET_TZ, *usual_et), window_h)
        ref = _reversal_by_day(series, norm, lambda d: fix_utc(d, tz, hh, mm), window_h)
        rows.append((name, mean_se(list(euro.values())), mean_se(list(etc.values())),
                     mean_se(list(ref.values()))))
    return len(mism), rows


def trade_study(window_h):
    """§4 — our trades with / against / outside the fix flow."""
    import pandas as pd
    p = _find_dump()
    if not p:
        return None, ("trade dump not found in data/histdata/ or data/ — run "
                      "`python run_backtest_histdata.py` first")
    df = pd.read_csv(p)
    need = {"opened_at", "pair", "direction", "pnl"}
    if not need.issubset(df.columns):
        return None, f"dump missing columns {sorted(need - set(df.columns))}"
    df = df.dropna(subset=list(need))
    if "leg_idx" in df.columns:                       # base positions only
        df = df[df["leg_idx"].fillna(1) == 1]
    ts = pd.to_datetime(df["opened_at"], utc=True, errors="coerce")
    df = df.assign(_ts=ts).dropna(subset=["_ts"])
    rows = []
    # iterrows, not itertuples: itertuples renames the leading-underscore `_ts`
    # column (the P71/P73 AttributeError).
    for _, r in df.iterrows():
        flow = clock_flow_dir(r["_ts"], window_h)
        if flow == 0:
            b = "outside"
        else:
            b = "with" if int(r["direction"]) == flow else "against"
        mis = is_mismatch(r["_ts"].tz_convert(ET_TZ).date())
        rows.append((split_of(r["_ts"].year), b, float(r["pnl"]), mis))
    return rows, p


def _wr_pf(pnls):
    n = len(pnls)
    if not n:
        return 0, float("nan"), float("nan")
    w = sum(1 for x in pnls if x > 0)
    g = sum(x for x in pnls if x > 0)
    l = -sum(x for x in pnls if x < 0)
    return n, 100.0 * w / n, (g / l if l > 0 else float("inf"))


# ─────────────────────────────── report ─────────────────────────────────────────
def _f(x, nd=2):
    return "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{nd}f}"


def build_report(series, window_h, label, coverage, with_trades=True):
    days = _days(next(iter(series.values())))
    n_is = sum(1 for d in days if split_of(d.year) == "IS")
    n_oos = sum(1 for d in days if split_of(d.year) == "OOS")
    L = [f"# P78 — the institutional FX clock ({label})", "",
         f"_coverage: {coverage}; trading days IS {n_is} / OOS {n_oos}; "
         f"window ±{window_h:g}h around each anchor_", ""]

    # §2 first — it carries the verdict
    res, plac = fix_study(series, days, window_h)
    verdicts = {}
    L += ["## §2 The fix reversal — the verdict", "",
          "R = dollar move into the anchor minus dollar move after it, USD basket, "
          "bp/day. Positive = dollar bid into the fix, offered after. `pctl` = share "
          "of placebo clock times this fix beats (needs ≥95 in BOTH halves).", "",
          "| fix | R IS | t IS | pctl IS | R OOS | t OOS | pctl OOS | pooled t | verdict |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, s in res.items():
        (mi, si, ni), (mo, so, no), (ma, sa, na) = s["IS"], s["OOS"], s["ALL"]
        ti = mi / si if si and not math.isnan(si) else float("nan")
        to = mo / so if so and not math.isnan(so) else float("nan")
        ta = ma / sa if sa and not math.isnan(sa) else float("nan")
        pi = percentile_rank(mi, plac["IS"])
        po = percentile_rank(mo, plac["OOS"])
        v = fix_verdict(mi, ta, pi, mo, po)
        verdicts[name] = v
        L.append(f"| {name} | {_f(mi)} | {_f(ti,1)} | {pi:.0f} | {_f(mo)} | {_f(to,1)} "
                 f"| {po:.0f} | {_f(ta,1)} | **{v}** |")
    trade_day = [verdicts.get("ECB"), verdicts.get("WMR")]
    overall = ("GREEN" if "GREEN" in trade_day else
               "YELLOW" if "YELLOW" in trade_day else "RED")
    gap_h = 2.75                                   # ECB 08:15 -> WMR 11:00 ET
    if 2 * window_h > gap_h:
        L += ["", f"> ⚠️ **ECB and WMR windows overlap** (±{window_h:g}h each, fixes "
              f"{gap_h:g}h apart). A real ECB effect leaks into WMR with the OPPOSITE "
              "sign — the planted-effect drive showed WMR at t −3.5 with nothing "
              "planted there. Narrowing the window (`--window 1.375`) cut that to "
              "t −2.5 but did NOT remove it: the effect itself lasts hours, longer "
              "than the gap. **ECB and WMR are not independent tests.** If ECB is "
              "GREEN, a negative WMR is the expected echo, not a second finding."]
    L += ["", f"**VERDICT: {overall}** (ECB {verdicts.get('ECB')} · WMR "
              f"{verdicts.get('WMR')} · Tokyo {verdicts.get('TOKYO')} — Tokyo is "
              "reported but not counted; it is outside every killzone).", "",
          f"_placebo: {len(plac['IS'])} clock times, every 15 min ET, excluding "
          f"±{PLACEBO_EXCLUDE_MIN} min around the real fixes._", ""]

    # §1
    prof = hourly_profile(series)
    marks = {1: "CLS window opens", 3: "London open / CLS settle target · **London KZ**",
             4: "London KZ", 6: "CLS window closes", 7: "**NY AM KZ**",
             8: "ECB fix 08:15 · US data 08:30 · NY AM", 9: "NY AM",
             10: "NY option cut 10:00", 11: "WMR fix 11:00", 12: "noon block",
             17: "NY close / rollover", 20: "Tokyo fix 20:55"}
    L += ["## §1 Average dollar move by ET hour (USD basket)", "",
          "Mean bp per hour; positive = dollar up. t = mean / SE.", "",
          "| ET hour | IS bp | t | OOS bp | t | clock |", "|---|---|---|---|---|---|"]
    for h in range(24):
        mi, si, _ = prof["IS"].get(h, (float("nan"),) * 2 + (0,))
        mo, so, _ = prof["OOS"].get(h, (float("nan"),) * 2 + (0,))
        ti = mi / si if si and not math.isnan(si) else float("nan")
        to = mo / so if so and not math.isnan(so) else float("nan")
        L.append(f"| {h:02d}:00 | {_f(mi)} | {_f(ti,1)} | {_f(mo)} | {_f(to,1)} | {marks.get(h,'')} |")
    L += ["", "_Home-hours claim (Ranaldo): dollar up during European hours "
          "(~03-09 ET), down during US hours (~11-15 ET). Read sign AND both halves._", ""]

    # §3
    nm, rows = dst_study(series, days, window_h)
    L += ["## §3 Daylight-saving natural experiment", "",
          f"{nm} mismatch days (Europe 5h ahead of New York, not 6). On those days "
          "the European fixes sit one hour LATER in ET. If the effect follows the "
          "European clock, `at Euro clock` carries it and `at usual ET` does not.", "",
          "| fix | at Euro clock R (n) | MDE | at usual ET R | MDE | normal days R |",
          "|---|---|---|---|---|---|"]
    for name, (me, se_, ne), (mu, su, _), (mr, sr, nr) in rows:
        L.append(f"| {name} | {_f(me)} ({ne}) | {mde(se_):.2f} | {_f(mu)} | "
                 f"{mde(su):.2f} | {_f(mr)} ({nr}) |")
    L += ["", "_MDE = minimum detectable effect (2 SE). Where |R| < MDE the "
          "comparison is UNDERPOWERED — that is a statement about sample size, "
          "not about the clock._", ""]

    # §4
    if with_trades:
        tr, src = trade_study(window_h)
        L += ["## §4 Our trades — with / against the fix flow", ""]
        if tr is None:
            L += [f"_{src}_", ""]
        else:
            note = ("" if overall == "GREEN" else
                    "**§2 is not GREEN, so this table is DESCRIPTIVE ONLY** — "
                    "there is no established flow to be with or against.")
            L += [f"_dump: {os.path.relpath(src, ROOT)}; base legs only. 'with' = "
                  f"trade direction matches the expected pair move in the ±{window_h:g}h "
                  "around the ECB/WMR fix._", ""]
            if note:
                L += [note, ""]
            L += ["| split | bucket | n | WR% | PF |", "|---|---|---|---|---|"]
            for split in ("IS", "OOS"):
                for b in ("with", "against", "outside"):
                    n, wr, pf = _wr_pf([p for s, bb, p, _ in tr if s == split and bb == b])
                    L.append(f"| {split} | {b} | {n} | {wr:.1f} | {pf:.2f} |")
            for split in ("IS", "OOS"):
                nw, ww, _ = _wr_pf([p for s, b, p, _ in tr if s == split and b == "with"])
                na, wa, _ = _wr_pf([p for s, b, p, _ in tr if s == split and b == "against"])
                if nw and na:
                    d = (ww - wa) / 100.0
                    pbar = (ww * nw + wa * na) / (100.0 * (nw + na))
                    se = math.sqrt(pbar * (1 - pbar) * (1 / nw + 1 / na)) if 0 < pbar < 1 else float("nan")
                    L.append(f"\n_{split}: with − against = {100*d:+.1f}pp "
                             f"({d/se:+.2f} SE); a gap that size needs ~{n_needed(pbar, d)} "
                             f"trades per bucket to reach 2 SE (have {nw}/{na})._")
            mis = [(b, p) for _, b, p, m in tr if m]
            n, wr, pf = _wr_pf([p for _, p in mis])
            L += ["", f"_Trades opened on daylight-saving mismatch days: {n} "
                  f"(WR {wr:.1f}%, PF {pf:.2f}). These are the days London opens at "
                  "04:00 ET and the WMR fix lands at 12:00 ET, inside the noon block._", ""]
    return "\n".join(L) + "\n", overall


# ─────────────────────────────── main ───────────────────────────────────────────
def _publish(path):
    def _git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)
    _git("add", "-f", path)
    if _git("diff", "--cached", "--quiet", "--", path).returncode == 0:
        print("\n  REPORT UNCHANGED — nothing pushed. If you expected new numbers you "
              "are probably running stale code: git pull.")
        return
    sha = _git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown"
    if _git("commit", "-q", "-m", f"fx clock report (auto, on {sha})").returncode:
        print("\n  (commit failed — paste the report above)")
        return
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    ok = _git("push", "origin", "HEAD").returncode == 0
    print("\n  RESULTS PUSHED — Claude can read data/fx_clock_report.md" if ok
          else "\n  (auto-push failed — paste the report above)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=float, default=2.0, help="hours either side of an anchor")
    ap.add_argument("--null", action="store_true", help="random-walk data (must read RED)")
    ap.add_argument("--plant", type=float, default=0.0,
                    help="with --null: plant a dollar W of this many bp at the ECB fix")
    ap.add_argument("--seed", type=int, default=11, help="with --null: RNG seed")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.null:
        series = _synthetic(a.plant, a.seed)
        label = f"RANDOM-WALK NULL, planted {a.plant:g}bp" if a.plant else "RANDOM-WALK NULL"
        coverage = "synthetic 5-min, 2022-2025 weekdays"
        text, verdict = build_report(series, a.window, label, coverage, with_trades=False)
        print(text)
        return 0
    series = {}
    for p in PAIRS:
        c = _load_closes(p)
        if c is not None and len(c):
            series[p] = c
    if not series:
        print(f"No HistData M1 found in {DATA}. Expected e.g. EURUSD_2022.csv.")
        return 1
    cov = ", ".join(f"{p} {c.index.min():%Y-%m-%d}→{c.index.max():%Y-%m-%d} "
                    f"({len(c):,} bars)" for p, c in series.items())
    text, verdict = build_report(series, a.window, "real data", cov)
    print(text)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    open(REPORT, "w", encoding="utf-8").write(text)
    if not a.no_push:
        _publish(REPORT)
    return 0


def selftest():
    import datetime as dt
    import pandas as pd
    pd.Timedelta(BAR_RULE), pd.Timedelta(H1_RULE)           # aliases must parse (P77)
    pd.Series([1.0], index=pd.DatetimeIndex(["2024-01-02"], tz="UTC")).resample(H1_RULE).last()
    assert split_of(2022) == "IS" and split_of(2025) == "OOS" and split_of(2021) is None
    d = dt.date
    # DST: ECB fix in ET — normal 08:15, mismatch 09:15 (verified against pytz)
    et = lambda t: t.tz_convert(ET_TZ).strftime("%H:%M")
    assert et(fix_utc(d(2026, 3, 2), "Europe/Berlin", 14, 15)) == "08:15"
    assert et(fix_utc(d(2026, 3, 10), "Europe/Berlin", 14, 15)) == "09:15"
    assert et(fix_utc(d(2026, 10, 30), "Europe/Berlin", 14, 15)) == "09:15"
    assert et(fix_utc(d(2026, 11, 3), "Europe/Berlin", 14, 15)) == "08:15"
    assert et(fix_utc(d(2026, 3, 10), "Europe/London", 16, 0)) == "12:00"
    assert not is_mismatch(d(2026, 3, 2)) and is_mismatch(d(2026, 3, 10))
    assert is_mismatch(d(2026, 10, 30)) and not is_mismatch(d(2026, 7, 1))
    # sign: pair DOWN into the fix and UP after = dollar up then down = R > 0
    pre, post, R = reversal(1.1000, 1.0990, 1.1000)
    assert pre > 0 and post < 0 and R > 0
    assert reversal(1.1, 1.1, 1.1)[2] == 0
    m, se, n = mean_se([1.0, 2.0, 3.0])
    assert abs(m - 2) < 1e-12 and n == 3 and abs(se - (1 / math.sqrt(3))) < 1e-12
    assert mean_se([])[2] == 0 and math.isnan(mean_se([5.0])[1])
    assert fix_verdict(1.0, 3.0, 99, 1.0, 97) == "GREEN"
    assert fix_verdict(1.0, 3.0, 99, 1.0, 80) == "YELLOW"      # placebo not beaten OOS
    assert fix_verdict(1.0, 1.5, 99, 1.0, 99) == "RED"         # pooled t too small
    assert fix_verdict(0.3, 0.5, 62, 0.2, 67) == "RED"         # the null's own numbers
    assert fix_verdict(1.0, 3.0, 99, -0.1, 99) == "RED"        # sign flips
    assert fix_verdict(float("nan"), 3, 99, 1, 99) == "NO DATA"
    assert percentile_rank(5, [1, 2, 3, 10]) == 75.0
    # clock flow: 07:00 ET on a normal day is inside the 2h BEFORE the 08:15 ECB fix
    t = pd.Timestamp("2026-03-02 07:00", tz=ET_TZ).tz_convert("UTC")
    assert clock_flow_dir(t, 2.0) == -1
    t = pd.Timestamp("2026-03-02 09:00", tz=ET_TZ).tz_convert("UTC")
    assert clock_flow_dir(t, 2.0) == +1
    t = pd.Timestamp("2026-03-02 03:30", tz=ET_TZ).tz_convert("UTC")
    assert clock_flow_dir(t, 2.0) == 0                          # London KZ: outside
    t = pd.Timestamp("2026-03-10 09:00", tz=ET_TZ).tz_convert("UTC")
    assert clock_flow_dir(t, 2.0) == -1                         # mismatch: fix is 09:15
    assert n_needed(0.44, 0.05) > n_needed(0.44, 0.15) > 0
    assert n_needed(0.44, 0.0) == 0
    pa = _placebo_anchors()
    assert 8 * 60 + 15 not in pa and 0 in pa and len(pa) > 40
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

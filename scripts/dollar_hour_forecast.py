"""P126 — an honest forecast of the CURRENT hour's dollar move (Stage 0 + Stage 1).

Spec: research/specs/P126_dollar_hour_forecast.md (approved 2026-11-07).

DECISION GRID  every 5 min in London 03:00-04:55 ET and NY 07:00-09:55 ET (60 per weekday).
               Each decision t belongs to the H1 candle h0 = t floored to the hour (UTC hours
               = whole ET hours, so the boundaries match the engine's 60min bars).

OUTCOME        sign(DXY at the end of the current H1 candle - DXY now)
                 "now"       = OPEN of the first M1 bar starting at t (bounce trap fix, spec §5.3)
                 hour end    = CLOSE of the last M1 bar of the H1 candle (future; the answer only)
               Ties dropped. A random walk scores 50% for ANY rule.

PREDICTORS     (pre-registered, spec §7). "move this hour" = last COMPLETED M1 close (bar label
               < t) - the H1 candle's open (first M1 bar label >= h0, which must also be < t).
               At t = h0 nothing in the hour has closed -> move = 0 -> no call.
  R1 dxy_hour     sign(DXY move this hour)
  R2 dxy_m5_bos   engine htf_bias on COMPLETED DXY M5 bars
  R3 dxy_m15_bos  engine htf_bias on COMPLETED DXY M15 bars
                  (lookback = config.SWING_LOOKBACK_STH = 8, what every engine DXY gate call passes)
  R4 cross_hour   EURGBP + AUDNZD move this hour, vote of signs (opposite signs -> no call).
                  Sign convention (arbitrary, both FOLLOW and FADE are tested): cross up -> DXY up.
  R5 gold_hour    -sign(XAUUSD move this hour)            (gold up -> dollar down)
  R6 index_hour   -sign(SPXUSD % move + NSXUSD % move)     (risk-on -> dollar down)
  R7 vote         sign(R1+...+R6); tie -> no call
  pairs_hour      -sign(EURUSD + GBPUSD + NZDUSD % move) — REPORTED ONLY (trap 1: ~DXY itself)

PASS (Stage 1, spec §8)  same sign beyond 2 day-clustered SE in IS, OOS AND 2026; hit >= 55%
               (FOLLOW) or <= 45% (FADE) in every period; Null A and Null B pooled within 2 SE.

STAGE 0 (spec §2)  (1) from the P125 `mleaky` trade dumps (IS/OOS): the engine's leaky DXY H1
               read (forming H1 candle = its full-hour close) vs the honest one (last closed H1
               candle) at every first-leg entry; WR / PF / avg R when they agree vs differ.
               Both reads are pure functions of UDXUSD + the entry time, so they are computed
               here instead of in the engine (no engine change). (2) on the grid: how often the
               leaky read's sign = sign(hour close - now). (3) rough accuracy -> WR mapping.

--null [A|B|both]  A = independent random walks; B = pairs/gold/indices tied to DXY + bid-quote
               noise. Same code path. Writes the _null.md and a JSON the real report merges.
"""
import argparse
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)
import dollar_read_study as drs   # noqa: E402  (load_utc, null_frame, cl_mean, split_of)

NY = drs.NY
SYMS = ["UDXUSD", "EURUSD", "GBPUSD", "NZDUSD", "EURGBP", "AUDNZD", "XAUUSD", "SPXUSD", "NSXUSD"]
KZ = ((3 * 60, 5 * 60, "london"), (7 * 60, 10 * 60, "ny"))   # [start, end) ET minutes
STEP = 5
import config  # noqa: E402
LB = config.SWING_LOOKBACK_STH              # 8: the lookback the engine's DXY gate passes (backtest.py ~3905)
NOW_SLACK_MIN = 2                          # first M1 bar starting at t may be up to 2 min late
END_MIN_MINUTE = 50                        # hour-end bar must be at :50 or later (data gaps)
RULES = ["dxy_hour", "dxy_m5_bos", "dxy_m15_bos", "cross_hour", "gold_hour", "index_hour", "vote"]
DIAG = ["pairs_hour"]
SPLITS = ("IS", "OOS", "2026")
MINLEFT = ((0, 15), (15, 30), (30, 45), (45, 60))
OUT = os.path.join(ROOT, "data", "dollar_hour_forecast_report.md")
NULL_OUT = os.path.join(ROOT, "data", "dollar_hour_forecast_null.md")
NULL_JSON = os.path.join(ROOT, "data", "dollar_hour_forecast_null.json")
DUMPS = {"IS": "mm_golden_is_{m}_p125_trades.csv", "OOS": "mm_golden_oos_{m}_p125_trades.csv"}


# ───────────────────────────── pure pieces ─────────────────────────────

def bos_series(h, l, c, lb=LB):
    """engine ict.bias.htf_bias evaluated on every bar as the LAST bar: +1 if close > max high
    of the prior lb bars, -1 if close < their min low, else 0. htf_bias needs lb+3 bars."""
    import numpy as np
    from numpy.lib.stride_tricks import sliding_window_view as sw
    n = len(c)
    out = np.zeros(n, dtype=int)
    if n < lb + 3:
        return out
    hh = sw(h[:-1], lb).max(axis=1)        # hh[k] = max h[k:k+lb] -> prior window of bar k+lb
    ll = sw(l[:-1], lb).min(axis=1)
    i = np.arange(lb, n)
    bull = c[i] > hh
    bear = c[i] < ll
    v = np.where(bull, 1, np.where(bear, -1, 0))
    v[i < lb + 2] = 0
    out[lb:] = v
    return out


def vote2(a, b):
    """Vote of two signs: same -> that sign, opposite -> 0, one zero -> the other."""
    import numpy as np
    s = np.sign(a) + np.sign(b)
    return np.sign(s).astype(int)


def majority(cols):
    import numpy as np
    return np.sign(np.sum(np.vstack(cols), axis=0)).astype(int)


def minutes_left(t_ns, h0_ns):
    return 60 - (t_ns - h0_ns) // 60_000_000_000


# ───────────────────────────── per-symbol reads ─────────────────────────────

class Sym:
    def __init__(self, df):
        self.idx = df.index.as_unit("ns").asi8
        self.o = df["o"].values
        self.c = df["c"].values
        self.n = len(self.idx)

    def hour_move(self, t, h0):
        """Relative move so far this hour from COMPLETED M1 bars only (label < t). 0 if none."""
        import numpy as np
        jl = np.searchsorted(self.idx, t, side="left") - 1          # last label < t
        jo = np.searchsorted(self.idx, h0, side="left")             # first label >= h0
        ok = (jl >= 0) & (jo < self.n)
        jl_c = np.clip(jl, 0, self.n - 1)
        jo_c = np.clip(jo, 0, self.n - 1)
        ok &= (self.idx[jl_c] >= h0) & (self.idx[jo_c] < t) & (jo_c <= jl_c)
        mv = np.where(ok, (self.c[jl_c] - self.o[jo_c]) / self.o[jo_c], 0.0)
        return mv, ok


def tf_frame(df, rule):
    """Resample, compute BOS per bar; return (labels_ns, done_ns, bos)."""
    import pandas as pd
    agg = {"o": "first", "h": "max", "l": "min", "c": "last"}
    b = df.resample(rule).agg(agg).dropna()
    bos = bos_series(b["h"].values, b["l"].values, b["c"].values)
    bi = b.index.as_unit("ns")
    lab = bi.asi8
    done = (bi + pd.Timedelta(rule)).asi8
    return lab, done, bos


def asof_done(done, vals, t):
    """Value of the last bar COMPLETE at or before t (0 if none)."""
    import numpy as np
    p = np.searchsorted(done, t, side="right") - 1
    return np.where(p >= 0, vals[np.clip(p, 0, len(vals) - 1)], 0)


def at_label(lab, vals, h0):
    """Value of the bar whose label == h0 (the FORMING bar, full window = leaky); 0 if absent."""
    import numpy as np
    p = np.searchsorted(lab, h0, side="left")
    pc = np.clip(p, 0, len(lab) - 1)
    return np.where((p < len(lab)) & (lab[pc] == h0), vals[pc], 0)


# ───────────────────────────── grid + outcome ─────────────────────────────

def grid(dxy_df):
    """Decision times (UTC ns) for every weekday ET date in the DXY data."""
    import numpy as np
    import pandas as pd
    et = dxy_df.index.tz_convert(NY)
    dates = pd.DatetimeIndex(np.unique(et.normalize().tz_localize(None)))
    dates = dates[dates.day_of_week < 5]
    offs = []
    for a, b, _ in KZ:
        offs += list(range(a, b, STEP))
    offs = np.array(offs, dtype="int64")
    naive = (dates.values.astype("datetime64[m]")[:, None] + offs[None, :].astype("timedelta64[m]")).ravel()
    t = pd.DatetimeIndex(naive).tz_localize(NY, ambiguous="NaT", nonexistent="NaT").dropna().tz_convert("UTC")
    return t


def outcome(S, t, h0):
    """(y, now_ok): sign(close of last M1 bar of the hour - open of first M1 bar at/after t)."""
    import numpy as np
    jn = np.searchsorted(S.idx, t, side="left")
    jnc = np.clip(jn, 0, S.n - 1)
    ok = (jn < S.n) & (S.idx[jnc] <= t + NOW_SLACK_MIN * 60_000_000_000)
    he = h0 + 3_600_000_000_000
    je = np.searchsorted(S.idx, he, side="left") - 1
    jec = np.clip(je, 0, S.n - 1)
    ok &= (je > jn) & (S.idx[jec] >= h0 + END_MIN_MINUTE * 60_000_000_000) & (S.idx[jec] < he)
    y = np.where(ok, np.sign(S.c[jec] - S.o[jnc]), 0).astype(int)
    # trap demo: same outcome measured from the LAST CLOSED M1 close (the broken "now")
    jl = np.clip(jn - 1, 0, S.n - 1)
    y_bad = np.where(ok, np.sign(S.c[jec] - S.c[jl]), 0).astype(int)
    last_bar = np.where(ok & (jn >= 1), np.sign(S.c[jl] - S.o[jl]), 0).astype(int)
    return y, ok, y_bad, last_bar


# ───────────────────────────── build all decisions ─────────────────────────────

def build(frames):
    import numpy as np
    dxy = frames["UDXUSD"]
    T = grid(dxy).as_unit("ns")
    t = T.asi8
    h0 = T.floor("60min").as_unit("ns").asi8
    S = {s: Sym(frames[s]) for s in frames}
    y, ok, y_bad, last_bar = outcome(S["UDXUSD"], t, h0)
    cov = {}
    mv = {}
    for s in SYMS:
        if s in S:
            m, okm = S[s].hour_move(t, h0)
        else:
            m, okm = np.zeros(len(t)), np.zeros(len(t), dtype=bool)
        mv[s] = m
        cov[s] = okm
    pred = {}
    pred["dxy_hour"] = np.sign(mv["UDXUSD"]).astype(int)
    lab5, done5, b5 = tf_frame(dxy, "5min")
    lab15, done15, b15 = tf_frame(dxy, "15min")
    lab60, done60, b60 = tf_frame(dxy, "60min")
    pred["dxy_m5_bos"] = asof_done(done5, b5, t).astype(int)
    pred["dxy_m15_bos"] = asof_done(done15, b15, t).astype(int)
    pred["cross_hour"] = vote2(mv["EURGBP"], mv["AUDNZD"])
    pred["gold_hour"] = -np.sign(mv["XAUUSD"]).astype(int)
    pred["index_hour"] = -np.sign(mv["SPXUSD"] + mv["NSXUSD"]).astype(int)
    pred["vote"] = majority([pred[r] for r in RULES[:-1]])
    pred["pairs_hour"] = -np.sign(mv["EURUSD"] + mv["GBPUSD"] + mv["NZDUSD"]).astype(int)
    leaky = at_label(lab60, b60, h0).astype(int)        # forming H1 candle, full-hour close
    honest = asof_done(done60, b60, t).astype(int)      # last CLOSED H1 candle
    et = T.tz_convert(NY)
    years = np.asarray(et.year)
    D = dict(t=t, h0=h0, y=y, ok=ok, y_bad=y_bad, last_bar=last_bar, pred=pred, cov=cov,
             leaky=leaky, honest=honest,
             split=np.array([drs.split_of(v) for v in years]),
             sess=np.where(np.asarray(et.hour) < 6, "london", "ny"),
             mleft=minutes_left(t, h0),
             day=np.asarray(et.date, dtype="datetime64[D]").astype("int64"))
    return D


# ───────────────────────────── scoring ─────────────────────────────

def score(p, y, day, m=None):
    import numpy as np
    k = (p != 0) & (y != 0)
    if m is not None:
        k &= m
    n = int(k.sum())
    if n < 30:
        return None
    hit = (p[k] == y[k]).astype(float) * 100
    mu, se = drs.cl_mean(hit, day[k])
    return dict(n=n, days=int(len(np.unique(day[k]))), hit=float(mu), se=float(se))


def fmt(c):
    if c is None:
        return "—"
    return f"{c['n']}/{c['days']}d {c['hit']:.1f}% ({c['hit']-50:+.1f}±{c['se']:.1f})"


def short(c):
    if c is None:
        return "—"
    return f"{c['hit']:.1f} ({c['hit']-50:+.1f}±{c['se']:.1f})"


def cells(D):
    """All scored cells: {rule: {split: cell, 'ALL': cell}} for the main outcome."""
    out = {}
    for r in RULES + DIAG:
        out[r] = {s: score(D["pred"][r], D["y"], D["day"], D["split"] == s) for s in SPLITS}
        out[r]["ALL"] = score(D["pred"][r], D["y"], D["day"])
    return out


def verdict(rule, C, NA, NB):
    """Spec §8 pass rule. Returns (passes, side, reason)."""
    cs = [C[rule][s] for s in SPLITS]
    if any(c is None for c in cs):
        return False, "", "missing period"
    lifts = [c["hit"] - 50 for c in cs]
    sides = {1 if v > 0 else -1 for v in lifts}
    if len(sides) != 1:
        return False, "", "sign flips"
    side = sides.pop()
    if not all(abs(c["hit"] - 50) > 2 * c["se"] for c in cs):
        return False, "FOLLOW" if side > 0 else "FADE", "< 2 SE in a period"
    if not all((c["hit"] >= 55) if side > 0 else (c["hit"] <= 45) for c in cs):
        return False, "FOLLOW" if side > 0 else "FADE", "misses the 55% bar"
    for nm, N in (("Null A", NA), ("Null B", NB)):
        nc = (N or {}).get(rule, {}).get("ALL") if N else None
        if nc is None:
            return False, "", f"{nm} missing"
        if abs(nc["hit"] - 50) > 2 * nc["se"]:
            return False, "", f"{nm} not ~50%"
    return True, "FOLLOW" if side > 0 else "FADE", "PASS"


# ───────────────────────────── report ─────────────────────────────

def coverage_lines(D):
    import numpy as np
    L = ["## Coverage", "",
         "| period | days | decisions | with outcome | " + " | ".join(f"{s} move ok%" for s in SYMS) + " |",
         "|---|---|---|---|" + "---|" * len(SYMS)]
    for s in SPLITS:
        m = D["split"] == s
        n = int(m.sum())
        if n == 0:
            L.append(f"| {s} | 0 | 0 | 0 |" + " — |" * len(SYMS))
            continue
        row = [s, str(len(np.unique(D["day"][m]))), str(n), str(int((D["ok"] & m & (D["y"] != 0)).sum()))]
        for sy in SYMS:
            row.append(f"{100 * D['cov'][sy][m].mean():.0f}")
        L.append("| " + " | ".join(row) + " |")
    L += ["", "'move ok%' = share of decisions where that symbol had a completed M1 bar this hour "
          "(0% = symbol missing -> its rule makes no call). The :00 decisions never have one (5 of 60 "
          "per day), so ~92% is full coverage.", ""]
    return L


def report(D, title, NA=None, NB=None, stage0=None, is_null=False):
    import numpy as np
    C = cells(D)
    L = [f"# {title}", "",
         "Outcome: sign(DXY at the END of the current H1 candle − DXY NOW), now = open of the first M1 "
         "bar starting at t. Coin = 50% for ANY rule. Cell = n decisions/days, hit% (lift vs 50 ± "
         "DAY-CLUSTERED SE). A rule passes (spec §8) only with the same sign beyond 2 SE in IS, OOS AND "
         "2026, hit >= 55% (FOLLOW) or <= 45% (FADE) every period, and Null A / Null B pooled within 2 SE.",
         ""]
    L += coverage_lines(D)
    hdr = "| rule | IS | OOS | 2026 |"
    sep = "|---|---|---|---|"
    if not is_null:
        hdr += " Null A (pooled) | Null B (pooled) | verdict |"
        sep += "---|---|---|"
    L += ["## Stage 1 — main outcome (pass cells)", "", hdr, sep]
    for r in RULES:
        row = [r] + [fmt(C[r][s]) for s in SPLITS]
        if not is_null:
            row.append(fmt((NA or {}).get(r, {}).get("ALL")))
            row.append(fmt((NB or {}).get(r, {}).get("ALL")))
            ok, side, why = verdict(r, C, NA, NB)
            row.append(f"**{side} PASS**" if ok else f"fail — {why}")
        L.append("| " + " | ".join(row) + " |")
    L += ["", "Reported only (not a pass cell; trap 1 — the pairs ARE most of DXY):", "", hdr, sep]
    for r in DIAG:
        row = [r] + [fmt(C[r][s]) for s in SPLITS]
        if not is_null:
            row += [fmt((NA or {}).get(r, {}).get("ALL")), fmt((NB or {}).get(r, {}).get("ALL")), "—"]
        L.append("| " + " | ".join(row) + " |")
    if not is_null:
        npass = sum(verdict(r, C, NA, NB)[0] for r in RULES)
        L += ["", f"**Stage 1 verdict: {npass} of {len(RULES)} rules pass.**"
              + (" Stage 2 (engine) is warranted." if npass else " No honest forecast of the dollar hour "
                 "found; Stage 2 is not run."), ""]

    # bounce-trap demonstration (spec §5.3)
    L += ["## Bounce-trap check (diagnostic, not a pass cell)", "",
          "Rule = fade the last completed M1 candle. Scored against the hour close measured from the "
          "LAST CLOSED M1 close (the broken 'now') vs from the OPEN of the next minute (the study's 'now'). "
          "With bid-quote noise the broken version reads above 50% on noise alone; the fixed one must read ~50%.",
          "", "| 'now' = | IS | OOS | 2026 | ALL |", "|---|---|---|---|---|"]
    fade = -D["last_bar"]
    for nm, yy in (("last close (broken)", D["y_bad"]), ("next open (used)", D["y"])):
        row = [nm] + [short(score(fade, yy, D["day"], D["split"] == s)) for s in SPLITS]
        row.append(short(score(fade, yy, D["day"])))
        L.append("| " + " | ".join(row) + " |")
    L.append("")

    # secondary outcome
    L += ["## Secondary outcome (descriptive) — does the rule call the H1 candle's own htf_bias break?", "",
          "Scored only where the CURRENT H1 candle's full-hour close breaks the prior 8 H1 bars "
          "(the leaky gate's +1/-1, lookback 8). Not 50% on a random walk — compare with the null.", "",
          "| rule | IS | OOS | 2026 | share of decisions with a break |", "|---|---|---|---|---|"]
    lk = D["leaky"]
    for r in RULES:
        row = [r] + [short(score(D["pred"][r], lk, D["day"], D["split"] == s)) for s in SPLITS]
        row.append(f"{100 * (lk != 0).mean():.1f}%")
        L.append("| " + " | ".join(row) + " |")
    L.append("")

    # splits
    L += ["## Splits (read only for a rule that passes) — minutes left in the hour and session", "",
          "| rule | split | " + " | ".join(f"{a}-{b} min left" for a, b in MINLEFT) + " | london | ny |",
          "|---|---|" + "---|" * (len(MINLEFT) + 2)]
    for r in RULES:
        for s in SPLITS:
            m = D["split"] == s
            row = [r, s]
            for a, b in MINLEFT:
                mm = m & (D["mleft"] > a) & (D["mleft"] <= b)
                row.append(short(score(D["pred"][r], D["y"], D["day"], mm)))
            for ses in ("london", "ny"):
                row.append(short(score(D["pred"][r], D["y"], D["day"], m & (D["sess"] == ses))))
            L.append("| " + " | ".join(row) + " |")
    L.append("")

    # Stage 0 (2): leaky / honest DXY H1 read accuracy on the grid
    L += ["## Stage 0 — the accuracy bar", "",
          "### (2) The engine's DXY H1 read as a forecast of THIS target (grid)", "",
          "leaky = htf_bias on the H1 candle containing t, full-hour close (what the leaky engine used); "
          "honest = htf_bias on the last CLOSED H1 candle. Hit = read's sign = sign(hour close − now), "
          "on decisions where the read is non-zero.", "",
          "| read | IS | OOS | 2026 | ALL | share non-zero |", "|---|---|---|---|---|---|"]
    for nm in ("leaky", "honest"):
        v = D[nm]
        row = [nm] + [fmt(score(v, D["y"], D["day"], D["split"] == s)) for s in SPLITS]
        row += [fmt(score(v, D["y"], D["day"])), f"{100 * (v != 0).mean():.1f}%"]
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    if stage0:
        L += stage0
    return "\n".join(L), C


# ───────────────────────────── Stage 0 from the P125 dumps ─────────────────────────────

def _legs(path):
    import pandas as pd
    d = pd.read_csv(path)
    d["opened_at"] = pd.to_datetime(d["opened_at"], utc=True)
    return d


def _stats(d):
    import numpy as np
    if len(d) == 0:
        return "—"
    w = (d["pnl"] > 0).mean() * 100
    gp, gl = d.loc[d["pnl"] > 0, "pnl"].sum(), -d.loc[d["pnl"] < 0, "pnl"].sum()
    pf = gp / gl if gl > 0 else float("inf")
    risk = (d["entry"] - d["init_stop"]).abs()
    r = np.where(risk > 0, (d["exit"] - d["entry"]) * d["direction"] / risk, np.nan)
    return f"{len(d)} / {w:.1f}% / {pf:.2f} / {np.nanmean(r):+.2f}"


def stage0_dumps(dxy_df, grid_acc):
    """Spec §2 (1) and (3) from data/mm_golden_{is,oos}_mleaky_p125_trades.csv."""
    import numpy as np
    lab60, done60, b60 = tf_frame(dxy_df, "60min")
    L = ["### (1) Leaky vs honest DXY H1 read at every first-leg entry (P125 `mleaky` dumps)", "",
         "Both reads recomputed from UDXUSD at the leg's `opened_at` (the engine's decision bar). "
         "Cell = first legs n / WR / PF / avg R. 'differ' = the two reads are not equal. "
         "'with' = the read's dollar direction matches the trade (pair short = dollar up).", "",
         "| period | all first legs | reads agree | reads differ | leaky read WITH trade | honest read WITH trade | "
         "honest read 0 / against |", "|---|---|---|---|---|---|---|"]
    wr = {}
    for s, pat in DUMPS.items():
        p = os.path.join(ROOT, "data", pat.format(m="mleaky"))
        if not os.path.exists(p):
            L.append(f"| {s} | dump missing ({os.path.basename(p)}) | | | | | |")
            continue
        d = _legs(p)
        allw = (d["pnl"] > 0).mean() * 100
        d1 = d[d["leg_idx"] == 1].copy()
        t = d1["opened_at"].values.astype("datetime64[ns]").astype("int64")
        h0 = d1["opened_at"].dt.floor("60min").values.astype("datetime64[ns]").astype("int64")
        d1["lk"] = at_label(lab60, b60, h0)
        d1["hn"] = asof_done(done60, b60, t)
        dol = -d1["direction"]
        L.append("| " + " | ".join([
            s, _stats(d1), _stats(d1[d1.lk == d1.hn]), _stats(d1[d1.lk != d1.hn]),
            _stats(d1[d1.lk == dol]), _stats(d1[d1.hn == dol]), _stats(d1[d1.hn != dol])]) + " |")
        L.append(f"| {s} read mix | leaky +1/0/-1: {(d1.lk>0).sum()}/{(d1.lk==0).sum()}/{(d1.lk<0).sum()} | "
                 f"honest +1/0/-1: {(d1.hn>0).sum()}/{(d1.hn==0).sum()}/{(d1.hn<0).sum()} | "
                 f"differ {100*(d1.lk!=d1.hn).mean():.0f}% | | | |")
        ph = os.path.join(ROOT, "data", pat.format(m="mdxyH1"))
        wr_h = (_legs(ph)["pnl"] > 0).mean() * 100 if os.path.exists(ph) else None
        wr[s] = (allw, wr_h)
    L.append("")
    # (3) mapping
    L += ["### (3) Rough accuracy -> win-rate mapping (spec §2.3; a straight line, not a model)", "",
          "WR (all legs) of `mleaky` (leaky DXY H1) and `mdxyH1` (honest DXY H1) from the P125 dumps, against "
          "the grid accuracy of each read in (2) over the same period. Linear through the two points.", "",
          "| period | leaky acc / WR | honest acc / WR | WR per +1pp accuracy | WR at 55% acc | acc needed for 42% WR |",
          "|---|---|---|---|---|---|"]
    for s in ("IS", "OOS"):
        if s not in wr or wr[s][1] is None or s not in grid_acc:
            L.append(f"| {s} | — | — | — | — | — |")
            continue
        (wl, wh), (al, ah) = wr[s], grid_acc[s]
        if al is None or ah is None or al == ah:
            L.append(f"| {s} | — | — | — | — | — |")
            continue
        slope = (wl - wh) / (al - ah)
        w55 = wh + slope * (55 - ah)
        need = ah + (42 - wh) / slope if slope else float("nan")
        L.append(f"| {s} | {al:.1f}% / {wl:.1f}% | {ah:.1f}% / {wh:.1f}% | {slope:+.2f} | {w55:.1f}% | {need:.1f}% |")
    L += ["", "Caveat: the leaky read is non-zero on only a share of decisions and the engine gates on more than "
          "the DXY H1 read; this line is the spec's rough bar, not a prediction of Stage 2.", ""]
    return L


# ───────────────────────────── nulls ─────────────────────────────

NULL_BASE = {"UDXUSD": 100.0, "EURUSD": 1.10, "GBPUSD": 1.27, "NZDUSD": 0.62, "EURGBP": 0.86,
             "AUDNZD": 1.08, "XAUUSD": 1900.0, "SPXUSD": 4500.0, "NSXUSD": 15000.0}
NULL_DAYS = 1741        # 2022-01-03 .. ~2026-10-09 so all three periods exist


def null_frames(kind, off=0):
    """off = 0 is the pre-registered null the verdict uses; other offsets only feed the
    seed-robustness table (so one unlucky seed is visible as luck, not hidden by re-seeding)."""
    import numpy as np
    import pandas as pd
    if kind == "A":
        return {s: drs.null_frame(300 + off + i, NULL_BASE[s], NULL_BASE[s] * 0.00004, days=NULL_DAYS)
                for i, s in enumerate(SYMS)}
    # B: correlated by construction + bid-quote noise
    rng = np.random.default_rng(7 + off)
    idx = pd.date_range("2022-01-03", periods=NULL_DAYS * 1440, freq="1min", tz="UTC")
    idx = idx[idx.day_of_week < 5]
    n = len(idx)
    sig = 0.00004
    zd = rng.normal(0, sig, n)
    beta = {"UDXUSD": 1.0, "EURUSD": -0.9, "GBPUSD": -0.7, "NZDUSD": -0.6, "EURGBP": -0.2,
            "AUDNZD": 0.1, "XAUUSD": -0.4, "SPXUSD": -0.2, "NSXUSD": -0.25}
    idio = {"UDXUSD": 0.0, "EURUSD": 0.4, "GBPUSD": 0.7, "NZDUSD": 0.8, "EURGBP": 0.6,
            "AUDNZD": 0.6, "XAUUSD": 1.5, "SPXUSD": 1.5, "NSXUSD": 2.0}
    out = {}
    for s in SYMS:
        r = beta[s] * zd + rng.normal(0, sig * idio[s], n) if idio[s] else zd.copy()
        lat = NULL_BASE[s] * np.exp(np.r_[0.0, np.cumsum(r)])          # latent at minute boundaries
        noise = 0.75 * np.std(r) * NULL_BASE[s]          # bid-quote noise ~ 0.75 x 1-min move
        e = lambda: rng.normal(0, noise, n)
        o = lat[:-1] + e()                                              # first tick of the minute
        c = lat[1:] + e()                                               # last tick of the minute
        w = np.abs(rng.normal(0, noise, n))
        out[s] = pd.DataFrame({"o": o, "h": np.maximum(o, c) + w, "l": np.minimum(o, c) - w, "c": c},
                              index=idx)
        del lat, o, c, w
    return out


def cells_json(C):
    return {r: {k: v for k, v in d.items()} for r, d in C.items()}


def run_null(kinds):
    res = {}
    texts = []
    for k in kinds:
        fr = null_frames(k)
        D = build(fr)
        del fr
        txt, C = report(D, f"P126 NULL {k} — " + ("independent random walks" if k == "A" else
                        "DXY-correlated walks + bid-quote noise"), is_null=True)
        res[k] = cells_json(C)
        rob = [f"### Null {k} seed robustness (pooled lift / SE, z) — verdict uses seed offset 0 only", "",
               "| seed offset | " + " | ".join(RULES + DIAG) + " |", "|---|" + "---|" * len(RULES + DIAG)]
        for off in (0, 1000, 2000, 3000):
            if off:
                fr = null_frames(k, off)
                C2 = cells(build(fr))
                del fr
            else:
                C2 = C
            rob.append(f"| {off} | " + " | ".join(
                f"{(C2[r]['ALL']['hit']-50)/C2[r]['ALL']['se']:+.2f}" if C2[r]['ALL'] else "—"
                for r in RULES + DIAG) + " |")
        rob += ["", "A calibrated null gives z ~ N(0,1): about 1 in 20 cells beyond ±2 by chance.", ""]
        texts.append(txt + "\n\n" + "\n".join(rob))
        print(f"null {k} done", flush=True)
    return res, texts


# ───────────────────────────── selftest ─────────────────────────────

def selftest():
    import numpy as np
    import pandas as pd
    import config  # noqa: F401
    from ict.bias import htf_bias
    from collections import namedtuple
    Bar = namedtuple("Bar", "Open High Low Close")
    rng = np.random.default_rng(1)
    c = 1 + np.cumsum(rng.normal(0, 0.001, 400))
    h = c + np.abs(rng.normal(0, 0.0005, 400))
    l = c - np.abs(rng.normal(0, 0.0005, 400))
    b = bos_series(h, l, c)
    bars = [Bar(c[i], h[i], l[i], c[i]) for i in range(400)]
    for i in range(400):
        assert b[i] == htf_bias(bars[:i + 1], lookback=LB), (i, b[i])
    assert (b != 0).sum() > 10
    # vote / majority
    assert list(vote2(np.array([1, 1, -1, 0, 0]), np.array([1, -1, -1, 2, 0]))) == [1, 0, -1, 1, 0]
    assert list(majority([np.array([1, 1, 0]), np.array([1, -1, 0]), np.array([0, -1, 0])])) == [1, -1, 0]
    # hour_move uses only bars with label < t, and the open of the hour's first bar
    idx = pd.date_range("2024-03-05 13:00", periods=60, freq="1min", tz="UTC")
    o = np.arange(60, dtype=float) + 100
    df = pd.DataFrame({"o": o, "h": o + 0.5, "l": o - 0.5, "c": o + 0.25}, index=idx)
    S = Sym(df)
    h0 = np.array([idx[0].value])
    for k in (0, 1, 10, 55):
        t = np.array([idx[k].value])
        mv, ok = S.hour_move(t, h0)
        if k == 0:
            assert not ok[0] and mv[0] == 0
        else:
            assert ok[0] and abs(mv[0] - ((o[k - 1] + 0.25) - 100) / 100) < 1e-12
        df2 = df.copy()
        df2.iloc[k:, :] = 1e6                     # the bar at t and later must never be read
        mv2, _ = Sym(df2).hour_move(t, h0)
        assert mv2[0] == mv[0]
    # outcome: open of bar at t vs close of the :59 bar
    t = np.array([idx[10].value])
    y, ok, yb, lb_ = outcome(S, t, h0)
    assert ok[0] and y[0] == np.sign((o[59] + 0.25) - o[10])
    # forming vs closed H1 read helpers
    lab = np.array([0, 10, 20]); vals = np.array([1, -1, 1]); done = lab + 10
    assert at_label(lab, vals, np.array([10]))[0] == -1 and at_label(lab, vals, np.array([15]))[0] == 0
    assert asof_done(done, vals, np.array([19]))[0] == 1 and asof_done(done, vals, np.array([20]))[0] == -1
    # grid: 60 decisions per weekday, first 03:00 ET, last 09:55 ET
    g = grid(pd.DataFrame({"c": [1.0]}, index=pd.DatetimeIndex(["2024-07-03 12:00"], tz="UTC")))
    et = g.tz_convert(NY)
    assert len(g) == 60 and et[0].hour == 3 and et[0].minute == 0 and et[-1].hour == 9 and et[-1].minute == 55
    assert minutes_left(np.array([idx[10].value]), h0)[0] == 50
    # pass rule
    mk = lambda hit, se: dict(n=1000, days=200, hit=hit, se=se)
    good = {"x": {"IS": mk(57, 1), "OOS": mk(56, 1), "2026": mk(55.5, 2), "ALL": mk(56, 1)}}
    nul = {"x": {"ALL": mk(50.5, 1)}}
    assert verdict("x", good, nul, nul)[0]
    bad = {"x": dict(good["x"], OOS=mk(54, 1))}
    assert not verdict("x", bad, nul, nul)[0]
    flip = {"x": dict(good["x"], OOS=mk(44, 1))}
    assert verdict("x", flip, nul, nul)[2] == "sign flips"
    assert not verdict("x", good, {"x": {"ALL": mk(53, 1)}}, nul)[0]
    fade = {"x": {"IS": mk(43, 1), "OOS": mk(44, 1), "2026": mk(44.5, 0.2), "ALL": mk(44, 1)}}
    assert verdict("x", fade, nul, nul)[:2] == (True, "FADE")
    print("selftest ok")


# ───────────────────────────── main ─────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", nargs="?", const="both", choices=["A", "B", "both"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    if a.null:
        kinds = ["A", "B"] if a.null == "both" else [a.null]
        res, texts = run_null(kinds)
        out = a.out or NULL_OUT
        with open(out, "w") as f:
            f.write("\n\n".join(texts) + "\n")
        js = os.path.splitext(out)[0] + ".json"
        prev = {}
        if os.path.exists(js):
            with open(js) as f:
                prev = json.load(f)
        prev.update(res)
        with open(js, "w") as f:
            json.dump(prev, f)
        print("\n\n".join(texts))
        return
    frames = {}
    for s in SYMS:
        df = drs.load_utc(s)
        if df is None:
            print("missing", s, flush=True)
            continue
        frames[s] = df
        print(s, len(df), df.index[0], df.index[-1], flush=True)
    if "UDXUSD" not in frames:
        sys.exit("UDXUSD required")
    if not os.path.exists(NULL_JSON):
        print("null JSON missing -> running both nulls first", flush=True)
        res, texts = run_null(["A", "B"])
        with open(NULL_JSON, "w") as f:
            json.dump(res, f)
        with open(NULL_OUT, "w") as f:
            f.write("\n\n".join(texts) + "\n")
    with open(NULL_JSON) as f:
        nj = json.load(f)
    D = build(frames)
    missing = [s for s in SYMS if s not in frames]
    grid_acc = {}
    for s in ("IS", "OOS"):
        m = D["split"] == s
        la = score(D["leaky"], D["y"], D["day"], m)
        ho = score(D["honest"], D["y"], D["day"], m)
        grid_acc[s] = (la["hit"] if la else None, ho["hit"] if ho else None)
    st0 = stage0_dumps(frames["UDXUSD"], grid_acc)
    title = "P126 Stage 0 + Stage 1 — can the dollar's CURRENT hour be forecast honestly?"
    txt, _ = report(D, title, nj.get("A"), nj.get("B"), stage0=st0)
    if missing:
        txt = txt.replace("## Coverage", f"**Missing symbols: {', '.join(missing)}** (their rules make no call)\n\n## Coverage", 1)
    out = a.out or OUT
    with open(out, "w") as f:
        f.write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()

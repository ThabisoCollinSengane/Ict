"""P124 — can ICT session position predict whether price CLOSES up or down? (Polymarket-shaped)

Trader: "code a strategy that predicts whether price will close up or down based on where it is
in that session, using ICT concepts." A prediction-market up/down contract pays only on that.

Every 15 min from 03:00 to 11:45 ET (weekdays), EURUSD / GBPUSD / NZDUSD, using only M1 bars
that have already CLOSED. Windows: the NY DAY (00:00 -> 17:00 ET, the FX day close) and the
current clock HOUR.

TARGETS
  *_vs_now   does the window close ABOVE THE PRICE NOW?  On a random walk this is 50% for any
             rule — the honest test, and what a fairly priced contract leaves you to beat.
  *_vs_open  does the window close above its OPEN (how up/down contracts settle)? Mid-window,
             price already above the open makes 'up' likelier ON NOISE ALONE. Baseline B0 =
             sign(now - open) gets that for free and a live market price already contains it;
             a rule only adds something if it beats B0.

ICT RULES (+1 up / -1 down / 0 no call), all from bars before the decision time:
  open_side   price vs the 00:00 ET (midnight) open
  judas       Power of 3: the day already traded >= 5 pips through the midnight open one way
              and price is now back on the other side -> the other way
  asia_sweep  Asia range (19:00-24:00 ET the evening before): one side taken since 00:00 and
              price back inside -> the opposite way (both sides taken = no call)
  pd_sweep    the prior NY day's high/low taken today and price back inside -> the opposite way
  discount    price in the bottom 30% of today's range so far -> up, top 30% -> down
  vote        sign of judas + asia_sweep + pd_sweep + discount

Hit% ± DAY-CLUSTERED SE (the three pairs on one day are largely one dollar bet). Gate: lift
beyond 2 SE with the same sign in IS 2022-23, OOS 2024-25 AND 2026, and hit >= 52% (a 51c
contract plus fees). --null runs the same code on random walks: every vs_now lift must read ~0.
"""
import argparse
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dollar_read_study as drs   # noqa: E402

NY = drs.NY
PIP = drs.PIP
PAIRS = drs.PAIRS
DEC_START, DEC_END, STEP = 3 * 60, 12 * 60, 15
DAY_END = 17 * 60
JUDAS_PIPS = 5.0
RULES = ["open_side", "judas", "asia_sweep", "pd_sweep", "discount", "vote"]
TARGETS = ["day_vs_now", "hour_vs_now", "day_vs_open", "hour_vs_open"]
SPLITS = ("IS", "OOS", "2026")


# ─────────────────────────────── rules (pure) ───────────────────────────────

def rules(px, mid_open, day_hi, day_lo, asia_hi, asia_lo, pd_hi, pd_lo, pip=PIP):
    """ICT calls at one moment. day_hi/day_lo = range since 00:00 ET up to now."""
    def sgn(x):
        return 1 if x > 0 else (-1 if x < 0 else 0)
    r = {"open_side": sgn(px - mid_open)}
    j = 0
    if day_lo <= mid_open - JUDAS_PIPS * pip and px > mid_open:
        j += 1
    if day_hi >= mid_open + JUDAS_PIPS * pip and px < mid_open:
        j -= 1
    r["judas"] = sgn(j)
    a = 0
    if asia_hi is not None:
        took_lo, took_hi = day_lo < asia_lo, day_hi > asia_hi
        if took_lo and not took_hi and px > asia_lo:
            a = 1
        elif took_hi and not took_lo and px < asia_hi:
            a = -1
    r["asia_sweep"] = a
    p = 0
    if pd_hi is not None:
        took_lo, took_hi = day_lo < pd_lo, day_hi > pd_hi
        if took_lo and not took_hi and px > pd_lo:
            p = 1
        elif took_hi and not took_lo and px < pd_hi:
            p = -1
    r["pd_sweep"] = p
    rngw = day_hi - day_lo
    d = 0
    if rngw > 0:
        pos = (px - day_lo) / rngw
        d = 1 if pos <= 0.3 else (-1 if pos >= 0.7 else 0)
    r["discount"] = d
    r["vote"] = sgn(r["judas"] + r["asia_sweep"] + r["pd_sweep"] + r["discount"])
    return r


# ─────────────────────────────── events ───────────────────────────────

def build(df, pair):
    """One row per (decision time): rules + outcomes. df = M1 o/h/l/c, UTC index (bar open)."""
    import numpy as np
    et = df.index.tz_convert(NY)
    mod = (et.hour * 60 + et.minute).values
    dates = np.asarray(et.date, dtype="datetime64[D]")
    o, h, l, c = (df[k].values for k in ("o", "h", "l", "c"))
    rows = []
    udays = np.unique(dates)
    starts = np.searchsorted(dates, udays, side="left")
    ends = np.searchsorted(dates, udays, side="right")
    prev = None                                     # prior NY day (hi, lo)
    for di, d in enumerate(udays):
        s, e = starts[di], ends[di]
        m = mod[s:e]
        blk = np.nonzero(m < DAY_END)[0]
        if len(blk) < 600 or m[blk[0]] > 5:          # need a near-complete day from ~00:00
            prev = None
            continue
        bi = s + blk
        bm = m[blk]
        mid_open = o[bi[0]]
        day_close = c[bi[-1]]
        if mod[bi[-1]] < DAY_END - 5:
            prev = None
            continue
        rhi = np.maximum.accumulate(h[bi])
        rlo = np.minimum.accumulate(l[bi])
        # Asia: 19:00-24:00 ET the calendar evening before
        asia_hi = asia_lo = None
        if di > 0 and (d - udays[di - 1]).astype(int) == 1:
            ps, pe = starts[di - 1], ends[di - 1]
            am = (mod[ps:pe] >= 19 * 60)
            if am.sum() >= 120:
                asia_hi, asia_lo = h[ps:pe][am].max(), l[ps:pe][am].min()
        wd = int(((d.astype("datetime64[D]").view("int64") - 4) % 7))   # 0 = Monday
        if wd < 5:
            for tm in range(DEC_START, DEC_END, STEP):
                k = np.searchsorted(bm, tm) - 1           # last bar that OPENED before tm (closed by tm)
                if k < 0 or tm - bm[k] > 5:
                    continue
                px = c[bi[k]]
                hs = (tm // 60) * 60
                hb = np.nonzero((bm >= hs) & (bm < hs + 60))[0]
                if len(hb) < 50 or bm[hb[-1]] < hs + 55 or tm == hs:
                    h_open = h_close = None
                else:
                    h_open, h_close = o[bi[hb[0]]], c[bi[hb[-1]]]
                rr = rules(px, mid_open, rhi[k], rlo[k], asia_hi, asia_lo,
                           prev[0] if prev else None, prev[1] if prev else None)
                rows.append(dict(pair=pair, day=str(d), year=int(str(d)[:4]), tm=tm, px=px,
                                 mid_open=mid_open, day_close=day_close, h_open=h_open,
                                 h_close=h_close, **rr))
        prev = (h[bi].max(), l[bi].min())
    return rows


# ─────────────────────────────── scoring ───────────────────────────────

def split_of(y):
    return "IS" if y <= 2023 else ("OOS" if y <= 2025 else "2026")


def outcome_cols(t):
    """Signed outcome per row for each target (+ up / - down / 0 flat), and pips moved."""
    import numpy as np
    out = {}
    hc = t.h_close.astype(float).values
    ho = t.h_open.astype(float).values
    out["day_vs_now"] = (t.day_close - t.px).values / PIP
    out["hour_vs_now"] = (hc - t.px.values) / PIP
    out["day_vs_open"] = (t.day_close - t.mid_open).values / PIP
    out["hour_vs_open"] = (hc - ho) / PIP
    base = {"day_vs_open": np.sign(t.px.values - t.mid_open.values),
            "hour_vs_open": np.sign(t.px.values - ho)}
    return out, base


def score(calls, mv, days):
    import numpy as np
    ok = (calls != 0) & ~np.isnan(mv) & (mv != 0)
    if ok.sum() < 30:
        return None
    hit = (np.sign(mv[ok]) == calls[ok]).astype(float) * 100
    hm, hse = drs.cl_mean(hit, days[ok])
    pm, pse = drs.cl_mean(calls[ok] * mv[ok], days[ok])
    return dict(n=int(ok.sum()), hit=hm, se=hse, pips=pm, pse=pse)


def fmt(s):
    if s is None:
        return "—"
    return f"{s['hit']:.1f}% ({s['hit']-50:+.1f}±{s['se']:.1f}) / {s['pips']:+.1f}p / n {s['n']}"


def report(rows, title, out_path):
    import numpy as np
    import pandas as pd
    t = pd.DataFrame(rows)
    t["split"] = t.year.map(split_of)
    t["sess"] = np.where(t.tm < 6 * 60, "london", "ny")
    mv, base = outcome_cols(t)
    days = pd.to_datetime(t.day).values.astype("datetime64[D]").astype("int64")
    L = [f"# {title}", "",
         "Cell = hit% (lift vs 50 ± day-clustered SE) / avg pips in the called direction / n calls. "
         "Decisions every 15 min 03:00-11:45 ET, completed M1 bars only. Costs not deducted. "
         "**Gate:** lift beyond 2 SE, same sign, in IS, OOS AND 2026, and hit >= 52% "
         "(the bar a ~51c up/down contract plus fees sets).",
         f"Rows: {len(t)} decisions, {t.day.nunique()} days, pairs {', '.join(sorted(t.pair.unique()))}.", ""]
    passes, cells = [], 0
    for tg in TARGETS:
        L += [f"## {tg}", "", "| rule | " + " | ".join(SPLITS) + " |", "|---|---|---|---|"]
        rl = (["B0 (already above/below the open)"] if tg in base else []) + RULES
        for r in rl:
            calls_all = np.nan_to_num(base[tg]).astype(int) if r.startswith("B0") else t[r].values
            cs = []
            res = []
            for sp in SPLITS:
                m = (t.split == sp).values
                s = score(calls_all[m], mv[tg][m], days[m])
                res.append(s)
                cs.append(fmt(s))
            L.append(f"| {r} | " + " | ".join(cs) + " |")
            if not r.startswith("B0") and tg.endswith("_vs_now"):   # vs_open passes on noise
                cells += 1
                if all(s is not None for s in res):
                    sg = [np.sign(s["hit"] - 50) for s in res]
                    if len(set(sg)) == 1 and all(abs(s["hit"] - 50) > 2 * s["se"] for s in res) \
                            and all(s["hit"] >= 52 for s in res):
                        passes.append(f"{tg} / {r}")
        if tg in base:
            L += ["", f"For {tg} a rule only matters where it beats B0. Calls where the rule "
                  "DISAGREES with B0 (B0's free answer is wrong if the rule is right):", "",
                  "| rule | " + " | ".join(SPLITS) + " |", "|---|---|---|---|"]
            for r in RULES[1:]:
                cs = []
                for sp in SPLITS:
                    m = (t.split == sp).values & (t[r].values != 0) & (t[r].values != base[tg])
                    cs.append(fmt(score(t[r].values[m], mv[tg][m], days[m])))
                L.append(f"| {r} | " + " | ".join(cs) + " |")
        L.append("")
    L += ["## day_vs_now by session of the decision (vote rule)", "", "| session | " + " | ".join(SPLITS) + " |",
          "|---|---|---|---|"]
    for ss in ("london", "ny"):
        cs = []
        for sp in SPLITS:
            m = ((t.split == sp) & (t.sess == ss)).values
            cs.append(fmt(score(t["vote"].values[m], mv["day_vs_now"][m], days[m])))
        L.append(f"| {ss} | " + " | ".join(cs) + " |")
    L += ["", f"**Verdict:** {len(passes)} of {cells} rule x target cells pass the gate"
          + (f": {', '.join(passes)}." if passes else ".")
          + " Only *_vs_now cells are gated (the *_vs_open rules pass on random walks, see the null). At 2 SE in three periods with one sign, chance expects ~0 passes.",
          "", "Polymarket payout check: buying at 51c, EV per $1 = hit/0.51 - 1 "
          "(50% -> -2%, 52% -> +2%, 55% -> +7.8%).", ""]
    txt = "\n".join(L)
    with open(out_path, "w") as f:
        f.write(txt + "\n")
    print(txt)
    return passes


def selftest():
    o = 1.1000
    # Judas down through the open then back above -> up
    r = rules(1.1003, o, 1.1005, 1.0990, None, None, None, None)
    assert r["judas"] == 1 and r["open_side"] == 1
    r = rules(1.0995, o, 1.1010, 1.0994, None, None, None, None)
    assert r["judas"] == -1
    # Asia low taken, back inside -> up; both sides taken -> 0
    r = rules(1.1002, o, 1.1004, 1.0985, 1.1010, 1.0990, None, None)
    assert r["asia_sweep"] == 1
    r = rules(1.1002, o, 1.1012, 1.0985, 1.1010, 1.0990, None, None)
    assert r["asia_sweep"] == 0
    # PDH taken, back below -> down
    r = rules(1.1018, o, 1.1030, 1.0998, None, None, 1.1020, 1.0950)
    assert r["pd_sweep"] == -1
    # discount: bottom 30% of range -> up
    r = rules(1.0992, o, 1.1020, 1.0990, None, None, None, None)
    assert r["discount"] == 1
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--null", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "close_direction_report.md"))
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    rows = []
    if a.null:
        for i, p in enumerate(PAIRS):
            df = drs.null_frame(100 + i, 1.1, 0.00005, days=1760)
            df.index = df.index - __import__("pandas").Timedelta(hours=2)
            rows += build(df, p)
        report(rows, "P124 NULL (random walks) — every *_vs_now lift must read ~0", a.out)
        return
    for p in PAIRS:
        df = drs.load_utc(p)
        if df is None:
            print("no data", p)
            continue
        rows += build(df, p)
    report(rows, "P124 — does ICT session position predict the CLOSE direction? (EU/GU/NZ)", a.out)


if __name__ == "__main__":
    main()

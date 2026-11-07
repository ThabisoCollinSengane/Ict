"""P97 — does news and session decide whether a trade reaches its target?

Reads an engine trade dump (data/mm_golden_*_trades.csv or data/histdata/trades_dump.csv)
and data/news_events.csv. For every trade it records:

  news_in_trade   the highest-impact event released WHILE the trade was open
                  (Critical = NFP/CPI/FOMC per config.CRITICAL_NEWS_EVENTS, High, Medium, none)
  next_news_min   minutes from entry to the next event of any impact (same UTC day only)
  session         london / ny (the engine's `profile` column), entry hour in New York time

and splits target hits, full losses and profit factor by those labels, per half:
IS 2022-23, OOS 2024-25, and 2026 (this year) when the dump contains it.

Outcome labels: target = closed at the target; full loss = closed at a loss;
small/BE = closed at the stop at or above break-even (stop had been moved).

    python scripts/news_session_reach.py --dump data/mm_golden_full_p93_p94_trades.csv [--all]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config  # noqa: E402

CRIT = {e.upper() for e in config.CRITICAL_NEWS_EVENTS}
RANK = {"none": 0, "Medium": 1, "High": 2, "Critical": 3}


def load_news(path="data/news_events.csv"):
    n = pd.read_csv(path, comment="#")
    n["t"] = pd.to_datetime(n["utc_datetime"], utc=True)
    n["event_name"] = n["event_name"].fillna("")
    n["cls"] = np.where((n.impact == "High") & n.event_name.str.upper().isin(CRIT), "Critical",
                        n.impact)
    return n.sort_values("t").reset_index(drop=True)


def label(trades, news):
    t0 = pd.to_datetime(trades["opened_at"], utc=True)
    t1 = pd.to_datetime(trades["closed_at"], utc=True)
    nt = news["t"].values
    inside, nxt = [], []
    for a, b in zip(t0, t1):
        lo, hi = np.searchsorted(nt, a.to_datetime64(), "left"), np.searchsorted(nt, b.to_datetime64(), "right")
        cls = news["cls"].iloc[lo:hi]
        inside.append(max(cls, key=lambda c: RANK[c]) if len(cls) else "none")
        if lo < len(news) and news["t"].iloc[lo].date() == a.date():
            nxt.append((news["t"].iloc[lo] - a).total_seconds() / 60)
        else:
            nxt.append(np.nan)
    out = trades.copy()
    out["news_in_trade"] = inside
    out["next_news_min"] = nxt
    out["et_hour"] = t0.dt.tz_convert("America/New_York").dt.hour
    out["half"] = np.select([t0.dt.year <= 2023, t0.dt.year <= 2025], ["IS", "OOS"], "2026")
    out["outcome"] = np.select([out.reason.eq("target"), out.pnl < 0], ["target", "full_loss"], "small/BE")
    out["next_bucket"] = pd.cut(out.next_news_min, [-1, 60, 180, 1e9],
                                labels=["<=60m", "60-180m", ">180m"]).astype(object).fillna("none today")
    return out


def table(df, by, title):
    L = [f"### {title}", "", "| " + by + " | half | n | target % | full loss % | WR % | PF | med MFE pips |",
         "|---|---|---|---|---|---|---|---|"]
    for k in sorted(df[by].astype(str).unique()):
        for h in ("IS", "OOS", "2026"):
            g = df[(df[by].astype(str) == k) & (df.half == h)]
            if not len(g):
                continue
            w, l = g.pnl[g.pnl > 0].sum(), -g.pnl[g.pnl < 0].sum()
            pf = w / l if l else float("inf")
            L.append(f"| {k} | {h} | {len(g)} | {(g.outcome == 'target').mean()*100:.0f} | "
                     f"{(g.outcome == 'full_loss').mean()*100:.0f} | {(g.pnl > 0).mean()*100:.0f} | "
                     f"{pf:.2f} | {g.mfe_pips.median():.1f} |")
    return L + [""]


def report(df, name):
    L = [f"## {name} — {len(df)} trades", ""]
    L += table(df, "news_in_trade", "Highest-impact news released while the trade was open")
    L += table(df, "next_bucket", "Time from entry to the next news event (same UTC day)")
    L += table(df, "profile", "Session")
    L += table(df, "et_hour", "Entry hour (New York time)")
    return L


def selftest():
    news = pd.DataFrame({"utc_datetime": ["2024-01-05 13:30:00", "2024-01-05 15:00:00"],
                         "currency": ["USD", "USD"], "impact": ["High", "Medium"],
                         "event_name": ["NFP", ""]})
    news["t"] = pd.to_datetime(news.utc_datetime, utc=True)
    news["cls"] = np.where(news.event_name.str.upper().isin(CRIT) & (news.impact == "High"), "Critical",
                           news.impact)
    tr = pd.DataFrame({"opened_at": ["2024-01-05 13:00:00+00:00", "2024-01-05 14:00:00+00:00",
                                     "2024-01-05 16:00:00+00:00"],
                       "closed_at": ["2024-01-05 14:00:00+00:00", "2024-01-05 14:30:00+00:00",
                                     "2024-01-05 17:00:00+00:00"],
                       "reason": ["target", "stop", "stop"], "pnl": [10, -5, 1], "mfe_pips": [30, 2, 5]})
    o = label(tr, news)
    assert list(o.news_in_trade) == ["Critical", "none", "none"], o.news_in_trade.tolist()
    assert o.next_news_min.iloc[0] == 30 and o.next_news_min.iloc[1] == 60 and np.isnan(o.next_news_min.iloc[2])
    assert list(o.outcome) == ["target", "full_loss", "small/BE"]
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", nargs="+", default=[])
    ap.add_argument("--out", default="data/news_session_report.md")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    news = load_news()
    L = ["# P97 — news and session vs target reach", "",
         f"News calendar: {len(news)} events, {news.t.min():%Y-%m-%d} to {news.t.max():%Y-%m-%d} "
         f"(Critical {int((news.cls == 'Critical').sum())}, High {int((news.cls == 'High').sum())}, "
         f"Medium {int((news.cls == 'Medium').sum())}).", ""]
    for p in a.dump:
        d = pd.read_csv(p)
        d = label(d, news)
        nm = os.path.basename(p)
        L += report(d[d.entry_model == "mm_golden"], f"{nm} — MM trades")
        L += report(d[d.entry_model != "mm_golden"], f"{nm} — base trades")
    txt = "\n".join(L) + "\n"
    open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()

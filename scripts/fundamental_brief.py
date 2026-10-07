#!/usr/bin/env python3
"""Fundamental brief — a READER for the discretionary trader. Changes nothing.

    python scripts/fundamental_brief.py [--date YYYY-MM-DD] [--no-push]

WHAT THIS IS
------------
A story-builder. It answers "which pair has a fundamental story today, which
way, and when must I stay out" — then stops. It does NOT gate, size, or score
a trade, and nothing in the engine imports it. That is deliberate: the project
has nine measured-null variables on the analysis axis (P39/P40/P47/P48/P65/
P66/P68b/P69/P74), every one of which was trying to vote INSIDE the engine. A
reader cannot regress the 736-trade baseline because it has no path to it.

WHAT IT IS NOT
--------------
Not validated. No IS/OOS test exists for any of this, and none is implied.
Treat every line as context for your own judgement, not as a signal.

THE THREE INPUTS
----------------
  data/news_events.csv   calendar          (already in the repo)
  data/cb_stance.json    central-bank stance, MANUALLY maintained — rates move
                         4-8x a year, so a hand-kept file beats a scraper.
                         Must carry "verified": true or rate leans are withheld.
  data/bonds_src/DGS2.csv  US 2-year yield from FRED (optional)
                         python scripts/fetch_fred.py --series DGS2

THE RULE THAT MAKES IT SAFE
---------------------------
Fundamentals may only ever REMOVE a trade or choose BETWEEN two valid setups.
They may never create one. The price-action card still has to tick in full.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, time as dtime

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

import pytz                                     # noqa: E402
import config                                   # noqa: E402
from news_filter import NewsCalendar            # noqa: E402

UTC = pytz.utc
ET = pytz.timezone("America/New_York")

# Hawkish = currency-positive. Scores are ORDINAL only — the gap size is not a
# forecast, it just ranks one stance against another.
STANCE_SCORE = {
    "hiking": 2, "hawkish": 2, "hawkish_hold": 1, "neutral": 0,
    "dovish_hold": -1, "dovish": -2, "cutting": -2,
}
PAIR_CCY = {"EURUSD": "EUR", "GBPUSD": "GBP", "NZDUSD": "NZD"}
# P44 golden rule: short is GBPUSD, long is EURUSD.
GOLDEN_DIR = {"GBPUSD": -1, "EURUSD": +1}
STANCE_MAX_AGE_DAYS = 45                        # ~one full CB cycle


# ───────────────────────── pure logic (unit-tested) ─────────────────────────
def stance_lean(base_ccy: str, stance: dict) -> tuple[int, str]:
    """Rate-differential lean for a BASE/USD pair. +1 = long pair, -1 = short."""
    b = stance.get(base_ccy, {}).get("stance")
    u = stance.get("USD", {}).get("stance")
    if b not in STANCE_SCORE or u not in STANCE_SCORE:
        return 0, "stance missing"
    d = STANCE_SCORE[b] - STANCE_SCORE[u]
    why = f"{base_ccy} {b} vs USD {u}"
    if d == 0:
        return 0, why + " (level)"
    return (1 if d > 0 else -1), why


def yield_lean(series: list[tuple[str, float]], days: int = 5) -> tuple[int, str]:
    """US 2Y direction → dollar lean, expressed as a lean ON THE PAIRS.

    Yields up ⇒ dollar bid ⇒ every X/USD pair offered, so the pair lean is the
    NEGATIVE of the dollar move. Threshold 5bp filters noise.
    """
    if len(series) < 2:
        return 0, "no yield data"
    last_d, last_v = series[-1]
    ref = series[max(0, len(series) - 1 - days)]
    bp = (last_v - ref[1]) * 100.0
    arrow = "up" if bp > 0 else ("down" if bp < 0 else "flat")
    why = f"US2Y {last_v:.2f}% ({last_d}), {bp:+.0f}bp over {days}d → dollar {arrow}"
    if abs(bp) < 5.0:
        return 0, why + " (under 5bp, treated flat)"
    return (-1 if bp > 0 else 1), why


def combine(rate: int, yld: int) -> tuple[str, int]:
    """Agreement of the two FUNDAMENTAL reads with each other → the DRAW.

    Compares rate differential against US-2Y direction. It says NOTHING about
    what price is doing — see amd_reading(). The output is a DRAW: where price
    is likely to go once liquidity has been taken, which for a REVERSAL model is
    the direction we expect to ENTER, not the direction price is moving now.
    """
    if rate == 0 and yld == 0:
        return "NO READ", 0
    if rate != 0 and yld != 0:
        if rate == yld:
            return "AGREED", rate
        return "SPLIT", 0
    return "PARTIAL", (rate or yld)


def amd_reading(draw: int) -> list[str]:
    """How to read the draw against whatever price is actually doing.

    The correction that produced this (trader, 2026-10-06): fundamentals
    opposing the current move is NOT a stay-out signal. Price running against
    the draw is usually price going FOR LIQUIDITY first, and it then continues
    toward the draw. The opposition is the MANIPULATION leg — the setup
    forming — not a warning. Treating it as a veto (which the first version of
    this file did) throws away the most informative state the two layers
    produce together.
    """
    if draw == 0:
        return ["- No draw read today. Price action alone, as normal."]
    toward  = "SHORT" if draw < 0 else "LONG"
    against = "rallying" if draw < 0 else "selling off"
    withit  = "selling off" if draw < 0 else "rallying"
    return [
        f"- **Price {against} — AGAINST the draw** → likely the manipulation leg "
        f"taking liquidity. A reversal entry back toward the draw ({toward}) is the "
        "cleanest case this model has. **The opposition IS the setup.**",
        f"- **Price already {withit} — WITH the draw** → distribution may already be "
        "underway. A reversal entry here fades the draw, which is weaker; a "
        "continuation is breakout territory and late in the move.",
    ]


def golden_note(pair: str, lean: int) -> str:
    g = GOLDEN_DIR.get(pair)
    if g is None or lean == 0:
        return ""
    if g == lean:
        return "agrees with the golden rule"
    return "OPPOSES the golden rule — the algo will not take this side on this pair"


def overlaps_killzone(ev_et: datetime, kzs) -> str | None:
    """Name the killzone an ET event time falls inside, else None."""
    for name, start, end in kzs:
        sh, sm = (int(x) for x in start.split(":"))
        eh, em = (int(x) for x in end.split(":"))
        s, e = dtime(sh, sm), dtime(eh, em)
        t = ev_et.time()
        inside = (s <= t <= e) if s <= e else (t >= s or t <= e)   # wraps midnight
        if inside:
            return name
    return None


# ───────────────────────────── data loading ─────────────────────────────────
def _find(*cands):
    for c in cands:
        p = c if os.path.isabs(c) else os.path.join(_ROOT, c)
        if os.path.exists(p):
            return p
    return None


def load_stance():
    """Returns (stance_dict, warnings). Withholds leans unless verified=true."""
    p = _find("data/cb_stance.json")
    if not p:
        return {}, ["data/cb_stance.json MISSING — no rate leans. "
                    "Copy data/cb_stance.example.json, fill it in, set verified=true."]
    try:
        d = json.load(open(p))
    except Exception as exc:
        return {}, [f"cb_stance.json unreadable ({exc}) — no rate leans."]
    w = []
    if not d.get("verified"):
        w.append('cb_stance.json has "verified": false — RATE LEANS WITHHELD. '
                 "Check each bank's current rate yourself, then set it true. "
                 "I will not hand you a lean off numbers nobody confirmed.")
        return {}, w
    lv = d.get("last_verified")
    if lv:
        try:
            age = (datetime.utcnow().date() - datetime.strptime(lv, "%Y-%m-%d").date()).days
            if age > STANCE_MAX_AGE_DAYS:
                w.append(f"cb_stance.json last verified {age} days ago "
                         f"(> {STANCE_MAX_AGE_DAYS}) — re-check before trusting it.")
        except ValueError:
            w.append("last_verified is not YYYY-MM-DD — cannot age-check it.")
    else:
        w.append("cb_stance.json has no last_verified date.")
    return d.get("banks", {}), w


def load_us2y():
    p = _find("data/bonds_src/DGS2.csv", "data/bonds_src/dgs2.csv")
    if not p:
        return [], ("US 2Y absent — run: python scripts/fetch_fred.py --series DGS2 "
                    f"--start {datetime.utcnow().year - 1}-01-01")
    out = []
    for line in open(p).read().splitlines()[1:]:
        parts = line.split(",")
        if len(parts) < 2:
            continue
        try:
            out.append((parts[0].strip(), float(parts[1])))
        except ValueError:
            continue                              # "." = market holiday
    return out, None


def load_calendar():
    p = _find("data/news_events.csv", config.NEWS_CSV_PATH)
    cal = NewsCalendar()
    if not p:
        return cal, "news_events.csv MISSING — no calendar section."
    n = cal.load_csv(open(p).read())
    if not n:
        return cal, "news_events.csv parsed to 0 events."
    last = max(e[0] for e in cal.events)
    if last < UTC.localize(datetime.utcnow()):
        return cal, (f"calendar ENDS {last.date()} — it is in the past. "
                     "Events after that are invisible and nothing will be blocked.")
    return cal, None


# ───────────────────────── the institutional clock ──────────────────────────
# Published operating windows of the plumbing the money runs on, converted to
# ET for the given date (DST-aware per city). Sources: CLS settlement overview,
# FRB Fedwire hours, ECB reference-rate procedure, BoE RTGS timetable, WMR
# methodology, Krohn/Mueller/Whelan (J. Finance 2024) for the fix reversal.
CLOCK = [
    # (local tz,        hh, mm, label)
    ("Europe/Berlin",    7,  0, "CLS funding window OPENS (all 18 RTGS systems overlap)"),
    ("Europe/Berlin",    7,  0, "CLS Asia-Pacific pay-in window opens (NZD pays in)"),
    ("Europe/London",    6,  0, "CHAPS (sterling) opens"),
    ("Europe/London",    8,  0, "LONDON OPEN"),
    ("Europe/Berlin",    9,  0, "CLS settlement-completion target"),
    ("Europe/Berlin",   10,  0, "CLS early-closing pay-in deadline (Asia-Pacific window closes)"),
    ("Europe/Berlin",   12,  0, "CLS funding window CLOSES"),
    ("Europe/Berlin",   14, 15, "ECB FIX — dollar tends to be bid INTO it, offered AFTER"),
    ("America/New_York", 8, 30, "US data release slot (peak-volume half hour follows)"),
    ("America/New_York",10,  0, "NY OPTION CUT — expiring strikes can pin price"),
    ("Europe/London",   16,  0, "WMR LONDON FIX — dollar bid into it, offered after"),
    ("Europe/Berlin",   18,  0, "Euro T2 customer payments close"),
    ("Europe/London",   18,  0, "CHAPS closes"),
    ("America/New_York",17,  0, "NY CLOSE / value-date rollover — thinnest hour"),
]
FIX_NAMES = {"ECB FIX", "WMR LONDON FIX"}


def _et(day, tzname, hh, mm):
    tz = pytz.timezone(tzname)
    return tz.localize(datetime.combine(day, dtime(hh, mm))).astimezone(ET)


def eu_offset_hours(day) -> float:
    noon = UTC.localize(datetime.combine(day, dtime(12, 0)))
    b = noon.astimezone(pytz.timezone("Europe/Berlin")).utcoffset().total_seconds()
    n = noon.astimezone(ET).utcoffset().total_seconds()
    return (b - n) / 3600.0


def is_month_end(day) -> bool:
    """Last weekday of the month (holidays not modelled)."""
    nxt = day + timedelta(days=1)
    while nxt.weekday() >= 5:
        nxt += timedelta(days=1)
    return nxt.month != day.month


def clock_verdict():
    """The P78 verdict line from the measured report, if it has been run."""
    p = _find("data/fx_clock_report.md")
    if not p:
        return None
    for line in open(p, encoding="utf-8"):
        if line.startswith("**VERDICT:"):
            return line.strip().strip("*")
    return None


def clock_section(day, cal):
    L = ["## The institutional clock (ET)", ""]
    v = clock_verdict()
    if v:
        L += [f"_Measured on your 2022-25 data (P78): {v}_", ""]
    else:
        L += ["_⚠️ NOT YET MEASURED on your data. Run `python scripts/fx_clock_study.py`. "
              "Until it reads GREEN the fix lean below is published research on "
              "OTHER people's data, not a finding here._", ""]
    rows = sorted(((_et(day, tz, hh, mm), lab) for tz, hh, mm, lab in CLOCK),
                  key=lambda r: r[0])
    L += ["| ET | event | your windows |", "|---|---|---|"]
    for t, lab in rows:
        kz = overlaps_killzone(t, config.KILLZONES)
        noon = dtime(12, 0) <= t.time() < dtime(13, 0)
        where = f"inside **{kz}**" if kz else ("inside **noon block**" if noon else "—")
        L.append(f"| {t:%H:%M} | {lab} | {where} |")
    L.append("")

    off = eu_offset_hours(day)
    if abs(off - 6.0) > 1e-9:
        lon = _et(day, "Europe/London", 8, 0)
        ecb = _et(day, "Europe/Berlin", 14, 15)
        wmr = _et(day, "Europe/London", 16, 0)
        L += [f"> ⚠️ **Daylight-saving mismatch week** — Europe is {off:g}h ahead of "
              "New York, not 6. Every European event is **one hour LATER in ET**: "
              f"London opens {lon:%H:%M} ET (your London KZ catches the hour BEFORE "
              f"it plus its first hour), ECB fix {ecb:%H:%M} ET, and the WMR fix "
              f"{wmr:%H:%M} ET lands inside your noon block. P78 §3 tests whether "
              "the price effect follows the European clock on these days.", ""]
    if is_month_end(day):
        L += ["> **Month-end.** Fund managers re-hedge foreign equity at the last "
              "WMR fix of the month. Melvin & Prins: a foreign equity market that "
              "ROSE over the month predicts ITS currency WEAKENING into that fix. "
              "Check the month's equity performance yourself — this brief does not "
              "have equity data.", ""]
    d0 = UTC.localize(datetime.combine(day, dtime(0, 0)))
    if any(d0 <= e[0] < d0 + timedelta(days=1) and "FOMC" in (e[3] or "").upper()
           for e in cal.events):
        L += ["> **FOMC day.** Mueller, Tahbaz-Salehi & Vedolin (J. Finance 2017): "
              "short-dollar returns are significantly larger on scheduled FOMC days, "
              "more so under high uncertainty or easing. The decision itself is "
              "still a hard news block.", ""]
    L += ["_How it fits the draw: the morning dollar bid into the fixes is a common "
          "reason price runs AGAINST the draw first. After the ECB and WMR fixes that "
          "pressure lifts. A tilt of ~2bp/day on average — context for WHICH side has "
          "the wind, never a trigger._", ""]
    return L


# ──────────────────────────────── report ────────────────────────────────────
def build(day, stance, stance_w, us2y, us2y_w, cal, cal_w):
    L = [f"# Fundamental brief — {day:%a %d %b %Y}", "",
         "_A reader. It changes nothing in the algo and is not validated. "
         "Fundamentals may REMOVE a trade or choose BETWEEN two valid setups — "
         "never create one._", ""]

    warns = [w for w in ([*stance_w, us2y_w, cal_w]) if w]
    if warns:
        L += ["## ⚠️ Data warnings", ""] + [f"- {w}" for w in warns] + [""]

    yl, ywhy = yield_lean(us2y)
    L += ["## The dollar — the common driver", "",
          f"- {ywhy}", ""]
    if stance:
        us = stance.get("USD", {})
        if us:
            L.append(f"- Fed: **{us.get('stance','?')}** at {us.get('rate','?')}%"
                     + (f" · next {us['next_meeting']}" if us.get("next_meeting") else ""))
            L.append("")
    L += ["**Yields CONFIRM the dollar today — they do not predict tomorrow.** "
          "Measured 2022-26 (P79): on the same day US 5y/10y yields and the pairs move "
          "opposite (corr -0.25 to -0.40, every pair, both halves); the next day there "
          "is nothing, and this 5-day yield lean scored no edge at +1d or +5d. Use it "
          "like SMT — a cross-check on the move in front of you, not a forecast.", ""]

    # per pair
    L += ["## Per pair", ""]
    rows, detail = [], []
    for pair in config.PAIRS:
        ccy = PAIR_CCY.get(pair, "?")
        rl, rwhy = stance_lean(ccy, stance)
        label, net = combine(rl, yl)
        arrow = {1: "LONG", -1: "SHORT", 0: "—"}[net]
        rows.append((pair, label, arrow, golden_note(pair, net)))
        d = [f"### {pair} — {label}" + (f", lean {arrow}" if net else ""), "",
             f"- rates: {rwhy}" + (f" → {'long' if rl>0 else 'short'}" if rl else " → flat"),
             f"- dollar: {'long' if yl>0 else ('short' if yl<0 else 'flat')} the pair"]
        gn = golden_note(pair, net)
        if gn:
            d.append(f"- golden rule: **{gn}**")
        if pair == "NZDUSD":
            d.append("- ⚠️ NZD is driven more by RISK APPETITE, China data and dairy "
                     "than by rate differentials. Treat the rate lean here as the "
                     "weakest of the three, and check equity futures yourself.")
        d += ["", "_Read against price:_"] + amd_reading(net)
        detail += d + [""]

    L += ["| pair | story | lean | vs golden rule |", "|---|---|---|---|"]
    L += [f"| {p} | {lb} | {ar} | {gn or '—'} |" for p, lb, ar, gn in rows]
    L += [""] + detail

    L += clock_section(day, cal)

    # today's calendar + killzone collisions
    L += ["## Today's calendar", ""]
    d0 = UTC.localize(datetime.combine(day, dtime(0, 0)))
    todays = sorted((e for e in cal.events if d0 <= e[0] < d0 + timedelta(days=1)),
                    key=lambda e: e[0])
    if not todays:
        L += ["_No calendar events for this date._", ""]
    else:
        L += ["| ET | UTC | ccy | impact | event | killzone |", "|---|---|---|---|---|---|"]
        collisions = []
        for ev_dt, ccy, imp, name in todays:
            et = ev_dt.astimezone(ET)
            kz = overlaps_killzone(et, config.KILLZONES)
            if kz:
                collisions.append((et, ccy, imp, name or "-", kz))
            L.append(f"| {et:%H:%M} | {ev_dt:%H:%M} | {ccy} | {imp} | {name or '-'} "
                     f"| {'**' + kz + '**' if kz else '—'} |")
        L.append("")
        if collisions:
            L += ["### ⚠️ Events landing INSIDE a killzone", ""]
            for et, ccy, imp, name, kz in collisions:
                L.append(f"- **{et:%H:%M} ET — {ccy} {imp} {name}** sits inside "
                         f"**{kz}**. The engine's news filter blocks its own window; "
                         "for a manual entry, this is the one to stand aside for.")
            L.append("")
    if cal.is_nfp_week(UTC.localize(datetime.combine(day, dtime(12, 0)))):
        L += ["> **NFP week.** Mon/Tue score a narrative point (the only P47 factor "
              "that passed both splits: WR 62.5%/52.1% vs ~42% baseline). Wed-Fri "
              "are already gated as low-probability.", ""]

    # the card
    best = [r for r in rows if r[1] == "AGREED" and "OPPOSES" not in (r[3] or "")]
    L += ["## How to use this", ""]
    if best:
        L.append("**Clearest draw today: " +
                 ", ".join(f"{p} {ar}" for p, _, ar, _ in best) + ".** "
                 "That is where to LOOK — not permission to trade.")
    else:
        L.append("**No pair has an agreed draw today.** Normal and common. "
                 "Trade the price-action card as usual, or not at all.")
    L += ["",
          "**The draw is not a filter on today’s move.** It is where price is "
          "likely to go AFTER the liquidity is taken. This is a REVERSAL model, so "
          "the two things that should agree are the **draw** and the **trade "
          "direction** — never the draw and whatever price is doing right now. "
          "Price running the other way is the manipulation leg: that is the setup "
          "forming, not a warning.", "",
          "| what you see | how to read it |", "|---|---|",
          "| price running **against** the draw | the liquidity raid. A reversal "
          "entry back toward the draw is the cleanest case here. |",
          "| price running **with** the draw already | distribution may be underway "
          "— a reversal entry now fades the draw, and a continuation is late. |",
          "| **no** draw read | price action alone. Normal. |", "",
          "1. The draw says which pair and which way to **look**.",
          "2. Price action says **when** — full card, every box, as always.",
          "3. A draw with no setup is **not a trade**. Ever.",
          "4. The thing to question is a setup whose **trade direction** opposes an "
          "AGREED draw. A setup entered against the recent **move** is normal and "
          "expected — that is what this model does.",
          "5. **Two things lining up is not a signal.** Nine measured-null "
          "combinations in this project say so. Nothing here outranks the card.", "",
          "### ⚠️ The honest limit of this framing", "",
          "“Price went against the fundamentals, so it was going for liquidity "
          "first” can explain **every** outcome after the fact — including the ones "
          "where the fundamentals were simply wrong and price just kept going. A "
          "story that cannot be wrong predicts nothing.", "",
          "So record the state instead of feeling it. Per trade, log four fields:", "",
          "```",
          "draw_dir      LONG / SHORT / none      (from this brief, before the session)",
          "price_vs_draw against / with / flat    (what price was doing at entry)",
          "trade_dir     LONG / SHORT             (the side actually taken)",
          "outcome       R                        (not rands)",
          "```", "",
          "_After 50 trades that table answers it directly: did `against` + "
          "reversal-toward-the-draw actually beat `with`? Same test as everything "
          "else here — controls, and both halves._"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD (default: today UTC)")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()

    day = (datetime.strptime(a.date, "%Y-%m-%d").date() if a.date
           else datetime.utcnow().date())
    stance, sw = load_stance()
    us2y, yw = load_us2y()
    cal, cw = load_calendar()
    text = build(day, stance, sw, us2y, yw, cal, cw)
    print(text)
    out = os.path.join(_ROOT, "data", "fundamental_brief.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(text)
    if not a.no_push:
        def _git(*x):
            return subprocess.run(["git", *x], cwd=_ROOT, capture_output=True, text=True)
        _git("add", "-f", out)
        if _git("commit", "-q", "-m", f"Fundamental brief {day}").returncode == 0:
            _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
            if _git("push", "origin", "HEAD").returncode == 0:
                print("BRIEF PUSHED — Claude can read data/fundamental_brief.md")
        else:
            print("(brief unchanged — nothing pushed)")
    return 0


def _selftest():
    S = {"USD": {"stance": "hawkish_hold"}, "EUR": {"stance": "cutting"},
         "GBP": {"stance": "neutral"}, "NZD": {"stance": "hawkish"}}
    assert stance_lean("EUR", S)[0] == -1        # EUR cutting vs USD hawkish-hold
    assert stance_lean("GBP", S)[0] == -1
    assert stance_lean("NZD", S)[0] == +1
    assert stance_lean("JPY", S) == (0, "stance missing")
    assert stance_lean("USD", S)[0] == 0         # level against itself
    # yields: up ⇒ dollar bid ⇒ SHORT the pair
    up = [("2026-10-01", 4.00)] * 5 + [("2026-10-06", 4.20)]
    dn = [("2026-10-01", 4.20)] * 5 + [("2026-10-06", 4.00)]
    flat = [("2026-10-01", 4.00)] * 5 + [("2026-10-06", 4.02)]
    assert yield_lean(up)[0] == -1
    assert yield_lean(dn)[0] == +1
    assert yield_lean(flat)[0] == 0              # 2bp < 5bp threshold
    assert yield_lean([])[0] == 0
    assert combine(-1, -1) == ("AGREED", -1)
    assert combine(-1, +1) == ("SPLIT", 0)
    assert combine(0, -1) == ("PARTIAL", -1)
    assert combine(0, 0) == ("NO READ", 0)
    # amd_reading: opposition must read as the SETUP, never as a veto
    sh = " ".join(amd_reading(-1)); lo = " ".join(amd_reading(+1))
    assert "opposition IS the setup" in sh and "opposition IS the setup" in lo
    assert "rallying \u2014 AGAINST the draw" in sh      # draw short -> rally is the raid
    assert "selling off \u2014 AGAINST the draw" in lo   # draw long  -> selloff is the raid
    assert "SHORT" in sh and "LONG" in lo
    assert len(amd_reading(0)) == 1 and "alone" in amd_reading(0)[0]
    for d in (-1, 0, 1):
        assert not any("skip" in x.lower() or "stay out" in x.lower()
                       for x in amd_reading(d)), "amd_reading must not veto"
    assert "OPPOSES" in golden_note("EURUSD", -1)      # golden EURUSD is LONG only
    assert "agrees" in golden_note("EURUSD", +1)
    assert "OPPOSES" in golden_note("GBPUSD", +1)
    assert golden_note("NZDUSD", +1) == ""             # no golden rule for NZD
    assert golden_note("EURUSD", 0) == ""
    kz = [("London Open", "03:00", "05:00"), ("New York AM", "07:00", "10:00")]
    mk = lambda h, m: ET.localize(datetime(2026, 10, 6, h, m))
    assert overlaps_killzone(mk(3, 30), kz) == "London Open"
    assert overlaps_killzone(mk(8, 30), kz) == "New York AM"
    assert overlaps_killzone(mk(6, 0), kz) is None
    assert overlaps_killzone(mk(5, 0), kz) == "London Open"     # inclusive edge
    assert overlaps_killzone(mk(23, 0), [("Wrap", "22:00", "01:00")]) == "Wrap"
    assert overlaps_killzone(mk(0, 30), [("Wrap", "22:00", "01:00")]) == "Wrap"
    assert overlaps_killzone(mk(12, 0), [("Wrap", "22:00", "01:00")]) is None
    # clock
    from datetime import date
    assert eu_offset_hours(date(2026, 3, 2)) == 6.0
    assert eu_offset_hours(date(2026, 3, 10)) == 5.0       # US moved first
    assert eu_offset_hours(date(2026, 10, 30)) == 5.0      # EU moved back first
    assert _et(date(2026, 3, 2), "Europe/Berlin", 14, 15).strftime("%H:%M") == "08:15"
    assert _et(date(2026, 3, 10), "Europe/Berlin", 14, 15).strftime("%H:%M") == "09:15"
    assert _et(date(2026, 3, 10), "Europe/London", 16, 0).strftime("%H:%M") == "12:00"
    assert is_month_end(date(2026, 10, 30)) and not is_month_end(date(2026, 10, 29))
    assert is_month_end(date(2026, 5, 29))                  # Fri; 30/31 are weekend
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

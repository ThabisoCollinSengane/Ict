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
    L += ["All three pairs are X/USD, so this one read leans every pair at once. "
          "A dollar bid is a headwind for EURUSD/GBPUSD/NZDUSD longs.", ""]

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
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

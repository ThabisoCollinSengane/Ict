#!/usr/bin/env python3
"""What happens WHEN price arrives at an HTF gap — respect, or break through?

P68b measured whether price is DRAWN to an unfilled W/D/H4 gap and found nothing:
reached 90-95%, but an identical band the same distance away on the other side of
price is reached just as often. Arrival carries no directional information.

So arrival is not the question. This measures the REACTION, which is the trader's
actual model and is untested:

  * price arrives at the gap and is REJECTED  -> the gap held (respect)
  * price CLOSES THROUGH the far side         -> breakaway; the gap is now an
                                                 IFVG and should hold on retest
  * after either, does structure shift and does price run the other way?

None of this needs the gap to be a magnet — price gets there regardless. The
edge, if there is one, is in what the gap does once price is standing on it.

⚠️ EVERY rate here is reported against a CONTROL: the same classification run on
a mirror band (same width, same distance, opposite side of price). Price arriving
at ANY level reverses sometimes; only the LIFT over that baseline is evidence
that the gap did the work. P68b read GREEN on a random walk without this.

⚠️ The reaction is confirmed in a SHORT window and the excursion is measured FROM
the confirmation bar FORWARD, so the confirmation can never contain its own
outcome (the P65c / P66 / P68b failure, three times over).

Measurement only. Nothing here ships to the engine.

Run:  python scripts/fvg_reaction_study.py [--tfs W,D,240T]
      python scripts/fvg_reaction_study.py --selftest      # no data needed
"""
from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

REPORT = os.path.join(ROOT, "data", "fvg_reaction_report.md")
PAIRS = ("EURUSD", "GBPUSD", "NZDUSD")
IS_YEARS = (2022, 2023)
OOS_YEARS = (2024, 2025)
PIP = 0.0001                      # all three pairs are 4-decimal quotes
NO_PUSH = False


# ─────────────────────────── pure logic (unit-testable) ────────────────────────

def classify_reaction(o, h, l, c, touch, bottom, top, gdir, window):
    """RESPECT / BREAK / UNRESOLVED at a zone price has just traded into.

    Orientation: a BULLISH gap (gdir +1) sits BELOW price, so price arrives from
    ABOVE. Its NEAR side is `top` (the side price came from) and its FAR side is
    `bottom`.
      respect = a body closes back beyond the NEAR side  (rejected, went back)
      break   = a body closes beyond the FAR  side       (went straight through)
    A bearish gap is the mirror. Whichever happens FIRST is the verdict.

    "Body" means BOTH open and close are beyond the edge — the project's
    full-body-close inversion rule, not a wick poke.

    Returns (verdict, bar_index). The bar index is where the reaction CONFIRMED;
    every forward measurement starts there, never at `touch`.
    """
    end = min(touch + 1 + window, len(c))
    near, far = (top, bottom) if gdir > 0 else (bottom, top)
    for j in range(touch, end):
        lo_body, hi_body = min(o[j], c[j]), max(o[j], c[j])
        if gdir > 0:
            if lo_body > near:
                return "respect", j
            if hi_body < far:
                return "break", j
        else:
            if hi_body < near:
                return "respect", j
            if lo_body > far:
                return "break", j
    return "unresolved", -1


def excursion(h, l, start, ref, direction, horizon):
    """(favourable, adverse) pip excursion from `start`, measured FORWARD only.

    `direction` is where the reaction says price should go: +1 up, -1 down.
    Both legs are reported so a symmetric pair can be recognised as a coin flip
    rather than read as an edge (the P65/P66 lesson — medFav must beat medAdv).
    """
    end = min(start + 1 + horizon, len(h))
    if end <= start + 1:
        return None
    hi = max(h[start + 1:end])
    lo = min(l[start + 1:end])
    up, dn = (hi - ref) / PIP, (ref - lo) / PIP
    return (up, dn) if direction > 0 else (dn, up)


def retest_holds(o, h, l, c, start, bottom, top, gdir, horizon, window):
    """After a BREAK, does the inverted zone hold when price comes back to it?

    This is the trader's "if the FVG is broken it should be treated as an IFVG".
    A bullish gap broken DOWNWARD becomes resistance: price returning up into it
    should be rejected back DOWN. Returns True/False, or None if never retested.
    """
    brk = -1 if gdir > 0 else +1          # the direction the break went
    end = min(start + 1 + horizon, len(c))
    for j in range(start + 1, end):
        if l[j] <= top and h[j] >= bottom:          # retested the zone
            # held = a body closes back out on the break side, within `window`
            stop = min(j + 1 + window, len(c))
            for k in range(j, stop):
                lo_body, hi_body = min(o[k], c[k]), max(o[k], c[k])
                if brk < 0 and hi_body < bottom:
                    return True
                if brk > 0 and lo_body > top:
                    return True
                # failed: a body closed back through the far side instead
                if brk < 0 and lo_body > top:
                    return False
                if brk > 0 and hi_body < bottom:
                    return False
            return False
    return None


def reaction_direction(verdict, gdir):
    """Which way the reaction says price goes from the confirmation bar.

    A BULLISH gap (gdir +1) sits BELOW price and is bullish support: price
    retraces DOWN into it, and RESPECTING it means bouncing back UP — the gap's
    own direction. BREAKING it means carrying on DOWN, against it.

    Inlined, this mapping was wrong (respect read as -gdir) and would have
    inverted every favourable/adverse column in the report while every pure-logic
    test still passed — the project's recurring failure mode: the wiring is what
    goes wrong, so the wiring is what needs a test.
    """
    if verdict == "respect":
        return gdir
    if verdict == "break":
        return -gdir
    return 0


def control_zone(close, bottom, top, gdir):
    """The CONTROL: same width, same distance, OPPOSITE side of price.

    Returns (bottom, top, gdir) — and the gdir is INVERTED, which is the whole
    subtlety. A bullish gap sits below price and is approached DOWNWARD, so its
    near side is its top. The mirror sits ABOVE price and is approached UPWARD,
    so its near side is its BOTTOM. Handing the control the gap's own orientation
    scores its rejections as breaks and vice versa.

    That bug produced respect 58% vs control 23% — a +35pp "edge" — ON A RANDOM
    WALK, where the true lift must be zero. The null run is what exposed it.
    """
    return (2.0 * close - top, 2.0 * close - bottom, -gdir)


def summarise(rows):
    """rows = list of (verdict, fav, adv). Rates + median excursions."""
    n = len(rows)
    if not n:
        return {"n": 0}
    res = [r for r in rows if r[0] == "respect"]
    brk = [r for r in rows if r[0] == "break"]

    def _med(vals):
        s = sorted(v for v in vals if v is not None)
        return s[len(s) // 2] if s else None
    return {
        "n": n,
        "respect": 100.0 * len(res) / n,
        "break": 100.0 * len(brk) / n,
        "unres": 100.0 * sum(1 for r in rows if r[0] == "unresolved") / n,
        "res_fav": _med([r[1] for r in res]), "res_adv": _med([r[2] for r in res]),
        "brk_fav": _med([r[1] for r in brk]), "brk_adv": _med([r[2] for r in brk]),
    }


def verdict(gap_is, gap_oos, ctl_is, ctl_oos, min_lift=5.0):
    """GREEN needs the gap to out-respect its control in BOTH splits AND the
    respect branch to pay asymmetrically. A rate with no payoff is a coin flip
    with extra steps."""
    if not gap_is.get("n") or not gap_oos.get("n"):
        return "RED", "no reactions in one or both splits"
    if not ctl_is.get("n") or not ctl_oos.get("n"):
        return "RED", "control missing — result uninterpretable"
    la = gap_is["respect"] - ctl_is["respect"]
    lb = gap_oos["respect"] - ctl_oos["respect"]
    tag = (f"respect {gap_is['respect']:.0f}%/{gap_oos['respect']:.0f}% vs control "
           f"{ctl_is['respect']:.0f}%/{ctl_oos['respect']:.0f}% "
           f"(lift {la:+.1f}pp IS / {lb:+.1f}pp OOS)")
    if la < min_lift or lb < min_lift:
        return "RED", (f"{tag} — arriving at a gap is no more likely to reverse "
                       f"than arriving at any band the same distance away")
    pays = all(s["res_fav"] is not None and s["res_adv"] is not None
               and s["res_fav"] > s["res_adv"] for s in (gap_is, gap_oos))
    if not pays:
        return "YELLOW", f"{tag} — but the respect branch does not pay (medFav <= medAdv)"
    return "GREEN", f"{tag} — and the respect branch pays in both splits"


# ─────────────────────────────── data plumbing ────────────────────────────────

def run(tfs, react_win, horizon, retest_h):
    from triple_sweep_study import _load, _resample
    from fvg_draw_study import find_fvgs, first_touch

    out = {}
    for tf in tfs:
        B = {k: [] for k in ("gapIS", "gapOOS", "ctlIS", "ctlOOS")}
        # the retest rate needs its own baseline too: escaping a band you have
        # already broken is partly geometry, and reads 64-72% on a random walk
        holds = {"gapIS": [], "gapOOS": [], "ctlIS": [], "ctlOOS": []}
        for pair in PAIRS:
            m1 = _load(pair)
            if m1 is None:
                continue
            bars = _resample(m1, tf)
            o = bars["o"].to_numpy(); h = bars["h"].to_numpy()
            l = bars["l"].to_numpy(); c = bars["c"].to_numpy()
            years = bars.index.year.to_numpy()
            per_day = {"W": 1 / 5.0, "D": 1.0, "240T": 6.0}.get(tf, 6.0)
            lim = int(30 * per_day)

            for (i, bot, top, gdir) in find_fvgs(h, l):
                if i >= len(h) - 2:
                    continue
                key = "IS" if years[i] in IS_YEARS else "OOS"
                for tag, (bb, tt, gd) in (("gap", (bot, top, gdir)),
                                          ("ctl", control_zone(c[i], bot, top,
                                                               gdir))):
                    d = first_touch(h, l, i, bb, tt, lim)
                    if d is None:
                        continue
                    tb = i + d
                    v, cb = classify_reaction(o, h, l, c, tb, bb, tt, gd,
                                              react_win)
                    if v == "unresolved":
                        B[tag + key].append((v, None, None))
                        continue
                    ex = excursion(h, l, cb, c[cb],
                                   reaction_direction(v, gd), horizon)
                    B[tag + key].append((v, None, None) if ex is None
                                        else (v, ex[0], ex[1]))
                    # the breakaway -> IFVG claim, gap AND control
                    if v == "break":
                        hd = retest_holds(o, h, l, c, cb, bb, tt, gd,
                                          retest_h, react_win)
                        if hd is not None:
                            holds[tag + key].append(hd)
        out[tf] = {k: summarise(v) for k, v in B.items()}
        out[tf]["holds"] = {k: (len(v), 100.0 * sum(v) / len(v) if v else None)
                            for k, v in holds.items()}
    _write(out, tfs, react_win, horizon, retest_h)
    return 0


def _write(out, tfs, react_win, horizon, retest_h):
    L = ["# What does price DO when it reaches an HTF gap?", "",
         f"P68b showed arrival is not informative — a gap is reached as often as "
         f"an identical band on the other side of price. This asks the next "
         f"question instead: once price is THERE, does the gap hold?", "",
         f"`respect` = a body closed back out the side price came from. `break` = "
         f"a body closed through the far side. Confirmed within **{react_win}** "
         f"bars of the touch; the excursion is then measured **from the "
         f"confirmation bar forward** over **{horizon}** bars, so the "
         f"confirmation cannot contain its own outcome.", "",
         "**`control` is the row that decides it** — the same classification on a "
         "mirror band (same width, same distance, opposite side of price). Price "
         "reverses at arbitrary levels too; only the LIFT is evidence.", "",
         "`medFav`/`medAdv` are median pips in favour of / against the direction "
         "the reaction implies. **Symmetric medians are a coin flip**, whatever "
         "the rate says.", ""]
    for tf in tfs:
        st = out.get(tf, {})
        L += [f"## {tf}", "", "```",
              f"{'bucket':<12} {'n':>6} {'respect%':>9} {'break%':>8} "
              f"{'unres%':>7} {'resFav':>7} {'resAdv':>7} {'brkFav':>7} {'brkAdv':>7}",
              "-" * 76]
        for k, name in (("gapIS", "gap IS"), ("gapOOS", "gap OOS"),
                        ("ctlIS", "control IS"), ("ctlOOS", "control OOS")):
            s = st.get(k, {})
            if not s.get("n"):
                L.append(f"{name:<12} {0:>6}   —")
                continue
            f = lambda x: "—" if x is None else f"{x:.1f}"
            L.append(f"{name:<12} {s['n']:>6} {s['respect']:>8.1f}% "
                     f"{s['break']:>7.1f}% {s['unres']:>6.1f}% "
                     f"{f(s['res_fav']):>7} {f(s['res_adv']):>7} "
                     f"{f(s['brk_fav']):>7} {f(s['brk_adv']):>7}")
        L.append("```")
        hd = st.get("holds", {})
        line = []
        for k in ("IS", "OOS"):
            gn, gp = hd.get("gap" + k, (0, None))
            cn, cp = hd.get("ctl" + k, (0, None))
            lift = ("—" if (gp is None or cp is None) else f"{gp - cp:+.1f}pp")
            line.append(
                f"{k}: gap {gn} retests "
                + ("—" if gp is None else f"{gp:.0f}% held")
                + f", control {cn} "
                + ("—" if cp is None else f"{cp:.0f}%")
                + f" → **lift {lift}**")
        L += ["", f"*Breakaway → IFVG — does a BROKEN gap hold when price comes "
                  f"back to it (within {retest_h} bars)? Escaping a band you "
                  f"already broke is partly geometry and reads 64-72% on a random "
                  f"walk, so read the lift, not the rate:*", ""]
        L += ["  - " + x for x in line]
        L += [""]
        v, why = verdict(st.get("gapIS", {}), st.get("gapOOS", {}),
                         st.get("ctlIS", {}), st.get("ctlOOS", {}))
        L += [f"**Verdict: {v}** — {why}", ""]
    L += ["---", "",
          "A respect rate at or below the control means the gap is not the actor "
          "— price was going to turn there as often as anywhere. In that case the "
          "bias-flip state machine has nothing to stand on and the reaction, not "
          "the study, is what needs rethinking. Measurement only; nothing ships."]
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    if not NO_PUSH:
        _publish(REPORT)


def _publish(path):
    import subprocess

    def _git(*a):
        return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True)

    _git("add", "-f", path)
    if _git("diff", "--cached", "--quiet", "--", path).returncode == 0:
        print(f"\n  report unchanged — nothing to commit. Paste "
              f"{os.path.basename(path)} if Claude has not seen it.")
        return
    sha = (_git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown")
    if _git("commit", "-q", "-m", f"FVG reaction report (auto, on {sha})").returncode:
        print("\n  (commit failed — paste the report above)")
        return
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    p = _git("push", "origin", "HEAD")
    print(f"\n  RESULTS PUSHED — Claude can read data/{os.path.basename(path)}"
          if p.returncode == 0 else
          "\n  (auto-push failed — paste the report above)\n" + p.stderr[-300:])


# ──────────────────────────────── selftest ────────────────────────────────────

def selftest():
    # bullish gap [0.90, 0.95]; price arrives from above and is REJECTED back up
    #        idx    0     1     2     3
    o = [1.00, 0.96, 0.97, 0.99]
    c = [0.97, 0.94, 0.99, 1.00]
    h = [1.01, 0.97, 1.00, 1.01]
    l = [0.96, 0.93, 0.96, 0.98]
    #  bar 2 body is 0.97-0.99, entirely above the near side (0.95) -> respect
    v, b = classify_reaction(o, h, l, c, 1, 0.90, 0.95, +1, 4)
    assert (v, b) == ("respect", 2), (v, b)

    # same gap, price CLOSES THROUGH the far side (0.90) -> break
    o2 = [1.00, 0.96, 0.89, 0.87]
    c2 = [0.97, 0.94, 0.87, 0.86]
    h2 = [1.01, 0.97, 0.93, 0.88]     # wick still in the gap, BODY fully below
    l2 = [0.96, 0.93, 0.86, 0.85]
    v2, b2 = classify_reaction(o2, h2, l2, c2, 1, 0.90, 0.95, +1, 4)
    assert (v2, b2) == ("break", 2), (v2, b2)

    # a WICK through the far side is NOT a break — the body must clear it
    o3 = [1.00, 0.96, 0.93, 0.93]
    c3 = [0.97, 0.94, 0.92, 0.93]
    h3 = [1.01, 0.97, 0.94, 0.94]
    l3 = [0.96, 0.93, 0.85, 0.92]     # deep wick to 0.85, body stays inside
    assert classify_reaction(o3, h3, l3, c3, 1, 0.90, 0.95, +1, 3)[0] == "unresolved"

    # bearish mirror: gap [1.05, 1.10] ABOVE price, rejected back DOWN
    ob = [1.00, 1.04, 1.03, 1.01]
    cb = [1.03, 1.06, 1.01, 1.00]
    hb = [1.04, 1.11, 1.04, 1.02]
    lb = [0.99, 1.03, 1.00, 0.99]
    assert classify_reaction(ob, hb, lb, cb, 1, 1.05, 1.10, -1, 4)[0] == "respect"

    # excursion: measured forward only, and the legs swap with direction
    eh = [1.00, 1.05, 1.02]
    el = [1.00, 0.99, 0.97]
    up = excursion(eh, el, 0, 1.00, +1, 5)
    assert abs(up[0] - 500) < 1e-6 and abs(up[1] - 300) < 1e-6, up
    dn = excursion(eh, el, 0, 1.00, -1, 5)
    assert abs(dn[0] - 300) < 1e-6 and abs(dn[1] - 500) < 1e-6, dn
    assert excursion(eh, el, 2, 1.00, +1, 5) is None      # nothing ahead

    # breakaway -> IFVG: bullish gap broken DOWN, retest rejected back down = held
    ro = [0.88, 0.92, 0.87]
    rc = [0.86, 0.93, 0.86]
    rh = [0.89, 0.96, 0.88]           # bar 1 wicks back into [0.90, 0.95]
    rl = [0.85, 0.91, 0.85]
    assert retest_holds(ro, rh, rl, rc, 0, 0.90, 0.95, +1, 5, 3) is True
    # ... and if it closes back ABOVE the zone instead, it failed
    fo = [0.88, 0.92, 0.97]
    fc = [0.86, 0.93, 0.99]
    fh = [0.89, 0.96, 1.00]
    fl = [0.85, 0.91, 0.96]
    assert retest_holds(fo, fh, fl, fc, 0, 0.90, 0.95, +1, 5, 3) is False
    # never retested -> None, not False
    no, nc = [0.88, 0.86, 0.84], [0.86, 0.84, 0.82]
    nh, nl = [0.89, 0.87, 0.85], [0.85, 0.83, 0.81]
    assert retest_holds(no, nh, nl, nc, 0, 0.90, 0.95, +1, 5, 3) is None

    # the direction mapping — a bullish gap is support, so respecting it means
    # bouncing back UP (its own direction) and breaking it means carrying on DOWN
    assert reaction_direction("respect", +1) == +1
    assert reaction_direction("break", +1) == -1
    assert reaction_direction("respect", -1) == -1
    assert reaction_direction("break", -1) == +1
    assert reaction_direction("unresolved", +1) == 0

    s = summarise([("respect", 10.0, 4.0), ("respect", 20.0, 6.0),
                   ("break", 5.0, 5.0), ("unresolved", None, None)])
    assert s["n"] == 4 and s["respect"] == 50.0 and s["break"] == 25.0, s
    assert s["res_fav"] == 20.0 and s["res_adv"] == 6.0, s

    # the control band must be mirrored AND re-oriented: a bullish gap below
    # price maps to a band above price, which is approached from the other side
    cb_, ct_, cg_ = control_zone(1.00, 0.90, 0.95, +1)
    assert abs(cb_ - 1.05) < 1e-9 and abs(ct_ - 1.10) < 1e-9, (cb_, ct_)
    assert cg_ == -1, cg_
    assert control_zone(1.00, 1.05, 1.10, -1)[2] == +1

    G = {"n": 100, "respect": 60.0, "res_fav": 20.0, "res_adv": 8.0}
    C = {"n": 100, "respect": 50.0}
    assert verdict(G, G, C, C)[0] == "GREEN"
    # a big rate with no lift over the control is not a result
    assert verdict(G, G, {"n": 100, "respect": 59.0},
                   {"n": 100, "respect": 59.0})[0] == "RED"
    # lift in one split only
    assert verdict(G, G, C, {"n": 100, "respect": 59.0})[0] == "RED"
    # lift, but the branch does not pay
    NP = {"n": 100, "respect": 60.0, "res_fav": 8.0, "res_adv": 20.0}
    assert verdict(NP, NP, C, C)[0] == "YELLOW"
    print("selftest OK — reaction classify (respect/break/wick), direction "
          "mapping, excursion, breakaway retest, summarise, control verdict")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tfs", default="W,D,240T")
    ap.add_argument("--react-window", type=int, default=3,
                    help="bars after the touch in which the reaction must confirm")
    ap.add_argument("--horizon", type=int, default=12,
                    help="bars the excursion is measured over, from the "
                         "confirmation bar forward")
    ap.add_argument("--retest-horizon", type=int, default=30,
                    help="bars to wait for a retest of a broken gap")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    global NO_PUSH
    NO_PUSH = a.no_push
    return run(tuple(a.tfs.split(",")), a.react_window, a.horizon,
               a.retest_horizon)


if __name__ == "__main__":
    sys.exit(main())

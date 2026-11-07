"""ICT 2022 Episode 12 — Market Structure for Precision Technicians.

Fractal swing-point classification into a three-tier hierarchy:

    STH / STL  — Short-Term High / Low   (a basic 3-bar swing)
    ITH / ITL  — Intermediate-Term High / Low
    LTH / LTL  — Long-Term High / Low

The tiers are RECURSIVE, not just different lookbacks (that is the crude
approximation the old `bias.classify_swing_structure` used). The real ICT
definition is fractal:

    • A Short-Term High (STH) is a candle whose High is greater than the High
      of the candle on each side (a 3-bar fractal high). STL is the inverse.

    • An Intermediate-Term High (ITH) is a SHORT-TERM HIGH that has a LOWER
      short-term high on each side of it. So we first reduce the candle series
      to its STH sequence, then find the 3-point fractal highs WITHIN that
      sequence. ITL is the inverse on STLs.

    • A Long-Term High (LTH) is an INTERMEDIATE-TERM HIGH that has a lower
      intermediate-term high on each side. Same fractal rule, one level up.

Why this matters for the algo (the trader's reasoning, captured verbatim):

    "The problem with STH/STL is they usually get taken out, forming a new
     ITH/ITL while leaving the LTH/LTL intact — a double sweep on liquidity.
     If the algo knows the context of market structure it knows those are just
     minor runs on liquidity; the LTL/LTH or ITH/ITL is still intact, meaning
     the trend is still continuing — it's just a Judas. Breakouts can also be
     confirmed: we'd know which swing forms next and which fails depending on
     the bigger-timeframe draw on liquidity."

So this module exposes, per timeframe:
    • the most recent confirmed swing of each tier (price + bar index)
    • whether each tier's last swing is still INTACT or has been SWEPT
    • the directional structure read (are we making higher ITHs/ITLs = bullish
      intermediate structure, or lower = bearish)

`candles` is ordered oldest → newest; `candles[-1]` is the most recent bar.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Swing:
    """A classified swing point."""
    price: float
    bar_index: int      # index into the ORIGINAL candle list
    kind: str           # "high" or "low"
    tier: str           # "STH"/"STL"/"ITH"/"ITL"/"LTH"/"LTL"
    swept: bool = False  # True once price has traded through it since it formed


def _fractal_highs(points):
    """Return indices i (into `points`) where points[i].price is a 3-point
    fractal high: strictly greater than its immediate neighbours' price.

    `points` is a list of objects with a `.price` attribute, in chronological
    order. The first and last points can never be confirmed fractals (no bar
    on one side), matching ICT's "confirmed swing needs a candle each side".
    """
    out = []
    for i in range(1, len(points) - 1):
        if points[i].price > points[i - 1].price and points[i].price > points[i + 1].price:
            out.append(i)
    return out


def _fractal_lows(points):
    """Indices i where points[i].price is a 3-point fractal low."""
    out = []
    for i in range(1, len(points) - 1):
        if points[i].price < points[i - 1].price and points[i].price < points[i + 1].price:
            out.append(i)
    return out


def _base_swings(candles):
    """Reduce raw candles to their Short-Term swing highs and lows (STH/STL).

    A bar is an STH if its High exceeds both neighbours' Highs; an STL if its
    Low is below both neighbours' Lows. Returns (sth_points, stl_points) where
    each element is a lightweight node carrying price + original bar index.
    """
    sth, stl = [], []
    for i in range(1, len(candles) - 1):
        p, l, r = candles[i], candles[i - 1], candles[i + 1]
        if p.High > l.High and p.High > r.High:
            sth.append(_Node(p.High, i))
        if p.Low < l.Low and p.Low < r.Low:
            stl.append(_Node(p.Low, i))
    return sth, stl


@dataclass
class _Node:
    price: float
    bar_index: int


def _promote(nodes, kind: str):
    """Promote a list of same-kind swing nodes one tier up the fractal.

    Given STH nodes, returns the subset that are fractal highs WITHIN the STH
    sequence (→ ITH candidates). Given STL nodes, returns fractal lows (→ ITL).
    `kind` is "high" or "low". Preserves original bar indices.
    """
    if kind == "high":
        idx = _fractal_highs(nodes)
    else:
        idx = _fractal_lows(nodes)
    return [nodes[i] for i in idx]


def classify(candles) -> dict:
    """Full fractal classification of a candle series into the 3-tier hierarchy.

    Returns a dict:
        {
          "sth": [Swing, ...],  "stl": [Swing, ...],   # short-term
          "ith": [Swing, ...],  "itl": [Swing, ...],   # intermediate
          "lth": [Swing, ...],  "ltl": [Swing, ...],   # long-term
        }
    Each list is chronological (oldest → newest). Empty lists when the series
    is too short to confirm a tier.
    """
    empty = {k: [] for k in ("sth", "stl", "ith", "itl", "lth", "ltl")}
    if candles is None or len(candles) < 3:
        return empty

    sth_n, stl_n = _base_swings(candles)
    ith_n = _promote(sth_n, "high")
    itl_n = _promote(stl_n, "low")
    lth_n = _promote(ith_n, "high")
    ltl_n = _promote(itl_n, "low")

    def wrap(nodes, tier, kind):
        return [Swing(n.price, n.bar_index, kind, tier) for n in nodes]

    result = {
        "sth": wrap(sth_n, "STH", "high"),
        "stl": wrap(stl_n, "STL", "low"),
        "ith": wrap(ith_n, "ITH", "high"),
        "itl": wrap(itl_n, "ITL", "low"),
        "lth": wrap(lth_n, "LTH", "high"),
        "ltl": wrap(ltl_n, "LTL", "low"),
    }
    _mark_swept(result, candles)
    return result


def _mark_swept(result: dict, candles) -> None:
    """Flag each swing `swept` if any LATER bar traded through its price.

    A high is swept when a subsequent bar's High exceeds it; a low is swept
    when a subsequent bar's Low drops below it. The most recent UNSWEPT swing
    of each tier is the live structural reference (the level still holding).
    """
    n = len(candles)
    for key, swings in result.items():
        for s in swings:
            later = candles[s.bar_index + 1:]
            if not later:
                continue
            if s.kind == "high":
                s.swept = any(c.High > s.price for c in later)
            else:
                s.swept = any(c.Low < s.price for c in later)


def last_intact(result: dict, tier: str) -> Swing | None:
    """Most recent UNSWEPT swing of `tier` ("LTH"/"LTL"/"ITH"/"ITL"/"STH"/"STL").

    This is the structural level still holding — the one a stop should sit
    beyond, or whose break constitutes a genuine BOS at that tier.
    """
    key = tier.lower()
    swings = result.get(key, [])
    for s in reversed(swings):
        if not s.swept:
            return s
    return None


def last_swing(result: dict, tier: str) -> Swing | None:
    """Most recent swing of `tier` regardless of swept state (chronological)."""
    swings = result.get(tier.lower(), [])
    return swings[-1] if swings else None


def trail_stop_level(candles, direction, tier, buf_pips, pip, cur_price):
    """Structural trailing-stop candidate: just beyond the latest INTACT swing.

    LONG  (direction +1): (intact STL or ITL).price - buf_pips*pip  -> stop below.
    SHORT (direction -1): (intact STH or ITH).price + buf_pips*pip  -> stop above.

    `tier` is "st" (short-term STH/STL) or "it" (intermediate ITH/ITL). Returns
    None when there is no intact swing of that tier, or the computed level is on
    the wrong side of `cur_price` (would be an invalid / instant stop). The
    caller decides whether it improves on the current stop (only-tighten).
    """
    res = classify(candles)
    if direction > 0:
        sw = last_intact(res, "ITL" if tier == "it" else "STL")
        if sw is None:
            return None
        cand = sw.price - buf_pips * pip
        return cand if cand < cur_price else None
    if direction < 0:
        sw = last_intact(res, "ITH" if tier == "it" else "STH")
        if sw is None:
            return None
        cand = sw.price + buf_pips * pip
        return cand if cand > cur_price else None
    return None


def structure_direction(result: dict) -> int:
    """Intermediate-term structural read from the ITH/ITL sequence.

    +1 (bullish): the last two ITLs are rising (higher intermediate lows) — the
        market is making higher lows at the intermediate tier → uptrend intact.
    -1 (bearish): the last two ITHs are falling (lower intermediate highs).
     0: indeterminate / conflicting / insufficient swings.

    ICT: trend is defined by the intermediate-term tier. Short-term sweeps that
    leave the ITH/ITL intact do NOT change this read — that is the whole point
    of the double-sweep / Judas distinction.
    """
    ith = result.get("ith", [])
    itl = result.get("itl", [])
    bull = bear = False
    if len(itl) >= 2 and itl[-1].price > itl[-2].price:
        bull = True
    if len(ith) >= 2 and ith[-1].price < ith[-2].price:
        bear = True
    if bull and not bear:
        return +1
    if bear and not bull:
        return -1
    return 0


def is_minor_sweep(result: dict, direction: int) -> bool:
    """True when the latest move is a Short-Term sweep that left the
    Intermediate/Long term structure INTACT — i.e. a Judas, not a reversal.

    For a LONG bias (direction +1): an STL was swept (minor sell-side raid) but
    the most recent ITL is still unswept → the down-move is just a liquidity
    grab below short-term lows; the intermediate uptrend holds → continuation.

    For a SHORT bias (direction -1): an STH was swept but the most recent ITH
    is still intact.

    Returns False if the relevant intermediate level has itself been broken
    (that would be a real structural shift, not a minor sweep).
    """
    if direction > 0:
        stl = last_swing(result, "STL")
        itl = last_intact(result, "ITL")
        # A short-term low was taken out, but an intermediate low still holds.
        return bool(stl and stl.swept and itl is not None)
    if direction < 0:
        sth = last_swing(result, "STH")
        ith = last_intact(result, "ITH")
        return bool(sth and sth.swept and ith is not None)
    return False

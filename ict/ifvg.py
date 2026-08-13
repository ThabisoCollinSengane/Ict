"""Inversion Fair Value Gaps (IFVG) for the Market Maker model watcher.

A 3-candle FVG that is later VIOLATED by a full-body close through it inverts
into a support/demand (bullish) or resistance/supply (bearish) zone. These HTF
inversion zones repel price toward the draw on liquidity — a Judas one timeframe
up — so the live engine watches them to time retracement entries.

Bars use the uppercase Open/High/Low/Close namedtuple shared across ict/
(oldest -> newest), so this works on the live MT5 bar feed unchanged.
"""
from __future__ import annotations


def _fvgs(bars):
    """3-candle FVG boxes: list of (form_idx, lo, hi). Gap direction is
    irrelevant here — the inversion decides the tradable side."""
    out = []
    for i in range(2, len(bars)):
        c0, c2 = bars[i - 2], bars[i]
        if c0.High < c2.Low:            # gap up
            out.append((i, c0.High, c2.Low))
        elif c0.Low > c2.High:          # gap down
            out.append((i, c2.High, c0.Low))
    return out


def _inversion(bars, form_idx, lo, hi, scan):
    """First full-body close outside the (mitigated) box -> IFVG.
    Returns (inv_idx, idir, lo, hi) or None. idir +1 = demand, -1 = supply."""
    touched = False
    end = min(len(bars), form_idx + 1 + scan)
    for j in range(form_idx + 1, end):
        c = bars[j]
        if c.Low <= hi and c.High >= lo:
            touched = True
        if not touched:
            continue
        if c.Open > hi and c.Close > hi:      # full body above -> demand
            return (j, +1, lo, hi)
        if c.Open < lo and c.Close < lo:      # full body below -> supply
            return (j, -1, lo, hi)
    return None


def latest_inversion(bars, lo, hi):
    """Inversion direction of a KNOWN FVG box (lo, hi), judged against `bars`.

    Cross-timeframe: the box can be defined on a higher timeframe and the
    full-body close that inverts it judged on this (same or next-lower) timeframe's
    bars — the cascade rule "the full-body close is judged on the first TF that
    identified the IFVG and the following lower TF". Requires a TOUCH into the box
    first (ICT: a gap must be traded into before it can invert), then the first
    full-body close beyond it decides the side.

    Returns +1 (demand/support — closed a full body ABOVE the box),
            -1 (supply/resistance — closed a full body BELOW), or 0 (no inversion).
    A later full-body close back through the other way is treated as spent (0).
    """
    touched = False
    idir = 0
    for c in bars:
        if c.Low <= hi and c.High >= lo:
            touched = True
        if not touched:
            continue
        if idir == 0:
            if c.Open > hi and c.Close > hi:
                idir = +1
            elif c.Open < lo and c.Close < lo:
                idir = -1
        else:
            # spent if a full body later closes the opposite way through the box
            if idir > 0 and c.Open < lo and c.Close < lo:
                return 0
            if idir < 0 and c.Open > hi and c.Close > hi:
                return 0
    return idir


def find_inversion_fvgs(bars, direction=0, scan=60, max_zones=3, still_intact=True):
    """Recent inversion FVGs as dicts {dir, lo, hi, mid, inv_idx}, newest first.

    direction: +1 keep only bullish IFVGs (demand/support), -1 only bearish
    (supply/resistance), 0 = both. still_intact drops a zone that a later bar
    has closed a full body through the other way (a dead inversion).
    """
    if not bars or len(bars) < 3:
        return []
    n = len(bars)
    zones = []
    for (form_idx, lo, hi) in _fvgs(bars):
        inv = _inversion(bars, form_idx, lo, hi, scan)
        if inv is None:
            continue
        inv_idx, idir, zlo, zhi = inv
        if direction and idir != direction:
            continue
        if still_intact:
            dead = False
            for k in range(inv_idx + 1, n):
                c = bars[k]
                if idir > 0 and c.Open < zlo and c.Close < zlo:
                    dead = True
                    break
                if idir < 0 and c.Open > zhi and c.Close > zhi:
                    dead = True
                    break
            if dead:
                continue
        zones.append({"dir": idir, "lo": zlo, "hi": zhi,
                      "mid": (zlo + zhi) / 2.0, "inv_idx": inv_idx})
    zones.sort(key=lambda z: z["inv_idx"], reverse=True)
    return zones[:max_zones]

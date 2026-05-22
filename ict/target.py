"""Hierarchical target picker: PWH/PWL -> PDH/PDL -> session H/L -> CBDR.

Per user spec, targets are ALWAYS recognized liquidity pools on HIGHER
timeframes and we PREFER the higher-TF target when it gives acceptable
RR. The picker walks pools in HTF priority order and returns the first
one that meets `min_rr` (if provided). If no target meets min_rr, the
HTF-priority-highest still-untouched pool is returned as the "best
available" — the caller decides whether to skip.
"""

from dataclasses import dataclass
from typing import Optional

from ict.levels import DayLevels


@dataclass
class Target:
    name: str
    price: float
    distance_pips: float


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


# Lower rank = higher priority. Weekly > Daily > Session > CBDR.
_HTF_RANK = {
    "PWH": 0, "PWL": 0,
    "PDH": 1, "PDL": 1,
    "LondonHigh": 2, "LondonLow": 2,
    "AsiaHigh": 3,   "AsiaLow": 3,
    "CBDRHigh": 4,   "CBDRLow": 4,
}


def candidates(levels: DayLevels, cbdr_high, cbdr_low, direction: int) -> list[tuple]:
    out = []
    if direction > 0:
        if levels.pdh is not None: out.append(("PDH", levels.pdh))
        if levels.pwh is not None: out.append(("PWH", levels.pwh))
        if levels.london_high is not None: out.append(("LondonHigh", levels.london_high))
        if levels.asia_high is not None: out.append(("AsiaHigh", levels.asia_high))
        if cbdr_high is not None: out.append(("CBDRHigh", cbdr_high))
    else:
        if levels.pdl is not None: out.append(("PDL", levels.pdl))
        if levels.pwl is not None: out.append(("PWL", levels.pwl))
        if levels.london_low is not None: out.append(("LondonLow", levels.london_low))
        if levels.asia_low is not None: out.append(("AsiaLow", levels.asia_low))
        if cbdr_low is not None: out.append(("CBDRLow", cbdr_low))
    return out


def pick(
    symbol: str,
    levels: DayLevels,
    cbdr_high: Optional[float],
    cbdr_low: Optional[float],
    direction: int,
    current_price: float,
    risk_pips: Optional[float] = None,
    min_rr: Optional[float] = None,
) -> Optional[Target]:
    """Highest-priority untouched liquidity pool in trade direction.

    If risk_pips + min_rr are provided, walk HTF -> LTF order and return
    the first pool that satisfies reward/risk_pips >= min_rr. If none
    qualify, return the highest-TF still-untouched pool (caller decides).
    """
    pip = _pip(symbol)
    cands = candidates(levels, cbdr_high, cbdr_low, direction)
    if direction > 0:
        valid = [(n, px) for n, px in cands if px > current_price]
    else:
        valid = [(n, px) for n, px in cands if px < current_price]
    if not valid:
        return None
    # Sort by HTF rank (lower = better), tie-break by distance ascending.
    valid.sort(key=lambda t: (_HTF_RANK.get(t[0], 9), abs(t[1] - current_price)))

    if risk_pips is not None and min_rr is not None and risk_pips > 0:
        for name, px in valid:
            reward = abs(px - current_price) / pip
            if reward / risk_pips >= min_rr:
                return Target(name=name, price=px, distance_pips=reward)

    name, px = valid[0]
    return Target(name=name, price=px, distance_pips=abs(px - current_price) / pip)

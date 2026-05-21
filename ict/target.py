"""Hierarchical target picker: PDH/PDL -> PWH/PWL -> prior-session H/L -> CBDR.

Per user spec, targets are ALWAYS recognized liquidity pools, never arbitrary
R-multiples. We measure RR; we do not engineer it.

Filter: a candidate target is only valid if price has NOT already traded
through it in the current session (i.e., the liquidity is still resting).
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


def candidates(levels: DayLevels, cbdr_high, cbdr_low, direction: int) -> list[tuple]:
    """Return [(name, price)] for every level on the correct side of trade
    direction. Caller filters by price/session-state.
    """
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
) -> Optional[Target]:
    """Nearest valid (still-resting) liquidity pool in the trade direction."""
    pip = _pip(symbol)
    cands = candidates(levels, cbdr_high, cbdr_low, direction)
    valid = []
    for name, px in cands:
        if direction > 0 and px > current_price:
            valid.append((name, px))
        elif direction < 0 and px < current_price:
            valid.append((name, px))
    if not valid:
        return None
    name, px = min(valid, key=lambda t: abs(t[1] - current_price))
    return Target(name=name, price=px, distance_pips=abs(px - current_price) / pip)

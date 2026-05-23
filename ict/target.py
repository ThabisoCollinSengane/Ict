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
from ict.structure import classify_intermediates, last_unmitigated


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


def pick_dol(
    symbol: str,
    htf_candles_by_tf: dict,
    levels: DayLevels,
    cbdr_high: Optional[float],
    cbdr_low: Optional[float],
    direction: int,
    current_price: float,
    risk_pips: Optional[float] = None,
    min_rr: Optional[float] = None,
) -> Optional[Target]:
    """Structural Draw-on-Liquidity picker.

    Walks HTFs (D1 -> H4 -> H1 -> M15) for the most recent unmitigated
    opposite-side ITH/ITL — the structural anchor the market is being drawn
    toward. If a higher TF has no qualifying unmitigated level, the search
    descends to the next TF down (rather than abandoning structural targeting
    entirely). Static rank picker (PWH/PWL/PDH/PDL/session/CBDR) remains the
    final fallback if every TF is silent.

    `htf_candles_by_tf`: { "D": [Bar,...], "240T": [...], "60T": [...], "15T": [...] }
    Missing keys are skipped silently.
    """
    target_kind = -1 if direction < 0 else +1  # shorts target ITLs below
    for tf in ("D", "240T", "60T", "15T"):
        bars = htf_candles_by_tf.get(tf)
        if not bars:
            continue
        ints = classify_intermediates(bars)
        # Walk unmitigated levels of the target kind in reverse-chronological
        # order, taking the first one that's beyond current_price (i.e., a
        # genuine draw, not a level price already crossed).
        candidates = [l for l in reversed(ints)
                      if l.kind == target_kind and not l.mitigated
                      and ((direction < 0 and l.price < current_price)
                           or (direction > 0 and l.price > current_price))]
        if not candidates:
            continue
        lvl = candidates[0]
        pip = _pip(symbol)
        dist = abs(lvl.price - current_price) / pip
        if risk_pips is None or min_rr is None or (dist / risk_pips) >= min_rr:
            name = f"{tf}_{'ITL' if direction < 0 else 'ITH'}"
            return Target(name=name, price=lvl.price, distance_pips=dist)

    return pick(symbol, levels, cbdr_high, cbdr_low, direction, current_price,
                risk_pips=risk_pips, min_rr=min_rr)

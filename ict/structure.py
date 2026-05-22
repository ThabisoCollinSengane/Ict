"""ICT market structure: ITH / ITL / STH / STL classification.

Short-term highs/lows (STH/STL) are the basic pivots. Intermediate-term
highs/lows (ITH/ITL) are STH/STL that are higher/lower than the STH/STL
on either side — they are the structural anchors used for HTF bias.

We track "unmitigated" state: an ITH stays the bearish-side target until a
later candle trades through it; an ITL stays the bullish-side target until
traded through.
"""

from dataclasses import dataclass
from typing import Optional

from ict.swings import find_swings, Swing


@dataclass
class IntermediateLevel:
    index: int
    price: float
    kind: int          # +1 = ITH, -1 = ITL
    mitigated: bool = False


def classify_intermediates(candles, left=None, right=None) -> list[IntermediateLevel]:
    """Walk the swing series and tag intermediate highs/lows.

    An STH at index k is an ITH if there is at least one STH on each side with
    a strictly lower price. Same logic mirrored for ITL.
    """
    swings = find_swings(candles, left, right)
    highs = [s for s in swings if s.kind == +1]
    lows = [s for s in swings if s.kind == -1]

    out: list[IntermediateLevel] = []
    for i in range(1, len(highs) - 1):
        if highs[i].price > highs[i - 1].price and highs[i].price > highs[i + 1].price:
            out.append(IntermediateLevel(highs[i].index, highs[i].price, +1))
    for i in range(1, len(lows) - 1):
        if lows[i].price < lows[i - 1].price and lows[i].price < lows[i + 1].price:
            out.append(IntermediateLevel(lows[i].index, lows[i].price, -1))

    out.sort(key=lambda x: x.index)
    _mark_mitigation(candles, out)
    return out


def _mark_mitigation(candles, levels: list[IntermediateLevel]) -> None:
    for lvl in levels:
        for c in candles[lvl.index + 1:]:
            if lvl.kind == +1 and c.High > lvl.price:
                lvl.mitigated = True
                break
            if lvl.kind == -1 and c.Low < lvl.price:
                lvl.mitigated = True
                break


def last_unmitigated(levels: list[IntermediateLevel], kind: int) -> Optional[IntermediateLevel]:
    for lvl in reversed(levels):
        if lvl.kind == kind and not lvl.mitigated:
            return lvl
    return None


def bias_holds_on_tf(candles, direction: int, current_price: float,
                     left=None, right=None) -> bool:
    """True if the most recent unmitigated ITH/ITL on this TF still
    structurally supports `direction`.

    For shorts (-1): an unmitigated ITH must exist and sit above current_price
      (price is still below the ITH that anchored the bearish leg).
    For longs (+1): an unmitigated ITL must exist and sit below current_price.

    Returns False if no qualifying unmitigated level exists — structure on
    this TF gives no read for that side.
    """
    if direction == 0:
        return False
    levels = classify_intermediates(candles, left, right)
    kind = +1 if direction < 0 else -1
    lvl = last_unmitigated(levels, kind)
    if lvl is None:
        return False
    return (lvl.price > current_price) if direction < 0 else (lvl.price < current_price)


def directional_pull(candles, left=None, right=None) -> int:
    """+1 if the last unmitigated structural pull is up (toward a fresh ITH),
    -1 if down (toward a fresh ITL), 0 if undetermined.

    We compare the indices of the most recent unmitigated ITH vs ITL: whichever
    is more recent wins, because that's the level the market is still drawing
    toward.
    """
    levels = classify_intermediates(candles, left, right)
    ith = last_unmitigated(levels, +1)
    itl = last_unmitigated(levels, -1)
    if ith is None and itl is None:
        return 0
    if ith is None:
        return -1
    if itl is None:
        return +1
    return +1 if ith.index > itl.index else -1

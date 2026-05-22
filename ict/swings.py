"""Pivot-based swing point detection.

A bar at index `i` is a swing high if its High is strictly greater than the
High of the `left` bars before it AND the `right` bars after it. Mirrors for
swing low.

Returns lists of (index, price) tuples ordered oldest -> newest.
"""

from dataclasses import dataclass
from typing import Iterable

import config


@dataclass(frozen=True)
class Swing:
    index: int
    price: float
    kind: int          # +1 = swing high, -1 = swing low


def find_swings(candles, left: int = None, right: int = None) -> list[Swing]:
    left = left if left is not None else config.PIVOT_LEFT
    right = right if right is not None else config.PIVOT_RIGHT
    out: list[Swing] = []
    n = len(candles)
    for i in range(left, n - right):
        h = candles[i].High
        l = candles[i].Low
        if all(h > candles[i - k].High for k in range(1, left + 1)) and \
           all(h > candles[i + k].High for k in range(1, right + 1)):
            out.append(Swing(i, h, +1))
        if all(l < candles[i - k].Low for k in range(1, left + 1)) and \
           all(l < candles[i + k].Low for k in range(1, right + 1)):
            out.append(Swing(i, l, -1))
    return out


def last_swing_high(candles, left=None, right=None) -> Swing | None:
    for s in reversed(find_swings(candles, left, right)):
        if s.kind == +1:
            return s
    return None


def last_swing_low(candles, left=None, right=None) -> Swing | None:
    for s in reversed(find_swings(candles, left, right)):
        if s.kind == -1:
            return s
    return None

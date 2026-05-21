"""Smart Money Technique (SMT) divergence — NYO-based.

Setup is valid when the traded pair leads the move relative to the NY true
day open (NYO) while the other pair lags on the opposite side:

  BULLISH  setup: traded > NYO_traded  AND  other < NYO_other
  BEARISH  setup: traded < NYO_traded  AND  other > NYO_other

Same-side -> no SMT. The traded pair must always be the leader.
"""

from dataclasses import dataclass
from typing import Optional

import config


@dataclass
class SMTSignal:
    direction: int
    traded_distance_pips: float
    other_distance_pips: float


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def confirm(
    traded_symbol: str,
    traded_price: float,
    traded_nyo: float,
    other_symbol: str,
    other_price: float,
    other_nyo: float,
    direction: int,
) -> Optional[SMTSignal]:
    if traded_nyo is None or other_nyo is None:
        return None

    pip_t = _pip(traded_symbol)
    pip_o = _pip(other_symbol)
    min_pips = config.SMT_MIN_DISTANCE_PIPS

    traded_dist = (traded_price - traded_nyo) / pip_t
    other_dist = (other_price - other_nyo) / pip_o

    if direction > 0:
        if traded_dist > min_pips and other_dist < -min_pips:
            return SMTSignal(+1, traded_dist, other_dist)
        return None
    if direction < 0:
        if traded_dist < -min_pips and other_dist > min_pips:
            return SMTSignal(-1, traded_dist, other_dist)
        return None
    return None

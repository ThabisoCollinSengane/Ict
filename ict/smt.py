"""Smart Money Technique (SMT) divergence — NYO-based, lag-detection.

Classical ICT SMT: the two correlated pairs should NOT move in lockstep.
The traded pair leads; the other pair LAGS. "Lag" means the other pair
is either on the OPPOSITE side of its NYO (cleanest divergence) OR is
on the same side but with smaller magnitude (less far from its own NYO).

  BULLISH  setup: traded > NYO_traded by >= min_pips
                  AND other_dist < traded_dist - lag_margin
  BEARISH  setup: traded < NYO_traded by >= min_pips
                  AND other_dist > traded_dist + lag_margin

(Distances are signed: positive = above NYO, negative = below.)
This is the textbook ICT divergence read: leader makes a stronger
move away from anchor than the lagger does in the same window.
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
    lag_margin_pips: float = 2.0,
) -> Optional[SMTSignal]:
    if traded_nyo is None or other_nyo is None:
        return None

    pip_t = _pip(traded_symbol)
    pip_o = _pip(other_symbol)
    min_pips = config.SMT_MIN_DISTANCE_PIPS

    traded_dist = (traded_price - traded_nyo) / pip_t   # signed pips from NYO
    other_dist = (other_price - other_nyo) / pip_o

    if direction > 0:
        # Traded must be meaningfully above its NYO.
        if traded_dist < min_pips:
            return None
        # Other lags if it's measurably less far above its NYO than traded
        # is above its NYO (or below its NYO entirely — even better).
        if other_dist > traded_dist - lag_margin_pips:
            return None
        return SMTSignal(+1, traded_dist, other_dist)

    if direction < 0:
        if traded_dist > -min_pips:
            return None
        if other_dist < traded_dist + lag_margin_pips:
            return None
        return SMTSignal(-1, traded_dist, other_dist)

    return None

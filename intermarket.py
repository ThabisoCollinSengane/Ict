"""Intermarket signals: DXY + EURGBP → direction and pair preference score.

Original table (kept for reference, still used by _maybe_pyramid's resolve() call):

  | DXY  | EURGBP | Preferred pair        |
  |------|--------|-----------------------|
  | Bear | Bull   | LONG EURUSD  (score 1.0) |
  | Bear | Bear   | LONG GBPUSD  (score 1.0) |
  | Bull | Bull   | SHORT GBPUSD (score 1.0) |
  | Bull | Bear   | SHORT EURUSD (score 1.0) |

Extended table (new resolve_pair_direction, used for initial entry):

  DXY alone is sufficient to determine USD direction. EURGBP is a PREFERENCE
  score that says which pair to favour — but BOTH pairs can trade:

  DXY Bear (-1) → implied direction = LONG for all USD pairs (+1)
    EURGBP Bull  → EURUSD preferred (score 1.0), GBPUSD secondary (0.5)
    EURGBP Bear  → GBPUSD preferred (score 1.0), EURUSD secondary (0.5)
    EURGBP Flat  → both equal (score 0.75)

  DXY Bull (+1) → implied direction = SHORT for all USD pairs (-1)
    EURGBP Bull  → GBPUSD preferred  (score 1.0), EURUSD secondary (0.5)
    EURGBP Bear  → EURUSD preferred  (score 1.0), GBPUSD secondary (0.5)
    EURGBP Flat  → both equal (score 0.75)

  DXY Flat (0)  → no trade (direction unknown, hard gate)
"""

from dataclasses import dataclass


@dataclass
class IntermarketSignal:
    pair: str       # "GBPUSD" or "EURUSD"
    direction: int  # +1 long, -1 short


_TABLE = {
    (-1, +1): IntermarketSignal("EURUSD", +1),
    (-1, -1): IntermarketSignal("GBPUSD", +1),
    (+1, +1): IntermarketSignal("GBPUSD", -1),
    (+1, -1): IntermarketSignal("EURUSD", -1),
}


def resolve(dxy_bias: int, eurgbp_bias: int) -> IntermarketSignal | None:
    """Legacy: requires both DXY and EURGBP non-zero. Used by pyramid IM check."""
    if dxy_bias == 0 or eurgbp_bias == 0:
        return None
    return _TABLE.get((dxy_bias, eurgbp_bias))


def resolve_pair_direction(
    dxy_bias: int,
    eurgbp_bias: int,
    pair: str,
) -> tuple[int, float] | tuple[None, float]:
    """Return (direction, im_score) for a specific pair.

    Requires only DXY to be non-zero. EURGBP adjusts the preference score
    (1.0 = preferred pair, 0.75 = neutral / no EURGBP signal, 0.5 = secondary).

    Returns (None, 0.0) if DXY is flat — caller should skip the trade.
    """
    if dxy_bias == 0:
        return None, 0.0

    direction = -dxy_bias   # DXY inverse: DXY down = USD pairs up

    if eurgbp_bias == 0:
        score = 0.75        # DXY direction but no pair preference
    elif dxy_bias == -1:    # USD weak → buy USD pairs
        if pair == "EURUSD":
            score = 1.0 if eurgbp_bias == +1 else 0.5
        else:               # GBPUSD
            score = 1.0 if eurgbp_bias == -1 else 0.5
    else:                   # USD strong → sell USD pairs (dxy_bias == +1)
        if pair == "EURUSD":
            score = 1.0 if eurgbp_bias == -1 else 0.5
        else:               # GBPUSD
            score = 1.0 if eurgbp_bias == +1 else 0.5

    return direction, score

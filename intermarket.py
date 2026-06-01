"""Intermarket signals: DXY + relative-strength cross → direction and pair score.

Two pair families supported, each driven by DXY and a cross for pair selection:

  EUR/GBP family  — reference cross: EURGBP
    DXY Bear (-1) → USD weak → LONG EURUSD or GBPUSD
      EURGBP Bull  → EURUSD preferred (score 1.0), GBPUSD secondary (0.5)
      EURGBP Bear  → GBPUSD preferred (score 1.0), EURUSD secondary (0.5)
      EURGBP Flat  → both equal (score 0.75); default pair = EURUSD

  AUD/NZD family  — reference cross: AUDNZD
    DXY Bear (-1) → USD weak → LONG AUDUSD or NZDUSD
      AUDNZD Bull  → AUDUSD preferred (score 1.0), NZDUSD secondary (0.5)
      AUDNZD Bear  → NZDUSD preferred (score 1.0), AUDUSD secondary (0.5)
      AUDNZD Flat  → both equal (score 0.75); default pair = AUDUSD

  DXY Bull (+1) → USD strong → direction inverts; PREFERRED pair is the WEAKER one.
  DXY Flat  (0) → no trade (direction unknown, hard gate).
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
    ref_bias: int,
    pair: str,
    primary_pair: str = "EURUSD",
) -> tuple[int, float] | tuple[None, float]:
    """Return (direction, im_score) for a specific pair.

    primary_pair — the pair preferred when ref_bias > 0 and DXY is bearish:
      "EURUSD" for EUR/GBP family (EURGBP > 0 → EUR strong → EURUSD is the long)
      "AUDUSD" for AUD/NZD family (AUDNZD > 0 → AUD strong → AUDUSD is the long)

    Scoring:
      1.0 — preferred pair for the current DXY + ref_bias combination
      0.75 — ref_bias is flat (no cross signal; DXY direction only)
      0.5  — secondary pair (cross disagrees; caller typically skips this)

    Returns (None, 0.0) if DXY is flat — caller should gate the trade out.
    """
    if dxy_bias == 0:
        return None, 0.0

    direction = -dxy_bias   # DXY inverse: DXY down → USD pairs rally

    if ref_bias == 0:
        score = 0.75
    elif dxy_bias == -1:    # USD weak → buy the stronger of the two
        # preferred pair is primary when its currency is stronger (ref_bias > 0)
        score = 1.0 if (ref_bias > 0) == (pair == primary_pair) else 0.5
    else:                   # USD strong → short the weaker of the two (dxy_bias == +1)
        # preferred pair is primary when its currency is weaker (ref_bias < 0)
        score = 1.0 if (ref_bias < 0) == (pair == primary_pair) else 0.5

    return direction, score

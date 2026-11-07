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


def resolve_gold_direction(
    dxy_bias: int,
    silver_bias: int,
    aud_bias: int,
) -> tuple[int, float] | tuple[None, float]:
    """Gold (XAUUSD) intermarket gate — DXY + silver + AUDUSD 2-of-3 breadth.

    Gold moves INVERSE to the dollar, so the primary direction is -dxy_bias:
      DXY down → gold LONG ; DXY up → gold SHORT ; DXY flat → no trade (hard gate).

    Silver (XAGUSD) and AUDUSD are POSITIVE confirmers (they co-move with gold —
    the metals complex and the commodity/risk-currency complex). This mirrors the
    EURUSD+GBPUSD+DXY 2-of-3 logic: DXY always agrees by construction, so at least
    one of silver/AUD must also confirm for a valid 2-of-3.

    Silver DIVERGING (moving opposite the gold direction) is a low-breadth warning
    — the metals move lacks breadth — so it SUPPRESSES the trade even when AUD
    agrees (a documented gold failure mode).

    Returns (direction, im_score) or (None, 0.0):
      1.0  — all three agree (DXY + silver + AUD)
      0.75 — DXY + exactly one confirmer (the other flat)
    """
    if dxy_bias == 0:
        return None, 0.0
    direction = -dxy_bias                      # gold is inverse to the dollar
    if silver_bias == -direction:              # silver diverges → suppress
        return None, 0.0
    confirmers = ((1 if silver_bias == direction else 0)
                  + (1 if aud_bias == direction else 0))
    if confirmers == 0:                        # only DXY agrees → below 2-of-3
        return None, 0.0
    return direction, (1.0 if confirmers == 2 else 0.75)


def resolve_index_direction(
    dxy_bias: int,
    sibling_bias: int,
    ref_bias: int,
) -> tuple[int, float] | tuple[None, float]:
    """US index gate (US500 / US100) — indices move INVERSE to the dollar.

    Same 3-market breadth logic as gold: DXY is the primary hard gate (sign-
    flipped — DXY down → indices long); the SIBLING index (the other traded
    index) and US30 (ref) are positive confirmers. This IS the SMT read — the
    correlated indices should move together; if the sibling DIVERGES the move
    lacks breadth (classic SMT non-confirmation) → suppress, even if US30 agrees.
    Requires ≥2-of-3.

    Returns (direction, im_score) or (None, 0.0):
      1.0  — DXY + sibling + US30 all agree
      0.75 — DXY + one confirmer (the other flat)
    """
    # Identical breadth math to gold: primary inverse + 2 positive confirmers,
    # first-confirmer (sibling) divergence suppresses.
    return resolve_gold_direction(dxy_bias, sibling_bias, ref_bias)

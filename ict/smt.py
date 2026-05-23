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


# ---- Structural SMT (3-asset HTF-first walk) -------------------------------
#
# Operator-spec: textbook ICT SMT looks at *structural breaks* across the
# three correlated assets (EURUSD, GBPUSD, DXY) on HIGHER timeframes first,
# then descends. On any given TF, the ideal pattern for a bearish setup is:
#
#   DXY takes out a recent swing HIGH  (USD strong)
#   EURUSD takes out a recent swing LOW
#   GBPUSD takes out a recent swing LOW
#
# All three aligned -> confirmed. Two aligned + one diverging -> SMT
# divergence: the diverging instrument is the leading edge of the next
# reversal. Less than two -> no read.
#
# Walk W1 -> D1 -> H4 -> H1 -> M15 and return the FIRST TF with a
# non-absent reading. M5 is intentionally excluded — operator-spec: "M5 is
# for entries only, not analysis."

from dataclasses import dataclass as _dc, field as _field

from ict.swings import find_swings as _find_swings


_STRUCTURAL_TFS = ("W", "D", "240T", "60T", "15T")


@_dc
class StructuralSMT:
    tf: Optional[str]            # TF where the reading was taken
    state: str                   # "confirmed" | "divergence" | "absent"
    dxy_aligned: bool
    eur_aligned: bool
    gbp_aligned: bool
    divergent: list = _field(default_factory=list)   # ["EUR", "GBP", "DXY"] subset

    @property
    def is_warning(self) -> bool:
        return self.state == "divergence"


def _broke_recent_swing(bars, kind: int, lookback: int = 30) -> bool:
    """True if the latest close has broken beyond the most recent swing of
    `kind` within the last `lookback` bars.
        kind=+1  -> took out a recent swing HIGH (made a new high)
        kind=-1  -> took out a recent swing LOW (made a new low)
    """
    if not bars or len(bars) < 5:
        return False
    swings = _find_swings(bars)
    if not swings:
        return False
    cutoff = len(bars) - lookback
    relevant = [s for s in swings if s.kind == kind and s.index >= cutoff]
    if not relevant:
        return False
    last_close = bars[-1].Close
    target = relevant[-1].price
    return last_close > target if kind == +1 else last_close < target


def structural_on_tf(direction: int, bars_eur, bars_gbp, bars_dxy) -> StructuralSMT:
    """Tri-asset structural SMT read on a single timeframe.

    For SHORTs (direction=-1) the expected break pattern is DXY high broken
    + EUR low broken + GBP low broken (USD strong, pairs weak). Mirror for
    longs.
    """
    if direction == -1:
        dxy_aligned = _broke_recent_swing(bars_dxy, +1)
        eur_aligned = _broke_recent_swing(bars_eur, -1)
        gbp_aligned = _broke_recent_swing(bars_gbp, -1)
    else:
        dxy_aligned = _broke_recent_swing(bars_dxy, -1)
        eur_aligned = _broke_recent_swing(bars_eur, +1)
        gbp_aligned = _broke_recent_swing(bars_gbp, +1)

    count = sum([dxy_aligned, eur_aligned, gbp_aligned])
    divergent = []
    if not dxy_aligned: divergent.append("DXY")
    if not eur_aligned: divergent.append("EUR")
    if not gbp_aligned: divergent.append("GBP")

    if count == 3:
        state = "confirmed"
    elif count == 2:
        state = "divergence"
    else:
        state = "absent"

    return StructuralSMT(
        tf=None, state=state,
        dxy_aligned=dxy_aligned, eur_aligned=eur_aligned, gbp_aligned=gbp_aligned,
        divergent=divergent,
    )


def structural_walk(direction: int, eur_by_tf: dict, gbp_by_tf: dict,
                    dxy_by_tf: dict) -> StructuralSMT:
    """Walk W1 -> D1 -> H4 -> H1 -> M15 and return the first TF that
    produces a non-absent SMT read.

    Each `*_by_tf` is a dict keyed by TF string ("W", "D", "240T", "60T",
    "15T") -> list[Bar].
    """
    for tf in _STRUCTURAL_TFS:
        eur = eur_by_tf.get(tf, []) or []
        gbp = gbp_by_tf.get(tf, []) or []
        dxy = dxy_by_tf.get(tf, []) or []
        if not (eur and gbp and dxy):
            continue
        res = structural_on_tf(direction, eur, gbp, dxy)
        if res.state != "absent":
            res.tf = tf
            return res
    return StructuralSMT(
        tf=None, state="absent",
        dxy_aligned=False, eur_aligned=False, gbp_aligned=False,
        divergent=["DXY", "EUR", "GBP"],
    )

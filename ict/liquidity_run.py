"""Liquidity-run (sweep) validation: fake-run vs real-run.

Per user spec:
  - A FAKE run = wick pierces a level but body closes back INSIDE the level
    on the next-higher TF candle. This is the manipulation leg of AMD; we
    trade it as a reversal.
  - A REAL run = body closes BEYOND the level on the next-higher TF candle.
    Continuation, not reversal — skip.

Validation rule:
  - M5 entry trigger -> M15 close decides.
  - M15 entry trigger -> H1 close decides.

Wick depth in pips qualifies / boosts the score:
  - depth >= SWEEP_MIN_PIPS  → valid sweep
  - depth >= SWEEP_STRONG_PIPS → score multiplier (handled in game_theory)
"""

from dataclasses import dataclass
from typing import Optional

import config


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


def _cfg_pips(d: dict, symbol: str) -> float:
    return d.get(symbol, d.get("DEFAULT", 0.0))


@dataclass
class SweepResult:
    valid: bool
    direction: int          # +1 (low swept, expect up), -1 (high swept, expect down)
    swept_level: float
    wick_depth_pips: float
    strong: bool            # depth >= SWEEP_STRONG_PIPS
    reason: str = ""


CONFIRM_TF = {"5T": "15T", "15T": "60T"}


def validate(
    entry_tf_bars: list,
    confirm_tf_bars: list,
    entry_tf: str,
    symbol: str,
    swept_level: float,
    direction: int,
) -> SweepResult:
    """Validate that the most recent action on `entry_tf` is a fake run of
    `swept_level` toward `direction`, confirmed by the matching candle on the
    next higher TF.

    `direction` is the EXPECTED reversal direction (+1 long, -1 short). For a
    long, we expect the LOW (swept_level) to be pierced and price to close
    back above it.
    """
    pip = _pip(symbol)
    min_pips = _cfg_pips(config.SWEEP_MIN_PIPS, symbol)
    strong_pips = _cfg_pips(config.SWEEP_STRONG_PIPS, symbol)
    tol = config.FAKE_RUN_CLOSE_TOL_PIPS * pip

    if not entry_tf_bars:
        return SweepResult(False, direction, swept_level, 0.0, False, "no entry bars")

    last = entry_tf_bars[-1]

    if direction > 0:
        wick_depth = max(0.0, swept_level - last.Low) / pip
        pierced = last.Low < swept_level
        closed_back = last.Close > swept_level - tol
    else:
        wick_depth = max(0.0, last.High - swept_level) / pip
        pierced = last.High > swept_level
        closed_back = last.Close < swept_level + tol

    if not pierced:
        return SweepResult(False, direction, swept_level, 0.0, False, "no piercing")
    if wick_depth < min_pips:
        return SweepResult(False, direction, swept_level, wick_depth, False,
                           f"wick {wick_depth:.1f}p < min {min_pips}p")
    if not closed_back:
        return SweepResult(False, direction, swept_level, wick_depth, False,
                           "entry-TF close did not return inside")

    # Confirm with next-higher TF's most recent CLOSED candle.
    if confirm_tf_bars:
        conf = confirm_tf_bars[-1]
        if direction > 0 and conf.Close <= swept_level - tol:
            return SweepResult(False, direction, swept_level, wick_depth, False,
                               "confirm-TF closed below the swept low (real run)")
        if direction < 0 and conf.Close >= swept_level + tol:
            return SweepResult(False, direction, swept_level, wick_depth, False,
                               "confirm-TF closed above the swept high (real run)")

    return SweepResult(True, direction, swept_level, wick_depth,
                       wick_depth >= strong_pips, "ok")


def confirm_tf_for(entry_tf: str) -> Optional[str]:
    return CONFIRM_TF.get(entry_tf)

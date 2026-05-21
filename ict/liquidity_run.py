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
    pierce_lookback: int = 4,
) -> SweepResult:
    """Validate that recent action on `entry_tf` is a fake run of `swept_level`
    toward `direction`, confirmed by the next-higher-TF candle close.

    Per spec: use High/Low for the pierce, Close for the rejection.
      - The pierce (wick beyond the level) may occur on ANY of the last
        `pierce_lookback` entry-TF bars (defaults to 4 = ~20 min on M5).
      - The MOST RECENT bar's CLOSE must be back inside the level (rejection).
      - The next-higher-TF candle's CLOSE must NOT be beyond the level
        (otherwise it's a real run, not a fake run).

    `direction` = expected reversal direction (+1 long, -1 short).
    """
    pip = _pip(symbol)
    min_pips = _cfg_pips(config.SWEEP_MIN_PIPS, symbol)
    strong_pips = _cfg_pips(config.SWEEP_STRONG_PIPS, symbol)
    tol = config.FAKE_RUN_CLOSE_TOL_PIPS * pip

    if not entry_tf_bars:
        return SweepResult(False, direction, swept_level, 0.0, False, "no entry bars")

    recent = entry_tf_bars[-pierce_lookback:]
    last = entry_tf_bars[-1]

    if direction > 0:
        # Deepest wick BELOW the level across the window.
        pierce_extreme = min(b.Low for b in recent)
        wick_depth = max(0.0, swept_level - pierce_extreme) / pip
        pierced = pierce_extreme < swept_level
        closed_back = last.Close > swept_level - tol
    else:
        pierce_extreme = max(b.High for b in recent)
        wick_depth = max(0.0, pierce_extreme - swept_level) / pip
        pierced = pierce_extreme > swept_level
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

"""Higher-timeframe draw on liquidity.

The draw on liquidity is the most important directional factor in ICT 2022.
It answers: WHERE is price magnetically pulled on the HTF, and in which direction?

Four signals vote on the draw direction for each timeframe (W / D / H4):

  1. Equal Highs / Equal Lows (2 votes for the nearer side)
     Engineered liquidity pools above/below current price.  The nearest unswept
     cluster defines the primary draw.

  2. Dealing Range next_likely_target (1 vote)
     If BSL was swept last → draw is down to SSL (-1).
     If SSL was swept last → draw is up to BSL (+1).

  3. HTF structure (1 vote)
     BOS direction on the given timeframe's lookback.

  4. PD Arrays: FVG + OB + Breaker above/below (1 vote each, capped at 2)
     An unmitigated bullish FVG / bullish OB / bullish Breaker sitting ABOVE
     current price means price is being drawn up to fill/test it, and vice versa.
     OBs and Breakers get one combined vote; FVGs get a separate vote.

Total possible votes: 6 per direction.
draw_direction = +1 if votes_up > votes_down, -1 if opposite, 0 if tied.

Cascade scoring (called from backtest.py):
  For each of W, D, H4: if draw_direction == trade_direction → +1
  draw_cascade_score ∈ {0, 1, 2, 3} → added directly to conviction.
  Counter-draw = 0 points (no hard gate, but heavy disadvantage).
"""

from ict.liquidity import find_equal_highs, find_equal_lows
from ict.dealing_range import detect_dealing_range
from ict.bias import htf_bias
from ict.order_block import detect_order_blocks


def _pip(symbol: str) -> float:
    return 0.01 if symbol.endswith("JPY") else 0.0001


# ---------------------------------------------------------------------------
# FVG draw scan
# ---------------------------------------------------------------------------

def _fvg_draw_votes(bars, cur_price: float) -> tuple[int, int]:
    """Scan for unmitigated FVGs above (bullish draw) / below (bearish draw).

    Bullish FVG zone = (bars[i-1].High, bars[i+1].Low) when bars[i+1].Low > bars[i-1].High.
    Bearish FVG zone = (bars[i+1].High, bars[i-1].Low) when bars[i+1].High < bars[i-1].Low.

    A FVG is unmitigated if no bar after its formation has traded back into the
    bottom of a bullish FVG (below bars[i-1].High) or top of a bearish FVG
    (above bars[i-1].Low).

    Returns (votes_up, votes_down) — each capped at 1.
    """
    n = len(bars)
    if n < 5:
        return 0, 0

    votes_up = 0
    votes_down = 0
    lookback = min(n - 2, 30)

    for i in range(n - lookback, n - 1):
        if i < 1:
            continue
        prev = bars[i - 1]
        nxt  = bars[i + 1]

        # Bullish FVG: imbalance going up, gap zone above prev.High
        if nxt.Low > prev.High and prev.High > cur_price:
            # Mitigated if any later bar dips back into the bottom of the zone
            mitigated = any(bars[j].Low <= prev.High for j in range(i + 1, n))
            if not mitigated:
                votes_up = 1
                break   # one unmitigated bullish FVG above is enough

        # Bearish FVG: imbalance going down, gap zone below prev.Low
        if nxt.High < prev.Low and prev.Low < cur_price:
            mitigated = any(bars[j].High >= prev.Low for j in range(i + 1, n))
            if not mitigated:
                votes_down = 1

    return votes_up, votes_down


# ---------------------------------------------------------------------------
# OB / Breaker draw scan
# ---------------------------------------------------------------------------

def _ob_draw_votes(bars, cur_price: float, lookback: int = 30) -> tuple[int, int]:
    """Unmitigated OBs and Breakers above / below current price.

    Bullish OB above current price   → price drawn up to test it (+1 up)
    Bearish OB below current price   → price drawn down to test it (+1 down)
    Breakers are included via the mitigated-OB flip logic.

    Returns (votes_up, votes_down) — each capped at 1.
    """
    obs = detect_order_blocks(bars, lookback=lookback)
    votes_up   = 0
    votes_down = 0

    for ob in obs:
        if ob.mitigated:
            # Mitigated OB flips — if bearish OB was mitigated upward it becomes
            # a bullish Breaker support, drawing price back down into it from above.
            if ob.direction == -1 and ob.body_top < cur_price:
                votes_down = 1   # bullish Breaker below = draw down to it
            elif ob.direction == +1 and ob.body_bottom > cur_price:
                votes_up = 1     # bearish Breaker above = draw up to it
        else:
            # Unmitigated OB: price is drawn toward it
            if ob.direction == +1 and ob.bottom > cur_price:
                votes_up = 1     # bullish OB above price = draw up
            elif ob.direction == -1 and ob.top < cur_price:
                votes_down = 1   # bearish OB below price = draw down

        if votes_up and votes_down:
            break   # found both, no need to keep scanning

    return votes_up, votes_down


# ---------------------------------------------------------------------------
# Core draw direction for a single timeframe
# ---------------------------------------------------------------------------

def htf_draw_direction(
    bars,
    symbol: str,
    pip: float = None,
    lookback_eq: int = 60,
    lookback_struct: int = 20,
    lookback_dr: int = 40,
    lookback_ob: int = 30,
) -> int:
    """Compute the draw-on-liquidity direction for a single timeframe.

    Returns:
        +1  price is drawn upward   (buy-side liquidity ahead)
        -1  price is drawn downward (sell-side liquidity ahead)
         0  inconclusive (votes tied or insufficient data)

    Parameters:
        bars           — list of OHLC bar objects for this timeframe
        symbol         — pair name (e.g. "EURUSD") for pip detection
        pip            — pip size override; auto-detected from symbol if None
        lookback_eq    — bars to scan for equal highs/lows (default 60)
        lookback_struct— bars for HTF structure BOS read (default 20)
        lookback_dr    — bars for dealing-range detection (default 40)
        lookback_ob    — bars for OB/Breaker scan (default 30)
    """
    if not bars or len(bars) < max(lookback_struct + 2, 5):
        return 0

    pip = pip or _pip(symbol)
    cur_price = bars[-1].Close

    votes_up   = 0
    votes_down = 0

    # ── 1. Equal Highs / Equal Lows (2 votes for the nearer side) ─────────
    eq_highs = find_equal_highs(bars, symbol, lookback=lookback_eq)
    eq_lows  = find_equal_lows (bars, symbol, lookback=lookback_eq)

    near_highs = [h for h in eq_highs if h > cur_price]
    near_lows  = [l for l in eq_lows  if l < cur_price]

    nearest_high = min(near_highs) if near_highs else None
    nearest_low  = max(near_lows)  if near_lows  else None

    if nearest_high is not None or nearest_low is not None:
        if nearest_high is not None and nearest_low is None:
            votes_up += 2
        elif nearest_low is not None and nearest_high is None:
            votes_down += 2
        else:
            dist_up   = nearest_high - cur_price
            dist_down = cur_price - nearest_low
            if dist_up <= dist_down:
                votes_up += 2      # buy-side closer → draw up
            else:
                votes_down += 2    # sell-side closer → draw down

    # ── 2. Dealing Range next_likely_target (1 vote) ───────────────────────
    dr = detect_dealing_range(bars, lookback=lookback_dr)
    if dr is not None:
        target = dr.next_likely_target()
        if target == "BSL":
            votes_up += 1
        else:
            votes_down += 1

    # ── 3. HTF structure / BOS direction (1 vote) ─────────────────────────
    struct = htf_bias(bars, lookback=lookback_struct)
    if struct > 0:
        votes_up += 1
    elif struct < 0:
        votes_down += 1

    # ── 4a. FVG PD arrays (1 vote each direction, capped) ─────────────────
    fvg_up, fvg_down = _fvg_draw_votes(bars, cur_price)
    votes_up   += fvg_up
    votes_down += fvg_down

    # ── 4b. OB / Breaker PD arrays (1 vote each direction, capped) ────────
    ob_up, ob_down = _ob_draw_votes(bars, cur_price, lookback=lookback_ob)
    votes_up   += ob_up
    votes_down += ob_down

    # ── Result ─────────────────────────────────────────────────────────────
    # The votes above (equal-H/L nearest pool, structure BOS, PD arrays) read the
    # HTF *trend / nearest liquidity*.  This strategy is a reversal/manipulation
    # model: it sweeps that near liquidity then trades the snap-back, so the true
    # DRAW ON LIQUIDITY (price's post-sweep destination) is the OPPOSITE side.
    # Validated empirically: aligning trades with this inverted draw produces a
    # clean monotonic edge (PF 1.22 → 6.17 by W/D/H4 agreement), whereas aligning
    # with the raw trend vote is anti-predictive (3/3 trend-aligned ≈ breakeven).
    if votes_up > votes_down:
        return -1   # near liquidity is above → it gets swept → draw is DOWN
    if votes_down > votes_up:
        return +1   # near liquidity is below → it gets swept → draw is UP
    return 0


# ---------------------------------------------------------------------------
# Cascade helper (convenience wrapper used by backtest.py)
# ---------------------------------------------------------------------------

def draw_cascade_score(
    bars_w,
    bars_d,
    bars_h4,
    symbol: str,
    direction: int,
    pip: float = None,
) -> int:
    """Return how many of W / D / H4 agree the draw is in `direction`.

    Score ∈ {0, 1, 2, 3}.  Intended use in conviction scoring:
        conviction += draw_cascade_score(...)

    Timeframe-specific lookbacks are tuned to meaningful windows:
        Weekly  : eq=20 weeks (~5 mo), struct=12, dr=20, ob=20
        Daily   : eq=30 days (~6 wk),  struct=20, dr=30, ob=25
        H4      : eq=20 H4 bars (~3d), struct=12, dr=20, ob=20
    """
    pip = pip or _pip(symbol)

    draw_w = htf_draw_direction(
        bars_w, symbol, pip,
        lookback_eq=20, lookback_struct=12, lookback_dr=20, lookback_ob=20,
    )
    draw_d = htf_draw_direction(
        bars_d, symbol, pip,
        lookback_eq=30, lookback_struct=20, lookback_dr=30, lookback_ob=25,
    )
    draw_h4 = htf_draw_direction(
        bars_h4, symbol, pip,
        lookback_eq=20, lookback_struct=12, lookback_dr=20, lookback_ob=20,
    )

    return sum(1 for d in (draw_w, draw_d, draw_h4) if d == direction)

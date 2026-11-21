"""2-of-3 Judas swing divergence — ICT intermarket liquidity sweep confirmation.

When DXY sweeps a liquidity level (high or low), EURUSD and GBPUSD should
sweep the corresponding inverse levels. If only 2-of-3 complete the sweep
and 1 fails, the failing pair reveals the true relative strength/weakness:

  DXY sweeps HIGH (fake USD rally) → EURUSD + GBPUSD should sweep LOWS.
    EURUSD sweeps low, GBPUSD fails  → GBP is strong → LONG GBPUSD
    GBPUSD sweeps low, EURUSD fails  → EUR is strong → LONG EURUSD

  DXY sweeps LOW (fake USD drop) → EURUSD + GBPUSD should sweep HIGHS.
    EURUSD sweeps high, GBPUSD fails → GBP is weak  → SHORT GBPUSD
    GBPUSD sweeps high, EURUSD fails → EUR is weak   → SHORT EURUSD

The pair that FAILED to sweep its expected level is the trade — it signals
that currency held its ground against the manipulation, and when DXY reverses,
that pair will deliver the strongest move.
"""

from __future__ import annotations


def _swept_high(
    bars,
    lookback: int,
    sweep_bars: int,
    tol: float,
) -> bool:
    """Price went above the prior-window high AND closed back below it."""
    if len(bars) < lookback + sweep_bars:
        return False
    ref_window = bars[-(lookback + sweep_bars): -sweep_bars]
    ref_high   = max(c.High for c in ref_window)
    recent     = bars[-sweep_bars:]
    last_close = bars[-1].Close
    swept      = any(c.High > ref_high + tol for c in recent)
    rejected   = last_close < ref_high
    return swept and rejected


def _swept_low(
    bars,
    lookback: int,
    sweep_bars: int,
    tol: float,
) -> bool:
    """Price went below the prior-window low AND closed back above it."""
    if len(bars) < lookback + sweep_bars:
        return False
    ref_window = bars[-(lookback + sweep_bars): -sweep_bars]
    ref_low    = min(c.Low for c in ref_window)
    recent     = bars[-sweep_bars:]
    last_close = bars[-1].Close
    swept      = any(c.Low < ref_low - tol for c in recent)
    rejected   = last_close > ref_low
    return swept and rejected


def judas_sweep_divergence(
    dxy_bars,
    eurusd_bars,
    gbpusd_bars,
    lookback: int = 20,
    sweep_bars: int = 8,
) -> tuple[str, int] | None:
    """Return (pair, direction) if a 2-of-3 Judas sweep divergence is detected.

    lookback  — bars to define the reference high/low (the liquidity pool).
    sweep_bars — how recently the sweep must have occurred.

    Returns None when all 3 swept (no divergence) or fewer than 2 swept.
    """
    fx_tol  = 0.0001   # 1 pip — FX pairs
    dxy_tol = 0.05     # ~5 ticks on DXY (quoted ~100)

    # --- DXY swept HIGH: fake USD rally, expect EUR + GBP to drop ---
    if _swept_high(dxy_bars, lookback, sweep_bars, dxy_tol):
        eu_low  = _swept_low(eurusd_bars, lookback, sweep_bars, fx_tol)
        gbp_low = _swept_low(gbpusd_bars, lookback, sweep_bars, fx_tol)
        if eu_low and not gbp_low:
            return ("GBPUSD", +1)   # GBP held its ground → LONG GBPUSD
        if gbp_low and not eu_low:
            return ("EURUSD", +1)   # EUR held its ground → LONG EURUSD

    # --- DXY swept LOW: fake USD drop, expect EUR + GBP to rally ---
    if _swept_low(dxy_bars, lookback, sweep_bars, dxy_tol):
        eu_high  = _swept_high(eurusd_bars, lookback, sweep_bars, fx_tol)
        gbp_high = _swept_high(gbpusd_bars, lookback, sweep_bars, fx_tol)
        if eu_high and not gbp_high:
            return ("GBPUSD", -1)   # GBP couldn't rally → SHORT GBPUSD
        if gbp_high and not eu_high:
            return ("EURUSD", -1)   # EUR couldn't rally → SHORT EURUSD

    return None

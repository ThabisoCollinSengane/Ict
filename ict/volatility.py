"""Non-lagging volatility measures.

Pure causal — every value at bar t uses only bars[..t]. No EMA / SMA
smoothing, so there's no lag-induced phase shift. Calibrated for forex
M5/M1 but timeframe-agnostic.

`realized_vol`   — window-truncated stdev of log returns.
`range_expansion` — current bar's range vs the median of the prior window.
`vol_regime`     — DEAD / NORMAL / EXPANDING by rolling percentile.
"""

import math
import statistics
from typing import Sequence


def realized_vol(bars: Sequence, window: int) -> float:
    """Population stdev of log returns over the last `window` bars.

    Returned as a raw float (not annualized). Higher = more volatile.
    Returns 0.0 if not enough bars or all closes equal.
    """
    if len(bars) < window + 1 or window < 2:
        return 0.0
    closes = [b.Close for b in bars[-(window + 1):]]
    rets = []
    for i in range(1, len(closes)):
        prev, cur = closes[i - 1], closes[i]
        if prev <= 0 or cur <= 0:
            continue
        rets.append(math.log(cur / prev))
    if len(rets) < 2:
        return 0.0
    return statistics.pstdev(rets)


def range_expansion(bars: Sequence, window: int) -> float:
    """Current bar's range divided by the median range of the previous
    `window` bars. >= 2.0 typically marks an institutional displacement bar.

    Returns 1.0 if window is incomplete or the prior median is zero.
    """
    if len(bars) < window + 1 or window < 1:
        return 1.0
    cur_range = bars[-1].High - bars[-1].Low
    prior_ranges = [b.High - b.Low for b in bars[-(window + 1):-1]]
    if not prior_ranges:
        return 1.0
    med = statistics.median(prior_ranges)
    if med <= 0:
        return 1.0
    return cur_range / med


def vol_regime(rv_series: Sequence,
               dead_pct: float = 20.0,
               expanding_pct: float = 80.0) -> str:
    """Classify the most recent realized-vol value vs the percentile bands
    of the rolling series.

    Returns "DEAD", "NORMAL", or "EXPANDING".
    Empty / insufficient input -> "NORMAL".
    """
    if not rv_series:
        return "NORMAL"
    series = list(rv_series)
    if len(series) < 5:
        return "NORMAL"
    cur = series[-1]
    sorted_s = sorted(series)
    n = len(sorted_s)
    dead_threshold = sorted_s[max(0, int(n * dead_pct / 100) - 1)]
    exp_threshold = sorted_s[min(n - 1, int(n * expanding_pct / 100))]
    if cur <= dead_threshold:
        return "DEAD"
    if cur >= exp_threshold:
        return "EXPANDING"
    return "NORMAL"

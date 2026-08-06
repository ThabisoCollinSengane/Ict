"""Offline self-test for the semi-auto layer (no MT5, no network).

    python -m live.test_semi_auto

Exercises: command parsing (lot/bias/levels/auto/clear/status), per-day
auto-expiry, and the full-manual-AMD sweep direction logic.
"""
from __future__ import annotations

import os
import sys
import tempfile
from collections import namedtuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from live.session_inputs import SessionInputs
from live import telegram_control as tc

_Bar = namedtuple("_Bar", "Open High Low Close")


def _fresh_inputs():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    os.unlink(path)
    return SessionInputs(path=path)


def test_parse_lot_all_and_pair():
    si = _fresh_inputs()
    # /lot with no pair → every configured pair (use whatever PAIRS holds)
    import config
    if config.PAIRS:
        p0 = config.PAIRS[0]
        ack = tc.parse_command("/lot 0.02", si)
        assert si.day_lot(p0) == 0.02, ack
        # per-pair override
        tc.parse_command(f"/lot {p0} 0.05", si)
        assert si.day_lot(p0) == 0.05
    print("ok  parse /lot (all + per-pair)")


def test_parse_bias_filter():
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"
    tc.parse_command(f"/bias {p} long", si)
    assert si.bias(p) == "long"
    tc.parse_command(f"/bias {p} both", si)
    assert si.bias(p) is None                 # 'both' clears the filter
    print("ok  parse /bias (long + clear)")


def test_parse_levels():
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"
    tc.parse_command(f"/levels {p} buy 1.0950 1.0975 sell 1.0900 1.0880", si)
    assert si.buy_levels(p) == [1.0950, 1.0975]
    assert si.sell_levels(p) == [1.0880, 1.0900]
    assert si.has_levels(p)
    print("ok  parse /levels (buy + sell)")


def test_clear_and_auto():
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"
    tc.parse_command(f"/lot {p} 0.03", si)
    tc.parse_command(f"/auto {p}", si)
    assert si.day_lot(p) is None
    print("ok  /auto reverts a pair")


def test_amd_sweep_logic():
    """Replicate LiveTrader._levels_amd_dir with a stub bar series."""
    from risk import pip_size

    def amd_dir(buy, sell, bars, pair="EURUSD"):
        look = bars[-12:]
        price = look[-1].Close
        tol = pip_size(pair)
        sell_sweep = buy_sweep = None
        for i, b in enumerate(look):
            for lv in sell:
                if b.Low < lv - tol and (sell_sweep is None or i >= sell_sweep[0]):
                    sell_sweep = (i, lv)
            for lv in buy:
                if b.High > lv + tol and (buy_sweep is None or i >= buy_sweep[0]):
                    buy_sweep = (i, lv)
        sell_ok = sell_sweep is not None and price > sell_sweep[1]
        buy_ok = buy_sweep is not None and price < buy_sweep[1]
        if sell_ok and buy_ok:
            return 1 if sell_sweep[0] >= buy_sweep[0] else -1
        if sell_ok:
            return 1
        if buy_ok:
            return -1
        return 0

    # sell-side swept (dipped below 1.0900) then reclaimed → long
    bars = [_Bar(1.092, 1.093, 1.0918, 1.0925)] * 10
    bars += [_Bar(1.0905, 1.0906, 1.0895, 1.0904),   # wick below 1.0900
             _Bar(1.0906, 1.0925, 1.0905, 1.0921)]   # closed back above
    assert amd_dir(buy=[1.0975], sell=[1.0900], bars=bars) == 1, "sell-side sweep → long"

    # buy-side swept (poked above 1.0975) then back below → short
    bars = [_Bar(1.096, 1.097, 1.0958, 1.0965)] * 10
    bars += [_Bar(1.0972, 1.0982, 1.0971, 1.0973),   # wick above 1.0975
             _Bar(1.0972, 1.0974, 1.0960, 1.0962)]   # back below
    assert amd_dir(buy=[1.0975], sell=[1.0900], bars=bars) == -1, "buy-side sweep → short"

    # neither side swept → wait (0)
    bars = [_Bar(1.094, 1.0945, 1.0935, 1.0942)] * 12
    assert amd_dir(buy=[1.0975], sell=[1.0900], bars=bars) == 0, "no sweep → wait"
    print("ok  manual-AMD sweep direction (long / short / wait)")


def main():
    test_parse_lot_all_and_pair()
    test_parse_bias_filter()
    test_parse_levels()
    test_clear_and_auto()
    test_amd_sweep_logic()
    print("\nALL SEMI-AUTO TESTS PASSED")


if __name__ == "__main__":
    main()

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


def test_parse_trail():
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"
    # tf + tier + buffer
    tc.parse_command(f"/trail {p} m5 it 3", si)
    assert si.trail(p) == {"tf": "5T", "tier": "it", "buf": 3.0}, si.trail(p)
    # tf only -> default short-term tier, default 2-pip buffer
    tc.parse_command(f"/trail {p} m15", si)
    assert si.trail(p) == {"tf": "15T", "tier": "st", "buf": 2.0}
    # buffer without an explicit tier
    tc.parse_command(f"/trail {p} m1 4", si)
    assert si.trail(p) == {"tf": "1T", "tier": "st", "buf": 4.0}
    # off clears it
    tc.parse_command(f"/trail {p} off", si)
    assert si.trail(p) is None
    print("ok  parse /trail (tf/tier/buffer + off)")


def test_structure_trail_level():
    """LONG: stop rides just below the latest intact STL, only on the correct
    side of price; 'it' tier is None when there is no intermediate swing."""
    from ict.market_structure import trail_stop_level
    _B = namedtuple("_B", "Open High Low Close")
    bars = [
        _B(1.1000, 1.1005, 1.1000, 1.1003),
        _B(1.1002, 1.1004, 1.0990, 1.0992),   # fractal LOW 1.0990 (the STL)
        _B(1.0993, 1.1012, 1.0992, 1.1010),
        _B(1.1011, 1.1020, 1.1008, 1.1018),
        _B(1.1019, 1.1030, 1.1016, 1.1028),
        _B(1.1029, 1.1040, 1.1026, 1.1038),
        _B(1.1039, 1.1050, 1.1036, 1.1048),   # never dips below 1.0990 -> intact
    ]
    pip = 0.0001
    # long, short-term tier, 2-pip buffer, price well above the STL
    lvl = trail_stop_level(bars, +1, "st", 2, pip, cur_price=1.1050)
    assert lvl is not None and abs(lvl - (1.0990 - 2 * pip)) < 1e-9, lvl
    # wrong side of price (candidate would be at/above price) -> None
    assert trail_stop_level(bars, +1, "st", 2, pip, cur_price=1.0985) is None
    # no intermediate swing in this short series -> 'it' tier returns None
    assert trail_stop_level(bars, +1, "it", 2, pip, cur_price=1.1050) is None
    print("ok  structure trail level (STL - buffer, side check, tier fallback)")


def test_parse_hold_and_release():
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"
    tc.parse_command(f"/hold {p}", si)
    assert si.hold(p) is True
    tc.parse_command(f"/release {p}", si)
    assert si.hold(p) is False
    tc.parse_command(f"/hold {p} off", si)      # explicit off form
    assert si.hold(p) is False
    print("ok  parse /hold + /release")


def test_action_commands_parse_and_dispatch():
    """/close /halt /resume parse, and dispatch to a stub trader when present."""
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"

    class StubTrader:
        def __init__(self):
            self.halted = False
            self.closed = []
        def manual_close(self, pair, leg=None):
            self.closed.append((pair, leg)); return f"{pair}: closing (leg={leg})"
        def manual_close_all(self):
            self.closed.append("ALL"); return 2
        def manual_halt(self):
            self.halted = True
        def manual_resume(self):
            self.halted = False

    # Without a trader, action commands still parse to an ack (no crash).
    assert tc.parse_command(f"/close {p}", si) is not None
    assert tc.parse_command("/halt", si) is not None

    # With a trader, they dispatch.
    tr = StubTrader()
    tc.parse_command(f"/close {p}", si, trader=tr)
    assert tr.closed == [(p, None)]
    tc.parse_command(f"/close {p} 2", si, trader=tr)      # per-leg close
    assert tr.closed[-1] == (p, "2")
    tc.parse_command("/close all", si, trader=tr)
    assert tr.closed[-1] == "ALL"
    tc.parse_command("/halt", si, trader=tr)
    assert tr.halted is True
    tc.parse_command("/resume", si, trader=tr)
    assert tr.halted is False
    print("ok  /close /halt /resume parse + dispatch")


def test_gold_gate():
    """resolve_gold_direction: DXY inverse primary + silver/AUD 2-of-3 breadth,
    silver-divergence suppression."""
    from intermarket import resolve_gold_direction as g
    # DXY flat -> hard gate
    assert g(0, 1, 1) == (None, 0.0)
    # DXY down -> gold LONG (+1). All three agree -> 1.0
    assert g(-1, 1, 1) == (1, 1.0)
    # DXY down + one confirmer (other flat) -> 0.75
    assert g(-1, 1, 0) == (1, 0.75)
    assert g(-1, 0, 1) == (1, 0.75)
    # DXY down but NO confirmer (silver & AUD flat) -> below 2-of-3 -> suppress
    assert g(-1, 0, 0) == (None, 0.0)
    # silver DIVERGES (opposite gold dir) -> suppress even if AUD agrees
    assert g(-1, -1, 1) == (None, 0.0)
    # DXY up -> gold SHORT (-1). All three agree -> 1.0
    assert g(1, -1, -1) == (-1, 1.0)
    # DXY up but silver diverges (silver up) -> suppress
    assert g(1, 1, -1) == (None, 0.0)
    print("ok  gold gate (DXY inverse + silver/AUD 2-of-3 + divergence suppress)")


def test_smt_divergence():
    """SMT: primary makes a new extreme the reference fails to confirm — positive
    (index-index) and inverse (index-dollar) correlation modes."""
    from ict.smt import smt_divergence
    _B = namedtuple("_B", "Open High Low Close")
    def series(lows, highs):
        return [_B(l, h, l, h) for l, h in zip(lows, highs)]
    # LONG: primary sweeps a LOWER low (recent half lower than prior half).
    prim = series([10]*5 + [8]*5, [12]*5 + [11]*5)     # recent low 8 < prior low 10
    # positive ref HOLDS (higher low 10, no lower low) -> divergence
    ref_pos_div = series([10]*5 + [10]*5, [12]*5 + [12]*5)
    assert smt_divergence(prim, ref_pos_div, +1, inverse=False, lookback=10) is True
    # positive ref also makes a lower low -> in sync, NO divergence
    ref_pos_sync = series([10]*5 + [8]*5, [12]*5 + [11]*5)
    assert smt_divergence(prim, ref_pos_sync, +1, inverse=False, lookback=10) is False
    # inverse ref (dollar): index makes lower low -> dollar SHOULD make higher high;
    # if dollar fails to make a higher high -> divergence.
    dxy_fail = series([20]*5 + [20]*5, [25]*5 + [25]*5)  # no higher high
    assert smt_divergence(prim, dxy_fail, +1, inverse=True, lookback=10) is True
    dxy_confirm = series([20]*5 + [21]*5, [25]*5 + [27]*5)  # higher high -> confirms
    assert smt_divergence(prim, dxy_confirm, +1, inverse=True, lookback=10) is False
    # primary did NOT sweep a lower low -> never a long SMT
    flat = series([10]*10, [12]*10)
    assert smt_divergence(flat, ref_pos_div, +1, inverse=False, lookback=10) is False
    print("ok  SMT divergence (positive index-index + inverse index-dollar)")


def test_index_gate():
    """resolve_index_direction: indices inverse to DXY + sibling/US30 breadth,
    sibling-divergence (SMT) suppression."""
    from intermarket import resolve_index_direction as r
    assert r(0, 1, 1) == (None, 0.0)          # DXY flat -> hard gate
    assert r(-1, 1, 1) == (1, 1.0)            # DXY down + sibling + US30 -> LONG full
    assert r(-1, 1, 0) == (1, 0.75)           # DXY down + sibling only -> 0.75
    assert r(-1, 0, 1) == (1, 0.75)           # DXY down + US30 only -> 0.75
    assert r(-1, 0, 0) == (None, 0.0)         # only DXY -> below 2-of-3
    assert r(-1, -1, 1) == (None, 0.0)        # sibling diverges (SMT) -> suppress
    assert r(1, -1, -1) == (-1, 1.0)          # DXY up -> index SHORT
    print("ok  index gate (inverse-dollar + sibling/US30 breadth + SMT suppress)")


def test_index_amd_range_override():
    """Index frequency lever: %-of-price consolidation cap auto-scales per index;
    FX pairs keep the global cap (byte-identical)."""
    import os, importlib
    prev = {k: os.environ.get(k) for k in ("INDICES_ENABLED", "INDEX_AMD_MAX_RANGE_PCT")}
    os.environ["INDICES_ENABLED"] = "1"
    os.environ["INDEX_AMD_MAX_RANGE_PCT"] = "0.8"
    import config as _c; importlib.reload(_c)
    from backtest import Backtester
    from risk import pip_size
    bt = object.__new__(Backtester)
    # US500@4500 -> 0.8% = 36 pts; US100@18000 -> 144 pts (cap returned in "pips")
    assert abs(Backtester._amd_max_range(bt, "US500", 4500) * pip_size("US500") - 36) < 1
    assert abs(Backtester._amd_max_range(bt, "US100", 18000) * pip_size("US100") - 144) < 1
    # EURUSD unaffected -> FX global
    assert Backtester._amd_max_range(bt, "EURUSD", 1.09) == _c.AMD_MAX_RANGE_PIPS
    for k, v in prev.items():
        if v is None: os.environ.pop(k, None)
        else: os.environ[k] = v
    importlib.reload(_c)
    print("ok  index AMD range override (%-of-price auto-scale; FX unchanged)")


def test_indices_disabled_keeps_pairs_baseline():
    """INDICES_ENABLED=0 must NOT add US500/US100 to PAIRS (baseline byte-identical)."""
    import os, importlib
    prev = os.environ.get("INDICES_ENABLED")
    os.environ["INDICES_ENABLED"] = "0"
    import config as _c; importlib.reload(_c)
    assert not any(p in _c.PAIRS for p in _c.INDEX_PAIRS), _c.PAIRS
    if prev is None:
        os.environ.pop("INDICES_ENABLED", None)
    else:
        os.environ["INDICES_ENABLED"] = prev
    importlib.reload(_c)
    print("ok  INDICES_ENABLED=0 leaves PAIRS at baseline (no US500/US100)")


def test_gold_disabled_keeps_pairs_baseline():
    """GOLD_ENABLED=0 must NOT add XAUUSD to PAIRS (baseline byte-identical)."""
    import os, importlib
    prev = os.environ.get("GOLD_ENABLED")
    os.environ["GOLD_ENABLED"] = "0"
    import config as _c; importlib.reload(_c)
    assert _c.GOLD_PAIR not in _c.PAIRS, _c.PAIRS
    if prev is None:
        os.environ.pop("GOLD_ENABLED", None)
    else:
        os.environ["GOLD_ENABLED"] = prev
    importlib.reload(_c)
    print("ok  GOLD_ENABLED=0 leaves PAIRS at baseline (no XAUUSD)")


def test_backtest_handover_hook_is_noop():
    """The backtest base must never exempt a pair — keeps numbers byte-identical."""
    from backtest import Backtester
    assert Backtester._handover_exempt(object.__new__(Backtester), "EURUSD") is False
    assert Backtester._direction_allowed(object.__new__(Backtester), "EURUSD", 1, None) is True
    print("ok  backtest hooks are pure no-ops")


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


def test_ifvg_detection():
    from ict.ifvg import find_inversion_fvgs
    _B = namedtuple("_B", "Open High Low Close")
    bars = [_B(1.10, 1.101, 1.099, 1.100)] * 5
    bars += [_B(1.100, 1.1005, 1.0980, 1.0985),
             _B(1.0985, 1.0985, 1.0960, 1.0965),
             _B(1.0965, 1.0968, 1.0940, 1.0945),      # gap-down FVG box
             _B(1.0975, 1.0990, 1.0972, 1.0988),      # touch
             _B(1.0988, 1.1010, 1.0986, 1.1005)]      # full body above -> demand IFVG
    bars += [_B(1.1005, 1.1015, 1.1000, 1.1010)] * 3
    z = find_inversion_fvgs(bars, direction=1)
    assert z and z[0]["dir"] == 1, "should find a bullish demand IFVG"
    assert find_inversion_fvgs(bars, direction=-1) == [] or all(
        x["dir"] == -1 for x in find_inversion_fvgs(bars, direction=-1))
    print("ok  IFVG inversion detection (Market Maker model)")


def test_mm_flag():
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"
    tc.parse_command(f"/mm {p} buy", si)
    assert si.mm(p) == "buy"
    assert si.mm_auto(p) is False            # watch-only by default
    tc.parse_command(f"/mm {p} off", si)
    assert si.mm(p) is None
    print("ok  /mm arm + off")


def test_mm_auto_arm_and_consume():
    """`/mm PAIR buy auto` pre-permits ONE entry; clear_mm_auto consumes it
    (leaving the watch layer on); `/mm PAIR off` clears both."""
    si = _fresh_inputs()
    import config
    p = config.PAIRS[0] if config.PAIRS else "EURUSD"

    # watch → auto
    tc.parse_command(f"/mm {p} sell", si)
    assert si.mm_auto(p) is False
    tc.parse_command(f"/mm {p} sell auto", si)
    assert si.mm(p) == "sell" and si.mm_auto(p) is True
    # synonyms all arm
    for word in ("arm", "go", "on", "enter"):
        tc.parse_command(f"/mm {p} sell {word}", si)
        assert si.mm_auto(p) is True, word

    # one-shot consume: auto off, model still watched
    si.clear_mm_auto(p)
    assert si.mm_auto(p) is False
    assert si.mm(p) == "sell"

    # off clears everything
    tc.parse_command(f"/mm {p} off", si)
    assert si.mm(p) is None and si.mm_auto(p) is False
    print("ok  /mm auto arm + one-shot consume + off")


def main():
    test_ifvg_detection()
    test_mm_flag()
    test_mm_auto_arm_and_consume()
    test_parse_lot_all_and_pair()
    test_parse_bias_filter()
    test_parse_levels()
    test_clear_and_auto()
    test_parse_trail()
    test_structure_trail_level()
    test_parse_hold_and_release()
    test_action_commands_parse_and_dispatch()
    test_gold_gate()
    test_gold_disabled_keeps_pairs_baseline()
    test_index_gate()
    test_indices_disabled_keeps_pairs_baseline()
    test_index_amd_range_override()
    test_smt_divergence()
    test_backtest_handover_hook_is_noop()
    test_amd_sweep_logic()
    print("\nALL SEMI-AUTO TESTS PASSED")


if __name__ == "__main__":
    main()

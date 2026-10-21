"""Unit tests for ict/market_structure.py — fractal LTH/ITH/STH classifier.

Run: python test_market_structure.py
Plain-assert style (repo has no pytest dependency).
"""

from dataclasses import dataclass
from ict import market_structure as ms


@dataclass
class Bar:
    High: float
    Low: float
    Close: float = 0.0
    Open: float = 0.0


def mk(pairs):
    """pairs: list of (high, low) → list of Bars."""
    return [Bar(High=h, Low=l, Close=(h + l) / 2) for h, l in pairs]


def test_basic_swings():
    bars = mk([(1.0, 0.9), (1.1, 1.0), (1.2, 1.1), (1.1, 1.0),
               (1.0, 0.9), (1.1, 1.0), (1.2, 1.1)])
    r = ms.classify(bars)
    assert len(r["sth"]) >= 1
    assert len(r["stl"]) >= 1


def test_fractal_recursion():
    bars = mk([(1.0, 0.9), (1.2, 1.0), (1.0, 0.8),
               (1.3, 1.1), (1.5, 1.2), (1.3, 1.0),
               (1.1, 0.9), (1.3, 1.0), (1.1, 0.8)])
    r = ms.classify(bars)
    iths = [round(s.price, 2) for s in r["ith"]]
    assert len(r["ith"]) >= 1
    assert any(abs(p - 1.5) < 0.01 for p in iths)


def test_swept_flag():
    bars = mk([(1.0, 0.9), (1.2, 1.0), (1.0, 0.8),
               (1.1, 0.9), (1.5, 1.2), (1.3, 1.0)])
    r = ms.classify(bars)
    swept = {round(s.price, 2): s.swept for s in r["sth"]}
    assert swept.get(1.2) is True


def test_last_intact_skips_swept():
    bars = mk([(1.0, 0.9), (1.2, 1.0), (1.0, 0.8),
               (1.1, 0.9), (1.5, 1.2), (1.3, 1.0)])
    r = ms.classify(bars)
    li = ms.last_intact(r, "STH")
    assert li is None or li.price != 1.2


def test_empty_and_tiny_safe():
    empty = {k: [] for k in ("sth", "stl", "ith", "itl", "lth", "ltl")}
    assert ms.classify([]) == empty
    assert ms.classify(mk([(1.0, 0.9)]))["sth"] == []
    assert ms.last_intact(ms.classify([]), "LTH") is None
    assert ms.structure_direction(ms.classify([])) == 0
    assert ms.is_minor_sweep(ms.classify([]), +1) is False


def test_direction_and_sweep_return_types():
    bars = mk([(1.0, 0.90), (1.2, 0.80), (1.0, 0.85), (1.3, 1.00),
               (1.1, 0.90), (1.4, 0.95), (1.2, 0.88), (1.5, 1.05),
               (1.3, 0.98), (1.6, 1.10), (1.4, 1.02)])
    r = ms.classify(bars)
    assert ms.structure_direction(r) in (-1, 0, 1)
    assert isinstance(ms.is_minor_sweep(r, +1), bool)
    assert isinstance(ms.is_minor_sweep(r, -1), bool)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        t()
        print(f"  PASS  {t.__name__}")
        passed += 1
    print(f"\n{passed}/{len(tests)} tests passed ✅")

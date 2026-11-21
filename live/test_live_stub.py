"""Offline drive of the LIVE engine on a fake MT5 feed (no terminal, no network).

    python -m live.test_live_stub [--days 6] [--seed 7]

Why this exists: LiveTrader inherits every signal method from Backtester but does
NOT call Backtester.__init__, so any state the backtest sets up in __init__ and
the live class forgets is an AttributeError that only appears on a live entry
check. py_compile and unit tests of the pure logic never reach it (the project's
P47/P48/P63 lesson). This module swaps `live.mt5_connector` for an in-memory fake
(random-walk M1 for every symbol, aggregated to any timeframe, orders always
fill), constructs LiveTrader, and walks the real `_run_once` loop bar by bar
through the killzones, plus direct calls into the MM-model helpers. Any exception
fails the run and is printed with its traceback.
"""
from __future__ import annotations

import argparse
import os
import sys
import traceback
import types
from collections import Counter, namedtuple
from datetime import datetime, timedelta, timezone

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

Bar = namedtuple("Bar", "time open high low close volume")
Acc = namedtuple("Acc", "login balance equity margin_free currency leverage server")

_TF_MIN = {"1T": 1, "5T": 5, "10T": 10, "15T": 15, "20T": 20, "30T": 30, "60T": 60,
           "240T": 240, "D": 1440, "W": 10080}
_START = {"EURUSD": 1.08, "GBPUSD": 1.27, "NZDUSD": 0.61, "EURGBP": 0.85, "AUDNZD": 1.09,
          "AUDUSD": 0.66, "USDJPY": 150.0, "USDCAD": 1.36, "USDSEK": 10.5, "USDCHF": 0.88}


def make_fake_mt(days: int, seed: int, end: datetime):
    """Build a module object exposing the slice of live.mt5_connector the engine uses."""
    rng = np.random.default_rng(seed)
    n = days * 1440 + 1440
    t0 = end - timedelta(minutes=n)
    times = np.array([int((t0 + timedelta(minutes=i)).timestamp()) for i in range(n)])
    common = rng.normal(0, 1, n)                       # shared dollar factor
    m1 = {}
    for sym, p0 in _START.items():
        vol = p0 * 0.00012
        sign = -1 if sym.startswith("USD") else 1
        steps = (0.6 * sign * common + 0.8 * rng.normal(0, 1, n)) * vol
        close = p0 + np.cumsum(steps)
        opn = np.r_[close[0], close[:-1]]
        wick = np.abs(rng.normal(0, vol, n))
        m1[sym] = (opn, np.maximum(opn, close) + wick, np.minimum(opn, close) - wick, close)

    mod = types.ModuleType("live.mt5_connector")
    mod.NOW = end
    mod.MT5_MAGIC = 770022
    mod.TRADEABLE = ("EURUSD", "GBPUSD", "NZDUSD")
    mod.INTERMARKET = ("EURGBP", "AUDNZD", "AUDUSD")
    mod.DXY_CONSTITUENTS = ("EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF")
    mod.ALL_SYMBOLS = tuple(dict.fromkeys(mod.TRADEABLE + mod.INTERMARKET + mod.DXY_CONSTITUENTS))
    mod.orders = []
    mod.calls = Counter()

    def resolve_symbol(base):
        return base if base in m1 else None

    def _upto():
        return int(np.searchsorted(times, int(mod.NOW.timestamp()), side="right"))

    def get_bars(base, tf, count, include_forming=False):
        mod.calls[(base, tf)] += 1
        if base not in m1 or tf not in _TF_MIN:
            return []
        k = _upto()                                    # M1 bars that have started by NOW
        o, h, l, c = (a[:k] for a in m1[base])
        tt = times[:k]
        step = _TF_MIN[tf] * 60
        key = tt // step
        out = []
        starts = np.r_[0, np.nonzero(np.diff(key))[0] + 1]
        ends = np.r_[starts[1:], len(key)]
        for s, e in zip(starts, ends):
            out.append(Bar(int(key[s] * step), float(o[s]), float(h[s:e].max()),
                           float(l[s:e].min()), float(c[e - 1]), float(e - s)))
        if out and not include_forming:
            out = out[:-1]                             # the live connector drops it
        return out[-count:]

    def tick(base):
        if base not in m1:
            return None
        c = float(m1[base][3][max(_upto() - 1, 0)])
        return (c - 0.00004, c + 0.00004)

    def account():
        return Acc(1, 1000.0 / 18.5, 1000.0 / 18.5, 1000.0, "USD", 500, "stub")

    def market_order(base, lots, direction, sl=None, tp=None, comment="", **kw):
        mod.orders.append((mod.NOW, base, lots, direction, sl, tp, comment))
        return {"ok": True, "ticket": len(mod.orders), "retcode": 0, "comment": "stub"}

    mod.resolve_symbol = resolve_symbol
    mod.resolve_all = lambda symbols=None: {s: s for s in m1}
    mod.get_bars = get_bars
    mod.tick = tick
    mod.pip_size = lambda b: 0.01 if b.endswith("JPY") else 0.0001
    mod.account = account
    mod.positions = lambda base=None: []
    mod.market_order = market_order
    mod.modify_sl_tp = lambda *a, **k: True
    mod.close_position = lambda *a, **k: True
    mod.connect = lambda **k: True
    mod.shutdown = lambda: None
    mod.wait_for_bar = lambda *a, **k: True
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=6)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    os.chdir(ROOT)
    os.makedirs("data", exist_ok=True)
    end = datetime(2026, 3, 13, 21, 0, tzinfo=timezone.utc)      # a Friday evening
    fake = make_fake_mt(a.days + 30, a.seed, end)
    sys.modules["live.mt5_connector"] = fake
    import live
    live.mt5_connector = fake
    import config
    config.FOREXFACTORY_XML_URL = "http://127.0.0.1:9/none"      # no network: CSV fallback
    from live import run_live
    run_live._notify = lambda msg: True

    start = end - timedelta(days=a.days)
    fake.NOW = start
    trader = run_live.LiveTrader()
    errors = Counter()
    first = {}

    def guard(label, fn, *args):
        try:
            return fn(*args)
        except Exception as e:                          # noqa: BLE001
            k = f"{label}: {type(e).__name__}: {e}"
            errors[k] += 1
            first.setdefault(k, traceback.format_exc())
            return None

    t = start
    steps = 0
    while t <= end:
        fake.NOW = t
        if t.weekday() < 5:
            guard("_run_once", trader._run_once, t)
            steps += 1
        t += timedelta(minutes=5)

    # Direct calls into the MM-model helpers at a London-killzone moment.
    fake.NOW = datetime(2026, 3, 12, 8, 30, tzinfo=timezone.utc)
    now = fake.NOW
    for label, fn, args in [
        ("_prev_session_range", trader._prev_session_range, ("EURUSD", now)),
        ("_mm_quadrant", trader._mm_quadrant, (now,)),
        ("_dealing_range_cascade(UDXUSD)", trader._dealing_range_cascade, ("UDXUSD", now)),
        ("_htf_pair_smt", trader._htf_pair_smt, ("EURUSD", 1, now)),
        ("_disp_mss(UDXUSD)", trader._disp_mss, ("UDXUSD", -1, now)),
        ("_smtx", trader._smtx, (1, now)),
        ("_mm_golden_entry(EURUSD)", trader._mm_golden_entry, ("EURUSD", now)),
        ("_mm_golden_entry(GBPUSD)", trader._mm_golden_entry, ("GBPUSD", now)),
    ]:
        r = guard(label, fn, *args)
        print(f"  {label:34s} -> {r!r}"[:160])

    # Forced MM open: replace the backtest MM decision with a fixed position so the
    # live wrapper (forming-bar mode, direction filter, MT5 order) is exercised even
    # when the random feed never produces a full MM setup.
    from backtest import Backtester
    real = Backtester._mm_golden_entry
    seen_forming = []

    def fake_entry(self, pair, t):
        seen_forming.append(self._bars_forming)
        px = fake.tick(pair)[0]
        self.active[pair] = {"direction": -1, "target": px - 0.0040, "entry_model": "mm_golden",
                             "im_scenario": "golden", "legs": [{"entry": px, "stop": px + 0.0008,
                             "units": 2000, "leg_idx": 1, "opened_at": t}]}
    Backtester._mm_golden_entry = fake_entry
    try:
        trader.active.pop("GBPUSD", None)
        n0 = len(fake.orders)
        guard("forced_mm_open", trader._mm_golden_entry, "GBPUSD", now)
        ok_open = len(fake.orders) == n0 + 1 and fake.orders[-1][6] == "ict_mm" and "GBPUSD" in trader.active
        trader.active.pop("GBPUSD", None)
        trader.inputs.bias = lambda pair: "long"          # trader set /bias GBPUSD long
        n1 = len(fake.orders)
        guard("forced_mm_filtered", trader._mm_golden_entry, "GBPUSD", now)
        ok_filter = len(fake.orders) == n1 and "GBPUSD" not in trader.active
        print(f"  forced MM open sends ict_mm order: {ok_open}; /bias filter blocks it: {ok_filter}; "
              f"forming-bar mode inside: {seen_forming}; after: {trader._bars_forming}")
        if not (ok_open and ok_filter and all(seen_forming) and not trader._bars_forming):
            errors["forced MM wrapper check failed"] += 1
            first.setdefault("forced MM wrapper check failed", "")
    finally:
        Backtester._mm_golden_entry = real

    print(f"\nwalked {steps} M5 steps; orders sent {len(fake.orders)}; "
          f"open {list(trader.active)}; trades closed {len(trader.trades)}")
    for o in fake.orders:
        print("  ORDER", o)
    g = trader.gate
    print("  funnel:", {k: g[k] for k in ("checks", "in_killzone", "news_clear",
                                         "consolidation_found", "entry_opened") if k in g})
    mm = {k: v for k, v in g.items() if k.startswith(("mm_", "mm_quad"))}
    print("  mm counters:", dict(sorted(mm.items(), key=lambda kv: -kv[1])[:14]))
    print("  UDXUSD fetches:", sum(v for (s, _tf), v in fake.calls.items() if s == "UDXUSD"))
    if errors:
        print(f"\nFAIL — {sum(errors.values())} exceptions, {len(errors)} distinct:")
        for k, v in errors.most_common():
            print(f"\n[{v}x] {k}\n{first[k]}")
        return 1
    print("\nOK — no exceptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

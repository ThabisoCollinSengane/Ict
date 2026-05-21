"""Synthetic-data smoke test: exercises every new module to confirm the
pipeline runs without crashing. Not a behavioral test — just import + shape.
"""

import math
import random
from collections import namedtuple
from datetime import timedelta

import pandas as pd

import config
from ict.swings import find_swings, last_swing_high, last_swing_low
from ict.structure import classify_intermediates, directional_pull
from ict.mss import latest_mss, mss_direction
from ict.fvg import enumerate_fvgs, first_fvg_after, detect_new_fvg
from ict.order_block import detect_order_blocks
from ict.breaker import detect_breakers
from ict.levels import build_day_levels
from ict.cls_cycles import cbdr_hl, cycle_phases, in_macro_window
from ict.liquidity_zones import collect_zones, most_recent_tap
from ict.liquidity_run import validate as validate_sweep
from ict.smt import confirm as smt_confirm
from ict.intermarket import resolve as resolve_intermarket
from ict.target import pick as pick_target
from ict.game_theory import score_setup, passes as gt_passes
from ict.entry import build as build_entry
from ict.killzones import in_used_killzone, first_hour_elapsed, can_enter_new_pipeline


Bar = namedtuple("Bar", "Open High Low Close")


def synth_bars(n=400, seed=42, drift=0.0):
    random.seed(seed)
    px = 1.10
    bars = []
    for _ in range(n):
        o = px
        c = px + random.gauss(drift, 0.001)
        h = max(o, c) + abs(random.gauss(0, 0.0005))
        l = min(o, c) - abs(random.gauss(0, 0.0005))
        bars.append(Bar(o, h, l, c))
        px = c
    return bars


def synth_df(n=400, seed=42, drift=0.0):
    bars = synth_bars(n, seed, drift)
    idx = pd.date_range("2024-01-01", periods=n, freq="5min", tz="UTC")
    return pd.DataFrame({
        "Open": [b.Open for b in bars],
        "High": [b.High for b in bars],
        "Low": [b.Low for b in bars],
        "Close": [b.Close for b in bars],
    }, index=idx)


def main():
    print("\n--- swings ---")
    bars = synth_bars(200)
    swings = find_swings(bars)
    print(f"  {len(swings)} swings, last_high={last_swing_high(bars)}, "
          f"last_low={last_swing_low(bars)}")

    print("\n--- structure ---")
    levels = classify_intermediates(bars)
    print(f"  {len(levels)} intermediates, directional_pull={directional_pull(bars)}")

    print("\n--- mss ---")
    print(f"  latest_mss={latest_mss(bars)} direction={mss_direction(bars)}")

    print("\n--- fvg ---")
    print(f"  total FVGs={len(enumerate_fvgs(bars, 'EURUSD'))}, "
          f"latest_detect={detect_new_fvg(bars, 'EURUSD')}")

    print("\n--- order blocks / breakers ---")
    obs = detect_order_blocks(bars)
    brs = detect_breakers(bars, tf="15T")
    print(f"  {len(obs)} OBs, {len(brs)} breakers")

    print("\n--- levels (NYO, PDH/PDL, sessions) ---")
    df = synth_df(2000)
    ts = df.index[-1]
    dl = build_day_levels(df, ts)
    print(f"  {dl}")

    print("\n--- cls cycles ---")
    print(f"  phases at {ts} -> {cycle_phases(ts)}")
    print(f"  macro at {ts} -> {in_macro_window(ts)}")
    print(f"  cbdr -> {cbdr_hl(df, ts)}")

    print("\n--- liquidity zones ---")
    tf_bars = {"5T": bars, "15T": bars[::3], "240T": bars[::48], "D": bars[::288],
               "W": bars[::288 * 7] or bars, "60T": bars[::12]}
    zones = collect_zones(tf_bars, direction=+1)
    print(f"  {len(zones)} bullish zones; recent tap @ {bars[-1].Close} -> "
          f"{most_recent_tap(zones, bars[-1].Close)}")

    print("\n--- liquidity run (synthetic fake run) ---")
    fake_bars = bars[:-1] + [Bar(bars[-1].Open, bars[-1].High,
                                  bars[-1].Low - 0.0005, bars[-1].Open + 0.0001)]
    res = validate_sweep(
        entry_tf_bars=fake_bars, confirm_tf_bars=fake_bars[::3],
        entry_tf="5T", symbol="EURUSD",
        swept_level=fake_bars[-2].Low, direction=+1,
    )
    print(f"  {res}")

    print("\n--- smt ---")
    print(f"  bull case -> {smt_confirm('EURUSD', 1.1010, 1.1000, 'GBPUSD', 1.2990, 1.3000, +1)}")
    print(f"  same-side -> {smt_confirm('EURUSD', 1.1010, 1.1000, 'GBPUSD', 1.3010, 1.3000, +1)}")

    print("\n--- intermarket ---")
    print(f"  (dxy=-1, eurgbp=+1) -> {resolve_intermarket(-1, +1)}")

    print("\n--- target ---")
    if dl is not None:
        t = pick_target("EURUSD", dl, None, None, +1, bars[-1].Close)
        print(f"  pick(+1) -> {t}")

    print("\n--- game theory ---")
    s = score_setup(swept_level_name="PDL", sweep_strong=True,
                    htf_zone_kind="fvg", htf_zone_tf="D",
                    timestamp=ts, london_first_hour_dir=-1,
                    trade_direction=+1, session_phase="ny_am")
    print(f"  total={s.total:.2f} bonuses={s.bonuses} passes={gt_passes(s)}")

    print("\n--- killzones ---")
    ny_kz = pd.Timestamp("2024-06-03 08:00", tz="UTC")  # ~04:00 NY = London KZ
    print(f"  in_used at {ny_kz} -> {in_used_killzone(ny_kz)} "
          f"first_hour_elapsed={first_hour_elapsed(ny_kz)} "
          f"can_enter={can_enter_new_pipeline(ny_kz)}")

    print("\n--- entry ---")
    from ict.fvg import FVG
    from ict.target import Target
    fake_fvg = FVG(direction=+1, top=1.1010, bottom=1.1005, bar_index=10)
    fake_tgt = Target(name="PDH", price=1.1100, distance_pips=90)
    sig = build_entry(
        pair="EURUSD", direction=+1, trigger_fvg=fake_fvg,
        swept_price=1.0990, target=fake_tgt, confluence_score=2.0,
        swept_level_name="PDL", htf_zone_kind="fvg", htf_zone_tf="D",
    )
    print(f"  {sig}")

    print("\nALL MODULES OK")


if __name__ == "__main__":
    main()

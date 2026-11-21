"""P92 — reversal vs continuation at the zone tap, split by the Episode-22 SMT reading.

The engine (MM_GOLDEN_M1_SMTX=1) logs every MM setup that reached a confirmed M1
shift on the traded pair, with how many of EURUSD / GBPUSD / DXY shifted on KEY
swings (`shifts`) and what SMT the last 30 minutes showed (`smt`: smt / cont / none /
noref). This walks raw M1 forward from each event and simulates, on the SAME events:

  reversal      the trade the MM model takes: direction d, stop beyond the tap
                extreme + 1 pip (3-10 pips), target 2R
  continuation  the opposite trade: price keeps going through the zone. Stop beyond
                the high/low the reversal attempt made since the tap + 1 pip (3-10
                pips), target 2R

Trader's rule under test: >=2 shifts + SMT -> the reversal pays; >=2 shifts and NO
SMT -> price continues, so the continuation should beat the reversal there. Outside
the engine (R units, no sizing, no caps) — a lever must be confirmed in the engine.

    python scripts/smtx_study.py [--events data/histdata/mm_smtx_events.csv] [--out data/smtx_report.md]
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from m1_skip_study import load_pair, pip_of, simulate, pf_r  # noqa: E402

BUF, MIN_STOP, MAX_STOP, RR, HOLD, FRICTION, TAP_LB = 1.0, 3.0, 10.0, 2.0, 240, 0.5, 60


def _clamp_stop(entry, stop, d, pip):
    dist = (entry - stop) * d / pip
    if dist < MIN_STOP:
        return entry - d * MIN_STOP * pip
    if dist > MAX_STOP:
        return entry - d * MAX_STOP * pip
    return stop


def sim_event(m1, ev):
    pip = pip_of(ev["pair"])
    t = pd.Timestamp(ev["t"])
    if t.tzinfo is None:
        t = t.tz_localize("UTC")
    k = int(m1.index.searchsorted(t, side="left")) - 1      # last completed M1 bar
    if k < TAP_LB or k >= len(m1) - 2:
        return None
    h, l, c = m1["High"].values, m1["Low"].values, m1["Close"].values
    d = int(ev["direction"])
    lo = k - TAP_LB
    ti = lo + (int(np.argmin(l[lo:k + 1])) if d > 0 else int(np.argmax(h[lo:k + 1])))
    out = {}
    # reversal
    e = c[k] + d * FRICTION * pip
    s = (l[ti] - BUF * pip) if d > 0 else (h[ti] + BUF * pip)
    s = _clamp_stop(e, s, d, pip)
    out["rev"] = simulate(h, l, c, k, d, e, s, e + d * RR * abs(e - s), HOLD)[0]
    # continuation
    cd = -d
    e = c[k] + cd * FRICTION * pip
    s = (h[ti:k + 1].max() + BUF * pip) if d > 0 else (l[ti:k + 1].min() - BUF * pip)
    s = _clamp_stop(e, s, cd, pip)
    out["cont"] = simulate(h, l, c, k, cd, e, s, e + cd * RR * abs(e - s), HOLD)[0]
    return out


def bucket(ev):
    if ev["shifts"] < 2:
        return "shift<2"
    return f"shift>=2 & {ev['smt']}"


def run(events, loader=load_pair):
    ev = events.copy()
    ev["t"] = pd.to_datetime(ev["t"], utc=True)
    ev["day"] = ev["t"].dt.date
    ev["ext_r"] = ev["ext"].round(5)
    ev = ev.drop_duplicates(subset=["pair", "day", "direction", "ext_r"], keep="first")
    ev["half"] = np.where(ev["t"].dt.year <= 2023, "IS", "OOS")
    rows = []
    for pair, grp in ev.groupby("pair"):
        m1 = loader(pair, sorted(set(grp["t"].dt.year) | {y + 1 for y in grp["t"].dt.year}))
        if m1 is None:
            continue
        for _, e in grp.iterrows():
            r = sim_event(m1, e)
            if r:
                rows.append({"half": e["half"], "bucket": bucket(e), **r})
    return pd.DataFrame(rows), len(events), len(ev)


def report(df, n_raw, n_dedup):
    L = ["# P92 — reversal vs continuation by Episode-22 SMT reading", "",
         f"events logged {n_raw}, unique setups {n_dedup}, simulated {len(df)}. "
         f"R units, 2R target, stop 3-10 pips, {HOLD} M1 bars max, {FRICTION} pip friction.", "",
         "| bucket | half | n | reversal WR / PF / sumR | continuation WR / PF / sumR | better |",
         "|---|---|---|---|---|---|"]
    order = ["shift>=2 & smt", "shift>=2 & cont", "shift>=2 & none", "shift>=2 & noref", "shift<2"]
    for b in order:
        for hf in ("IS", "OOS"):
            g = df[(df.bucket == b) & (df.half == hf)] if len(df) else df
            if not len(g):
                continue
            rv, ct = g["rev"], g["cont"]
            best = "reversal" if rv.sum() > ct.sum() else "continuation"
            L.append(f"| {b} | {hf} | {len(g)} | {(rv > 0).mean()*100:.0f}% / {pf_r(rv):.2f} / {rv.sum():+.1f} | "
                     f"{(ct > 0).mean()*100:.0f}% / {pf_r(ct):.2f} / {ct.sum():+.1f} | {best} |")
    L += ["", "Trader's rule predicts: `shift>=2 & smt` -> reversal better in BOTH halves; "
          "`shift>=2 & cont/none` -> continuation better in BOTH halves."]
    return "\n".join(L) + "\n"


def selftest():
    idx = pd.date_range("2022-01-03 08:00", periods=400, freq="1min", tz="UTC")
    # down into a low at bar 150 then rally: reversal long should win, continuation short lose
    p = np.r_[np.linspace(1.10, 1.09, 151), np.linspace(1.09, 1.12, 249)]
    m1 = pd.DataFrame({"Open": p, "High": p + 0.0002, "Low": p - 0.0002, "Close": p}, index=idx)
    ev = {"pair": "EURUSD", "t": idx[160], "direction": 1}
    r = sim_event(m1, ev)
    assert r["rev"] > 0 and r["cont"] < 0, r
    ev2 = {"pair": "EURUSD", "t": idx[160], "direction": -1}
    m2 = m1.copy()
    m2[["Open", "High", "Low", "Close"]] = 2.2 - m1[["Open", "Low", "High", "Close"]].values
    r2 = sim_event(m2, ev2)
    assert r2["rev"] > 0 and r2["cont"] < 0, r2
    print("selftest ok", r, r2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default=None)
    ap.add_argument("--out", default="data/smtx_report.md")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    path = a.events or next((p for p in ("data/histdata/mm_smtx_events.csv", "data/mm_smtx_events.csv")
                             if os.path.exists(p)), None)
    if not path:
        print("no events file"); return
    df, n_raw, n_dedup = run(pd.read_csv(path))
    txt = report(df, n_raw, n_dedup)
    print(txt)
    open(a.out, "w").write(txt)


if __name__ == "__main__":
    main()

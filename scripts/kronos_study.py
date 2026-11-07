"""P121 — does KRONOS predict the next hours of EURUSD / GBPUSD / NZDUSD better than a coin?

Same harness as P120 (scripts/dollar_read_study.py): at fixed killzone times (03:00, 04:00,
07:00, 08:00, 09:00 ET, weekdays) Kronos reads the last CONTEXT completed H1 bars of each pair
and forecasts the close PRED_LEN bars ahead; its direction is scored on
  race   +10 pips vs -10 pips first (M1 path, 8h cap) — coin = 50%
  fwd1 / fwd4   pips over the next 1h / 4h in the called direction — coin = 0
with DAY-CLUSTERED standard errors.

⚠️ Kronos's pretraining corpus reportedly ends June 2024, so 2022-01..2024-06 is CONTAMINATED
(the model may have seen those very candles) and only 2024-07 onwards is a fair test.

Two phases so the slow part can be split by year on separate runners:
  --forecast --year Y   run Kronos on year Y, write data/kronos_fc/kronos_fc_<Y>.csv
  --report              score every forecast file -> data/kronos_report.md
"""
import argparse
import glob
import math
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dollar_read_study as drs   # noqa: E402

PAIRS = drs.PAIRS
NY = drs.NY
HOURS_ET = (3, 4, 7, 8, 9)
CONTEXT = int(os.environ.get("KRONOS_CONTEXT", "400"))
PRED_LEN = int(os.environ.get("KRONOS_PRED_LEN", "4"))
SAMPLES = int(os.environ.get("KRONOS_SAMPLES", "5"))
FC_DIR = os.path.join(ROOT, "data", "kronos_fc")
CLEAN_FROM = "2024-07-01"


def split_of(ts):
    import pandas as pd
    if ts < pd.Timestamp(CLEAN_FROM, tz="UTC"):
        return "contaminated 2022-01..2024-06"
    return "CLEAN 2024-07..2025-12" if ts.year <= 2025 else "CLEAN 2026"


def decision_times(idx, year):
    import numpy as np
    et = idx.tz_convert(NY)
    keep = (et.year == year) & np.isin(et.hour, HOURS_ET) & (et.minute == 0) & (et.dayofweek < 5)
    return idx[keep]


def h1_completed(df):
    """H1 bars (UTC) with the time each one is COMPLETE."""
    return drs.resample(df, "60min")


def forecast_year(year, max_minutes):
    import numpy as np
    import pandas as pd
    import kronos_bridge
    os.makedirs(FC_DIR, exist_ok=True)
    out = os.path.join(FC_DIR, f"kronos_fc_{year}.csv")
    frames = {p: drs.load_utc(p) for p in PAIRS}
    h1 = {p: h1_completed(f) for p, f in frames.items() if f is not None}
    times = decision_times(frames["EURUSD"].index, year)
    rows, t0 = [], time.time()
    for k, t in enumerate(times):
        batch, names = [], []
        for p, b in h1.items():
            n = int(np.searchsorted(b["done"].values, np.datetime64(t.tz_convert(None)), side="right"))
            if n < CONTEXT:
                continue
            seg = b.iloc[n - CONTEXT:n][["o", "h", "l", "c"]]
            batch.append(seg)
            names.append(p)
        if not batch:
            continue
        try:
            mv = kronos_bridge.forecast(batch, pred_len=PRED_LEN, samples=SAMPLES, seed=k)
        except Exception as e:   # one bad window must not kill a 5h job
            print("forecast failed", t, e)
            continue
        for p, m in zip(names, mv):
            rows.append((p, t.isoformat(), m / drs.PIP))
        if k % 50 == 0:
            el = (time.time() - t0) / 60
            print(f"{year} {k}/{len(times)} {t} {el:.1f} min", flush=True)
            if el > max_minutes:
                print("time budget reached — writing what we have")
                break
    pd.DataFrame(rows, columns=["pair", "t", "kronos_pips"]).to_csv(out, index=False)
    print("wrote", out, len(rows))


def report(out_path):
    import numpy as np
    import pandas as pd
    files = sorted(glob.glob(os.path.join(FC_DIR, "kronos_fc_*.csv")))
    if not files:
        sys.exit("no forecast files")
    fc = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    fc["t"] = pd.to_datetime(fc["t"], utc=True)
    lines = ["# P121 — Kronos direction vs a coin (completed H1 bars, EU/GU/NZ)", "",
             f"Kronos-small, context {CONTEXT} H1 bars, forecast {PRED_LEN}h ahead, {SAMPLES} sampled "
             "paths averaged. Decision times 03/04/07/08/09:00 ET. Cell = n checks/days / race hit% "
             "(lift vs coin ± day-clustered SE) / fwd 1h pips ± SE / fwd 4h pips ± SE, in Kronos's "
             "called direction. Coin = 50% / 0 / 0. Costs not deducted (~1.3 pips).", "",
             "⚠️ **Only the CLEAN rows count.** Kronos's pretraining reportedly ends June 2024; "
             "the contaminated rows may be memory, not forecasting.", "",
             f"Forecast files: {', '.join(os.path.basename(f) for f in files)} ({len(fc)} forecasts).", ""]
    per = {}
    for p in PAIRS:
        sub = fc[fc.pair == p].sort_values("t")
        if sub.empty:
            continue
        df = drs.load_utc(p)
        times = pd.DatetimeIndex(sub["t"])
        race, f1, f4 = drs.outcomes(df, times)
        d = np.sign(sub["kronos_pips"].values).astype(int)
        days = np.asarray(times.tz_convert(NY).date, dtype="datetime64[D]").astype("int64")
        split = np.array([split_of(x) for x in times])
        per[p] = dict(d=d, race=race, f1=f1, f4=f4, days=days, split=split,
                      mag=np.abs(sub["kronos_pips"].values), year=times.tz_convert(NY).year)
    splits = ["contaminated 2022-01..2024-06", "CLEAN 2024-07..2025-12", "CLEAN 2026"]
    lines += ["| period | " + " | ".join(per) + " | ALL |", "|---|" + "---|" * (len(per) + 1)]
    for sp in splits:
        row = [sp]
        acc = [[], [], [], [], []]
        for p, P in per.items():
            m = P["split"] == sp
            row.append(drs.fmt(drs.cell(P["d"][m], P["race"][m], P["f1"][m], P["f4"][m], P["days"][m])))
            for a, k in zip(acc, ("d", "race", "f1", "f4", "days")):
                a.append(P[k][m])
        row.append(drs.fmt(drs.cell(*[np.concatenate(a) for a in acc])))
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Confident calls only (|forecast| in the top third of that pair's forecasts)", "",
              "| period | ALL |", "|---|---|"]
    for sp in splits:
        acc = [[], [], [], [], []]
        for p, P in per.items():
            thr = np.quantile(P["mag"], 2 / 3)
            m = (P["split"] == sp) & (P["mag"] >= thr)
            for a, k in zip(acc, ("d", "race", "f1", "f4", "days")):
                a.append(P[k][m])
        lines.append(f"| {sp} | {drs.fmt(drs.cell(*[np.concatenate(a) for a in acc]))} |")
    lines += ["", "## By year (all pairs; race lift pp ± SE / fwd 4h pips ± SE)", "",
              "| " + " | ".join(str(y) for y in range(2022, 2027)) + " |", "|---" * 5 + "|"]
    cells = []
    for y in range(2022, 2027):
        acc = [[], [], [], [], []]
        for P in per.values():
            m = P["year"] == y
            for a, k in zip(acc, ("d", "race", "f1", "f4", "days")):
                a.append(P[k][m])
        c = drs.cell(*[np.concatenate(a) for a in acc])
        cells.append("—" if c is None else f"{c['hit']-50:+.1f}±{c['se']:.1f} / {c['f4']:+.1f}±{c['f4se']:.1f}")
    lines += ["| " + " | ".join(cells) + " |", ""]
    txt = "\n".join(lines)
    with open(out_path, "w") as f:
        f.write(txt + "\n")
    print(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forecast", action="store_true")
    ap.add_argument("--year", type=int)
    ap.add_argument("--max-minutes", type=float, default=300)
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "kronos_report.md"))
    a = ap.parse_args()
    if a.forecast:
        forecast_year(a.year, a.max_minutes)
    if a.report:
        report(a.out)


if __name__ == "__main__":
    main()

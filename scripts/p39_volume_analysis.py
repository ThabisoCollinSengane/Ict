#!/usr/bin/env python3
"""P39 — Volume-as-confidence analysis (measurement only, no engine changes).

Measures whether tick volume adds orthogonal edge as a per-trade confidence
signal on the ICT strategy's entries. Two hypotheses, per the P39 handover:

  H1 friction ratio  — ticks on the sweep/entry M5 bar relative to the mean of
                       the previous N bars. High ratio = real institutional
                       participation; low ratio = retail noise wick.
  H2 directional     — net delta (up-ticks vs down-ticks, Lee-Ready style bid
     delta             classification) on that bar, and whether it aligns with
                       the trade direction.

Both hypotheses are reported in BOTH directions (the handover is explicit that
sweeps-that-reverse and breakouts-that-continue have opposite volume priors), so
results are split by `entry_model` (judas vs breakout) as well as pooled.

Deliberately stdlib-only (no pandas/numpy): tick aggregation is pure counting
and the analysis is grouping/averaging, so the script runs on a bare Python
install and can be unit-tested without the scientific stack.

Two phases — run `aggregate` once (slow, I/O bound), then `analyse` as often as
you like (fast, re-runnable):

    # 1. aggregate raw tick zips → compact per-month M5 tick/delta counts
    python scripts/p39_volume_analysis.py aggregate <tick_zip_dir>

    # 2. join to the trade log and write the report
    python scripts/p39_volume_analysis.py analyse

    # or both in sequence
    python scripts/p39_volume_analysis.py all <tick_zip_dir>

Input tick files: HistData TICK product zips, named
`HISTDATA_COM_ASCII_<PAIR>_T<YYYYMM>.zip`, each containing a CSV of
`YYYYMMDD HHMMSSmmm,bid,ask,volume`. The volume column is zeros (HistData
strips it) — real tick volume is the COUNT of ticks per bin, which is what we
compute. Timestamps are Eastern Standard Time (fixed UTC-5), matching the
convention already used by run_backtest_histdata.py.

Output: `data/p39_volume_report.md`
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import re
import sqlite3
import statistics
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# ── Paths ────────────────────────────────────────────────────────────────────
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_REPO, "data")
AGG_DIR = os.path.join(DATA_DIR, "p39_agg")
REPORT_PATH = os.path.join(DATA_DIR, "p39_volume_report.md")

# ── Constants ────────────────────────────────────────────────────────────────
M5 = 300                      # seconds per M5 bin
EST_OFFSET = timedelta(hours=5)   # HistData ET → UTC (matches run_backtest_histdata)
BASELINE_BARS = 20            # H1: mean ticks over the previous 20 M5 bars
SWEEP_LOOKBACK = 6            # bars before entry searched for the sweep proxy
CONTROL_MIN_GAP_H = 2         # control-1: control bars ≥2h from any signal
MIN_RISK = 1e-5               # degenerate-R floor (~0.1 pip) — skip below this

# H1 buckets, per the handover
BUCKETS = (
    ("low",    0.00, 0.65),
    ("normal", 0.65, 1.20),
    ("high",   1.20, 1.80),
    ("spike",  1.80, float("inf")),
)

IS_YEARS = {2022, 2023}       # in-sample
OOS_YEARS = {2024, 2025}      # out-of-sample

_ZIP_RE = re.compile(r"ASCII_([A-Z]{6})_T(\d{4})(\d{2})", re.IGNORECASE)


def _bucket(ratio: float | None) -> str:
    if ratio is None:
        return "unknown"
    for name, lo, hi in BUCKETS:
        if lo <= ratio < hi:
            return name
    return "unknown"


def _split(year: int) -> str:
    if year in IS_YEARS:
        return "IS"
    if year in OOS_YEARS:
        return "OOS"
    return "other"


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1 — aggregate raw ticks → M5 counts
# ═════════════════════════════════════════════════════════════════════════════

def _parse_tick_ts(field: str) -> int | None:
    """`YYYYMMDD HHMMSSmmm` (ET) → UTC epoch seconds. None if malformed."""
    try:
        date_s, time_s = field.split(" ")
        dt = datetime(
            int(date_s[0:4]), int(date_s[4:6]), int(date_s[6:8]),
            int(time_s[0:2]), int(time_s[2:4]), int(time_s[4:6]),
            tzinfo=timezone.utc,
        )
    except (ValueError, IndexError):
        return None
    return int((dt + EST_OFFSET).timestamp())


def aggregate_month(zip_path: str, out_path: str) -> tuple[int, int]:
    """Stream one pair-month of ticks into M5 bins. Returns (ticks, bins).

    Memory-safe: reads line by line and only ever holds the per-bin counters,
    never the raw tick stream (a single month can be 100M+ rows uncompressed).

    Delta classification (Lee & Ready 1991, bid-only variant): a tick whose bid
    is above the previous bid is buy-initiated, below is sell-initiated, equal
    is neutral. The ~34% neutral rate is expected and left unclassified rather
    than forced to a side.
    """
    bins: dict[int, list[int]] = {}       # bin_start → [ticks, buy, sell, neutral]
    prev_bid: float | None = None
    n_ticks = 0

    with zipfile.ZipFile(zip_path) as zf:
        members = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not members:
            return (0, 0)
        with zf.open(members[0]) as raw:
            for line in raw:
                try:
                    parts = line.decode("ascii", "replace").rstrip().split(",")
                    if len(parts) < 2:
                        continue
                    ts = _parse_tick_ts(parts[0])
                    if ts is None:
                        continue
                    bid = float(parts[1])
                except (ValueError, IndexError):
                    continue

                slot = bins.setdefault(ts - (ts % M5), [0, 0, 0, 0])
                slot[0] += 1
                if prev_bid is not None:
                    if bid > prev_bid:
                        slot[1] += 1
                    elif bid < prev_bid:
                        slot[2] += 1
                    else:
                        slot[3] += 1
                prev_bid = bid
                n_ticks += 1

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bin_utc", "ticks", "buy", "sell", "neutral"])
        for b in sorted(bins):
            t, bu, se, ne = bins[b]
            w.writerow([b, t, bu, se, ne])
    return (n_ticks, len(bins))


def phase_aggregate(zip_dir: str, force: bool = False) -> list[dict]:
    """Aggregate every tick zip in `zip_dir`. Returns coverage rows."""
    if not os.path.isdir(zip_dir):
        print(f"ERROR: tick dir not found: {zip_dir}")
        sys.exit(1)

    paths = sorted(glob.glob(os.path.join(zip_dir, "*.zip")))
    # Non-zip artefacts (HistData sometimes serves a .txt "no data" placeholder)
    strays = [os.path.basename(p) for p in
              glob.glob(os.path.join(zip_dir, "*.txt"))]

    print(f"Tick dir : {zip_dir}")
    print(f"Zips     : {len(paths)}")
    if strays:
        print(f"Non-zip  : {len(strays)} (skipped: {', '.join(strays[:5])})")
    print()

    coverage = []
    for p in paths:
        base = os.path.basename(p)
        m = _ZIP_RE.search(base)
        if not m:
            print(f"  ? skip (unrecognised name): {base}")
            continue
        pair, yyyy, mm = m.group(1).upper(), m.group(2), m.group(3)

        if os.path.getsize(p) == 0:
            print(f"  ! EMPTY (0 bytes, failed download): {base}")
            coverage.append({"pair": pair, "month": f"{yyyy}-{mm}",
                             "ticks": 0, "bins": 0, "status": "empty file"})
            continue

        out = os.path.join(AGG_DIR, f"{pair}_{yyyy}{mm}_m5.csv")
        if os.path.exists(out) and not force:
            with open(out) as f:
                bins = max(0, sum(1 for _ in f) - 1)
            print(f"  · cached {pair} {yyyy}-{mm}  ({bins} bins)")
            coverage.append({"pair": pair, "month": f"{yyyy}-{mm}",
                             "ticks": -1, "bins": bins, "status": "cached"})
            continue

        try:
            n_ticks, n_bins = aggregate_month(p, out)
        except (zipfile.BadZipFile, OSError) as exc:
            print(f"  ! FAILED {base}: {exc}")
            coverage.append({"pair": pair, "month": f"{yyyy}-{mm}",
                             "ticks": 0, "bins": 0, "status": f"unreadable ({exc})"})
            continue

        if n_ticks == 0:
            print(f"  ! no ticks parsed: {base}")
            coverage.append({"pair": pair, "month": f"{yyyy}-{mm}",
                             "ticks": 0, "bins": 0, "status": "no parseable ticks"})
            continue

        print(f"  + {pair} {yyyy}-{mm}  {n_ticks:>10,} ticks → {n_bins:>5} M5 bins")
        coverage.append({"pair": pair, "month": f"{yyyy}-{mm}",
                         "ticks": n_ticks, "bins": n_bins, "status": "ok"})

    return coverage


# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2 — load aggregates + trades, measure, report
# ═════════════════════════════════════════════════════════════════════════════

def load_aggregates() -> dict[str, dict[int, tuple[int, int, int, int]]]:
    """pair → {bin_utc: (ticks, buy, sell, neutral)} from the phase-1 output."""
    series: dict[str, dict[int, tuple[int, int, int, int]]] = defaultdict(dict)
    for path in sorted(glob.glob(os.path.join(AGG_DIR, "*_m5.csv"))):
        pair = os.path.basename(path).split("_")[0]
        with open(path) as f:
            for row in csv.DictReader(f):
                series[pair][int(row["bin_utc"])] = (
                    int(row["ticks"]), int(row["buy"]),
                    int(row["sell"]), int(row["neutral"]),
                )
    return series


def _parse_dt(s: str) -> datetime | None:
    """Parse the trade log's timestamp forms into an aware UTC datetime."""
    s = (s or "").strip()
    if not s:
        return None
    s = s.replace("T", " ")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    # strip a trailing "+00:00"/"+0000" so a single strptime set covers it
    tz_suffix = re.search(r"([+-]\d{2}:?\d{2})$", s)
    if tz_suffix:
        s = s[: tz_suffix.start()].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def load_trades(path: str | None) -> list[dict]:
    """Load initial-entry trades from a CSV dump or the SQLite trade log.

    Accepts (in order of preference) an explicit --trades path, the backtest's
    `data/histdata/trades_dump.csv`, a P39-handover `data/trade_score_log.csv`,
    or `data/trade_log.db`. Only leg_idx == 1 rows are used, so pyramid legs
    don't double-count the same setup.
    """
    candidates = [path] if path else [
        os.path.join(DATA_DIR, "histdata", "trades_dump.csv"),
        os.path.join(DATA_DIR, "trades_dump.csv"),
        os.path.join(DATA_DIR, "trade_score_log.csv"),
        os.path.join(DATA_DIR, "trade_log.db"),
    ]
    src = next((c for c in candidates if c and os.path.exists(c)), None)
    if src is None:
        print("ERROR: no trade log found. Looked for:")
        for c in candidates:
            print(f"  - {c}")
        print("\nGenerate one by running the backtest first, e.g.:")
        print("  python run_backtest_histdata.py --years 2022 2024")
        sys.exit(1)

    rows: list[dict] = []
    if src.endswith(".db"):
        conn = sqlite3.connect(src)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute("SELECT * FROM trades")]
        conn.close()
    else:
        with open(src, newline="") as f:
            rows = list(csv.DictReader(f))
    print(f"Trade log: {src}  ({len(rows)} rows)")

    trades = []
    for r in rows:
        try:
            if str(r.get("leg_idx", "1")).strip() not in ("1", "1.0"):
                continue
            opened = _parse_dt(r.get("opened_at") or r.get("entry_time") or "")
            if opened is None:
                continue
            direction = int(float(r.get("direction", 0)))
            entry = float(r.get("entry", "nan"))
            pnl = float(r.get("pnl", r.get("pnl_zar", "nan")))
        except (TypeError, ValueError):
            continue
        if direction == 0 or entry != entry or pnl != pnl:   # NaN-safe
            continue

        # True R when the stop is available; else fall back to P&L-only metrics.
        r_mult = None
        try:
            stop = float(r.get("stop", "nan"))
            exit_p = float(r.get("exit", "nan"))
            risk = abs(entry - stop)
            if risk == risk and risk > MIN_RISK and exit_p == exit_p:
                r_mult = (exit_p - entry) * direction / risk
        except (TypeError, ValueError):
            pass

        trades.append({
            "pair": (r.get("pair") or "").upper(),
            "direction": direction,
            "opened": opened,
            "pnl": pnl,
            "r": r_mult,
            "win": pnl > 0,
            "entry_model": (r.get("entry_model") or "").strip() or "unknown",
            "entry_type": (r.get("entry_type") or "").strip() or "unknown",
            "session_side": (r.get("session_side") or "").strip() or "unknown",
            "split": _split(opened.year),
            "hour": opened.hour,
        })

    # De-dup: one record per (pair, opened_at) in case of repeated log appends.
    seen, uniq = set(), []
    for t in trades:
        key = (t["pair"], t["opened"])
        if key not in seen:
            seen.add(key)
            uniq.append(t)
    print(f"Usable initial entries: {len(uniq)} "
          f"(IS {sum(1 for t in uniq if t['split']=='IS')}, "
          f"OOS {sum(1 for t in uniq if t['split']=='OOS')})")
    return uniq


def measure(trades: list[dict], series: dict) -> tuple[list[dict], list[dict]]:
    """Attach friction ratio + delta to each trade. Returns (measured, controls).

    Sweep-bar identification: the engine does not log which M5 bar was the
    manipulation sweep, so this uses a documented PROXY — the highest-tick bar
    within SWEEP_LOOKBACK bars up to and including the entry bar. The entry
    bar's own friction is reported alongside it, unproxied. See the report's
    caveats section; exact attribution needs engine instrumentation.
    """
    measured, controls = [], []
    # trades per (pair, date) so control bars can avoid signal times
    by_day: dict[tuple[str, object], list[int]] = defaultdict(list)
    for t in trades:
        by_day[(t["pair"], t["opened"].date())].append(
            int(t["opened"].timestamp()))

    for t in trades:
        s = series.get(t["pair"])
        if not s:
            continue
        ts = int(t["opened"].timestamp())
        entry_bin = ts - (ts % M5)

        prior = [s[entry_bin - i * M5][0]
                 for i in range(1, BASELINE_BARS + 1)
                 if (entry_bin - i * M5) in s]
        if len(prior) < BASELINE_BARS // 2:      # too gappy to trust
            continue
        baseline = statistics.fmean(prior)
        if baseline <= 0:
            continue

        entry_rec = s.get(entry_bin)
        if entry_rec is None:
            continue

        # sweep proxy: densest bar in the lookback window
        window = [(s[entry_bin - i * M5], i)
                  for i in range(0, SWEEP_LOOKBACK + 1)
                  if (entry_bin - i * M5) in s]
        sweep_rec, sweep_off = max(window, key=lambda kv: kv[0][0])

        def _delta(rec):
            _, buy, sell, _n = rec
            tot = buy + sell
            return (buy - sell, (buy / tot) if tot else None)

        net_s, ratio_s = _delta(sweep_rec)
        m = dict(t)
        m.update({
            "friction_entry": entry_rec[0] / baseline,
            "friction_sweep": sweep_rec[0] / baseline,
            "sweep_offset": sweep_off,
            "bucket_entry": _bucket(entry_rec[0] / baseline),
            "bucket_sweep": _bucket(sweep_rec[0] / baseline),
            "net_delta": net_s,
            "delta_ratio": ratio_s,
            # H2: does aggressive flow on the sweep bar agree with the trade?
            "delta_aligned": (None if net_s == 0
                              else ((net_s > 0) == (t["direction"] > 0))),
            "baseline_ticks": baseline,
        })
        measured.append(m)

        # ── Control 1: a same-day bar ≥CONTROL_MIN_GAP_H from any signal ──
        gap = CONTROL_MIN_GAP_H * 3600
        signals = by_day[(t["pair"], t["opened"].date())]
        day0 = int(datetime(t["opened"].year, t["opened"].month, t["opened"].day,
                            tzinfo=timezone.utc).timestamp())
        for k in range(0, 288):                  # deterministic scan of the day
            cb = day0 + ((sweep_off * 37 + k * 53) % 288) * M5   # spread probe
            if cb not in s:
                continue
            if not all(abs(cb - sg) >= gap for sg in signals):
                continue
            cprior = [s[cb - i * M5][0] for i in range(1, BASELINE_BARS + 1)
                      if (cb - i * M5) in s]
            if len(cprior) < BASELINE_BARS // 2:
                continue
            cbase = statistics.fmean(cprior)
            if cbase <= 0:
                continue
            controls.append({
                "pair": t["pair"], "split": t["split"],
                "friction": s[cb][0] / cbase,
                "hour": datetime.fromtimestamp(cb, timezone.utc).hour,
            })
            break

    return measured, controls


# ── Stats helpers ────────────────────────────────────────────────────────────

def _stats(rows: list[dict]) -> dict:
    n = len(rows)
    if n == 0:
        return {"n": 0}
    wins = sum(1 for r in rows if r["win"])
    rs = [r["r"] for r in rows if r.get("r") is not None]
    return {
        "n": n,
        "wr": 100.0 * wins / n,
        "mean_r": statistics.fmean(rs) if rs else None,
        "med_r": statistics.median(rs) if rs else None,
        "n_r": len(rs),
        "mean_pnl": statistics.fmean([r["pnl"] for r in rows]),
    }


def _tbl(header: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(rows_) + " |" for rows_ in
            ([[str(c) for c in r] for r in rows])]
    return "\n".join(out)


def _fmt(s: dict) -> list[str]:
    if s["n"] == 0:
        return ["0", "—", "—", "—"]
    mr = f"{s['mean_r']:+.2f}" if s["mean_r"] is not None else "n/a"
    md = f"{s['med_r']:+.2f}" if s["med_r"] is not None else "n/a"
    return [str(s["n"]), f"{s['wr']:.1f}%", mr, md]


def _bucket_rows(rows: list[dict], key: str) -> list[list[str]]:
    out = []
    for name, _lo, _hi in BUCKETS:
        sub = [r for r in rows if r[key] == name]
        s_is = _stats([r for r in sub if r["split"] == "IS"])
        s_oos = _stats([r for r in sub if r["split"] == "OOS"])
        out.append([name] + _fmt(s_is) + _fmt(s_oos))
    return out


_BKT_HDR = ["bucket", "IS n", "IS WR", "IS meanR", "IS medR",
            "OOS n", "OOS WR", "OOS meanR", "OOS medR"]


def _wr(rows: list[dict]) -> float | None:
    return (100.0 * sum(1 for r in rows if r["win"]) / len(rows)) if rows else None


def verdict(measured: list[dict], controls: list[dict]) -> tuple[str, list[str]]:
    """Apply the handover's GREEN / YELLOW / RED decision rules."""
    notes = []
    effects = {}
    for split in ("IS", "OOS"):
        sub = [r for r in measured if r["split"] == split]
        lo = [r for r in sub if r["bucket_sweep"] == "low"]
        hi = [r for r in sub if r["bucket_sweep"] in ("high", "spike")]
        w_lo, w_hi = _wr(lo), _wr(hi)
        effects[split] = (None if (w_lo is None or w_hi is None)
                          else w_hi - w_lo, len(lo), len(hi))
        if w_lo is None or w_hi is None:
            notes.append(f"{split}: insufficient sample "
                         f"(low n={len(lo)}, high+spike n={len(hi)})")
        else:
            notes.append(f"{split}: WR(high+spike) − WR(low) = {w_hi - w_lo:+.1f}pp "
                         f"(low n={len(lo)} WR {w_lo:.1f}%, "
                         f"high+spike n={len(hi)} WR {w_hi:.1f}%)")

    e_is = effects["IS"][0]
    e_oos = effects["OOS"][0]
    if e_is is None or e_oos is None:
        return "RED (insufficient data)", notes

    same_sign = (e_is > 0) == (e_oos > 0)
    min_abs = min(abs(e_is), abs(e_oos))

    # Control-1: are sweep-bar frictions distinguishable from random bars?
    if controls:
        c_med = statistics.median([c["friction"] for c in controls])
        s_med = statistics.median([r["friction_sweep"] for r in measured])
        notes.append(f"Control-1 median friction: sweep {s_med:.2f}× vs "
                     f"control {c_med:.2f}× (n={len(controls)})")
        indistinguishable = abs(s_med - c_med) < 0.10
    else:
        indistinguishable = False
        notes.append("Control-1: no control bars sampled")

    if not same_sign:
        return "RED (IS and OOS disagree on sign)", notes
    if indistinguishable and min_abs < 3.0:
        return "RED (sweep friction indistinguishable from random bars)", notes
    if min_abs >= 5.0:
        return "GREEN (≥5pp both splits, consistent sign)", notes
    if min_abs < 3.0:
        return "RED (<3pp effect across splits)", notes
    return "YELLOW (3–5pp, consistent sign)", notes


def phase_analyse(coverage: list[dict] | None, trades_path: str | None) -> int:
    series = load_aggregates()
    if not series:
        print(f"ERROR: no aggregates in {AGG_DIR} — run the `aggregate` phase first.")
        return 1
    print(f"Aggregated pairs: "
          + ", ".join(f"{p} ({len(b)} bins)" for p, b in sorted(series.items())))

    trades = load_trades(trades_path)
    measured, controls = measure(trades, series)
    print(f"Trades with tick coverage: {len(measured)} "
          f"(control bars: {len(controls)})")
    if not measured:
        print("ERROR: no trades overlapped the tick data. Check that the tick "
              "months and the backtest years are the same period.")
        return 1

    vd, notes = verdict(measured, controls)

    # ── Build the report ────────────────────────────────────────────────────
    L: list[str] = []
    a = L.append
    a("# P39 — Volume-as-Confidence Analysis")
    a("")
    a(f"**Generated:** {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC  ")
    a("**Type:** measurement only — no engine changes, nothing shipped  ")
    a(f"**Verdict:** **{vd}**")
    a("")
    a("---")
    a("")

    # 1. coverage
    a("## 1. Data coverage")
    a("")
    if coverage:
        rows = [[c["pair"], c["month"],
                 (f"{c['ticks']:,}" if c["ticks"] > 0 else "—"),
                 str(c["bins"]), c["status"]] for c in coverage]
        a(_tbl(["pair", "month", "ticks", "M5 bins", "status"], rows))
    else:
        a("_(aggregate phase not run in this invocation — using cached "
          "aggregates in `data/p39_agg/`)_")
    a("")
    a("Aggregated M5 bins available per pair:")
    a("")
    a(_tbl(["pair", "M5 bins"],
           [[p, f"{len(b):,}"] for p, b in sorted(series.items())]))
    a("")
    tr_rows = []
    for split in ("IS", "OOS"):
        sub = [m for m in measured if m["split"] == split]
        yrs = sorted({m["opened"].year for m in sub})
        tr_rows.append([split, ", ".join(map(str, yrs)) or "—", str(len(sub))])
    a(_tbl(["split", "years", "measured trades"], tr_rows))
    a("")

    # 2. H1
    a("## 2. H1 — friction ratio (sweep-bar tick volume)")
    a("")
    a(f"Friction ratio = ticks on the bar ÷ mean ticks of the previous "
      f"{BASELINE_BARS} M5 bars. Buckets: low <0.65×, normal 0.65–1.20×, "
      f"high 1.20–1.80×, spike >1.80×.")
    a("")
    a("### Sweep bar (proxy: densest bar within "
      f"{SWEEP_LOOKBACK} bars up to entry)")
    a("")
    a(_tbl(_BKT_HDR, _bucket_rows(measured, "bucket_sweep")))
    a("")
    a("### Entry bar (unproxied — the M5 bin containing the fill)")
    a("")
    a(_tbl(_BKT_HDR, _bucket_rows(measured, "bucket_entry")))
    a("")
    a("### By entry model — the two opposite volume priors")
    a("")
    a("The handover notes sweeps-that-reverse and breakouts-that-continue have "
      "opposite expected volume signatures, so these are reported separately "
      "rather than pooled.")
    a("")
    for model in sorted({m["entry_model"] for m in measured}):
        sub = [m for m in measured if m["entry_model"] == model]
        a(f"**entry_model = `{model}`** (n={len(sub)})")
        a("")
        a(_tbl(_BKT_HDR, _bucket_rows(sub, "bucket_sweep")))
        a("")
    a("### Per pair")
    a("")
    for pair in sorted({m["pair"] for m in measured}):
        sub = [m for m in measured if m["pair"] == pair]
        a(f"**{pair}** (n={len(sub)})")
        a("")
        a(_tbl(_BKT_HDR, _bucket_rows(sub, "bucket_sweep")))
        a("")

    # 3. H2
    a("## 3. H2 — directional delta alignment")
    a("")
    a("Ticks classified by bid movement (up = buy-initiated, down = "
      "sell-initiated, unchanged = neutral and left unclassified). "
      "`aligned` = net delta on the sweep bar agrees with the trade direction.")
    a("")
    rows = []
    for label, pred in (("aligned", lambda r: r["delta_aligned"] is True),
                        ("against", lambda r: r["delta_aligned"] is False),
                        ("flat (net 0)", lambda r: r["delta_aligned"] is None)):
        sub = [r for r in measured if pred(r)]
        rows.append([label]
                    + _fmt(_stats([r for r in sub if r["split"] == "IS"]))
                    + _fmt(_stats([r for r in sub if r["split"] == "OOS"])))
    a(_tbl(["delta"] + _BKT_HDR[1:], rows))
    a("")

    # 4. cross-tab
    a("## 4. Cross-tabulation — friction bucket × delta alignment")
    a("")
    rows = []
    for name, _lo, _hi in BUCKETS:
        for al_label, al in (("aligned", True), ("against", False)):
            sub = [r for r in measured
                   if r["bucket_sweep"] == name and r["delta_aligned"] is al]
            if not sub:
                continue
            rows.append([name, al_label]
                        + _fmt(_stats([r for r in sub if r["split"] == "IS"]))
                        + _fmt(_stats([r for r in sub if r["split"] == "OOS"])))
    a(_tbl(["bucket", "delta"] + _BKT_HDR[1:], rows) if rows
      else "_No populated cells._")
    a("")

    # 5. controls
    a("## 5. Controls")
    a("")
    a("### Control 1 — friction on non-signal bars")
    a("")
    a(f"For each measured trade, a same-day M5 bar at least {CONTROL_MIN_GAP_H}h "
      "from any signal on that pair. If sweep friction matches this "
      "distribution, the signal is noise.")
    a("")
    if controls:
        cf = sorted(c["friction"] for c in controls)
        sf = sorted(r["friction_sweep"] for r in measured)

        def _q(v, p):
            return v[min(len(v) - 1, int(p * len(v)))]
        a(_tbl(["series", "n", "p25", "median", "p75", "mean"],
               [["sweep bars", len(sf), f"{_q(sf,.25):.2f}", f"{_q(sf,.5):.2f}",
                 f"{_q(sf,.75):.2f}", f"{statistics.fmean(sf):.2f}"],
                ["control bars", len(cf), f"{_q(cf,.25):.2f}", f"{_q(cf,.5):.2f}",
                 f"{_q(cf,.75):.2f}", f"{statistics.fmean(cf):.2f}"]]))
    else:
        a("_No control bars could be sampled._")
    a("")
    a("### Control 2 — effect without the entry-type filter")
    a("")
    a("Pooled across all entry types (above) and broken out per type (below). "
      "A real effect should hold across sub-populations; if it appears in only "
      "one type, treat it as over-fit.")
    a("")
    rows = []
    for et in sorted({m["entry_type"] for m in measured}):
        sub = [m for m in measured if m["entry_type"] == et]
        lo = [r for r in sub if r["bucket_sweep"] == "low"]
        hi = [r for r in sub if r["bucket_sweep"] in ("high", "spike")]
        w_lo, w_hi = _wr(lo), _wr(hi)
        rows.append([
            et, str(len(sub)), str(len(lo)), str(len(hi)),
            f"{w_lo:.1f}%" if w_lo is not None else "—",
            f"{w_hi:.1f}%" if w_hi is not None else "—",
            f"{w_hi - w_lo:+.1f}pp" if (w_lo is not None and w_hi is not None) else "—",
        ])
    a(_tbl(["entry_type", "n", "low n", "high+spike n",
            "WR low", "WR high+spike", "Δ"], rows))
    a("")
    a("### Control 3 — hour-of-day confound")
    a("")
    a("Tick volume varies systematically by session. If a bucket is really just "
      "\"trades in the first hour of London\", the effect is a session artefact.")
    a("")
    rows = []
    for h in sorted({m["hour"] for m in measured}):
        sub = [m for m in measured if m["hour"] == h]
        fr = sorted(r["friction_sweep"] for r in sub)
        comp = {b: sum(1 for r in sub if r["bucket_sweep"] == b)
                for b, _l, _h in BUCKETS}
        rows.append([f"{h:02d}:00", str(len(sub)),
                     f"{statistics.median(fr):.2f}",
                     f"{comp['low']}/{comp['normal']}/{comp['high']}/{comp['spike']}"])
    a(_tbl(["hour (UTC)", "n", "median friction", "low/normal/high/spike"], rows))
    a("")

    # 6-7. verdict + next action
    a("## 6. Verdict")
    a("")
    a(f"**{vd}**")
    a("")
    for n in notes:
        a(f"- {n}")
    a("")
    a("Decision rules (from the P39 handover): GREEN = ≥5pp WR gap between low "
      "and high friction, same sign in IS and OOS, survives control-3, with H2 "
      "also stratifying. YELLOW = one split only, or <5pp with consistent "
      "sign. RED = <3pp everywhere, sign disagreement, or controls "
      "indistinguishable.")
    a("")
    a("## 7. Recommended next action")
    a("")
    if vd.startswith("GREEN"):
        a("Build the confidence-modifier module — as a size **reducer** on "
          "noise-driven sweeps only, never a size-up above baseline (the P9 "
          "lesson: multipliers amplify tail risk). Validate against the full "
          "continuous run, not per-split PF, before shipping.")
    elif vd.startswith("YELLOW"):
        a("Park with this write-up. Re-check after demo trading provides live "
          "tick data. Do not tune thresholds on this dataset to chase GREEN — "
          "per the handover's anti-patterns, threshold sensitivity is a "
          "separate sub-experiment, run on IS only and validated on unseen OOS.")
    else:
        a("Close the volume question. Document the null and move on — a "
          "well-documented null is a shipped result.")
    a("")

    # 8. caveats
    a("## 8. Honest caveats")
    a("")
    a("- **Sweep-bar identification is a proxy.** The engine does not log which "
      "M5 bar was the manipulation sweep, so this uses the densest bar within "
      f"{SWEEP_LOOKBACK} bars up to the entry bar. That is a *tick-volume-"
      "selected* bar, which biases the sweep-bucket distribution upward "
      "relative to a structurally-identified sweep. The entry-bar table is the "
      "unbiased comparator. Exact attribution requires logging the sweep "
      "timestamp in the engine — the clean fix if this goes further.")
    a("- **Baseline is local.** The friction denominator is the previous "
      f"{BASELINE_BARS} bars, so it partly absorbs the session-volume profile — "
      "which is why control 3 matters.")
    a("- **Bid-only tick test.** HistData's volume column is zeros, so delta "
      "comes from bid movement. The ~34% unchanged-bid ticks are counted "
      "neutral, not forced to a side (Lee & Ready 1991).")
    a("- **Weekend/holiday gaps** produce sparse baselines; trades whose "
      f"lookback has fewer than {BASELINE_BARS // 2} populated bars are skipped "
      "rather than measured against a thin denominator.")
    a("- **R availability.** True R needs the stop price; rows without it are "
      "counted in WR but excluded from mean/median R (see `IS n` vs the R "
      "columns).")
    a("- **Sample sizes are reported per cell.** Small-n cells (n<20) are shown "
      "rather than pooled away — read them as indicative only.")
    a("")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"\nReport → {REPORT_PATH}")
    print(f"Verdict: {vd}")
    return 0


# ═════════════════════════════════════════════════════════════════════════════

def main() -> int:
    ap = argparse.ArgumentParser(description="P39 volume-as-confidence analysis")
    ap.add_argument("phase", choices=["aggregate", "analyse", "all"],
                    help="aggregate ticks, analyse aggregates, or both")
    ap.add_argument("tick_dir", nargs="?",
                    help="folder of HistData TICK zips (aggregate/all)")
    ap.add_argument("--trades", help="explicit path to the trade log CSV/DB")
    ap.add_argument("--force", action="store_true",
                    help="re-aggregate months already cached")
    args = ap.parse_args()

    print("=" * 64)
    print(" P39 — Volume-as-confidence analysis (measurement only)")
    print("=" * 64)
    print()

    coverage = None
    if args.phase in ("aggregate", "all"):
        if not args.tick_dir:
            print("ERROR: aggregate needs the tick zip folder.\n"
                  "  python scripts/p39_volume_analysis.py all <tick_zip_dir>")
            return 1
        coverage = phase_aggregate(args.tick_dir, force=args.force)
        if args.phase == "aggregate":
            print("\nAggregation done. Now run:\n"
                  "  python scripts/p39_volume_analysis.py analyse")
            return 0

    return phase_analyse(coverage, args.trades)


if __name__ == "__main__":
    sys.exit(main())

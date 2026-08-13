#!/usr/bin/env python3
"""What separates WINNING Market Maker IFVG adds from losers?

Reads the backtest trade dump (data/trades_dump.csv), isolates the MM
continuation legs (entry_type starts with "mm_"), and profiles winners vs losers
across every tag the leg carries — so we can find the quality filter that keeps
the PF-6.5 winners and drops the 36%-WR losers that blow MaxDD past -15%.

Produce the dump first (a MM-enabled run writes it):
    MM_CONTINUATION_ENABLED=1 MM_HTF_SMT_REQUIRED=1 \
        python run_backtest_histdata.py --years 2022 2023 2024 2025
    python scripts/mm_analysis.py            # writes data/mm_winners_report.md
    python scripts/mm_analysis.py --selftest # no data needed

entry_type encodes: mm_<pattern>_<entryTF>_ifvg<ifvgTF>  e.g. mm_fvg_m5_ifvg240T.
True R = (exit-entry)*direction / |entry-stop|. IS = 2022-23, OOS = 2024-25.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# run_backtest_histdata.py writes the dump under data/histdata/ by default; also
# accept data/ and the TRADE_CSV override. First existing path wins.
_DUMP_CANDIDATES = [
    os.environ.get("TRADE_CSV"),
    os.path.join(_ROOT, "data", "histdata", "trades_dump.csv"),
    os.path.join(_ROOT, "data", "trades_dump.csv"),
]
DUMP = next((p for p in _DUMP_CANDIDATES if p and os.path.exists(p)),
            _DUMP_CANDIDATES[1])
REPORT = os.path.join(_ROOT, "data", "mm_winners_report.md")

_ET = re.compile(r"^mm_(?P<pat>fvg|ob|breaker)_(?P<etf>m5|m1)_ifvg(?P<ifvg>.+)$")

# tag columns to profile (only those present in the dump are used)
DIMS = ["ifvg_tf", "pattern", "entry_tf", "htf_smt", "pair", "profile",
        "direction", "draw_score", "conf_bucket", "crt_tf", "mstruct_minor_sweep",
        "amd_swept_pdliq", "soj_type"]


def parse_entry_type(et):
    """(pattern, entry_tf, ifvg_tf) or (None, None, None) for non-MM rows."""
    m = _ET.match(str(et))
    if not m:
        return (None, None, None)
    return (m.group("pat"), m.group("etf"), m.group("ifvg"))


def true_r(entry, stop, exit_, direction):
    """R multiple off the leg's own stop; None when the stop is degenerate."""
    try:
        risk = abs(float(entry) - float(stop))
        if risk <= 0:
            return None
        return (float(exit_) - float(entry)) * float(direction) / risk
    except (TypeError, ValueError):
        return None


def pip_size(pair):
    return 0.01 if str(pair).upper().endswith("JPY") else 0.0001


def _stats(vals):
    """(n, mean, median, max) over a numeric list, Nones dropped."""
    xs = sorted(v for v in vals if v is not None and v == v)
    if not xs:
        return (0, None, None, None)
    n = len(xs)
    mean = sum(xs) / n
    mid = xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2
    return (n, mean, mid, xs[-1])


def _pf(rows):
    gp = sum(r for r in rows if r > 0)
    gl = -sum(r for r in rows if r < 0)
    return (gp / gl) if gl > 0 else (float("inf") if gp > 0 else 0.0)


def _agg(df):
    """(n, WR%, PF, meanR) over a frame with 'win' and 'R' columns."""
    n = len(df)
    if n == 0:
        return (0, None, None, None)
    wr = 100.0 * df["win"].mean()
    rs = [r for r in df["R"].tolist() if r is not None and r == r]  # drop None + NaN
    pf = _pf(rs) if rs else None
    meanr = (sum(rs) / len(rs)) if rs else None
    return (n, wr, pf, meanr)


def _fmt(v, kind="f"):
    if v is None:
        return "—"
    if v == float("inf"):
        return "∞"
    return f"{v:.0f}%" if kind == "wr" else f"{v:.2f}"


def _dim_table(mm, dim):
    import pandas as pd  # noqa: F401
    lines = [f"### by `{dim}`", "",
             "| value | n | WR | PF | meanR | IS WR/PF | OOS WR/PF |",
             "|---|---|---|---|---|---|---|"]
    vals = mm[dim].value_counts(dropna=False)
    for val, _cnt in vals.items():
        sub = mm[mm[dim].astype(str) == str(val)]
        n, wr, pf, mr = _agg(sub)
        i = _agg(sub[sub["split"] == "IS"])
        o = _agg(sub[sub["split"] == "OOS"])
        lines.append(f"| {val} | {n} | {_fmt(wr,'wr')} | {_fmt(pf)} | {_fmt(mr)} "
                     f"| {_fmt(i[1],'wr')}/{_fmt(i[2])} | {_fmt(o[1],'wr')}/{_fmt(o[2])} |")
    lines.append("")
    return lines


def analyse():
    import pandas as pd
    if not os.path.exists(DUMP):
        return [f"**ERROR: no trade dump at {os.path.relpath(DUMP, _ROOT)}.** Run a "
                "MM-enabled backtest first:\n\n```\nMM_CONTINUATION_ENABLED=1 "
                "MM_HTF_SMT_REQUIRED=1 python run_backtest_histdata.py "
                "--years 2022 2023 2024 2025\n```"]
    df = pd.read_csv(DUMP)
    if "entry_type" not in df.columns:
        return ["**ERROR: trade dump has no entry_type column.**"]
    parsed = df["entry_type"].map(parse_entry_type)
    df["pattern"] = [p[0] for p in parsed]
    df["entry_tf"] = [p[1] for p in parsed]
    df["ifvg_tf"] = [p[2] for p in parsed]
    mm = df[df["pattern"].notna()].copy()
    if mm.empty:
        return ["**No MM legs in the dump.** Was the run MM_CONTINUATION_ENABLED=1? "
                "(entry_type has no `mm_*` rows.)"]

    mm["win"] = mm["pnl"] > 0
    mm["R"] = [true_r(e, s, x, d) for e, s, x, d in
               zip(mm.get("entry"), mm.get("stop"), mm.get("exit"), mm.get("direction"))]
    mm["pips"] = [((float(x) - float(e)) * float(d) / pip_size(p))
                  if (x == x and e == e) else None
                  for e, x, d, p in
                  zip(mm.get("entry"), mm.get("exit"), mm.get("direction"), mm.get("pair"))]
    yr = pd.to_datetime(mm.get("opened_at"), errors="coerce").dt.year
    mm["split"] = yr.map(lambda y: "IS" if y in (2022, 2023) else
                         ("OOS" if y in (2024, 2025) else "?"))
    if "target_confluence" in mm.columns:
        mm["conf_bucket"] = mm["target_confluence"].map(
            lambda c: "≥4" if c >= 4 else ("3" if c == 3 else "<3"))

    n, wr, pf, mr = _agg(mm)
    L = ["# What separates winning MM IFVG adds from losers", "",
         f"Isolated **{n} MM continuation legs** from the trade dump. Overall: "
         f"**WR {_fmt(wr,'wr')} · PF {_fmt(pf)} · meanR {_fmt(mr)}**. Each table below "
         "is the SAME legs bucketed by one tag — a value with clearly higher WR/PF "
         "that HOLDS in both IS and OOS is a shippable quality filter; one that "
         "flips between splits is noise.", "",
         "_IS = 2022-23, OOS = 2024-25. R = (exit−entry)·dir / |entry−stop|._", ""]

    # winners-vs-losers headline: for each dim, the best-and-worst value by WR
    L += ["## Headline — strongest separators", "",
          "| tag | best value (WR, n) | worst value (WR, n) |", "|---|---|---|"]
    for dim in DIMS:
        if dim not in mm.columns:
            continue
        rows = []
        for val in mm[dim].dropna().unique():
            sub = mm[mm[dim].astype(str) == str(val)]
            if len(sub) >= 8:                 # ignore tiny buckets in the headline
                rows.append((str(val), 100.0 * sub["win"].mean(), len(sub)))
        if not rows:
            continue
        rows.sort(key=lambda r: r[1], reverse=True)
        best, worst = rows[0], rows[-1]
        L.append(f"| {dim} | {best[0]} ({best[1]:.0f}%, {best[2]}) | "
                 f"{worst[0]} ({worst[1]:.0f}%, {worst[2]}) |")
    L.append("")

    # win/loss pip + R economics
    wins = mm[mm["win"]]
    losses = mm[~mm["win"]]
    wn, wmean, wmed, wmax = _stats(wins["pips"].tolist())
    ln, lmean, lmed, lmax = _stats(losses["pips"].tolist())
    _, wrmean, _, wrmax = _stats([r for r in wins["R"].tolist()])
    _, lrmean, _, _ = _stats([r for r in losses["R"].tolist()])
    exp_pips = _stats(mm["pips"].tolist())[1]
    exp_r = _stats([r for r in mm["R"].tolist()])[1]
    L += ["## Win / loss economics", "",
          "| | n | avg pips | median pips | max pips | avg R |",
          "|---|---|---|---|---|---|",
          f"| **wins** | {wn} | {_fmt(wmean)} | {_fmt(wmed)} | {_fmt(wmax)} | {_fmt(wrmean)} |",
          f"| losses | {ln} | {_fmt(lmean)} | {_fmt(lmed)} | {_fmt(lmax)} | {_fmt(lrmean)} |",
          "",
          f"_Per-add expectancy: **{_fmt(exp_pips)} pips**, **{_fmt(exp_r)} R**. "
          f"Biggest win {_fmt(wmax)} pips / {_fmt(wrmax)}R._", ""]

    # where the big wins come from — avg win pips per bucket
    L += ["## Specs of the winning adds (winners only)", "",
          "For the winning legs only: how many, their share, and their pip size — "
          "so the 'good entry' profile is explicit.", ""]
    for dim in ("ifvg_tf", "pattern", "entry_tf", "pair", "draw_score", "conf_bucket"):
        if dim not in mm.columns:
            continue
        L += [f"### winners by `{dim}`", "",
              "| value | wins | % of wins | avg win pips | median | max |",
              "|---|---|---|---|---|---|"]
        tot = len(wins)
        for val, cnt in wins[dim].value_counts(dropna=False).items():
            sub = wins[wins[dim].astype(str) == str(val)]
            _, mean, med, mx = _stats(sub["pips"].tolist())
            share = 100.0 * cnt / tot if tot else 0
            L.append(f"| {val} | {cnt} | {share:.0f}% | {_fmt(mean)} | {_fmt(med)} | {_fmt(mx)} |")
        L.append("")

    L += ["## Full breakdown by tag (all legs)", ""]
    for dim in DIMS:
        if dim in mm.columns:
            L += _dim_table(mm, dim)
    return L


def _selftest():
    assert parse_entry_type("mm_fvg_m5_ifvg240T") == ("fvg", "m5", "240T")
    assert parse_entry_type("mm_breaker_m1_ifvgW") == ("breaker", "m1", "W")
    assert parse_entry_type("amd_fvg_m5") == (None, None, None)
    assert abs(true_r(1.1000, 1.0990, 1.1030, 1) - 3.0) < 1e-9      # +30/10 = 3R
    assert abs(true_r(1.1000, 1.1010, 1.0980, -1) - 2.0) < 1e-9     # short winner
    assert true_r(1.1, 1.1, 1.12, 1) is None                       # degenerate stop
    assert abs(_pf([3, -1, 2, -1]) - 2.5) < 1e-9
    print("selftest OK — entry_type parse, true R (long/short/degenerate), PF")
    return 0


def _publish(path):
    """Force-add (data/ is gitignored), commit, pull, push the report so Claude
    can read it without the manual git dance. Best-effort — prints on failure."""
    def _git(*args):
        return subprocess.run(["git", *args], cwd=_ROOT,
                              capture_output=True, text=True)
    _git("add", "-f", path)
    sha = (_git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown")
    _git("commit", "-q", "-m", f"MM winners report (auto, commit {sha})")
    _git("pull", "-q", "--no-rebase", "--no-edit", "origin", "HEAD")
    p = _git("push", "origin", "HEAD")
    if p.returncode == 0:
        print("RESULTS PUSHED — Claude can read data/mm_winners_report.md")
    else:
        print("(auto-push failed — paste the report above to Claude)\n" + p.stderr[-300:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-push", action="store_true",
                    help="write + print the report but don't commit/push it")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    text = "\n".join(analyse()) + "\n"
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)
    print(f"[report → {os.path.relpath(REPORT, _ROOT)}]")
    if not a.no_push:
        _publish(REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())

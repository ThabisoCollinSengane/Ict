#!/usr/bin/env python3
"""Draw-on-liquidity ladder study — how price reacts to each liquidity rung.

Two questions, both from the full trade dump (all pairs, 2022-2025):

  A · Targets — how does price react to each DRAW TYPE it aims at?
      Groups trades by `target_type` (pdh_pdl=prev 1-3 days, pwh_pwl=week,
      ith/itl=major swings, fib, swing, round_number). Reports n / win-rate /
      hit-rate (reached the target) / PF / mean-R, split IS vs OOS.

  B · The ladder — when the raid is done, WHERE does price actually go?
      Uses the per-trade draw ladder logged at entry (distance to the nearest
      UNSWEPT pool ahead at each rung: previous session H/L, 3-day, week, 30-day,
      60-day) and max-favorable-excursion (MFE). For each rung: of trades where
      that pool was a live draw ahead, what fraction did price DELIVER to
      (MFE >= distance), and the median distance. This is the ICT cascade —
      session -> 3d -> week -> 30d -> 60d — measured.

Run:  python scripts/draw_ladder_analysis.py            # reads data/histdata/trades_dump.csv
      python scripts/draw_ladder_analysis.py --selftest
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DUMP = os.path.join(DATA_DIR, "histdata", "trades_dump.csv")
REPORT = os.path.join(DATA_DIR, "draw_ladder_report.md")

RUNGS = [("previous session", "lad_sess"), ("3-day", "lad_d3"),
         ("weekly", "lad_wk"), ("30-day", "lad_d30"), ("60-day", "lad_d60")]


def _year(s):
    s = (s or "").strip()
    return s[:4] if len(s) >= 4 and s[:4].isdigit() else ""


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _split(rows):
    return ([r for r in rows if _year(r.get("opened_at")) in ("2022", "2023")],
            [r for r in rows if _year(r.get("opened_at")) in ("2024", "2025")])


def _pf(rows):
    pn = [_f(r.get("pnl")) for r in rows]
    pn = [p for p in pn if p is not None]
    gp = sum(p for p in pn if p > 0)
    gl = -sum(p for p in pn if p <= 0)
    return (gp / gl) if gl > 0 else (float("inf") if gp > 0 else None)


def _wr(rows):
    pn = [_f(r.get("pnl")) for r in rows]
    pn = [p for p in pn if p is not None]
    return (100.0 * sum(1 for p in pn if p > 0) / len(pn)) if pn else None


def _hit(rows):
    """Fraction whose exit reason was reaching the target."""
    r2 = [r for r in rows if r.get("reason")]
    if not r2:
        return None
    return 100.0 * sum(1 for r in r2 if r.get("reason") == "target") / len(r2)


def _fw(v, k):
    if v is None:
        return "—"
    return {"wr": f"{v:.1f}%", "pf": ("inf" if v == float("inf") else f"{v:.2f}"),
            "pct": f"{v:.0f}%", "pips": f"{v:.0f}"}.get(k, str(v))


def _med(vals):
    v = sorted(x for x in vals if x is not None)
    if not v:
        return None
    n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def target_table(rows):
    types = sorted({(r.get("target_type") or "?") for r in rows})
    L = ["## A · Targets — how price reacts to each draw type it aims at", "",
         "`hit` = reached the target (vs stopped/other). IS = 2022-23, OOS = 2024-25.", "",
         "| target type | n IS/OOS | WR IS | WR OOS | hit IS | hit OOS | PF IS | PF OOS |",
         "|---|---|---|---|---|---|---|---|"]
    order = ["pwh_pwl", "pdh_pdl", "ith_liquidity", "itl_liquidity",
             "fib_extension", "fvg", "ob", "equal_hl", "swing", "round_number"]
    types = [t for t in order if t in types] + [t for t in types if t not in order]
    for t in types:
        sub = [r for r in rows if (r.get("target_type") or "?") == t]
        i, o = _split(sub)
        if not sub:
            continue
        L.append(f"| `{t}` | {len(i)}/{len(o)} | {_fw(_wr(i),'wr')} | {_fw(_wr(o),'wr')} | "
                 f"{_fw(_hit(i),'pct')} | {_fw(_hit(o),'pct')} | {_fw(_pf(i),'pf')} | "
                 f"{_fw(_pf(o),'pf')} |")
    return L


def ladder_table(rows):
    L = ["## B · The ladder — when the raid is done, where does price deliver?", "",
         "For each rung: of trades where that pool was an UNSWEPT draw ahead at entry, "
         "the share price DELIVERED to (max-favorable-excursion reached the pool), plus "
         "the median distance to it. This is the ICT draw cascade, measured.", "",
         "| rung | n IS/OOS (draw ahead) | delivered IS | delivered OOS | median dist IS | median dist OOS |",
         "|---|---|---|---|---|---|"]
    for name, col in RUNGS:
        sub = [r for r in rows if _f(r.get(col)) is not None]
        i, o = _split(sub)

        def deliv(rr):
            if not rr:
                return None
            reached = sum(1 for r in rr if (_f(r.get("mfe_pips")) or -1) >= _f(r.get(col)))
            return 100.0 * reached / len(rr)
        L.append(f"| {name} | {len(i)}/{len(o)} | {_fw(deliv(i),'pct')} | {_fw(deliv(o),'pct')} | "
                 f"{_fw(_med([_f(r.get(col)) for r in i]),'pips')} | "
                 f"{_fw(_med([_f(r.get(col)) for r in o]),'pips')} |")
    L += ["", "_A rung with few trades 'ahead' means price had usually already taken "
          "that pool by entry (it sits behind the fade) — itself a finding: the nearer "
          "rungs get consumed first, exactly the cascade order._"]
    return L


def analyse(path):
    if not os.path.exists(path):
        return ["# Draw-ladder study", "", f"ERROR: no trade dump at `{path}` — run the backtest first."]
    with open(path) as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return ["# Draw-ladder study", "", "ERROR: empty trade dump."]
    has_ladder = "lad_d3" in rows[0]
    L = ["# Draw-on-liquidity ladder — how price reacts to each rung", "",
         f"_trades: {len(rows)} · IS = 2022-23, OOS = 2024-25_", ""]
    L += target_table(rows)
    L += [""]
    if has_ladder:
        L += ladder_table(rows)
    else:
        L += ["## B · The ladder", "", "⚠️ The `lad_*` / `mfe_pips` columns aren't in this "
              "dump — re-run the backtest on the current branch (the ladder instrumentation "
              "logs them), then re-run this analysis."]
    return L


def _selftest():
    rows = [
        {"target_type": "pwh_pwl", "reason": "target", "pnl": "100",
         "opened_at": "2022-05-01", "mfe_pips": "40", "lad_d3": "20", "lad_wk": "35",
         "lad_d30": "80", "lad_d60": "", "lad_sess": "12"},
        {"target_type": "pdh_pdl", "reason": "stop", "pnl": "-30",
         "opened_at": "2024-05-01", "mfe_pips": "8", "lad_d3": "15", "lad_wk": "",
         "lad_d30": "", "lad_d60": "", "lad_sess": "6"},
    ]
    assert abs(_wr(rows) - 50.0) < .1
    assert _hit([rows[0]]) == 100.0
    # ladder: for lad_d3, trade1 mfe40>=20 reached, trade2 mfe8<15 not → 50%
    sub = [r for r in rows if _f(r.get("lad_d3")) is not None]
    reached = sum(1 for r in sub if (_f(r.get("mfe_pips")) or -1) >= _f(r.get("lad_d3")))
    assert reached == 1 and len(sub) == 2, (reached, len(sub))
    assert _med([12.0, 6.0, 35.0]) == 12.0
    print("selftest OK — WR, hit-rate, ladder delivery, median all pass")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", default=DUMP)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    text = "\n".join(analyse(a.dump)) + "\n"
    with open(REPORT, "w") as f:
        f.write(text)
    print(text)
    print(f"[report → {REPORT}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())

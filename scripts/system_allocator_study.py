"""P109 — three systems (FX / gold / indices): pick the most probable one per session?

    python scripts/system_allocator_study.py --dumps data/mm_golden_full_idx05_p104_trades.csv ...

Each trade is put in a SLOT = (New York date, session). Sessions: London (opened before
06:00 ET) and NY. Every trade is measured in R (profit / initial risk) so systems sized
differently compare fairly: R = (exit - entry) x direction / |entry - init_stop| when the
dump has `init_stop` (P109 onward); otherwise per-unit move / the 80th-percentile losing move of that pair-year (~ a full stop).

Rules (learned on IS 2022-23, judged on OOS 2024-25 and 2026):
  all        take every system's trades (what the bot does now)
  fixed      each session trades ONLY its IS-best system
  pick       when more than one system trades in a slot, keep only the system with the
             best IS average R for that session; a lone system is always kept
  quality    in a contested slot keep the system whose trades score highest on the bot's
             own setup quality (draw_score + target_confluence), tie -> IS prior
  sizeup     keep all; the slot's IS-best system at 1.25x
  random     in a contested slot keep one system at random (500 reps) — the control
A selection rule only has value if it beats `all` AND `random`.
"""
import argparse

import numpy as np
import pandas as pd

SYS = {"XAUUSD": "Gold", "SPXUSD": "Indices", "NSXUSD": "Indices",
       "US500": "Indices", "US100": "Indices"}


def load(paths):
    fr = []
    for p in paths:                     # "file.csv:Gold" keeps only that system's trades
        f, _, only = p.partition(":")
        x = pd.read_csv(f)
        if only:
            x = x[x.pair.map(lambda q: SYS.get(q, "FX")) == only]
        fr.append(x)
    d = pd.concat(fr, ignore_index=True)
    d = d.drop_duplicates(subset=["pair", "opened_at", "leg_idx"]).copy()
    d["t"] = pd.to_datetime(d.opened_at, utc=True).dt.tz_convert("America/New_York")
    d["date"] = d.t.dt.date
    d["sess"] = np.where(d.t.dt.hour < 6, "London", "NY")
    d["sys"] = d.pair.map(lambda p: SYS.get(p, "FX"))
    d["year"] = d.t.dt.year
    d["half"] = np.select([d.year <= 2023, d.year <= 2025], ["IS", "OOS"], "2026")
    r = pd.Series(np.nan, index=d.index)
    if "init_stop" in d:
        ist = pd.to_numeric(d.init_stop, errors="coerce")
        risk = (d.entry - ist).abs()
        ok = risk > 0
        r[ok] = (d.exit - d.entry)[ok] * d.direction[ok] / risk[ok]
    miss = r.isna()
    if miss.any():
        mv = d.pnl / d.units                       # per-unit move: removes position size
        unit = mv[mv < 0].abs().groupby([d.pair, d.year]).quantile(0.8)   # ~ a full stop
        u = d.set_index(["pair", "year"]).index.map(unit).to_numpy(dtype=float)
        r[miss] = (mv / u)[miss]
    d["R"] = r
    q = pd.to_numeric(d.get("draw_score", 0), errors="coerce").fillna(0) \
        + pd.to_numeric(d.get("target_confluence", 0), errors="coerce").fillna(0)
    d["q"] = q
    return d.dropna(subset=["R"])


def stats(rs):
    rs = np.asarray(rs, dtype=float)
    if not len(rs):
        return 0, 0.0, np.nan, 0.0
    eq = np.cumsum(rs)
    dd = (np.maximum.accumulate(np.r_[0, eq])[1:] - eq).max()
    g, l = rs[rs > 0].sum(), -rs[rs < 0].sum()
    return len(rs), rs.sum(), (g / l if l else np.nan), dd


def apply(d, keep_mask, w=None):
    x = d[keep_mask].sort_values("t")
    rr = x.R * (w[keep_mask].loc[x.index] if w is not None else 1.0)
    return stats(rr.to_numpy())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dumps", nargs="+", required=True)
    ap.add_argument("--out", default="data/system_allocator_report.md")
    a = ap.parse_args()
    d = load(a.dumps)
    is_ = d[d.half == "IS"]
    prior = is_.groupby(["sess", "sys"]).R.mean()
    best = {s: prior.xs(s).idxmax() for s in prior.index.get_level_values(0).unique()}
    d["prior"] = d.set_index(["sess", "sys"]).index.map(prior).to_numpy(dtype=float)
    d["slot"] = list(zip(d.date, d.sess))
    nsys = d.groupby("slot").sys.nunique()
    d["contested"] = d.slot.map(nsys) > 1

    # pick: per slot keep the system with the best prior
    slot_best = d.groupby("slot").apply(lambda g: g.loc[g.prior.idxmax(), "sys"])
    pick = d.sys == d.slot.map(slot_best)
    # quality: per slot, system with the highest mean quality, tie -> prior
    sq = d.groupby(["slot", "sys"]).agg(q=("q", "mean"), p=("prior", "first")).reset_index()
    sq = sq.sort_values(["q", "p"], ascending=False).drop_duplicates("slot")
    qual = d.sys == d.slot.map(dict(zip(sq.slot, sq.sys)))
    fixed = d.sys == d.sess.map(best)
    w_up = pd.Series(np.where(d.sys == d.sess.map(best), 1.25, 1.0), index=d.index)

    L = ["# Three systems — pick the most probable per session? (P109)", "",
         f"{len(d)} trades from {len(a.dumps)} dump(s). R = profit / initial risk "
         f"({'init_stop' if 'init_stop' in d else 'proxy: per-unit move / 80th-pct losing move per pair-year (~ a full stop)'}).", "",
         "## Each system by session (n / WR / avg R / PF in R)", "",
         "| system | session | IS | OOS | 2026 |", "|---|---|---|---|---|"]
    for (sy, se), g in d.groupby(["sys", "sess"]):
        cells = []
        for h in ("IS", "OOS", "2026"):
            x = g[g.half == h].R
            n, tot, pf, _ = stats(x)
            cells.append(f"{n} / {(x > 0).mean()*100:.0f}% / {x.mean():+.2f} / {pf:.2f}" if n else "—")
        L.append(f"| {sy} | {se} | " + " | ".join(cells) + " |")
    L += ["", f"IS-best system per session: " + ", ".join(f"{k} -> {v}" for k, v in best.items()),
          f"Slots with more than one system trading: {int((nsys > 1).sum())} of {len(nsys)}.", "",
          "## Rules (total R / trades / PF / max drawdown in R)", "",
          "| rule | IS | OOS | 2026 |", "|---|---|---|---|"]
    rng = np.random.default_rng(9)
    rules = {"all": (pd.Series(True, index=d.index), None), "fixed": (fixed, None),
             "pick": (pick, None), "quality": (qual, None),
             "sizeup": (pd.Series(True, index=d.index), w_up)}
    for name, (m, w) in rules.items():
        cells = []
        for h in ("IS", "OOS", "2026"):
            hm = d.half == h
            n, tot, pf, dd = apply(d, m & hm, w)
            cells.append(f"{tot:+.1f}R / {n} / {pf:.2f} / {dd:.1f}")
        L.append(f"| {name} | " + " | ".join(cells) + " |")
    cells = []
    for h in ("IS", "OOS", "2026"):
        hd = d[d.half == h]
        tots = []
        for _ in range(500):
            ch = hd.groupby("slot").sys.agg(lambda s: rng.choice(s.unique()))
            tots.append(hd[hd.sys == hd.slot.map(ch)].R.sum())
        cells.append(f"median {np.median(tots):+.1f}R (5-95%: {np.percentile(tots,5):+.1f}..{np.percentile(tots,95):+.1f})")
    L.append("| random (control) | " + " | ".join(cells) + " |")
    corr = d.groupby(["date", "sys"]).R.sum().unstack()
    L += ["", "## Daily R correlation between systems (days both traded)", "",
          "```\n" + corr.corr(min_periods=20).round(2).to_string() + "\n```", ""]
    txt = "\n".join(L) + "\n"
    open(a.out, "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()

"""Backtest using real HistData.com 1-minute OHLC data.

Data files required in data/histdata/:
  GBPUSD_2025.csv, EURUSD_2025.csv, EURGBP_2025.csv, UDXUSD_2025.csv

HistData format:  YYYYMMDD HHMMSS;Open;High;Low;Close;Volume
Timezone:         US Eastern Standard Time (fixed UTC-5, no DST shift)

Uses the actual DXY index (UDXUSD) directly for DXY bias instead of the
6-constituent synthetic formula, since we have real index data.
"""

import argparse
import os
import sys
from collections import namedtuple

import pandas as pd

import config
from ict.bias import htf_bias
from ict.amd import detect_consolidation, detect_manipulation
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.killzones import can_open_new_trade
from ict.dealing_range import (
    detect_dealing_range, is_valid_entry_zone, is_valid_target_zone,
    is_nfp_week_low_probability, is_post_fomc_low_probability,
)
from intermarket import resolve as resolve_intermarket
from news_filter import NewsCalendar
from risk import position_size, pip_size
import backtest as bt_module   # reuse summarize()

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "histdata")

# HistData uses fixed Eastern Standard Time (UTC-5).  Add 5 h to get UTC.
_EST_OFFSET = pd.Timedelta(hours=5)

Bar = namedtuple("Bar", "Open High Low Close")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_m1(filepath: str) -> pd.DataFrame:
    """Load HistData ASCII M1 CSV and convert timestamps to UTC."""
    df = pd.read_csv(
        filepath, sep=";", header=None,
        names=["dt", "Open", "High", "Low", "Close", "Volume"],
        dtype={"Open": float, "High": float, "Low": float, "Close": float},
    )
    df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S") + _EST_OFFSET
    df = df.set_index("dt")[["Open", "High", "Low", "Close"]]
    df.index = df.index.tz_localize("UTC")
    return df


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return df.resample(rule).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    ).dropna()


def df_to_bars(df: pd.DataFrame) -> list[Bar]:
    return [Bar(r.Open, r.High, r.Low, r.Close) for r in df.itertuples(index=False)]


# ---------------------------------------------------------------------------
# Backtester subclass — swaps in real DXY for synthetic
# ---------------------------------------------------------------------------

class HistdataBacktester(bt_module.Backtester):
    """Identical to Backtester but uses real UDXUSD for DXY bias."""

    def __init__(self, data_5m: dict, dxy_5m: pd.DataFrame, data_m1: dict | None = None):
        super().__init__(data_5m)
        # Register raw M1 bars for tradeable pairs (fractal pattern detection on M1).
        if data_m1:
            for sym, df in data_m1.items():
                self.tf_dfs[(sym, "1T")]   = df
                self.tf_bars[(sym, "1T")]  = df_to_bars(df)
                self.tf_index[(sym, "1T")] = df.index
        # Register UDXUSD at all needed timeframes (including W for DXY FVG context).
        for tf_name, rule in [
            ("5T", None), ("15T", "15min"), ("60T", "60min"),
            ("240T", "240min"), ("D", "1D"), ("W", "1W"),
        ]:
            d = dxy_5m if rule is None else _resample(dxy_5m, rule)
            self.tf_dfs[("UDXUSD", tf_name)] = d
            self.tf_bars[("UDXUSD", tf_name)] = df_to_bars(d)
            self.tf_index[("UDXUSD", tf_name)] = d.index

    def _dxy_bias(self, tf, t, lookback=None) -> int:
        """Use real UDXUSD at any timeframe instead of ICE-formula synthetic DXY."""
        bars = self.bars_up_to("UDXUSD", tf, t)
        lb = lookback if lookback is not None else config.SWING_LOOKBACK
        return htf_bias(bars, lookback=lb)

    def _dxy_bias_1h(self, t, lookback=None) -> int:
        return self._dxy_bias("60T", t, lookback=lookback)

    def _dxy_bars(self, tf, t):
        """Use real UDXUSD bars for Judas divergence (matches _dxy_bias override)."""
        return self.bars_up_to("UDXUSD", tf, t)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ICT Intermarket Backtest")
    parser.add_argument(
        "--years", nargs="+", default=["2022", "2023", "2024", "2025"],
        metavar="YYYY",
        help="Which years to include (default: all four)",
    )
    args = parser.parse_args()
    requested_years = args.years

    label = "–".join([requested_years[0], requested_years[-1]])
    print("=" * 60)
    print(f"ICT Intermarket Backtest — HistData.com M1 data ({label})")
    print("=" * 60)

    years = requested_years
    # Core pairs required for the EUR/GBP family. AUD/NZD pairs are optional —
    # the backtest runs without them and gains those trades when data is added.
    core_syms     = ["GBPUSD", "EURUSD", "EURGBP", "UDXUSD"]
    optional_syms = ["AUDUSD", "NZDUSD", "AUDNZD"]
    # Gold complex — loaded only when the gold gate is enabled (config.GOLD_ENABLED).
    # XAUUSD is tradeable (in config.PAIRS); XAGUSD + AUDUSD are the confirmer refs.
    if config.GOLD_ENABLED:
        for _s in (config.GOLD_PAIR, config.GOLD_REF_SILVER, config.GOLD_REF_AUD):
            if _s not in core_syms and _s not in optional_syms:
                optional_syms.append(_s)
    # US indices — loaded only when the index gate is enabled. US500/US100 are
    # tradeable (in config.PAIRS); US30 is the confirmer ref.
    if config.INDICES_ENABLED:
        for _s in tuple(config.INDEX_PAIRS) + (config.INDEX_REF,):
            if _s not in core_syms and _s not in optional_syms:
                optional_syms.append(_s)

    import glob as _glob

    def _year_has_data(sym, yr):
        """True if annual OR at least one monthly file exists for this sym/year."""
        if os.path.exists(os.path.join(DATA_DIR, f"{sym}_{yr}.csv")):
            return True
        return bool(_glob.glob(os.path.join(DATA_DIR, f"{sym}_{yr}_*.csv")))

    # Filter to years where all core pairs have at least some data.
    years = [yr for yr in years if all(_year_has_data(s, yr) for s in core_syms)]
    if not years:
        print("ERROR: no data found for core pairs in requested years")
        print(f"  Core pairs needed: {core_syms}")
        print(f"  Data directory: {DATA_DIR}")
        sys.exit(1)

    # Determine which optional pairs have coverage for the same years.
    available_optional = [
        s for s in optional_syms
        if all(_year_has_data(s, yr) for yr in years)
    ]
    if available_optional:
        print(f"  Optional pairs available: {', '.join(available_optional)}")
    else:
        print("  Optional pairs (AUDUSD/NZDUSD/AUDNZD): not yet downloaded — "
              "download from HistData.com to enable AUD/NZD trades")

    syms = core_syms + available_optional

    print(f"\nLoading and resampling to 5-minute bars ({' + '.join(years)})...")
    data_5m = {}
    data_m1 = {}   # raw 1-minute bars for tradeable pairs (M1 pattern detection)
    dxy_5m = None
    _tradeable = set(config.PAIRS)  # GBPUSD, EURUSD, NZDUSD
    for sym in syms:
        frames = []
        for yr in years:
            annual = os.path.join(DATA_DIR, f"{sym}_{yr}.csv")
            if os.path.exists(annual):
                frames.append(load_m1(annual))
            else:
                # Fall back to monthly files: PAIR_YYYY_MM.csv (for partial years)
                import glob as _glob
                monthly = sorted(_glob.glob(os.path.join(DATA_DIR, f"{sym}_{yr}_*.csv")))
                if monthly:
                    for mp in monthly:
                        frames.append(load_m1(mp))
                else:
                    # Year data genuinely missing — skip silently (already gated above)
                    pass
        if not frames:
            continue
        m1 = pd.concat(frames).sort_index()
        m1 = m1[~m1.index.duplicated(keep='first')]
        m5 = _resample(m1, "5min")
        print(f"  {sym}: {len(m1):>7,} M1 → {len(m5):>6,} M5 bars  "
              f"{m5.index[0].date()} – {m5.index[-1].date()}  "
              f"close {m5['Close'].iloc[-1]:.5f}")
        if sym == "UDXUSD":
            dxy_5m = m5
        else:
            data_5m[sym] = m5
            # M1 bars registered for tradeable pairs — used for stop placement
            # (_m1_structure_stop anchors the stop to the nearest M1 swing).
            if sym in _tradeable:
                data_m1[sym] = m1

    print("\nRunning backtest...")
    backtester = HistdataBacktester(data_5m, dxy_5m, data_m1)
    backtester.run()

    print("\n=== Gate funnel (entries passing each filter) ===")
    max_v = max(backtester.gate.values()) or 1
    for k, v in backtester.gate.items():
        bar_width = min(v * 40 // max(max_v, 1), 40)
        bar = "█" * bar_width
        print(f"  {k:32s} {v:6d}  {bar}")

    print("\n=== Results ===")
    results = bt_module.summarize(backtester)
    for k, v in results.items():
        print(f"  {k:25s} {v}")

    # Per-year withdrawal (income) report — "did it make ends meet each year?"
    events = getattr(backtester, "withdrawal_events", [])
    if events:
        from collections import defaultdict
        by_year_amt = defaultdict(float)
        by_year_cnt = defaultdict(int)
        for ts, amt, _keep in events:
            yr = getattr(ts, "year", None) or "?"
            by_year_amt[yr] += amt
            by_year_cnt[yr] += 1
        print("\n=== Withdrawals (income) per year — amount, frequency, avg ===")
        for yr in sorted(by_year_amt, key=lambda x: str(x)):
            cnt = by_year_cnt[yr]
            avg = by_year_amt[yr] / cnt if cnt else 0
            print(f"  {yr}: R{by_year_amt[yr]:>12,.0f}  ({cnt:>3} withdrawals, "
                  f"~1 / {round(365/cnt) if cnt else 0}d, avg R{avg:,.0f})")
        tot = sum(by_year_amt.values())
        cnt_tot = sum(by_year_cnt.values())
        print(f"  TOTAL income: R{tot:,.0f} across {cnt_tot} withdrawals "
              f"(avg R{(tot/cnt_tot if cnt_tot else 0):,.0f} each)")
        print(f"  final working balance: R{backtester.equity:,.0f}  "
              f"(keep-level R{getattr(backtester, '_keep_level', 0):,.0f})")

    if backtester.trades:
        df = pd.DataFrame(backtester.trades)
        # Full trade dump for offline analysis (Judas vs continuation, session
        # breakdowns, same-day co-occurrence). Set TRADE_CSV to override path.
        _csv_path = os.environ.get("TRADE_CSV", os.path.join(DATA_DIR, "trades_dump.csv"))
        try:
            df.to_csv(_csv_path, index=False)
            print(f"\n[trade dump → {_csv_path}]")
        except Exception as _e:
            print(f"\n[trade dump skipped: {_e}]")
        print(f"\n=== Trade log ({len(backtester.trades)} trades) ===")
        cols = ["opened_at", "closed_at", "pair", "direction",
                "leg_idx", "entry", "exit", "units", "pnl", "reason",
                "session_side", "entry_type"]
        pd.set_option("display.max_rows", None)
        pd.set_option("display.width", 200)
        print(df[cols].to_string(index=False))

        print("\n=== Per-pair P&L (ZAR) ===")
        for pair, grp in df.groupby("pair"):
            w = (grp.pnl > 0).sum()
            print(f"  {pair}: {len(grp)} trades  "
                  f"wins={w}  losses={len(grp)-w}  "
                  f"P&L=R{grp.pnl.sum():.2f}")

        print("\n=== Per-year breakdown ===")
        print(f"  {'Year':<6} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'P&L ZAR':>12} {'MaxDD%':>8}")
        print("  " + "-" * 50)
        df["year"] = df["opened_at"].dt.year
        # Drawdown must be measured on the running account equity (carried across
        # years), not a per-year cumsum reset to 0 over a fixed R500 base — the
        # latter divides a within-year dip by ~R500 even after the account has
        # grown to six figures, producing impossible <-100% readings.
        df_sorted = df.sort_values("opened_at")
        equity = config.STARTING_CASH + df_sorted.pnl.cumsum()
        peak = equity.cummax()
        df_sorted = df_sorted.assign(_dd=(equity - peak) / peak * 100)
        for yr, grp in df_sorted.groupby("year"):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            dd = grp["_dd"].min() if len(grp) else 0
            print(f"  {yr:<6} {len(grp):>7} {w:>5} {wr:>5.1f}% {grp.pnl.sum():>12.2f} {dd:>7.1f}%")

        print("\n=== Per-pair × year ===")
        print(f"  {'Pair':<8} {'Year':<6} {'Trades':>7} {'Wins':>5} {'WR%':>6}")
        print("  " + "-" * 35)
        for (pair, yr), grp in df.groupby(["pair", "year"]):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            print(f"  {pair:<8} {yr:<6} {len(grp):>7} {w:>5} {wr:>5.1f}%")

        print("\n=== Entry-type breakdown ===")
        print(f"  {'Entry type':<20} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'Avg P&L':>10}")
        print("  " + "-" * 50)
        for etype, grp in df.groupby("entry_type"):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            print(f"  {etype:<20} {len(grp):>7} {w:>5} {wr:>5.1f}% {grp.pnl.mean():>10.2f}")

        # --- PD array setup type (FVG / OB / breaker) and timeframe ---
        def _parse_setup(entry_type_str):
            """Extract (pd_array, timeframe) from entry_type like 'amd_fvg_m5'."""
            s = str(entry_type_str).lower()
            for arr in ("fvg", "ob", "breaker"):
                if f"_{arr}_" in s or s.endswith(f"_{arr}"):
                    for tf in ("m1", "m5", "m15", "h1"):
                        if s.endswith(f"_{tf}"):
                            return arr.upper(), tf.upper()
                    return arr.upper(), "?"
            return "other", "?"

        df["setup_type"] = df["entry_type"].apply(lambda x: _parse_setup(x)[0])
        df["setup_tf"]   = df["entry_type"].apply(lambda x: _parse_setup(x)[1])

        print("\n=== PD array setup type (FVG / OB / breaker) ===")
        print(f"  {'Setup':<10} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
              f"{'P&L ZAR':>12} {'Avg P&L':>10} {'PF':>6}")
        print("  " + "-" * 58)
        for stype in ["FVG", "OB", "BREAKER", "other"]:
            grp = df[df["setup_type"] == stype]
            if grp.empty:
                continue
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            gw = grp.loc[grp.pnl > 0, "pnl"].sum()
            gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
            pf = (gw / gl) if gl > 0 else float("inf")
            print(f"  {stype:<10} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                  f"{grp.pnl.sum():>12.2f} {grp.pnl.mean():>10.2f} {pf:>6.2f}")

        print("\n  --- Setup type × timeframe ---")
        print(f"  {'Setup × TF':<16} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'PF':>6}")
        print("  " + "-" * 42)
        for (stype, tf), grp in df.groupby(["setup_type", "setup_tf"]):
            if grp.empty:
                continue
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            gw = grp.loc[grp.pnl > 0, "pnl"].sum()
            gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
            pf = (gw / gl) if gl > 0 else float("inf")
            print(f"  {stype+' '+tf:<16} {len(grp):>7} {w:>5} {wr:>5.1f}% {pf:>6.2f}")

        print("\n  --- Setup type × pair ---")
        print(f"  {'Setup × pair':<20} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'PF':>6}")
        print("  " + "-" * 46)
        for (stype, pair), grp in df.groupby(["setup_type", "pair"]):
            if grp.empty:
                continue
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            gw = grp.loc[grp.pnl > 0, "pnl"].sum()
            gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
            pf = (gw / gl) if gl > 0 else float("inf")
            print(f"  {stype+' '+pair:<20} {len(grp):>7} {w:>5} {wr:>5.1f}% {pf:>6.2f}")

        if "amd_source" in df.columns:
            print("\n=== AMD consolidation source ===")
            print(f"  {'Source':<18} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'PF':>6}")
            print("  " + "-" * 44)
            for src in ["m15_range", "session_range", ""]:
                grp = df[df["amd_source"] == src]
                if grp.empty:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                label = src if src else "(no AMD)"
                print(f"  {label:<18} {len(grp):>7} {w:>5} {wr:>5.1f}% {pf:>6.2f}")

            sr_widths = getattr(backtester, "_sr_widths", [])
            if sr_widths:
                sw = sorted(sr_widths)
                n = len(sw)
                med = sw[n // 2]
                p75 = sw[int(n * 0.75)]
                p90 = sw[int(n * 0.90)]
                print(f"\n  Session-range widths (n={n}): "
                      f"median={med:.1f} p75={p75:.1f} p90={p90:.1f} pips "
                      f"(cap={config.SESSION_RANGE_MAX_WIDTH_PIPS})")

        if "draw_score" in df.columns:
            print("\n=== HTF Draw cascade (W→D→H4 agreement) — all trades ===")
            print("  draw_score = how many of Weekly/Daily/H4 agreed with trade direction")
            print(f"  {'Draw score':<12} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>12} {'Avg P&L':>10} {'PF':>6}")
            print("  " + "-" * 62)
            for score in sorted(df["draw_score"].unique()):
                grp = df[df["draw_score"] == score]
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gross_win = grp.loc[grp.pnl > 0, "pnl"].sum()
                gross_loss = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
                label = f"{int(score)}/3"
                print(f"  {label:<12} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>12.2f} {grp.pnl.mean():>10.2f} {pf:>6.2f}")

        if "im_scenario" in df.columns:
            # ICT intermarket cheat sheet validation.
            # Scenarios come from (DXY H1 bias, EURGBP H1 bias) at entry:
            #   1a  DXY↑ + EURGBP↑  →  GBPUSD short  (Dollar strength, GBP weakest)
            #   1b  DXY↑ + EURGBP↓  →  EURUSD short  (Dollar strength, EUR weakest)
            #   2a  DXY↓ + EURGBP↑  →  EURUSD long   (Dollar weakness, EUR strongest)
            #   2b  DXY↓ + EURGBP↓  →  GBPUSD long   (Dollar weakness, GBP strongest)
            #   3a  DXY↑ + flat     →  both short     (Dollar strength, cross unclear)
            #   3b  DXY↓ + flat     →  both long      (Dollar weakness, cross unclear)
            #   N-long/N-short       →  NZDUSD (DXY + AUDNZD family)
            _scenario_predict = {
                "1a": ("GBPUSD", -1), "1b": ("EURUSD", -1),
                "2a": ("EURUSD", +1), "2b": ("GBPUSD", +1),
                "1a_h4": ("GBPUSD", -1), "1b_h4": ("EURUSD", -1),
                "2a_h4": ("EURUSD", +1), "2b_h4": ("GBPUSD", +1),
                "1a_ip": ("GBPUSD", -1), "1b_ip": ("EURUSD", -1),
                "2a_ip": ("EURUSD", +1), "2b_ip": ("GBPUSD", +1),
                "N-long": ("NZDUSD", +1), "N-short": ("NZDUSD", -1),
                "N-long_h4": ("NZDUSD", +1), "N-short_h4": ("NZDUSD", -1),
            }
            print("\n=== ICT Intermarket Cheat Sheet validation ===")
            print("  Checks whether each scenario's predicted pair+direction matches the actual trade.")
            print("  _h4 = H1 EURGBP flat, H4 used  |  _ip = H1+H4 both flat, individual pair momentum used")
            print(f"  {'Scenario':<12} {'Description':<34} {'Trades':>7} {'Wins':>5} "
                  f"{'WR%':>6} {'P&L ZAR':>12} {'PF':>6}")
            print("  " + "-" * 84)
            _desc = {
                "1a":     "DXY↑ + H1 EUR>GBP → GBPUSD short",
                "1b":     "DXY↑ + H1 GBP>EUR → EURUSD short",
                "2a":     "DXY↓ + H1 EUR>GBP → EURUSD long",
                "2b":     "DXY↓ + H1 GBP>EUR → GBPUSD long",
                "3a":     "DXY↑ + cross flat → EURUSD short",
                "3b":     "DXY↓ + cross flat → EURUSD long",
                "1a_h4":  "DXY↑ + H4 EUR>GBP → GBPUSD short",
                "1b_h4":  "DXY↑ + H4 GBP>EUR → EURUSD short",
                "2a_h4":  "DXY↓ + H4 EUR>GBP → EURUSD long",
                "2b_h4":  "DXY↓ + H4 GBP>EUR → GBPUSD long",
                "1a_ip":    "DXY↑ + IP EUR>GBP → GBPUSD short",
                "1b_ip":    "DXY↑ + IP GBP>EUR → EURUSD short",
                "2a_ip":    "DXY↓ + IP EUR>GBP → EURUSD long",
                "2b_ip":    "DXY↓ + IP GBP>EUR → GBPUSD long",
                "N-long":   "DXY↓ + NZD strong → NZDUSD long",
                "N-short":  "DXY↑ + NZD weak  → NZDUSD short",
                "N-long_h4":  "DXY↓ + H4 NZD strong → NZDUSD long",
                "N-short_h4": "DXY↑ + H4 NZD weak  → NZDUSD short",
                "?": "unclassified",
            }
            scenario_order = [
                "1a","1b","2a","2b","3a","3b",
                "1a_h4","1b_h4","2a_h4","2b_h4",
                "1a_ip","1b_ip","2a_ip","2b_ip",
                "N-long","N-short","N-long_h4","N-short_h4","?",
            ]
            for sc in scenario_order:
                grp = df[df["im_scenario"] == sc]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gross_win  = grp.loc[grp.pnl > 0, "pnl"].sum()
                gross_loss = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
                pred_pair, pred_dir = _scenario_predict.get(sc, (None, None))
                if pred_dir is None:
                    aligned_pct = "n/a"
                else:
                    if pred_pair is None:
                        aligned = (grp["direction"] == pred_dir).sum()
                    else:
                        aligned = ((grp["pair"] == pred_pair) & (grp["direction"] == pred_dir)).sum()
                    aligned_pct = f"{100*aligned/len(grp):>7.1f}%"
                desc = _desc.get(sc, sc)
                print(f"  {sc:<12} {desc:<34} {len(grp):>7} {w:>5} "
                      f"{wr:>5.1f}% {grp.pnl.sum():>12.2f} {pf:>6.2f}")

        if "entry_model" in df.columns:
            print("\n=== Entry model (Judas reversal vs intermarket breakout) ===")
            print("  breakout = EURUSD + GBPUSD + DXY all cleared M15 ranges in agreement (continuation)")
            print(f"  {'Model':<12} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'Avg P&L':>11} {'PF':>6}")
            print("  " + "-" * 64)
            for model, grp in df.groupby("entry_model"):
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gross_win  = grp.loc[grp.pnl > 0, "pnl"].sum()
                gross_loss = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
                print(f"  {model:<12} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {grp.pnl.mean():>11.2f} {pf:>6.2f}")

        if "profile" in df.columns:
            print("\n=== Session profile breakdown (London vs NY — independent AMD cycles) ===")
            print("  London profile: 03:00–05:00 ET — Judas sweep → reversal distribution")
            print("  NY profile:     07:00–10:00 ET — handover consolidation → continuation")
            print(f"  {'Profile':<10} {'Model':<12} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 64)
            for prof in ["london", "ny", "other"]:
                pg = df[df["profile"] == prof]
                if len(pg) == 0:
                    continue
                for model in sorted(pg["entry_model"].unique()) if "entry_model" in pg.columns else ["judas"]:
                    grp = pg[pg["entry_model"] == model]
                    if len(grp) == 0:
                        continue
                    w = (grp.pnl > 0).sum()
                    wr = 100 * w / len(grp)
                    gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                    gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                    pf = (gw / gl) if gl > 0 else float("inf")
                    print(f"  {prof:<10} {model:<12} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                          f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")
            # Profile totals
            print("  " + "-" * 64)
            for prof in ["london", "ny"]:
                grp = df[df["profile"] == prof]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                print(f"  {prof:<10} {'TOTAL':<12} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")

        if "session_phase" in df.columns:
            print("\n=== Session phase at entry (per-profile AMD cycle position) ===")
            print("  London profile phases:")
            print("    london_watch    = 03:00–03:30 ET — prime Judas sweep window")
            print("    london_judas    = London sweep detected → reversal distribution")
            print("    london_breakout = 03:30–05:00 ET, no sweep → breakout fallback")
            print("  NY profile phases:")
            print("    ny_judas        = NY own sweep detected → NY reversal/continuation")
            print("    ny_extend       = NY AM, no own sweep → handover continuation")
            print(f"  {'Phase':<22} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 62)
            _phase_order = [
                "london_watch", "london_judas", "london_breakout",
                "ny_judas", "ny_extend",
                "accumulation", "unknown",
            ]
            for ph in _phase_order:
                grp = df[df["session_phase"] == ph]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gross_win  = grp.loc[grp.pnl > 0, "pnl"].sum()
                gross_loss = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
                print(f"  {ph:<22} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")

        if "ny_cont" in df.columns:
            print("\n=== NY-AM continuation of London/DXY direction (P11) ===")
            print("  NY-AM entry in the same direction London set that day (DXY-wide).")
            print(f"  {'NY continuation':<16} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 58)
            for is_cont, label in [(True, "yes"), (False, "no")]:
                grp = df[df["ny_cont"] == is_cont]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                print(f"  {label:<16} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")
            # Of the captured NY continuations, how were they classified?
            cont = df[df["ny_cont"] == True]
            if len(cont) and "entry_model" in cont.columns:
                print("  -- captured NY continuations by entry_model --")
                for m, g in cont.groupby("entry_model"):
                    w = (g.pnl > 0).sum()
                    print(f"     {m:<12} {len(g):>4} trades  WR {100*w/len(g):>4.1f}%  "
                          f"P&L R{g.pnl.sum():>12.2f}")

        if "htf_fvg" in df.columns:
            print("\n=== HTF FVG 50% draw-on-liquidity conviction (P9) ===")
            print("  Unmitigated H4/D1/W1 FVG midpoint within tolerance of entry → +1 conviction.")
            print(f"  {'HTF FVG draw':<14} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 56)
            _fvg_label = {"W": "W1 FVG", "D": "D1 FVG", "240T": "H4 FVG", "": "none"}
            for tf in ("W", "D", "240T", ""):
                grp = df[df["htf_fvg"] == tf]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gross_win  = grp.loc[grp.pnl > 0, "pnl"].sum()
                gross_loss = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gross_win / gross_loss) if gross_loss > 0 else float("inf")
                print(f"  {_fvg_label.get(tf, tf):<14} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")

        if "dxy_fvg_tf" in df.columns:
            print("\n=== DXY level context — room to run (P13) ===")
            print("  DXY sitting at its own unmitigated W/D/H4 FVG mid → dollar has HTF draw room.")
            print(f"  {'DXY FVG TF':<14} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 56)
            _dxy_label = {"W": "W1 FVG", "D": "D1 FVG", "240T": "H4 FVG", "": "none"}
            for tf in ("W", "D", "240T", ""):
                grp = df[df["dxy_fvg_tf"] == tf]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                print(f"  {_dxy_label.get(tf, tf):<14} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")

        if "target_confluence" in df.columns:
            print("\n=== Target confluence scoring — TP area source agreement ===")
            print("  Score = # distinct source families (fib/fvg/ob/swing/round/pdh/pwh) "
                  "within tolerance of chosen TP.")
            print("  Higher score → more independent reasons price should reach that level.")
            print(f"  {'Score':<8} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6} {'Avg P&L':>10}")
            print("  " + "-" * 60)
            for score in sorted(df["target_confluence"].unique()):
                grp = df[df["target_confluence"] == score]
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                label = f"score={int(score)}"
                print(f"  {label:<8} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f} {grp.pnl.mean():>10.2f}")

        if "mstruct_pts" in df.columns:
            print("\n=== Market structure (Ep 12 LTH/ITH/STH fractal) ===")
            print("  Couples the fractal swing-tier read with the draw cascade. HTF")
            print("  intermediate structure agreeing with the trade = bigger draw in our favour.")

            def _ms_row(label, grp):
                if len(grp) == 0:
                    return
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                print(f"  {label:<22} {len(grp):>6} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>7.2f}")

            print(f"  {'Bucket':<22} {'Trades':>6} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>7}")
            print("  " + "-" * 64)
            df["_htf_agree"] = df["mstruct_htf_dir"] == df["direction"]
            _ms_row("HTF struct agrees",   df[df["_htf_agree"]])
            _ms_row("HTF struct disagrees", df[~df["_htf_agree"]])
            _ms_row("minor-sweep (Judas)", df[df["mstruct_minor_sweep"] == True])
            _ms_row("no minor-sweep",      df[df["mstruct_minor_sweep"] != True])
            print("  ── highest intact-structure timeframe ──")
            for tf in ("W", "D", "240T", "60T", "15T"):
                _ms_row(f"intact @ {tf}", df[df["mstruct_intact_tf"] == tf])

        if "crt_tf" in df.columns:
            print("\n=== HTF CRT Turtle Soup timing (P19) ===")
            print("  Prior H4/D range high/low swept on a wick + close back inside = HTF Judas.")
            print("  D1 sweep = +2 conviction, H4 sweep = +1 conviction.")
            print(f"  {'CRT sweep TF':<14} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 56)
            _crt_label = {"D": "D1 range", "240T": "H4 range", "": "no sweep"}
            for tf in ("D", "240T", ""):
                grp = df[df["crt_tf"] == tf]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                print(f"  {_crt_label.get(tf, tf):<14} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")

        if "smt_pair_pref" in df.columns:
            eu_gu = df[df["pair"].isin(["EURUSD", "GBPUSD"])]
            print("\n=== Intraday SMT pair preference (P44) — EURUSD/GBPUSD only ===")
            print("  'confirmed' = traded pair FAILED to confirm partner's sweep (weaker = bigger distribution)")
            print("  'opposing'  = traded pair LED the sweep (stronger = smaller distribution)")
            print(f"  {'SMT signal':<14} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6} {'Avg pips':>10}")
            print("  " + "-" * 66)
            for label in ("confirmed", "opposing", ""):
                grp = eu_gu[eu_gu["smt_pair_pref"] == label]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                avg_pips = grp["mfe_pips"].mean() if "mfe_pips" in grp.columns else 0
                display = label if label else "no divergence"
                print(f"  {display:<14} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f} {avg_pips:>10.1f}")
            # Per-pair breakdown within confirmed
            if (eu_gu["smt_pair_pref"] == "confirmed").any():
                print("\n  --- SMT confirmed by pair ---")
                conf = eu_gu[eu_gu["smt_pair_pref"] == "confirmed"]
                for p in ("EURUSD", "GBPUSD"):
                    grp = conf[conf["pair"] == p]
                    if len(grp) == 0:
                        continue
                    w = (grp.pnl > 0).sum()
                    wr = 100 * w / len(grp)
                    gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                    gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                    pf = (gw / gl) if gl > 0 else float("inf")
                    print(f"    {p:<10} {len(grp):>5} trades  WR {wr:>5.1f}%  PF {pf:>6.2f}  "
                          f"P&L {grp.pnl.sum():>12.2f}")
            # Per-direction breakdown within confirmed
            if (eu_gu["smt_pair_pref"] == "confirmed").any():
                print("\n  --- SMT confirmed by direction ---")
                conf = eu_gu[eu_gu["smt_pair_pref"] == "confirmed"]
                for d, dlabel in [(1, "LONG"), (-1, "SHORT")]:
                    grp = conf[conf["direction"] == d]
                    if len(grp) == 0:
                        continue
                    w = (grp.pnl > 0).sum()
                    wr = 100 * w / len(grp)
                    gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                    gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                    pf = (gw / gl) if gl > 0 else float("inf")
                    print(f"    {dlabel:<10} {len(grp):>5} trades  WR {wr:>5.1f}%  PF {pf:>6.2f}  "
                          f"P&L {grp.pnl.sum():>12.2f}")

        if "golden_rule" in df.columns:
            eu_gu = df[df["pair"].isin(["EURUSD", "GBPUSD"])]
            print("\n=== Golden rule: SELL GBP / BUY EUR (P44) — EURUSD/GBPUSD only ===")
            print("  GBP is structurally weaker (trends bearish) → SELL GBPUSD for shorts")
            print("  EUR is structurally stronger (trends bullish) → BUY EURUSD for longs")
            print(f"  {'Rule':<16} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6} {'Avg pips':>10}")
            print("  " + "-" * 68)
            for label in ("golden", "against"):
                grp = eu_gu[eu_gu["golden_rule"] == label]
                if len(grp) == 0:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                avg_pips = grp["mfe_pips"].mean() if "mfe_pips" in grp.columns else 0
                display = {"golden": "follows rule", "against": "against rule"}[label]
                print(f"  {display:<16} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f} {avg_pips:>10.1f}")
            # Breakdown: what does each pair × direction look like?
            print("\n  --- Pair × direction breakdown ---")
            print(f"    {'Setup':<22} {'Trades':>5} {'WR%':>6} {'PF':>6} "
                  f"{'P&L ZAR':>12} {'Rule':>10}")
            print("    " + "-" * 64)
            for p in ("EURUSD", "GBPUSD"):
                for d, dlabel in [(1, "LONG"), (-1, "SHORT")]:
                    grp = eu_gu[(eu_gu["pair"] == p) & (eu_gu["direction"] == d)]
                    if len(grp) == 0:
                        continue
                    w = (grp.pnl > 0).sum()
                    wr = 100 * w / len(grp)
                    gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                    gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                    pf = (gw / gl) if gl > 0 else float("inf")
                    rule = grp.iloc[0]["golden_rule"] if len(grp) > 0 else ""
                    rule_tag = "GOLDEN" if rule == "golden" else "against"
                    print(f"    {p+' '+dlabel:<22} {len(grp):>5} {wr:>5.1f}% {pf:>6.2f} "
                          f"{grp.pnl.sum():>12.2f} {rule_tag:>10}")
            # Cross-tab: golden rule × SMT pair pref (if both exist)
            if "smt_pair_pref" in eu_gu.columns:
                print("\n  --- Golden rule × SMT pair pref (cross-tab) ---")
                print(f"    {'Golden × SMT':<28} {'Trades':>5} {'WR%':>6} {'PF':>6}")
                print("    " + "-" * 48)
                for gr in ("golden", "against"):
                    for sp in ("confirmed", "opposing", ""):
                        grp = eu_gu[(eu_gu["golden_rule"] == gr) &
                                    (eu_gu["smt_pair_pref"] == sp)]
                        if len(grp) == 0:
                            continue
                        w = (grp.pnl > 0).sum()
                        wr = 100 * w / len(grp)
                        gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                        gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                        pf = (gw / gl) if gl > 0 else float("inf")
                        sp_label = sp if sp else "no div"
                        print(f"    {gr+' + '+sp_label:<28} {len(grp):>5} {wr:>5.1f}% {pf:>6.2f}")

        if "narrative_score" in df.columns:
            print("\n=== Narrative context scoring (P47) ===")
            print("  Factors: DOW tendency, NFP-week, rate decision, PD array provenance, seasonal")
            print(f"  {'Score':<8} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 52)
            for sc in sorted(df["narrative_score"].unique()):
                grp = df[df["narrative_score"] == sc]
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                gw = grp.loc[grp.pnl > 0, "pnl"].sum()
                gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
                pf = (gw / gl) if gl > 0 else float("inf")
                print(f"  {sc:<8} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>14.2f} {pf:>6.2f}")
            print("\n  --- Per-factor breakdown ---")
            print(f"  {'Factor':<20} {'Fired':>7} {'WR%':>6} {'PF':>6}   "
                  f"{'Absent':>7} {'WR%':>6} {'PF':>6}")
            print("  " + "-" * 70)
            for col, label in [("narrative_dow", "DOW (Tue/Wed)"),
                               ("narrative_nfp", "NFP week Mon/Tue"),
                               ("narrative_rate", "Rate decision"),
                               ("narrative_pd_prov", "PD prov (sweep)"),
                               ("narrative_seasonal", "Seasonal lean")]:
                if col not in df.columns:
                    continue
                if col == "narrative_rate":
                    fired = df[df[col] > 0]
                    absent = df[df[col] <= 0]
                else:
                    fired = df[df[col] == True]
                    absent = df[df[col] == False]
                def _wpf(g):
                    if len(g) == 0:
                        return 0, 0, 0.0
                    w = (g.pnl > 0).sum()
                    wr = 100 * w / len(g)
                    gw_ = g.loc[g.pnl > 0, "pnl"].sum()
                    gl_ = abs(g.loc[g.pnl < 0, "pnl"].sum())
                    pf_ = (gw_ / gl_) if gl_ > 0 else float("inf")
                    return len(g), wr, pf_
                fn, fwr, fpf = _wpf(fired)
                an, awr, apf = _wpf(absent)
                print(f"  {label:<20} {fn:>7} {fwr:>5.1f}% {fpf:>6.2f}   "
                      f"{an:>7} {awr:>5.1f}% {apf:>6.2f}")

        if "target_type" in df.columns:
            print("\n=== Draw on liquidity (target type) — all trades ===")
            print(f"  {'Draw on liquidity':<18} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                  f"{'P&L ZAR':>12} {'Avg P&L':>10}")
            print("  " + "-" * 62)
            for ttype, grp in df.groupby("target_type"):
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                print(f"  {ttype:<18} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                      f"{grp.pnl.sum():>12.2f} {grp.pnl.mean():>10.2f}")

            wins_df = df[df.pnl > 0]
            print("\n=== Winning trades only — by draw on liquidity ===")
            print(f"  {'Draw on liquidity':<18} {'Wins':>5} {'% of wins':>10} {'P&L ZAR':>12}")
            print("  " + "-" * 48)
            total_wins = len(wins_df)
            for ttype, grp in wins_df.groupby("target_type"):
                pct = 100 * len(grp) / total_wins if total_wins else 0
                print(f"  {ttype:<18} {len(grp):>5} {pct:>9.1f}% {grp.pnl.sum():>12.2f}")

            # --- Pyramids: draw on liquidity by leg type (initial vs pyramid add) ---
            if "leg_idx" in df.columns:
                df["leg_kind"] = df["leg_idx"].apply(
                    lambda i: "initial (L1)" if i == 1 else "pyramid (L2+)")
                print("\n=== Draw on liquidity — initial vs pyramid legs (winners) ===")
                print(f"  {'Leg':<14} {'Draw on liquidity':<18} {'Wins':>5} {'WR%':>6} {'P&L ZAR':>12}")
                print("  " + "-" * 60)
                for legk in ["initial (L1)", "pyramid (L2+)"]:
                    sub_all = df[df.leg_kind == legk]
                    for ttype, grp in sub_all[sub_all.pnl > 0].groupby("target_type"):
                        all_grp = sub_all[sub_all.target_type == ttype]
                        wr = 100 * len(grp) / len(all_grp) if len(all_grp) else 0
                        print(f"  {legk:<14} {ttype:<18} {len(grp):>5} {wr:>5.1f}% {grp.pnl.sum():>12.2f}")

            # --- Sessions: which killzone the winning draws were hit in ---
            def _killzone(ts):
                # opened_at is tz-aware UTC; killzones defined in NY time.
                ny = ts.tz_convert("America/New_York")
                h = ny.hour
                if 2 <= h < 5:
                    return "London Open"
                if 7 <= h < 10:
                    return "New York AM"
                if 20 <= h or h < 2:
                    return "Asian"
                return "Other"
            try:
                wins_df = wins_df.copy()
                wins_df["session"] = wins_df["opened_at"].apply(_killzone)
                print("\n=== Winning trades — by session × draw on liquidity ===")
                print(f"  {'Session':<13} {'Draw on liquidity':<18} {'Wins':>5} {'P&L ZAR':>12}")
                print("  " + "-" * 52)
                for sess, sgrp in wins_df.groupby("session"):
                    for ttype, grp in sgrp.groupby("target_type"):
                        print(f"  {sess:<13} {ttype:<18} {len(grp):>5} {grp.pnl.sum():>12.2f}")
                print("\n=== Winning trades — totals by session ===")
                print(f"  {'Session':<13} {'Wins':>5} {'% of wins':>10} {'P&L ZAR':>12}")
                print("  " + "-" * 44)
                for sess, sgrp in wins_df.groupby("session"):
                    pct = 100 * len(sgrp) / total_wins if total_wins else 0
                    print(f"  {sess:<13} {len(sgrp):>5} {pct:>9.1f}% {sgrp.pnl.sum():>12.2f}")
            except Exception as e:
                print(f"  (session breakdown skipped: {e})")

        print("\n=== Session-open side breakdown (above/below open) ===")
        print(f"  {'Category':<12} {'Trades':>7} {'Wins':>5} {'Losses':>7} {'WR%':>6} "
              f"{'P&L ZAR':>12} {'Avg P&L':>10}")
        print("  " + "-" * 65)
        for side in ["judas", "momentum", "no_open"]:
            g = df[df.session_side == side]
            if len(g) == 0:
                continue
            wins = (g.pnl > 0).sum()
            losses = len(g) - wins
            wr = 100 * wins / len(g)
            pnl = g.pnl.sum()
            avg = g.pnl.mean()
            label = {"judas": "below open", "momentum": "above open",
                     "no_open": "no session"}[side]
            print(f"  {label:<12} {len(g):>7} {wins:>5} {losses:>7} {wr:>5.1f}% "
                  f"{pnl:>11.2f} {avg:>10.2f}")

        if "soj_sweep" in df.columns:
            print("\n=== P26 — Session-open + daily-open pattern ===")
            print("  +1 per reference (session open / daily open) showing Judas sweep or")
            print("  pullback retest. Dual (+2) = both references fired.")
            print(f"  {'Bucket':<30} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'P&L ZAR':>14} {'PF':>6}")
            print("  " + "-" * 70)
            buckets = [
                (df["soj_type"] == "dual",    "SOJ dual (sess+daily, +2)"),
                (df["soj_type"] == "single",  "SOJ single reference (+1)"),
                (~df["soj_sweep"],             "no SOJ pattern"),
            ] if "soj_type" in df.columns else [
                (df.soj_sweep,   "SOJ fired"),
                (~df.soj_sweep,  "no SOJ"),
            ]
            for mask, label in buckets:
                g2 = df[mask]
                if len(g2) == 0:
                    continue
                wins2 = (g2.pnl > 0).sum()
                wr2 = 100 * wins2 / len(g2)
                gross_w = g2[g2.pnl > 0].pnl.sum()
                gross_l = abs(g2[g2.pnl < 0].pnl.sum())
                pf2 = (gross_w / gross_l) if gross_l else float("inf")
                print(f"  {label:<30} {len(g2):>7} {wins2:>5} {wr2:>5.1f}% "
                      f"{g2.pnl.sum():>13.2f} {pf2:>6.2f}")
    else:
        print("\nNo trades generated.")
        print("Check the gate funnel to see which filter is the bottleneck.")

    # ── Auto-push a results report so Claude sees it without a manual git dance ──
    if os.environ.get("NO_PUSH") != "1":
        try:
            _publish_backtest_report(results, backtester, requested_years,
                                       df if backtester.trades else None)
        except Exception as _e:
            print(f"[report push skipped: {_e}]")


def _publish_backtest_report(results, backtester, years, df=None):
    """Write data/backtest_report.md (summary + gate funnel + withdrawals +
    key analytics tables) and force-add/commit/pull/push it (data/ is
    gitignored). NO_PUSH=1 disables."""
    import subprocess
    root = os.path.dirname(os.path.abspath(__file__))
    span = "–".join([years[0], years[-1]])
    L = [f"# HistData backtest — {span} ({len(years)} yr)", "",
         "## Results", "", "```"]
    L += [f"{k:26s} {v}" for k, v in results.items()]
    L.append("```")
    g = getattr(backtester, "gate", {})
    if g:
        L += ["", "## Gate funnel", "", "```"]
        L += [f"{k:30s} {v}" for k, v in g.items()]
        L.append("```")
    ev = getattr(backtester, "withdrawal_events", [])
    if ev:
        tot = sum(a for _t, a, _k in ev)
        L += ["", f"_income: R{tot:,.0f} across {len(ev)} withdrawals · working "
              f"balance R{getattr(backtester, 'equity', 0):,.0f}_"]

    # ── Analytics tables (from the trade DataFrame) ──
    if df is not None and len(df) > 0:
        def _pf(grp):
            gw = grp.loc[grp.pnl > 0, "pnl"].sum()
            gl = abs(grp.loc[grp.pnl < 0, "pnl"].sum())
            return (gw / gl) if gl > 0 else float("inf")

        # --- PD array setup type ---
        def _parse_setup(et):
            s = str(et).lower()
            for arr in ("fvg", "ob", "breaker"):
                if f"_{arr}_" in s or s.endswith(f"_{arr}"):
                    for tf in ("m1", "m5", "m15", "h1"):
                        if s.endswith(f"_{tf}"):
                            return arr.upper(), tf.upper()
                    return arr.upper(), "?"
            return "other", "?"

        df["_setup_type"] = df["entry_type"].apply(lambda x: _parse_setup(x)[0])
        df["_setup_tf"]   = df["entry_type"].apply(lambda x: _parse_setup(x)[1])
        L += ["", "## PD array setup type (FVG / OB / breaker)", "", "```"]
        L.append(f"{'Setup':<10} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                 f"{'P&L ZAR':>12} {'PF':>6}")
        L.append("-" * 50)
        for stype in ["FVG", "OB", "BREAKER", "other"]:
            grp = df[df["_setup_type"] == stype]
            if grp.empty:
                continue
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            L.append(f"{stype:<10} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                     f"{grp.pnl.sum():>12.2f} {_pf(grp):>6.2f}")
        L.append("")
        L.append(f"{'Setup x TF':<16} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'PF':>6}")
        L.append("-" * 42)
        for (stype, tf), grp in df.groupby(["_setup_type", "_setup_tf"]):
            if grp.empty:
                continue
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            L.append(f"{stype+' '+tf:<16} {len(grp):>7} {w:>5} {wr:>5.1f}% {_pf(grp):>6.2f}")
        L.append("")
        L.append(f"{'Setup x pair':<20} {'Trades':>7} {'Wins':>5} {'WR%':>6} {'PF':>6}")
        L.append("-" * 46)
        for (stype, pair), grp in df.groupby(["_setup_type", "pair"]):
            if grp.empty:
                continue
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            L.append(f"{stype+' '+pair:<20} {len(grp):>7} {w:>5} {wr:>5.1f}% {_pf(grp):>6.2f}")
        L.append("```")

        # --- Entry-type breakdown ---
        L += ["", "## Entry-type breakdown", "", "```"]
        L.append(f"{'Entry type':<22} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                 f"{'Avg P&L':>10} {'PF':>6}")
        L.append("-" * 60)
        for etype, grp in df.groupby("entry_type"):
            w = (grp.pnl > 0).sum()
            wr = 100 * w / len(grp)
            L.append(f"{etype:<22} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                     f"{grp.pnl.mean():>10.2f} {_pf(grp):>6.2f}")
        L.append("```")

        # --- AMD source breakdown ---
        if "amd_source" in df.columns:
            L += ["", "## AMD consolidation source", "", "```"]
            L.append(f"{'Source':<18} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                     f"{'P&L ZAR':>12} {'PF':>6}")
            L.append("-" * 56)
            for src in ["m15_range", "session_range", ""]:
                grp = df[df["amd_source"] == src]
                if grp.empty:
                    continue
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                label = src if src else "(no AMD)"
                L.append(f"{label:<18} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                         f"{grp.pnl.sum():>12.2f} {_pf(grp):>6.2f}")
            L.append("```")

            sr_widths = getattr(backtester, "_sr_widths", [])
            if sr_widths:
                sw = sorted(sr_widths)
                n = len(sw)
                med = sw[n // 2]
                p75 = sw[int(n * 0.75)]
                p90 = sw[int(n * 0.90)]
                L.append(f"\n_Session-range widths (n={n}): "
                         f"median={med:.1f} p75={p75:.1f} p90={p90:.1f} pips "
                         f"(cap={config.SESSION_RANGE_MAX_WIDTH_PIPS})_")

        # --- Golden rule (P44) ---
        if "golden_rule" in df.columns:
            eurgbp = df[df.pair.isin(["EURUSD", "GBPUSD"])]
            if len(eurgbp) > 0:
                L += ["", "## Golden rule: SELL GBP / BUY EUR (P44)", "", "```"]
                L.append(f"{'Rule':<12} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                         f"{'P&L ZAR':>12} {'PF':>6}")
                L.append("-" * 50)
                for gr in ["golden", "against"]:
                    grp = eurgbp[eurgbp["golden_rule"] == gr]
                    if grp.empty:
                        continue
                    w = (grp.pnl > 0).sum()
                    wr = 100 * w / len(grp)
                    L.append(f"{gr:<12} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                             f"{grp.pnl.sum():>12.2f} {_pf(grp):>6.2f}")
                L.append("")
                L.append(f"{'Pair x dir x rule':<30} {'Trades':>5} {'WR%':>6} {'PF':>6}")
                L.append("-" * 50)
                for pair in ["EURUSD", "GBPUSD"]:
                    for d in [1, -1]:
                        for gr in ["golden", "against"]:
                            grp = eurgbp[(eurgbp.pair == pair) &
                                         (eurgbp.direction == d) &
                                         (eurgbp.golden_rule == gr)]
                            if grp.empty:
                                continue
                            w = (grp.pnl > 0).sum()
                            wr = 100 * w / len(grp)
                            dlbl = "LONG" if d == 1 else "SHORT"
                            L.append(f"{pair+' '+dlbl+' '+gr:<30} {len(grp):>5} "
                                     f"{wr:>5.1f}% {_pf(grp):>6.2f}")
                L.append("```")

        # --- SMT pair preference (P44) ---
        if "smt_pair_pref" in df.columns:
            eurgbp = df[df.pair.isin(["EURUSD", "GBPUSD"])]
            if len(eurgbp) > 0:
                L += ["", "## Intraday SMT pair preference (P44)", "", "```"]
                L.append(f"{'SMT pref':<14} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                         f"{'P&L ZAR':>12} {'PF':>6}")
                L.append("-" * 52)
                for sp in ["confirmed", "opposing", ""]:
                    grp = eurgbp[eurgbp["smt_pair_pref"] == sp]
                    if grp.empty:
                        continue
                    w = (grp.pnl > 0).sum()
                    wr = 100 * w / len(grp)
                    lbl = sp if sp else "no divergence"
                    L.append(f"{lbl:<14} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                             f"{grp.pnl.sum():>12.2f} {_pf(grp):>6.2f}")
                L.append("```")

        # --- Narrative context scoring (P47) ---
        if "narrative_score" in df.columns:
            L += ["", "## Narrative context scoring (P47)", "", "```"]
            L.append(f"{'Score':<8} {'Trades':>7} {'Wins':>5} {'WR%':>6} "
                     f"{'P&L ZAR':>12} {'PF':>6}")
            L.append("-" * 52)
            for sc in sorted(df["narrative_score"].unique()):
                grp = df[df["narrative_score"] == sc]
                w = (grp.pnl > 0).sum()
                wr = 100 * w / len(grp)
                L.append(f"{sc:<8} {len(grp):>7} {w:>5} {wr:>5.1f}% "
                         f"{grp.pnl.sum():>12.2f} {_pf(grp):>6.2f}")
            L.append("")
            L.append(f"{'Factor':<20} {'Fired':>7} {'WR%':>6} {'PF':>6}  "
                     f"{'Absent':>7} {'WR%':>6} {'PF':>6}")
            L.append("-" * 68)
            for col, label in [("narrative_dow", "DOW (Tue/Wed)"),
                               ("narrative_nfp", "NFP week Mon/Tue"),
                               ("narrative_rate", "Rate decision"),
                               ("narrative_pd_prov", "PD prov (sweep)"),
                               ("narrative_seasonal", "Seasonal lean")]:
                if col not in df.columns:
                    continue
                if col == "narrative_rate":
                    fired = df[df[col] > 0]
                    absent = df[df[col] <= 0]
                else:
                    fired = df[df[col] == True]
                    absent = df[df[col] == False]
                fn = len(fired)
                fwr = 100 * (fired.pnl > 0).sum() / fn if fn else 0
                fpf = _pf(fired) if fn else 0
                an = len(absent)
                awr = 100 * (absent.pnl > 0).sum() / an if an else 0
                apf = _pf(absent) if an else 0
                L.append(f"{label:<20} {fn:>7} {fwr:>5.1f}% {fpf:>6.2f}  "
                         f"{an:>7} {awr:>5.1f}% {apf:>6.2f}")
            L.append("```")

        # cleanup temp columns
        df.drop(columns=["_setup_type", "_setup_tf"], inplace=True, errors="ignore")

    out = os.path.join(root, "data", "backtest_report.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write("\n".join(L) + "\n")

    def _git(*a):
        return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True)
    sha = _git("rev-parse", "--short", "HEAD").stdout.strip() or "unknown"
    branch = _git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "HEAD"
    _git("add", "-f", out)
    _git("commit", "-q", "-m", f"HistData backtest {span} results (auto, {sha})")
    # Pull with rebase to avoid merge conflicts from code pushes
    _git("pull", "-q", "--rebase", "--no-edit", "origin", branch)
    pushed = False
    for attempt in range(4):
        if _git("push", "origin", branch).returncode == 0:
            pushed = True
            break
        import time
        time.sleep(2 ** (attempt + 1))
    if pushed:
        print(f"\nRESULTS PUSHED — Claude can read data/backtest_report.md")
    else:
        print("\n(auto-push failed — paste the === Results === block to Claude)")


if __name__ == "__main__":
    main()

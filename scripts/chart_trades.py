"""Trade chart viewer — plots backtest trades on M15 candlestick charts.

Reads data/trades_dump.csv (output of run_backtest_histdata.py) and the
HistData M1 CSVs, then generates a self-contained HTML file you can open
in any browser.

Candle colours: green = bullish (close ≥ open), black = bearish (close < open).
Each trade shows: entry arrow, initial stop line, target line, exit marker.

Usage:
    python scripts/chart_trades.py                        # all trades → data/trades_chart.html
    python scripts/chart_trades.py --pair EURUSD          # filter pair
    python scripts/chart_trades.py --years 2024 2025      # filter years
    python scripts/chart_trades.py --result win           # win / loss
    python scripts/chart_trades.py --scenario 1a          # filter im_scenario
    python scripts/chart_trades.py --max 50               # limit to first N trades
    python scripts/chart_trades.py --out my_chart.html
    python scripts/chart_trades.py --tf 60T               # candle timeframe (default 15T)
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "histdata")
TRADES_CSV = os.path.join(DATA_DIR, "trades_dump.csv")

# Candle window: bars before entry and after exit
BARS_BEFORE = 60
BARS_AFTER  = 30

PAIRS = ["EURUSD", "GBPUSD", "NZDUSD"]
TF_DEFAULT = "15min"

_EST_OFFSET = pd.Timedelta(hours=5)

_TF_ALIASES = {
    "1T": "1min", "5T": "5min", "15T": "15min",
    "30T": "30min", "60T": "60min", "240T": "240min",
    "1H": "1h", "4H": "4h",
}

def _norm_tf(tf: str) -> str:
    return _TF_ALIASES.get(tf, tf)

def _to_utc(t) -> pd.Timestamp:
    ts = pd.Timestamp(t)
    if ts.tzinfo is None:
        return ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _load_m1(pair: str, years: list[int]) -> pd.DataFrame:
    frames = []
    for yr in years:
        for suffix in ("", f"_{yr}"):
            path = os.path.join(DATA_DIR, f"{pair}{suffix}.csv")
            if not os.path.exists(path):
                path = os.path.join(DATA_DIR, f"{pair}_{yr}.csv")
            if os.path.exists(path):
                df = pd.read_csv(
                    path, sep=";", header=None,
                    names=["dt", "Open", "High", "Low", "Close", "Volume"],
                    dtype={"Open": float, "High": float, "Low": float, "Close": float},
                )
                df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S") + _EST_OFFSET
                df = df.set_index("dt")[["Open", "High", "Low", "Close"]]
                df.index = df.index.tz_localize("UTC")
                frames.append(df)
                break
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames).sort_index()


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return df.resample(_norm_tf(rule)).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    ).dropna()


def _window(ohlc: pd.DataFrame, entry_t, exit_t, before: int, after: int) -> pd.DataFrame:
    """Slice BARS_BEFORE bars before entry and BARS_AFTER bars after exit."""
    entry_t = _to_utc(entry_t)
    exit_t  = _to_utc(exit_t)
    idx = ohlc.index
    i_entry = idx.searchsorted(entry_t)
    i_exit  = idx.searchsorted(exit_t)
    lo = max(0, i_entry - before)
    hi = min(len(idx), i_exit + after + 1)
    return ohlc.iloc[lo:hi]


# ---------------------------------------------------------------------------
# Chart builder
# ---------------------------------------------------------------------------

_BG        = "#0d1117"   # page background
_PLOT_BG   = "#161b22"   # chart area
_GRID      = "#21262d"   # grid lines
_TEXT      = "#c9d1d9"   # labels
_GREEN     = "#3fb950"   # bullish candle / long entry
_BLACK_C   = "#161b22"   # bearish candle body (dark, visible on dark bg via white wick)
_WICK      = "#8b949e"   # candle wick colour
_STOP_COL  = "#f85149"   # stop line
_TARGET_COL= "#58a6ff"   # target line
_ENTRY_COL = "#e3b341"   # entry level line
_WIN_COL   = "#3fb950"
_LOSS_COL  = "#f85149"

CHART_H = 320  # px per trade chart


def _hover(row) -> str:
    direction = "LONG" if row["direction"] > 0 else "SHORT"
    win = "WIN" if row["pnl"] > 0 else "LOSS"
    stop = row.get("stop", float("nan"))
    tgt  = row.get("target", float("nan"))
    return (
        f"<b>{row['pair']} {direction} — {win}  R{row['pnl']:+.2f}</b><br>"
        f"Entry {row['entry']:.5f}  →  Exit {row['exit']:.5f}<br>"
        f"Stop {stop:.5f}  |  Target {tgt:.5f}<br>"
        f"Scenario: {row.get('im_scenario','?')}  Model: {row.get('entry_model','?')}<br>"
        f"Draw {row.get('draw_score',0)}/3  Confluence {row.get('target_confluence',0)}"
        f"  CRT {row.get('crt_tf','—')}<br>"
        f"{str(row['opened_at'])[:16]}  →  {str(row['closed_at'])[:16]}"
    )


def build_chart(trades_df: pd.DataFrame, ohlc_cache: dict, tf: str) -> go.Figure:
    n = len(trades_df)
    if n == 0:
        fig = go.Figure()
        fig.update_layout(title="No trades matched filter",
                          paper_bgcolor=_BG, font=dict(color=_TEXT))
        return fig

    # One row per trade, single column
    v_space = min(0.04, 0.9 / max(n - 1, 1)) if n > 1 else 0.04
    titles = []
    for _, row in trades_df.iterrows():
        direction = "▲ LONG" if row["direction"] > 0 else "▼ SHORT"
        badge = "✓ WIN" if row["pnl"] > 0 else "✗ LOSS"
        dt = str(row["opened_at"])[:16]
        titles.append(
            f"{badge}  {row['pair']} {direction}  R{row['pnl']:+.0f}  "
            f"| {row.get('im_scenario','?')} {row.get('entry_model','?')}  "
            f"draw {row.get('draw_score',0)}/3  {dt}"
        )

    fig = make_subplots(
        rows=n, cols=1,
        subplot_titles=titles,
        shared_xaxes=False,
        vertical_spacing=v_space,
    )

    for idx, (_, row) in enumerate(trades_df.iterrows()):
        r = idx + 1

        pair = row["pair"]
        ohlc = ohlc_cache.get(pair)
        if ohlc is None or ohlc.empty:
            continue

        ohlc_tf = _resample(ohlc, tf) if _norm_tf(tf) != "1min" else ohlc
        win_df  = _window(ohlc_tf, row["opened_at"], row["closed_at"], BARS_BEFORE, BARS_AFTER)
        if win_df.empty:
            continue

        bull = win_df["Close"] >= win_df["Open"]

        fig.add_trace(go.Candlestick(
            x=win_df.index,
            open=win_df["Open"], high=win_df["High"],
            low=win_df["Low"],   close=win_df["Close"],
            increasing=dict(line=dict(color=_GREEN,   width=1), fillcolor=_GREEN),
            decreasing=dict(line=dict(color=_WICK,    width=1), fillcolor=_BLACK_C),
            name=pair, showlegend=False,
            hovertext=_hover(row), hoverinfo="text",
        ), row=r, col=1)

        entry_t = _to_utc(row["opened_at"])
        exit_t  = _to_utc(row["closed_at"])
        entry_price  = row["entry"]
        exit_price   = row["exit"]
        stop_price   = row.get("stop",   None)
        target_price = row.get("target", None)
        direction    = row["direction"]
        x0 = win_df.index[0]
        x1 = win_df.index[-1]

        # Entry level (gold dotted)
        fig.add_shape(type="line", x0=x0, x1=x1, y0=entry_price, y1=entry_price,
                      line=dict(color=_ENTRY_COL, width=1, dash="dot"),
                      row=r, col=1)

        # Stop line (red)
        if stop_price is not None and not pd.isna(stop_price):
            fig.add_shape(type="line", x0=x0, x1=x1, y0=stop_price, y1=stop_price,
                          line=dict(color=_STOP_COL, width=1.5, dash="dash"),
                          row=r, col=1)

        # Target line (blue)
        if target_price is not None and not pd.isna(target_price):
            fig.add_shape(type="line", x0=x0, x1=x1, y0=target_price, y1=target_price,
                          line=dict(color=_TARGET_COL, width=1.5, dash="dot"),
                          row=r, col=1)

        # Shaded entry→exit zone
        zone_col = "rgba(63,185,80,0.07)" if row["pnl"] > 0 else "rgba(248,81,73,0.07)"
        fig.add_shape(type="rect", x0=entry_t, x1=exit_t,
                      y0=min(entry_price, exit_price) * 0.9999,
                      y1=max(entry_price, exit_price) * 1.0001,
                      fillcolor=zone_col, line=dict(width=0),
                      row=r, col=1)

        # Entry marker
        sym = "triangle-up" if direction > 0 else "triangle-down"
        col = _WIN_COL if direction > 0 else _STOP_COL
        fig.add_trace(go.Scatter(
            x=[entry_t], y=[entry_price], mode="markers",
            marker=dict(symbol=sym, size=16, color=col,
                        line=dict(color="#ffffff", width=1)),
            showlegend=False, hovertext=f"ENTRY {entry_price:.5f}", hoverinfo="text",
        ), row=r, col=1)

        # Exit marker
        exit_col = _WIN_COL if row["pnl"] > 0 else _LOSS_COL
        fig.add_trace(go.Scatter(
            x=[exit_t], y=[exit_price], mode="markers",
            marker=dict(symbol="x-thin", size=14, color=exit_col,
                        line=dict(color=exit_col, width=3)),
            showlegend=False,
            hovertext=f"EXIT {exit_price:.5f}  P&L R{row['pnl']:+.2f}", hoverinfo="text",
        ), row=r, col=1)

    # Style subplot titles: green for win, red for loss
    for i, (ann, (_, row)) in enumerate(
            zip(fig.layout.annotations, trades_df.iterrows())):
        ann.font = dict(size=11,
                        color=_WIN_COL if row["pnl"] > 0 else _LOSS_COL)
        ann.x = 0
        ann.xanchor = "left"

    fig.update_layout(
        height=max(600, n * (CHART_H + 40)),
        margin=dict(l=60, r=20, t=30, b=20),
        paper_bgcolor=_BG,
        plot_bgcolor=_PLOT_BG,
        font=dict(color=_TEXT, size=11),
        showlegend=False,
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        gridcolor=_GRID, gridwidth=1,
        zeroline=False,
        tickfont=dict(size=9, color=_TEXT),
        showline=True, linecolor=_GRID,
    )
    fig.update_yaxes(
        gridcolor=_GRID, gridwidth=1,
        zeroline=False,
        tickfont=dict(size=9, color=_TEXT),
        showline=True, linecolor=_GRID,
        tickformat=".5f",
    )

    return fig


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Plot backtest trades on candlestick charts")
    ap.add_argument("--pair",     help="Filter pair (EURUSD/GBPUSD/NZDUSD)")
    ap.add_argument("--years",    nargs="+", type=int, default=[2022, 2023, 2024, 2025])
    ap.add_argument("--result",   choices=["win", "loss"], help="Filter win or loss only")
    ap.add_argument("--scenario", help="Filter im_scenario (e.g. 1a, 2b, N-long)")
    ap.add_argument("--model",    help="Filter entry_model (judas/breakout)")
    ap.add_argument("--max",      type=int, default=30,  help="Max trades to chart (default 30)")
    ap.add_argument("--tf",       default=TF_DEFAULT, help="Candle timeframe (default 15T)")
    ap.add_argument("--out",      default=os.path.join(DATA_DIR, "trades_chart.html"))
    args = ap.parse_args()

    if not os.path.exists(TRADES_CSV):
        print(f"ERROR: {TRADES_CSV} not found — run run_backtest_histdata.py first")
        sys.exit(1)

    df = pd.read_csv(TRADES_CSV, parse_dates=["opened_at", "closed_at"])
    df["opened_at"] = pd.to_datetime(df["opened_at"], utc=True, errors="coerce")
    df["closed_at"] = pd.to_datetime(df["closed_at"], utc=True, errors="coerce")
    df = df.dropna(subset=["opened_at", "closed_at"])

    # Filters
    if args.pair:
        df = df[df["pair"] == args.pair.upper()]
    if args.result == "win":
        df = df[df["pnl"] > 0]
    elif args.result == "loss":
        df = df[df["pnl"] <= 0]
    if args.scenario:
        df = df[df["im_scenario"] == args.scenario]
    if args.model:
        df = df[df["entry_model"] == args.model]
    if args.years:
        df = df[df["opened_at"].dt.year.isin(args.years)]

    df = df.head(args.max)
    print(f"Charting {len(df)} trades on {args.tf} candles...")

    # Load OHLC data
    pairs_needed = df["pair"].unique().tolist()
    ohlc_cache: dict[str, pd.DataFrame] = {}
    for pair in pairs_needed:
        print(f"  Loading {pair} M1 data for years {args.years}...")
        ohlc_cache[pair] = _load_m1(pair, args.years)
        if ohlc_cache[pair].empty:
            print(f"  WARNING: no data found for {pair} — trades will be skipped")
        else:
            print(f"  {pair}: {len(ohlc_cache[pair]):,} M1 bars loaded")

    fig = build_chart(df, ohlc_cache, args.tf)

    out = os.path.abspath(args.out)
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"\nChart saved → {out}")
    print("Open in browser. Scroll down for each trade.")
    print("Legend: green candle=bullish | dark candle=bearish")
    print("        ▲▼ = entry  ✕ = exit  gold dot = entry level")
    print("        red dash = stop  blue dot = target")


if __name__ == "__main__":
    main()

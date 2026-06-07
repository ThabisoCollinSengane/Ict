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
TRADES_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "trades_dump.csv")

# Candle window: bars before entry and after exit
BARS_BEFORE = 60
BARS_AFTER  = 30

PAIRS = ["EURUSD", "GBPUSD", "NZDUSD"]
TF_DEFAULT = "15T"

_EST_OFFSET = pd.Timedelta(hours=5)


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
    return df.resample(rule).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    ).dropna()


def _window(ohlc: pd.DataFrame, entry_t, exit_t, before: int, after: int) -> pd.DataFrame:
    """Slice BARS_BEFORE bars before entry and BARS_AFTER bars after exit."""
    entry_t = pd.Timestamp(entry_t, tz="UTC") if not hasattr(entry_t, "tzinfo") else entry_t
    exit_t  = pd.Timestamp(exit_t,  tz="UTC") if not hasattr(exit_t,  "tzinfo") else exit_t
    idx = ohlc.index
    i_entry = idx.searchsorted(entry_t)
    i_exit  = idx.searchsorted(exit_t)
    lo = max(0, i_entry - before)
    hi = min(len(idx), i_exit + after + 1)
    return ohlc.iloc[lo:hi]


# ---------------------------------------------------------------------------
# Chart builder
# ---------------------------------------------------------------------------

def _candle_colours(df: pd.DataFrame):
    bull = df["Close"] >= df["Open"]
    inc_colour = ["#26a69a" if b else "#000000" for b in bull]  # green / black
    inc_line   = ["#26a69a" if b else "#000000" for b in bull]
    return inc_colour, inc_line


def _trade_label(row) -> str:
    direction = "LONG" if row["direction"] > 0 else "SHORT"
    win       = "WIN" if row["pnl"] > 0 else "LOSS"
    return (
        f"{row['pair']} {direction} {win}<br>"
        f"Scenario: {row.get('im_scenario','?')}  Model: {row.get('entry_model','?')}<br>"
        f"Entry: {row['entry']:.5f}  Stop: {row.get('stop', float('nan')):.5f}  "
        f"Target: {row.get('target', float('nan')):.5f}<br>"
        f"Exit: {row['exit']:.5f}  P&L: R{row['pnl']:+.2f}<br>"
        f"Opened: {row['opened_at']}  Closed: {row['closed_at']}<br>"
        f"Draw: {row.get('draw_score',0)}/3  "
        f"Confluence: {row.get('target_confluence',0)}  "
        f"CRT: {row.get('crt_tf','')}"
    )


def build_chart(trades_df: pd.DataFrame, ohlc_cache: dict, tf: str) -> go.Figure:
    n = len(trades_df)
    if n == 0:
        fig = go.Figure()
        fig.update_layout(title="No trades matched filter")
        return fig

    cols = min(3, n)
    rows = (n + cols - 1) // cols

    titles = []
    for _, row in trades_df.iterrows():
        direction = "▲ LONG" if row["direction"] > 0 else "▼ SHORT"
        win = "✓" if row["pnl"] > 0 else "✗"
        titles.append(
            f"{win} {row['pair']} {direction}  R{row['pnl']:+.0f}  "
            f"{str(row['opened_at'])[:16]}"
        )

    fig = make_subplots(
        rows=rows, cols=cols,
        subplot_titles=titles,
        shared_xaxes=False,
        vertical_spacing=0.06,
        horizontal_spacing=0.04,
    )

    for idx, (_, row) in enumerate(trades_df.iterrows()):
        r = idx // cols + 1
        c = idx  % cols + 1

        pair   = row["pair"]
        ohlc   = ohlc_cache.get(pair)
        if ohlc is None or ohlc.empty:
            continue

        ohlc_tf = _resample(ohlc, tf) if tf != "1T" else ohlc
        win_df  = _window(ohlc_tf, row["opened_at"], row["closed_at"], BARS_BEFORE, BARS_AFTER)
        if win_df.empty:
            continue

        inc_colour, inc_line = _candle_colours(win_df)

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=win_df.index,
            open=win_df["Open"], high=win_df["High"],
            low=win_df["Low"],   close=win_df["Close"],
            increasing=dict(line=dict(color="#26a69a"), fillcolor="#26a69a"),
            decreasing=dict(line=dict(color="#000000"), fillcolor="#000000"),
            name=pair, showlegend=False,
            hovertext=_trade_label(row),
        ), row=r, col=c)

        entry_t = pd.Timestamp(row["opened_at"], tz="UTC")
        exit_t  = pd.Timestamp(row["closed_at"],  tz="UTC")

        entry_price = row["entry"]
        exit_price  = row["exit"]
        stop_price  = row.get("stop", None)
        target_price = row.get("target", None)
        direction   = row["direction"]

        # Entry marker
        marker_sym = "triangle-up" if direction > 0 else "triangle-down"
        marker_col = "#00c853" if direction > 0 else "#ff1744"
        fig.add_trace(go.Scatter(
            x=[entry_t], y=[entry_price],
            mode="markers",
            marker=dict(symbol=marker_sym, size=14, color=marker_col),
            name="Entry", showlegend=False,
            hovertext=f"ENTRY {entry_price:.5f}",
        ), row=r, col=c)

        # Exit marker
        exit_col = "#00c853" if row["pnl"] > 0 else "#ff1744"
        fig.add_trace(go.Scatter(
            x=[exit_t], y=[exit_price],
            mode="markers",
            marker=dict(symbol="x", size=12, color=exit_col, line=dict(width=2, color=exit_col)),
            name="Exit", showlegend=False,
            hovertext=f"EXIT {exit_price:.5f}  P&L R{row['pnl']:+.2f}",
        ), row=r, col=c)

        x0 = win_df.index[0]
        x1 = win_df.index[-1]

        # Stop line (red dashed)
        if stop_price and not pd.isna(stop_price):
            fig.add_shape(type="line", x0=x0, x1=x1, y0=stop_price, y1=stop_price,
                          line=dict(color="#ff1744", width=1, dash="dash"),
                          row=r, col=c)

        # Target line (blue dashed)
        if target_price and not pd.isna(target_price):
            fig.add_shape(type="line", x0=x0, x1=x1, y0=target_price, y1=target_price,
                          line=dict(color="#2196f3", width=1, dash="dot"),
                          row=r, col=c)

        # Entry line (thin grey)
        fig.add_shape(type="line", x0=x0, x1=x1, y0=entry_price, y1=entry_price,
                      line=dict(color="#888888", width=1, dash="dot"),
                      row=r, col=c)

    fig.update_layout(
        title=dict(
            text=(
                f"ICT Strategy — {n} trades  |  "
                f"Green candle = bullish · Black candle = bearish  |  "
                f"▲/▼ = entry · X = exit · red dash = stop · blue dot = target"
            ),
            font=dict(size=13),
        ),
        height=max(500, rows * 420),
        paper_bgcolor="#1a1a2e",
        plot_bgcolor="#16213e",
        font=dict(color="#e0e0e0"),
        showlegend=False,
    )
    fig.update_xaxes(
        rangeslider_visible=False,
        gridcolor="#2a2a4a",
        tickfont=dict(size=9),
    )
    fig.update_yaxes(gridcolor="#2a2a4a", tickfont=dict(size=9))

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
    ap.add_argument("--max",      type=int, default=200, help="Max trades to chart (default 200)")
    ap.add_argument("--tf",       default=TF_DEFAULT, help="Candle timeframe (default 15T)")
    ap.add_argument("--out",      default=os.path.join(os.path.dirname(__file__), "..", "data", "trades_chart.html"))
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
    print("Open in any browser. Each subplot = one trade.")
    print("Hover over candles/markers for trade details.")


if __name__ == "__main__":
    main()

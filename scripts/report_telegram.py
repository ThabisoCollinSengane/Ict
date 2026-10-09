"""Send backtest results to Telegram.

Usage (from C:\\Ict on the VPS, or /home/user/Ict on the Linux box):
    python scripts/report_telegram.py
    python scripts/report_telegram.py --csv data/histdata/trades_dump.csv
    python scripts/report_telegram.py --years 2024 2025          # filter years
    python scripts/report_telegram.py --pair EURUSD              # filter pair
    python scripts/report_telegram.py --model judas              # filter entry model
    python scripts/report_telegram.py --session london           # filter session profile

Sends:
  1. Summary message  — headline stats (trades, WR, PF, equity, MaxDD)
  2. Equity curve PNG — running account equity over time
  3. Scenario table   — per-scenario WR / PF breakdown
  4. Session table    — London vs NY AM breakdown
"""
import argparse
import io
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

# ── resolve repo root so imports work from any cwd ───────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

import config

try:
    import certifi as _certifi
    _SSL_CTX = ssl.create_default_context(cafile=_certifi.where())
except ImportError:
    _SSL_CTX = ssl.create_default_context()

try:
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
except ImportError as exc:
    sys.exit(f"Missing dependency: {exc}. Run: pip install pandas matplotlib")

# ── defaults ─────────────────────────────────────────────────────────────────
_DATA_DIR   = os.path.join(_ROOT, "data", "histdata")
_CSV_DEFAULT = os.path.join(_DATA_DIR, "trades_dump.csv")


# ── Telegram helpers ─────────────────────────────────────────────────────────

def _token_chat():
    token   = getattr(config, "TELEGRAM_BOT_TOKEN", "") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = getattr(config, "TELEGRAM_CHAT_ID",   "") or os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        sys.exit("No Telegram credentials. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py.")
    return token, chat_id


def _post(url: str, data: bytes, content_type: str) -> dict:
    req = urllib.request.Request(url, data=data, headers={"Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        print(f"[telegram] HTTP {exc.code}: {body}")
        return {}
    except Exception as exc:
        print(f"[telegram] Error: {exc}")
        return {}


def send_text(text: str, token: str, chat_id: str) -> bool:
    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": "HTML",
    }).encode()
    resp = _post(url, payload, "application/json")
    return bool(resp.get("ok"))


def send_photo(png_bytes: bytes, caption: str, token: str, chat_id: str) -> bool:
    boundary = "ICTBotBoundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
        f"{chat_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="caption"\r\n\r\n'
        f"{caption}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="photo"; filename="equity.png"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + png_bytes + f"\r\n--{boundary}--\r\n".encode()

    url  = f"https://api.telegram.org/bot{token}/sendPhoto"
    resp = _post(url, body, f"multipart/form-data; boundary={boundary}")
    return bool(resp.get("ok"))


# ── stats helpers ─────────────────────────────────────────────────────────────

def _pf(df):
    gw = df.loc[df.pnl > 0, "pnl"].sum()
    gl = abs(df.loc[df.pnl < 0, "pnl"].sum())
    return gw / gl if gl > 0 else float("inf")


def _maxdd(series):
    peak = series.cummax()
    dd   = (series - peak) / peak * 100
    return dd.min()


def _equity_series(df, start_cash):
    df_s = df.sort_values("opened_at")
    return start_cash + df_s["pnl"].cumsum(), df_s


# ── chart builder ─────────────────────────────────────────────────────────────

def _equity_chart(df, start_cash: float, title: str) -> bytes:
    equity, df_s = _equity_series(df, start_cash)
    dates = pd.to_datetime(df_s["opened_at"])

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    ax.plot(dates.values, equity.values, color="#00c896", linewidth=1.4)
    ax.fill_between(dates.values, start_cash, equity.values,
                    where=(equity.values >= start_cash),
                    alpha=0.15, color="#00c896")
    ax.fill_between(dates.values, start_cash, equity.values,
                    where=(equity.values < start_cash),
                    alpha=0.25, color="#ff4d6d")

    ax.set_title(title, color="white", fontsize=11, pad=8)
    ax.tick_params(colors="#888888")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda v, _: f"R{v/1e6:.1f}M" if v >= 1e6 else f"R{v:,.0f}"
    ))
    for spine in ax.spines.values():
        spine.set_edgecolor("#333333")
    ax.grid(axis="y", color="#222222", linewidth=0.5)

    plt.tight_layout(pad=0.5)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ── message builders ──────────────────────────────────────────────────────────

def _summary_msg(df, start_cash: float, label: str) -> str:
    n       = len(df)
    wins    = (df.pnl > 0).sum()
    wr      = 100 * wins / n if n else 0
    pf      = _pf(df)
    total   = df.pnl.sum()
    equity, _ = _equity_series(df, start_cash)
    final   = equity.iloc[-1] if len(equity) else start_cash
    mdd     = _maxdd(equity)
    avg_w   = df.loc[df.pnl > 0, "pnl"].mean() if wins else 0
    avg_l   = df.loc[df.pnl < 0, "pnl"].mean() if (n - wins) else 0

    pf_str  = f"{pf:.2f}" if pf != float("inf") else "∞"
    sign    = "+" if total >= 0 else ""

    lines = [
        f"<b>BACKTEST REPORT — {label}</b>",
        "",
        f"Trades:    {n}  |  Wins: {wins}  |  WR: {wr:.1f}%",
        f"PF:        {pf_str}",
        f"Net P&L:   {sign}R{total:,.2f}",
        f"Equity:    R{start_cash:,.0f} → R{final:,.2f}",
        f"Max DD:    {mdd:.2f}%",
        f"Avg win:   R{avg_w:,.2f}  |  Avg loss: R{avg_l:,.2f}",
    ]

    # Per-year breakdown
    if "opened_at" in df.columns:
        df2 = df.copy()
        df2["year"] = pd.to_datetime(df2["opened_at"]).dt.year
        lines.append("")
        lines.append("<b>── By year ──</b>")
        lines.append("Year   Trades   WR%     P&L")
        for yr, g in df2.groupby("year"):
            w2  = (g.pnl > 0).sum()
            wr2 = 100 * w2 / len(g)
            lines.append(f"{yr}   {len(g):>5}   {wr2:>5.1f}%   R{g.pnl.sum():>12,.0f}")

    return "\n".join(lines)


def _scenario_msg(df) -> str:
    if "im_scenario" not in df.columns:
        return ""
    lines = ["<b>── By scenario ──</b>",
             "Scenario       Trades   WR%    PF"]
    for sc, g in df.groupby("im_scenario"):
        w   = (g.pnl > 0).sum()
        wr  = 100 * w / len(g)
        pf  = _pf(g)
        pfs = f"{pf:.2f}" if pf != float("inf") else "∞"
        lines.append(f"{sc:<14} {len(g):>5}   {wr:>5.1f}%  {pfs:>6}")
    return "\n".join(lines)


def _session_msg(df) -> str:
    lines = []

    if "profile" in df.columns:
        lines += ["<b>── By session ──</b>",
                  "Session     Trades   WR%     PF"]
        for pr, g in df.groupby("profile"):
            w   = (g.pnl > 0).sum()
            wr  = 100 * w / len(g)
            pf  = _pf(g)
            pfs = f"{pf:.2f}" if pf != float("inf") else "∞"
            label = pr.replace("_", " ").title()
            lines.append(f"{label:<11} {len(g):>5}   {wr:>5.1f}%  {pfs:>6}")

    if "entry_model" in df.columns:
        lines += ["", "<b>── By entry model ──</b>",
                  "Model         Trades   WR%     PF"]
        for m, g in df.groupby("entry_model"):
            w   = (g.pnl > 0).sum()
            wr  = 100 * w / len(g)
            pf  = _pf(g)
            pfs = f"{pf:.2f}" if pf != float("inf") else "∞"
            lines.append(f"{m:<13} {len(g):>5}   {wr:>5.1f}%  {pfs:>6}")

    return "\n".join(lines)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Send backtest report to Telegram")
    ap.add_argument("--csv",     default=_CSV_DEFAULT, help="Path to trades_dump.csv")
    ap.add_argument("--years",   nargs="+", type=int,  help="Filter to these years")
    ap.add_argument("--pair",    help="Filter to one pair (EURUSD / GBPUSD / NZDUSD)")
    ap.add_argument("--model",   help="Filter entry model (judas / breakout)")
    ap.add_argument("--session", help="Filter session profile (london / ny)")
    args = ap.parse_args()

    token, chat_id = _token_chat()

    # Load
    if not os.path.exists(args.csv):
        sys.exit(f"CSV not found: {args.csv}")
    df = pd.read_csv(args.csv, parse_dates=["opened_at", "closed_at"])
    if df.empty:
        sys.exit("trades_dump.csv is empty.")

    # Filters
    label_parts = ["4yr" if not args.years else "+".join(str(y) for y in args.years)]
    if args.years:
        df["_year"] = pd.to_datetime(df["opened_at"]).dt.year
        df = df[df["_year"].isin(args.years)]
        label_parts = [str(y) for y in args.years]
    if args.pair:
        df = df[df["pair"].str.upper() == args.pair.upper()]
        label_parts.append(args.pair.upper())
    if args.model:
        df = df[df["entry_model"] == args.model.lower()]
        label_parts.append(args.model)
    if args.session and "profile" in df.columns:
        df = df[df["profile"] == args.session.lower()]
        label_parts.append(args.session)

    if df.empty:
        sys.exit("No trades match the filters.")

    label       = " | ".join(label_parts)
    start_cash  = config.STARTING_CASH

    # 1 — summary text
    print("Sending summary...")
    ok = send_text(_summary_msg(df, start_cash, label), token, chat_id)
    print("  OK" if ok else "  FAILED")

    # 2 — equity curve image
    print("Sending equity curve...")
    png = _equity_chart(df, start_cash, f"Equity curve — {label}")
    ok  = send_photo(png, f"Equity curve — {label}", token, chat_id)
    print("  OK" if ok else "  FAILED")

    # 3 — scenario breakdown
    sc_msg = _scenario_msg(df)
    if sc_msg:
        print("Sending scenario breakdown...")
        ok = send_text(sc_msg, token, chat_id)
        print("  OK" if ok else "  FAILED")

    # 4 — session / model breakdown
    sess_msg = _session_msg(df)
    if sess_msg:
        print("Sending session breakdown...")
        ok = send_text(sess_msg, token, chat_id)
        print("  OK" if ok else "  FAILED")

    print("Done.")


if __name__ == "__main__":
    main()

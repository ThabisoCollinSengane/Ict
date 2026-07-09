"""MetaTrader 5 broker layer for Exness — connect, fetch bars, place/manage orders.

This module is the ONLY place that talks to the MetaTrader5 package. Everything
else in the live runtime calls these helpers, so the strategy code never touches
broker-specific quirks (symbol suffixes, filling modes, retcodes).

Design rules:
  - The `MetaTrader5` package only runs on Windows, so it is imported LAZILY (inside
    `_mt5()`), letting this file be imported/linted on any OS.
  - Every public function is defensive: it returns None / [] / False on failure and
    logs the reason — a transient broker error must never crash the trading loop.
  - Symbols are resolved dynamically. Exness appends suffixes (e.g. "EURUSDm" on
    cent/standard-plus accounts, "EURUSDz", etc.), so we map each logical base name
    ("EURUSD") to the broker's real symbol once and cache it.

Typical use:
    import live.mt5_connector as mt
    mt.connect(login=12345678, password="...", server="Exness-MT5Trial14")
    bars = mt.get_bars("EURUSD", "5T", 300)          # list[Bar], oldest→newest
    acc  = mt.account()                               # AccountInfo
    mt.market_order("EURUSD", 0.01, +1, sl=1.0850, tp=1.0920, comment="ict")
    mt.shutdown()
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

log = logging.getLogger("ict.mt5")

# ── Lazy MetaTrader5 import ───────────────────────────────────────────────────
_MT5 = None


def _mt5():
    """Return the MetaTrader5 module, importing on first use.

    Raises a clear error on non-Windows / missing package so the failure is
    obvious rather than an AttributeError deep in a call.
    """
    global _MT5
    if _MT5 is None:
        try:
            import MetaTrader5 as mt5  # noqa: N813
        except ImportError as e:
            raise RuntimeError(
                "MetaTrader5 package not available. It only runs on Windows with "
                "the MT5 terminal installed. Install with: pip install MetaTrader5"
            ) from e
        _MT5 = mt5
    return _MT5


# ── Logical symbol universe (base names the strategy uses) ────────────────────
# Tradeable pairs + intermarket crosses + DXY constituents (DXY is synthetic).
TRADEABLE = ("EURUSD", "GBPUSD", "NZDUSD")
INTERMARKET = ("EURGBP", "AUDNZD", "AUDUSD")
DXY_CONSTITUENTS = ("EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF")
ALL_SYMBOLS = tuple(dict.fromkeys(TRADEABLE + INTERMARKET + DXY_CONSTITUENTS))

# backtest TF code → MT5 timeframe constant name (resolved lazily in _tf()).
_TF_NAMES = {
    "1T": "TIMEFRAME_M1",
    "5T": "TIMEFRAME_M5",
    "15T": "TIMEFRAME_M15",
    "60T": "TIMEFRAME_H1",
    "240T": "TIMEFRAME_H4",
    "D": "TIMEFRAME_D1",
    "W": "TIMEFRAME_W1",
    # friendly aliases
    "M1": "TIMEFRAME_M1", "M5": "TIMEFRAME_M5", "M15": "TIMEFRAME_M15",
    "H1": "TIMEFRAME_H1", "H4": "TIMEFRAME_H4", "D1": "TIMEFRAME_D1",
    "W1": "TIMEFRAME_W1",
}

# logical base → resolved broker symbol (filled by resolve_symbol)
_SYMBOL_MAP: dict[str, str] = {}


@dataclass
class Bar:
    time: int            # POSIX seconds (bar open time, broker server time)
    open: float
    high: float
    low: float
    close: float
    volume: float        # tick volume


@dataclass
class AccountInfo:
    login: int
    balance: float
    equity: float
    margin_free: float
    currency: str
    leverage: int
    server: str


# ── Connection ────────────────────────────────────────────────────────────────
def connect(login: int | None = None, password: str | None = None,
            server: str | None = None, terminal_path: str | None = None,
            timeout_ms: int = 30_000) -> bool:
    """Initialise the MT5 terminal and (optionally) log in.

    If login/password/server are omitted, MT5 uses the account already signed in
    on the running terminal — handy once you've logged in manually in the GUI.
    Returns True on success.
    """
    mt5 = _mt5()
    kwargs = {"timeout": timeout_ms}
    if terminal_path:
        kwargs["path"] = terminal_path
    if login and password and server:
        kwargs.update(login=int(login), password=password, server=server)

    if not mt5.initialize(**kwargs):
        log.error("mt5.initialize failed: %s", mt5.last_error())
        return False

    info = mt5.account_info()
    if info is None:
        log.error("Connected to terminal but no account — log in first. %s",
                  mt5.last_error())
        return False
    log.info("MT5 connected: login=%s server=%s balance=%.2f %s",
             info.login, info.server, info.balance, info.currency)
    return True


def shutdown() -> None:
    """Close the MT5 connection. Safe to call even if never connected."""
    try:
        _mt5().shutdown()
    except Exception:  # noqa: BLE001 — shutdown must never raise
        pass


# ── Symbol resolution ─────────────────────────────────────────────────────────
def resolve_symbol(base: str) -> str | None:
    """Map a logical base ("EURUSD") to the broker's real symbol, and select it.

    Handles Exness suffixes by scanning the broker's symbol list for one whose
    name starts with the base (preferring an exact match). Caches the result and
    enables the symbol in MarketWatch so bars/ticks become available.
    """
    if base in _SYMBOL_MAP:
        return _SYMBOL_MAP[base]
    mt5 = _mt5()

    # exact match first
    candidates = []
    if mt5.symbol_info(base) is not None:
        candidates.append(base)
    # then suffixed variants (EURUSDm, EURUSD.r, EURUSDz, ...)
    for s in (mt5.symbols_get(f"{base}*") or []):
        if s.name != base:
            candidates.append(s.name)

    for name in candidates:
        if mt5.symbol_select(name, True):
            _SYMBOL_MAP[base] = name
            if name != base:
                log.info("Resolved %s → %s (broker suffix)", base, name)
            return name

    log.error("Could not resolve symbol for %s (broker offers no match)", base)
    return None


def resolve_all(symbols=ALL_SYMBOLS) -> dict[str, str]:
    """Resolve every symbol the strategy needs; returns {base: broker_name}.

    Logs any that fail so you catch a missing instrument (e.g. USDSEK) before the
    bot runs rather than mid-session.
    """
    out = {}
    for base in symbols:
        name = resolve_symbol(base)
        if name:
            out[base] = name
    missing = [b for b in symbols if b not in out]
    if missing:
        log.warning("Symbols NOT available on this broker: %s", ", ".join(missing))
    return out


def _tf(code: str):
    """Translate a backtest TF code to the MT5 timeframe constant."""
    name = _TF_NAMES.get(code)
    if name is None:
        raise ValueError(f"Unknown timeframe code: {code!r}")
    return getattr(_mt5(), name)


# ── Market data ───────────────────────────────────────────────────────────────
def get_bars(base: str, tf: str, count: int) -> list[Bar]:
    """Return the most recent `count` completed bars for `base` at `tf`.

    Oldest→newest. The currently-forming bar is dropped so the strategy only ever
    sees closed candles (no repaint). Returns [] on any error.
    """
    name = resolve_symbol(base)
    if name is None:
        return []
    mt5 = _mt5()
    # fetch one extra and drop the forming bar (position 0 is the current bar)
    rates = mt5.copy_rates_from_pos(name, _tf(tf), 0, count + 1)
    if rates is None or len(rates) == 0:
        log.warning("No rates for %s %s: %s", base, tf, mt5.last_error())
        return []
    rates = rates[:-1]          # drop the in-progress bar
    return [Bar(int(r["time"]), float(r["open"]), float(r["high"]),
                float(r["low"]), float(r["close"]), float(r["tick_volume"]))
            for r in rates]


def tick(base: str):
    """Return (bid, ask) for `base`, or None on error."""
    name = resolve_symbol(base)
    if name is None:
        return None
    t = _mt5().symbol_info_tick(name)
    if t is None:
        return None
    return (t.bid, t.ask)


def pip_size(base: str) -> float:
    """Pip size for a symbol: 0.01 for JPY pairs, else 0.0001."""
    return 0.01 if base.endswith("JPY") else 0.0001


# ── Account & positions ───────────────────────────────────────────────────────
def account() -> AccountInfo | None:
    info = _mt5().account_info()
    if info is None:
        return None
    return AccountInfo(info.login, info.balance, info.equity, info.margin_free,
                       info.currency, info.leverage, info.server)


def positions(base: str | None = None) -> list:
    """Open positions, optionally filtered to one base symbol. [] on error."""
    mt5 = _mt5()
    if base:
        name = resolve_symbol(base)
        pos = mt5.positions_get(symbol=name) if name else None
    else:
        pos = mt5.positions_get()
    return list(pos) if pos else []


# ── Order execution ───────────────────────────────────────────────────────────
def _filling_mode(name: str):
    """Pick a supported order-filling mode for the symbol (IOC→FOK→RETURN)."""
    mt5 = _mt5()
    info = mt5.symbol_info(name)
    modes = getattr(info, "filling_mode", 0) if info else 0
    # filling_mode is a bitmask; prefer IOC, then FOK, else RETURN
    if modes & mt5.SYMBOL_FILLING_IOC:
        return mt5.ORDER_FILLING_IOC
    if modes & mt5.SYMBOL_FILLING_FOK:
        return mt5.ORDER_FILLING_FOK
    return mt5.ORDER_FILLING_RETURN


def market_order(base: str, volume_lots: float, direction: int,
                 sl: float | None = None, tp: float | None = None,
                 deviation: int = 20, comment: str = "ict",
                 magic: int = 770022) -> dict | None:
    """Send a market order. direction +1 buy / -1 sell. Returns a result dict.

    Returns {"ok": bool, "ticket": int|None, "retcode": int, "comment": str}.
    Never raises — a failed send returns ok=False with the broker's retcode.
    """
    name = resolve_symbol(base)
    if name is None:
        return {"ok": False, "ticket": None, "retcode": -1, "comment": "unresolved symbol"}
    mt5 = _mt5()
    t = mt5.symbol_info_tick(name)
    if t is None:
        return {"ok": False, "ticket": None, "retcode": -1, "comment": "no tick"}

    price = t.ask if direction > 0 else t.bid
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": name,
        "volume": float(volume_lots),
        "type": mt5.ORDER_TYPE_BUY if direction > 0 else mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": int(deviation),
        "magic": int(magic),
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": _filling_mode(name),
    }
    if sl is not None:
        req["sl"] = float(sl)
    if tp is not None:
        req["tp"] = float(tp)

    res = mt5.order_send(req)
    if res is None:
        return {"ok": False, "ticket": None, "retcode": -1,
                "comment": f"order_send None: {mt5.last_error()}"}
    ok = res.retcode == mt5.TRADE_RETCODE_DONE
    if not ok:
        log.error("market_order %s %s %.2f failed: retcode=%s %s",
                  base, direction, volume_lots, res.retcode, res.comment)
    return {"ok": ok, "ticket": getattr(res, "order", None),
            "retcode": res.retcode, "comment": res.comment}


def modify_sl_tp(ticket: int, sl: float | None = None,
                 tp: float | None = None) -> bool:
    """Modify stop-loss / take-profit on an open position by its ticket."""
    mt5 = _mt5()
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        log.error("modify_sl_tp: position %s not found", ticket)
        return False
    p = pos[0]
    req = {
        "action": mt5.TRADE_ACTION_SLTP,
        "symbol": p.symbol,
        "position": int(ticket),
        "sl": float(sl) if sl is not None else p.sl,
        "tp": float(tp) if tp is not None else p.tp,
        "magic": p.magic,
    }
    res = mt5.order_send(req)
    ok = res is not None and res.retcode == mt5.TRADE_RETCODE_DONE
    if not ok:
        log.error("modify_sl_tp %s failed: %s",
                  ticket, getattr(res, "comment", mt5.last_error()))
    return ok


def close_position(ticket: int, deviation: int = 20) -> bool:
    """Close an open position by ticket with an opposite market order."""
    mt5 = _mt5()
    pos = mt5.positions_get(ticket=ticket)
    if not pos:
        log.error("close_position: %s not found", ticket)
        return False
    p = pos[0]
    t = mt5.symbol_info_tick(p.symbol)
    if t is None:
        return False
    is_buy = p.type == mt5.POSITION_TYPE_BUY
    req = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": p.symbol,
        "volume": p.volume,
        "type": mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY,
        "position": int(ticket),
        "price": t.bid if is_buy else t.ask,
        "deviation": int(deviation),
        "magic": p.magic,
        "comment": "ict close",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": _filling_mode(p.symbol),
    }
    res = mt5.order_send(req)
    ok = res is not None and res.retcode == mt5.TRADE_RETCODE_DONE
    if not ok:
        log.error("close_position %s failed: %s",
                  ticket, getattr(res, "comment", mt5.last_error()))
    return ok


def wait_for_bar(tf: str = "5T", poll_seconds: float = 2.0,
                 base: str = "EURUSD", timeout_seconds: float | None = None):
    """Block until a NEW completed bar of `tf` appears, then return it.

    Used by the live loop to wake once per closed candle. Returns the new Bar,
    or None if `timeout_seconds` elapses with no new bar — the caller uses that
    to run a stale-feed check instead of blocking forever on a frozen feed.
    """
    last_time = None
    bars = get_bars(base, tf, 2)
    if bars:
        last_time = bars[-1].time
    waited = 0.0
    while True:
        time.sleep(poll_seconds)
        waited += poll_seconds
        bars = get_bars(base, tf, 2)
        if bars and (last_time is None or bars[-1].time != last_time):
            return bars[-1]
        if timeout_seconds is not None and waited >= timeout_seconds:
            return None

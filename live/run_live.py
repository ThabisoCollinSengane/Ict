"""Phase 2 live strategy loop — drives backtest signal logic on live MT5 bars.

Architecture
------------
LiveTrader subclasses Backtester to reuse every ICT signal method unchanged
(conviction scoring, find_target, structure_stop, P9/P18/draw-cascade sizing).
Three thin overrides wire the live data + execution layer in:

  bars_up_to()    → MT5 get_bars instead of historical dicts
  _maybe_open()   → after parent creates self.active[pair], place real MT5 order
  _maybe_pyramid()→ same pattern for pyramid legs

Live position management (vs backtest simulation):
  _sync_closed_positions()  — detect legs closed by MT5 (SL/TP hit by broker)
  _update_live_positions()  — trail stops via modify_sl_tp, trigger pyramid check
  _force_close()            — close via MT5 (session handover, kill switch)

Usage on the VPS (DEMO account first — see LIVE_SETUP.md):
    $env:MT5_LOGIN="12345678"
    $env:MT5_PASSWORD="yourpassword"
    $env:MT5_SERVER="Exness-MT5Trial14"
    .\.venv\\Scripts\\python.exe -m live.run_live

Credentials via env vars only — NEVER hardcode them.
"""

from __future__ import annotations

import logging
import os
import sys
import urllib.request
from collections import namedtuple
from datetime import datetime, timezone

# Add repo root to path so imports work when run as a module from the VPS.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config
from backtest import Backtester   # reuse all ICT signal logic
from ict.killzones import can_open_new_trade
from news_filter import NewsCalendar
from risk import pip_size
from trade_log import TradeLog
import live.mt5_connector as mt

try:
    from scripts.notify import send_message as _notify
except Exception:
    def _notify(msg): return False  # noqa: E731

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("data/live.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("ict.live")

# Backtest Bar is namedtuple("Bar", "Open High Low Close").
# MT5 Bar has (time, open, high, low, close, volume) with lowercase fields.
# _BBar matches the uppercase convention the ict/ modules expect.
_BBar = namedtuple("_BBar", "Open High Low Close")


def _to_bars(mt_bars: list) -> list[_BBar]:
    return [_BBar(b.open, b.high, b.low, b.close) for b in mt_bars]


# ---------------------------------------------------------------------------
# LiveTrader
# ---------------------------------------------------------------------------

class LiveTrader(Backtester):
    """Live trading engine.

    Inherits all ICT signal logic from Backtester; overrides data access and
    order execution to use the MT5 broker layer.  Call connect() + run().
    """

    def __init__(self):
        # Do NOT call super().__init__() — it expects pre-loaded historical dicts.
        # Initialise all the state variables _maybe_open / _maybe_pyramid read.

        acc = mt.account()
        if acc is None:
            raise RuntimeError("MT5 not connected — call mt.connect() before LiveTrader()")

        self.equity       = self._zar(acc.balance)
        self.start_equity = self.equity
        self._peak_equity = self.equity

        # active positions: pair → {direction, target, legs:[{entry,stop,units,ticket,…}],…}
        self.active = {}
        self.trades = []

        # Circuit-breaker state
        self._consec_losses     = 0
        self._day_open_eq       = {}   # date → equity at day open
        self._drawdown_halt_until = None

        # Weekly / daily trade budgets
        self._week_total   = {}
        self._week_pair    = {}
        self._day_total    = {}
        self._day_pair     = {}
        self._day_pair_ny  = {}
        self._day_pair_pm  = {}

        # Session phase tracking
        self._judas_seen       = {}
        self._london_judas_open = {}
        self._london_dir       = {}

        # Caches (same keys as backtest; reused by inherited methods)
        self._mp_cache   = {}
        self._weekly_amd = {}
        self._draw_cache = {}

        # Diagnostic counters
        self.gate = {
            "checks": 0, "in_killzone": 0, "news_clear": 0,
            "nfp_fomc_ok": 0, "intermarket_signal": 0, "pair_matches": 0,
            "mss_h1_m15_m5_ok": 0,
            "daily_bias_ok": 0, "h1_bias_ok": 0, "h4_bias_ok": 0,
            "dealing_range_ok": 0, "consolidation_found": 0,
            "manipulation_correct_dir": 0,
            "m5_fvg_correct_dir": 0, "target_found": 0,
            "rr_ok": 0, "units_nonzero": 0, "limit_placed": 0,
            "drawdown_halt": 0, "daily_loss_halt": 0, "consec_loss_pause": 0,
            "weekly_cap": 0, "weekly_pair_cap": 0,
            "daily_cap": 0, "daily_pair_cap": 0,
            "weekly_amd_confirmed": 0, "session_handover_closed": 0,
            "htf_draw_full_cascade": 0, "htf_draw_partial": 0, "htf_draw_counter": 0,
            "htf_fvg_5050_hit": 0,
            "ote_zone": 0, "choch_confirmed": 0, "low_conviction": 0,
            "judas_divergence": 0, "ny_continuation": 0,
        }

        # News calendar: try live XML, fall back to CSV
        self.news = NewsCalendar()
        self._load_news()

        self.log = TradeLog()
        log.info("LiveTrader initialised — equity %.2f ZAR (acct: %.2f %s lev 1:%s)",
                 self.equity, acc.balance, acc.currency, acc.leverage)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _zar(amount_in_acct_ccy: float) -> float:
        """Convert account-currency amount to ZAR."""
        acc = mt.account()
        if acc and acc.currency == "ZAR":
            return amount_in_acct_ccy
        return amount_in_acct_ccy * config.USD_ZAR

    def _load_news(self):
        try:
            url = config.FOREXFACTORY_XML_URL
            with urllib.request.urlopen(url, timeout=10) as r:
                xml = r.read().decode("utf-8")
            n = self.news.load(xml)
            log.info("News: %d events from ForexFactory XML", n)
        except Exception as exc:
            log.warning("FF XML fetch failed (%s) — trying CSV fallback", exc)
            for path in ("data/news_events.csv", "./data/news_events.csv"):
                try:
                    with open(path) as f:
                        n = self.news.load_csv(f.read())
                    log.info("News: %d events from %s (may be stale)", n, path)
                    return
                except Exception:
                    continue
            log.warning("No news calendar loaded — news filter disabled")

    def _refresh_news(self):
        """Reload news calendar (call at start of each trading day)."""
        self._load_news()

    # ── Data access — MT5 bars ────────────────────────────────────────────────

    def bars_up_to(self, sym, tf, t, max_bars=None):
        """Fetch completed bars from MT5 and return in backtest Bar format.

        `t` is ignored — in live mode all bars are up to now.
        `max_bars` caps fetch count; 0 or None = up to 3000 (safe for H4/D/W full history).
        """
        count = max_bars if (max_bars and max_bars < 3000) else 3000
        return _to_bars(mt.get_bars(sym, tf, count))

    def _bar_at(self, sym, tf, t):
        bars = self.bars_up_to(sym, tf, t, max_bars=2)
        return bars[-1] if bars else None

    # ── Market profile overrides (uses tf_dfs/tf_index in backtest) ───────────
    # These are conviction bonuses only — returning safe approximations or None
    # means the hard gates and sizing levers still work correctly.

    def _daily_open(self, pair, t):
        bars = self.bars_up_to(pair, "D", t, max_bars=3)
        return bars[-1].Open if bars else None

    def _weekly_open(self, pair, t):
        bars = self.bars_up_to(pair, "W", t, max_bars=3)
        return bars[-1].Open if bars else None

    def _session_open(self, pair, sess_name, t):
        return None   # skip (needs intraday session-open tracking)

    def _get_weekly_amd(self, pair, t):
        return None   # skip (uses tf_bars DatetimeIndex not available in live)

    def _market_profile(self, pair, t):
        return None   # skip (uses tf_dfs not available in live)

    # ── Trade entry — wrap parent + place real MT5 order ─────────────────────

    def _maybe_open(self, pair, t):
        was_active = pair in self.active
        super()._maybe_open(pair, t)

        if was_active or pair not in self.active:
            return   # nothing new opened

        st  = self.active[pair]
        leg = st["legs"][0]
        lots = round(leg["units"] / config.LOT_UNITS, 2)
        lots = max(lots, config.MIN_LOT_SIZE)

        res = mt.market_order(
            pair, lots, st["direction"],
            sl=leg["stop"], tp=st["target"],
            comment=f"ict_{st.get('im_scenario', '')}",
        )
        if res and res["ok"]:
            leg["ticket"] = res["ticket"]
            _dir_str   = "LONG" if st["direction"] > 0 else "SHORT"
            _stop_pips = abs(leg["entry"] - leg["stop"]) / pip_size(pair)
            _rwd_pips  = abs(st["target"] - leg["entry"]) / pip_size(pair)
            log.info(
                "OPEN %s %s %.2f lots  entry≈%.5f  SL=%.5f  TP=%.5f  [%s %s]",
                "BUY" if st["direction"] > 0 else "SELL", pair, lots,
                leg["entry"], leg["stop"], st["target"],
                st.get("im_scenario", "?"), st.get("entry_model", "?"),
            )
            _notify(
                f"TRADE OPENED\n"
                f"{pair} {_dir_str} | {st.get('entry_model','?').upper()}\n"
                f"Entry:  {leg['entry']:.5f}\n"
                f"Stop:   {leg['stop']:.5f} ({_stop_pips:.1f} pips)\n"
                f"Target: {st['target']:.5f} ({_rwd_pips:.1f} pips)\n"
                f"Scenario: {st.get('im_scenario','?')} | Draw: {st.get('draw_score','?')}/3\n"
                f"Equity: R{self.equity:,.2f}"
            )
            self.log.upsert_position(pair, st)
        else:
            log.error("MT5 order FAILED for %s: %s", pair, res)
            del self.active[pair]

    def _maybe_pyramid(self, pair, t):
        if pair not in self.active:
            return
        st = self.active[pair]
        n_before   = len(st["legs"])
        prior_stop = st["legs"][-1]["stop"] if st["legs"] else None

        super()._maybe_pyramid(pair, t)

        if pair not in self.active:
            return
        st = self.active[pair]
        if len(st["legs"]) <= n_before:
            return   # no new leg added

        # _maybe_pyramid promotes the prior leg's stop to BE — sync it to MT5.
        if n_before > 0 and prior_stop is not None:
            prior = st["legs"][n_before - 1]
            if prior["stop"] != prior_stop and prior.get("ticket"):
                mt.modify_sl_tp(prior["ticket"], sl=prior["stop"], tp=st["target"])

        new_leg = st["legs"][-1]
        lots = round(new_leg["units"] / config.LOT_UNITS, 2)
        lots = max(lots, config.MIN_LOT_SIZE)

        res = mt.market_order(
            pair, lots, st["direction"],
            sl=new_leg["stop"], tp=st["target"],
            comment=f"ict_pyr{new_leg['leg_idx']}",
        )
        if res and res["ok"]:
            new_leg["ticket"] = res["ticket"]
            log.info("PYRAMID %s leg %d  %.2f lots  entry≈%.5f",
                     pair, new_leg["leg_idx"], lots, new_leg["entry"])
            self.log.upsert_position(pair, st)
        else:
            log.error("Pyramid order FAILED for %s leg %d: %s",
                      pair, new_leg["leg_idx"], res)
            st["legs"].pop()   # revert the leg

    def _force_close(self, pair, price, t, reason):
        """Close all MT5 positions for a pair (session handover, kill switch)."""
        st = self.active.get(pair)
        if st is None:
            return
        for leg in list(st["legs"]):
            ticket = leg.get("ticket")
            if ticket:
                mt.close_position(ticket)
        log.info("Force-closed %s (%s)", pair, reason)
        # State cleanup happens on next _sync_closed_positions call.

    # ── Live position management ──────────────────────────────────────────────

    def _sync_closed_positions(self, now):
        """Remove legs that MT5 has already closed (SL or TP hit by broker)."""
        for pair in list(self.active.keys()):
            st = self.active[pair]
            open_tickets = {p.ticket for p in (mt.positions(pair) or [])}

            live_legs = []
            for leg in st["legs"]:
                ticket = leg.get("ticket")
                if ticket is None or ticket in open_tickets:
                    live_legs.append(leg)
                else:
                    pnl_zar = self._deal_pnl_zar(ticket)
                    sign = "+" if (pnl_zar or 0) >= 0 else ""
                    log.info("MT5 closed %s ticket=%s  pnl=%s%.2f ZAR",
                             pair, ticket, sign, pnl_zar or 0)
                    if pnl_zar is not None:
                        if pnl_zar > 0:
                            self._consec_losses = 0
                        else:
                            self._consec_losses += 1
                    _dir_str = "LONG" if st["direction"] > 0 else "SHORT"
                    _pnl_str = f"{sign}R{abs(pnl_zar or 0):,.2f}"
                    _notify(
                        f"TRADE CLOSED\n"
                        f"{pair} {_dir_str} | ticket {ticket}\n"
                        f"P&L: {_pnl_str}\n"
                        f"Equity: R{self.equity:,.2f}"
                    )
                    self.trades.append({
                        "pair": pair, "direction": st["direction"],
                        "ticket": ticket, "closed_at": now,
                        "reason": "mt5_close", "pnl_zar": pnl_zar,
                    })

            st["legs"] = live_legs
            if not st["legs"]:
                del self.active[pair]
                self.log.delete_position(pair)

    def _deal_pnl_zar(self, ticket: int) -> float | None:
        """Retrieve realised P&L for a closed position from MT5 deal history."""
        try:
            mt5mod = mt._mt5()
            deals = mt5mod.history_deals_get(position=int(ticket))
            if not deals:
                return None
            profit = sum(d.profit for d in deals)
            acc = mt.account()
            if acc and acc.currency == "ZAR":
                return profit
            return profit * config.USD_ZAR
        except Exception:
            return None

    def _trail_stops(self, pair, cur_price, now):
        """Apply BE / lock / P23 milestone trailing and push updated SL to MT5.

        +10 pips → stop to break-even.
        +20 pips → stop locked at entry + 10 pips.
        +40/60/80… pips → milestone trail: stop at entry + (milestone − 10) pips.
        """
        st = self.active.get(pair)
        if st is None:
            return
        direction = st["direction"]
        target    = st["target"]
        pip       = pip_size(pair)

        for leg in st["legs"]:
            old_stop    = leg["stop"]
            entry       = leg["entry"]
            pips_profit = (cur_price - entry) * direction / pip
            new_stop    = old_stop

            # TRAIL_BE: move stop to entry at +TRAIL_BE_PIPS
            if pips_profit >= config.TRAIL_BE_PIPS:
                if direction > 0:
                    new_stop = max(new_stop, entry)
                else:
                    new_stop = min(new_stop, entry)

            # TRAIL_LOCK: lock +10 pips at +TRAIL_LOCK_PIPS
            if pips_profit >= config.TRAIL_LOCK_PIPS:
                locked = entry + 10 * pip * direction
                if direction > 0:
                    new_stop = max(new_stop, locked)
                else:
                    new_stop = min(new_stop, locked)

            # P23 milestone trail: every MILESTONE_TRAIL_STEP pips of additional
            # progress, ratchet stop to (milestone - MILESTONE_TRAIL_BUFFER) pips.
            if (config.MILESTONE_TRAIL_ENABLED
                    and pips_profit >= config.TRAIL_LOCK_PIPS + config.MILESTONE_TRAIL_STEP):
                _step      = config.MILESTONE_TRAIL_STEP
                _buf       = config.MILESTONE_TRAIL_BUFFER
                _milestone = int(pips_profit / _step) * _step
                _lock_ms   = entry + (_milestone - _buf) * pip * direction
                if direction > 0:
                    new_stop = max(new_stop, _lock_ms)
                else:
                    new_stop = min(new_stop, _lock_ms)

            if new_stop != old_stop:
                leg["stop"] = new_stop
                if leg.get("ticket"):
                    mt.modify_sl_tp(leg["ticket"], sl=new_stop, tp=target)
                    log.info("Trail %s %s  stop %.5f → %.5f  (+%.1f pips profit)",
                             "long" if direction > 0 else "short", pair,
                             old_stop, new_stop, pips_profit)

    def _update_live_positions(self, now):
        """Trail stops and attempt pyramid adds for all open positions."""
        for pair in list(self.active.keys()):
            q = mt.tick(pair)
            if q is None:
                continue
            cur_price = (q[0] + q[1]) / 2
            self._trail_stops(pair, cur_price, now)
            # Pyramid check: inherits parent's _maybe_pyramid logic.
            self._maybe_pyramid(pair, now)

    def _update_equity(self):
        """Sync self.equity from MT5 balance (realised P&L only, stable for sizing)."""
        acc = mt.account()
        if acc:
            self.equity = self._zar(acc.balance)
            self._peak_equity = max(self._peak_equity, self.equity)

    def _check_session_kill(self, now):
        """Close all positions if session equity drops > SESSION_DRAWDOWN_PCT."""
        if config.SESSION_DRAWDOWN_PCT <= 0 or not self.active:
            return
        day_key = now.date()
        session_eq = self._day_open_eq.get(day_key)
        if not session_eq:
            return
        acc = mt.account()
        if acc is None:
            return
        live_eq = self._zar(acc.equity)   # floating equity for the kill switch
        dd = (session_eq - live_eq) / session_eq * 100
        if dd >= config.SESSION_DRAWDOWN_PCT:
            log.warning("Session kill switch: %.1f%% floating DD — closing all", dd)
            _notify(
                f"CIRCUIT BREAKER: SESSION KILL SWITCH\n"
                f"Session loss: {dd:.1f}%\n"
                f"Equity: R{self._zar(acc.equity):,.2f}\n"
                f"All positions closing — halted for the day"
            )
            for pair in list(self.active.keys()):
                self._force_close(pair, 0, now, "session_kill")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        """Block until interrupted: wake on each M5 bar close, run strategy."""
        log.info("=" * 60)
        log.info("ICT live loop started — pairs: %s", ", ".join(config.PAIRS))
        log.info("Account: %.2f ZAR  leverage 1:%s", self.equity,
                 mt.account().leverage if mt.account() else "?")
        log.info("DEMO mode until smoke test confirmed — see LIVE_SETUP.md")
        log.info("=" * 60)

        while True:
            try:
                mt.wait_for_bar("5T")
                now = datetime.now(timezone.utc)
                self._run_once(now)
            except KeyboardInterrupt:
                log.info("KeyboardInterrupt — shutting down gracefully")
                break
            except Exception:
                log.exception("Unhandled exception in live loop — continuing")

        mt.shutdown()
        log.info("Live loop stopped. Open positions left in MT5 if any.")

    def _run_once(self, now: datetime):
        """One M5 bar: sync state → trail → new entries."""
        day_key = now.date()

        # Refresh news calendar once per day at midnight UTC.
        if day_key not in self._day_open_eq:
            self._refresh_news()

        # Sync equity from MT5 (uses balance = realised P&L).
        self._update_equity()

        # Record day-open equity for daily-loss and session-kill checks.
        if day_key not in self._day_open_eq:
            self._day_open_eq[day_key] = self.equity
            self._consec_losses = 0
            log.info("New day %s — equity %.2f ZAR", day_key, self.equity)
            _notify(
                f"NEW DAY — {day_key}\n"
                f"Equity: R{self.equity:,.2f}\n"
                f"Open positions: {len(self.active)}"
            )

        # Detect positions closed by broker (SL/TP hit).
        self._sync_closed_positions(now)

        # Session kill switch (floating equity).
        self._check_session_kill(now)

        # Trail stops on open positions + try pyramid adds.
        self._update_live_positions(now)

        # Session handover: close positions fighting the weekly AMD.
        if can_open_new_trade(now):
            self._check_session_handover(now)

        # New entry checks for each tradeable pair.
        for pair in config.PAIRS:
            if pair not in self.active:
                if can_open_new_trade(now, pair):
                    self._maybe_open(pair, now)

        # Periodic gate summary every 100 bars.
        total_checks = self.gate.get("checks", 0)
        if total_checks > 0 and total_checks % 100 == 0:
            placed = total_checks - self.gate.get("low_conviction", 0)
            log.info("Gate summary: %d checks / %d trades  equity=%.2f ZAR",
                     total_checks, len(self.trades), self.equity)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    login    = os.environ.get("MT5_LOGIN")
    password = os.environ.get("MT5_PASSWORD")
    server   = os.environ.get("MT5_SERVER")
    path     = os.environ.get("MT5_TERMINAL_PATH")

    log.info("Connecting to MT5…")
    ok = mt.connect(
        login=int(login) if login else None,
        password=password, server=server, terminal_path=path,
    )
    if not ok:
        log.error("MT5 connect failed — check terminal is running + credentials")
        return 1

    log.info("Resolving symbols…")
    resolved = mt.resolve_all()
    missing = [b for b in mt.ALL_SYMBOLS if b not in resolved]
    if missing:
        log.warning("Symbols not available on this account: %s", ", ".join(missing))

    trader = LiveTrader()
    trader.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())

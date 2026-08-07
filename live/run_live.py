r"""Phase 2 live strategy loop — drives backtest signal logic on live MT5 bars.

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
from ict import market_structure as mstruct
from ict.killzones import can_open_new_trade
from news_filter import NewsCalendar
from risk import pip_size
from trade_log import TradeLog
import live.mt5_connector as mt
from live.session_inputs import SessionInputs
from live import telegram_control

def _notify(msg):
    """Broadcast an alert to every authorised Telegram user (owner + admins +
    viewers) via the trading bot's token."""
    try:
        return telegram_control.broadcast(msg)
    except Exception:
        return False

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

        # Semi-auto manual overrides (Telegram). Per-day, per-pair: base lot,
        # direction filter, buy/sell-side levels for full manual AMD.
        self.inputs = SessionInputs()
        self._current_pair = None       # set before super()._maybe_open so
        self._templated = set()         # _pyramid_lots knows which pair it sizes
        self._manual_halt = False       # /halt: pause new entries + pyramid adds

        # Circuit-breaker state
        self._consec_losses     = 0
        self._day_open_eq       = {}   # date → equity at day open
        self._drawdown_halt_until = None

        # Stale-feed guard state: True while the MT5 feed is detected frozen, so
        # the STALE / RECOVERED alerts fire once per transition (not every loop).
        self._feed_stale = False

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

    # ── Semi-auto manual overrides ───────────────────────────────────────────

    def _pyramid_lots(self):
        """Base lot for the current pair. When the trader set a day lot via
        Telegram, that becomes the 1x base — the P18/P19/P41/draw multipliers
        still stack on top of it (per the trader's 'base lot' choice)."""
        lot = self.inputs.day_lot(self._current_pair) if self._current_pair else None
        if lot:
            return (lot, lot, lot)
        return super()._pyramid_lots()

    def _levels_amd_dir(self, pair, t) -> int:
        """Full manual AMD from the trader's levels: which side was swept?

        sell-side (below) swept + price reclaimed above it → +1 (hunt LONG toward
        buy-side). buy-side (above) swept + price back below → -1 (hunt SHORT
        toward sell-side). 0 = manipulation not done yet → wait. Uses the last 12
        completed M15 bars; the most recent sweep wins if both fired.
        """
        buy  = self.inputs.buy_levels(pair)
        sell = self.inputs.sell_levels(pair)
        if not buy and not sell:
            return 0
        bars = self.bars_up_to(pair, "15T", t, max_bars=60)
        look = bars[-12:] if bars else []
        if not look:
            return 0
        price = look[-1].Close
        tol = pip_size(pair)                       # 1-pip buffer beyond the level
        sell_sweep = buy_sweep = None              # (recency_index, level)
        for i, b in enumerate(look):
            for lv in sell:
                if b.Low < lv - tol and (sell_sweep is None or i >= sell_sweep[0]):
                    sell_sweep = (i, lv)
            for lv in buy:
                if b.High > lv + tol and (buy_sweep is None or i >= buy_sweep[0]):
                    buy_sweep = (i, lv)
        sell_ok = sell_sweep is not None and price > sell_sweep[1]   # reclaimed up
        buy_ok  = buy_sweep  is not None and price < buy_sweep[1]    # reclaimed down
        if sell_ok and buy_ok:
            return 1 if sell_sweep[0] >= buy_sweep[0] else -1
        if sell_ok:
            return 1
        if buy_ok:
            return -1
        return 0

    def _handover_exempt(self, pair) -> bool:
        """Live override: the trader's /hold keeps a pair open across the session
        handover (London->NY, NY AM->PM) - it then runs on stop/target/trail only."""
        return bool(self.inputs.hold(pair))

    # ── Manual actions (Telegram /close, /halt, /resume) ─────────────────────

    def manual_close(self, pair) -> str:
        """Close every open leg on `pair` at market now (Telegram /close PAIR)."""
        if pair not in self.active:
            return f"no open {pair} position"
        self._force_close(pair, 0, datetime.now(timezone.utc), "manual_close")
        log.warning("MANUAL CLOSE %s (Telegram)", pair)
        return f"{pair}: closing all legs at market"

    def manual_close_all(self) -> int:
        """Close every open position across all pairs. Returns how many pairs."""
        pairs = list(self.active.keys())
        for p in pairs:
            self._force_close(p, 0, datetime.now(timezone.utc), "manual_close")
        if pairs:
            log.warning("MANUAL CLOSE ALL %s (Telegram)", ", ".join(pairs))
        return len(pairs)

    def manual_halt(self) -> None:
        """Pause all new risk (entries + pyramid adds). Open trades keep running."""
        self._manual_halt = True
        log.warning("MANUAL HALT (Telegram) — no new entries/adds until /resume")

    def manual_resume(self) -> None:
        self._manual_halt = False
        log.info("Manual halt cleared (Telegram) — entries re-enabled")

    # ── Telegram read / query commands (read-only; never raise) ──────────────

    @staticmethod
    def _dir_word(d) -> str:
        return "bullish" if d > 0 else ("bearish" if d < 0 else "flat")

    def read_dxy_value(self):
        """Synthetic DXY from live constituent ticks (same math as the smoke test)."""
        try:
            from ict.dxy_synthetic import compute_dxy
            prices = {}
            for base in mt.DXY_CONSTITUENTS:
                q = mt.tick(base)
                if q:
                    prices[base] = (q[0] + q[1]) / 2.0
            return compute_dxy(prices)
        except Exception:
            return None

    def _pair_structure(self, pair):
        """Per-TF fractal structure + the intact ITH/ITL draws for one pair."""
        now = datetime.now(timezone.utc)
        q = mt.tick(pair)
        out = {"price": round((q[0] + q[1]) / 2, 5) if q else None}
        for tf, lbl in (("240T", "H4"), ("60T", "H1"), ("15T", "M15")):
            try:
                res = mstruct.classify(self.bars_up_to(pair, tf, now, max_bars=200))
                ith = mstruct.last_intact(res, "ITH")
                itl = mstruct.last_intact(res, "ITL")
                out[lbl] = {
                    "dir": mstruct.structure_direction(res),
                    "ith": round(ith.price, 5) if ith else None,
                    "itl": round(itl.price, 5) if itl else None,
                }
            except Exception:
                out[lbl] = {"dir": 0, "ith": None, "itl": None}
        return out

    def _plan_str(self, pair) -> str:
        bits = []
        if self.inputs.day_lot(pair) is not None:
            bits.append(f"lot {self.inputs.day_lot(pair):.2f}")
        if self.inputs.bias(pair):
            bits.append(f"{self.inputs.bias(pair)} only")
        if self.inputs.hold(pair):
            bits.append("HOLD")
        if self.inputs.has_levels(pair):
            bits.append("levels set")
        return ", ".join(bits) if bits else "auto"

    def read_structure(self, pair=None) -> str:
        """The market-structure read template (one pair, or all when pair=None)."""
        now = datetime.now(timezone.utc)
        sess = self._current_session(now) or "outside killzone"
        dxy = self.read_dxy_value()
        pairs = [pair] if pair else list(config.PAIRS)
        lines = [f"MARKET READ - {now:%H:%M} UTC",
                 f"Session: {sess}",
                 (f"DXY: {dxy:.2f}" if dxy else "DXY: n/a"), ""]
        for p in pairs:
            s = self._pair_structure(p)
            h4 = s.get("H4", {})
            lines.append(f"{p}  {s.get('price', '?')}")
            lines.append(f"  H4 {self._dir_word(h4.get('dir', 0))} | "
                         f"H1 {self._dir_word(s.get('H1', {}).get('dir', 0))} | "
                         f"M15 {self._dir_word(s.get('M15', {}).get('dir', 0))}")
            lines.append(f"  buy-side draw (ITH): {h4.get('ith') or '-'}")
            lines.append(f"  sell-side draw (ITL): {h4.get('itl') or '-'}")
            lines.append(f"  your plan: {self._plan_str(p)}")
            lines.append("")
        return "\n".join(lines).strip()

    def read_positions(self) -> str:
        if not self.active:
            return "No open positions."
        lines = ["OPEN POSITIONS"]
        for p, st in self.active.items():
            q = mt.tick(p)
            price = (q[0] + q[1]) / 2 if q else None
            pip = pip_size(p)
            d = st["direction"]
            leg = st["legs"][0]
            lines.append(f"{p} {'LONG' if d > 0 else 'SHORT'}  x{len(st['legs'])} leg(s)")
            lines.append(f"  entry {leg['entry']:.5f} | stop {leg['stop']:.5f} | tgt {st['target']:.5f}")
            if price is not None:
                lines.append(f"  now {price:.5f}  ({(price - leg['entry']) * d / pip:+.1f} pips)")
            lines.append(f"  {st.get('entry_model', '?')} | {st.get('im_scenario', '?')}")
        return "\n".join(lines)

    def read_account(self) -> str:
        self._update_equity()
        day = datetime.now(timezone.utc).date()
        dopen = self._day_open_eq.get(day, self.equity)
        dpl = self.equity - dopen
        dd = ((self._peak_equity - self.equity) / self._peak_equity * 100) if self._peak_equity else 0.0
        return ("ACCOUNT\n"
                f"equity: R{self.equity:,.2f}\n"
                f"day open: R{dopen:,.2f}  (P&L R{dpl:+,.2f})\n"
                f"peak: R{self._peak_equity:,.2f}  (drawdown {dd:.1f}%)\n"
                f"open positions: {len(self.active)}\n"
                f"consecutive losses: {self._consec_losses}\n"
                f"trading: {'HALTED — /resume' if self._manual_halt else 'active'}")

    def read_session(self) -> str:
        now = datetime.now(timezone.utc)
        sess = self._current_session(now)
        return ("SESSION\n"
                f"now: {now:%H:%M} UTC ({now:%a})\n"
                f"session: {sess or 'outside killzone'}\n"
                f"new entries allowed: {'yes' if can_open_new_trade(now) else 'no'}")

    def read_news(self) -> str:
        try:
            now = datetime.now(timezone.utc)
            evs = sorted((e for e in getattr(self.news, "events", []) if e[0] >= now),
                         key=lambda e: e[0])[:6]
            if not evs:
                return "No upcoming news events in the calendar."
            lines = ["UPCOMING NEWS (UTC)"]
            for dt, ccy, impact, name in evs:
                lines.append(f"{dt:%m-%d %H:%M} {ccy} [{impact}] {name}")
            return "\n".join(lines)
        except Exception as exc:  # noqa: BLE001
            return f"news unavailable: {exc}"

    def read_brief(self, header=None) -> str:
        """Full session brief: account line + per-pair structure + open positions
        + a command hint. Used on demand (/brief) and as the session template."""
        now = datetime.now(timezone.utc)
        self._update_equity()
        dopen = self._day_open_eq.get(now.date(), self.equity)
        dxy = self.read_dxy_value()
        sess = self._current_session(now) or "outside killzone"

        def w(x):
            return {1: "bull", -1: "bear", 0: "flat"}[x.get("dir", 0)]

        lines = [header or f"BRIEF - {now:%Y-%m-%d %H:%M} UTC",
                 f"Equity R{self.equity:,.0f} | day P&L R{self.equity - dopen:+,.0f} | "
                 f"{len(self.active)} open | {sess}",
                 (f"DXY {dxy:.2f}" if dxy else "DXY n/a"), ""]
        for p in config.PAIRS:
            s = self._pair_structure(p)
            h4 = s.get("H4", {})
            lines.append(
                f"{p} {s.get('price', '?')} | H4 {w(h4)} H1 {w(s.get('H1', {}))} "
                f"M15 {w(s.get('M15', {}))} | ITH {h4.get('ith') or '-'} "
                f"ITL {h4.get('itl') or '-'} | {self._plan_str(p)}")
        if self.active:
            lines += ["", self.read_positions()]
        lines += ["", "Reply — read: /read /positions /account /news | "
                  "plan: /lot /bias /levels /hold | act: /close /halt | /help"]
        return "\n".join(lines)

    def _direction_allowed(self, pair, direction, t) -> bool:
        """Live override of the backtest hook: apply the Telegram filters."""
        b = self.inputs.bias(pair)
        if b == "long" and direction != 1:
            return False
        if b == "short" and direction != -1:
            return False
        if self.inputs.has_levels(pair):
            amd = self._levels_amd_dir(pair, t)
            if amd == 0:                 # neither side swept yet — wait for the sweep
                return False
            if direction != amd:         # setup fights the manual AMD
                return False
        return True

    def _apply_manual_target(self, pair, st) -> None:
        """Full manual AMD target: aim the TP at the opposite-side level (the
        distribution draw). Uses the nearest qualifying level (RR>=1 and >=
        MIN_PIPS_TARGET); leaves the engine target if none qualifies."""
        if not self.inputs.has_levels(pair):
            return
        leg = st["legs"][0]
        entry, stop, d = leg["entry"], leg["stop"], st["direction"]
        pip = pip_size(pair)
        min_dist = max(config.MIN_PIPS_TARGET * pip, abs(entry - stop))
        if d > 0:
            cands = [l for l in self.inputs.buy_levels(pair) if l - entry >= min_dist]
            tgt = min(cands) if cands else None
        else:
            cands = [l for l in self.inputs.sell_levels(pair) if entry - l >= min_dist]
            tgt = max(cands) if cands else None
        if tgt is not None and tgt != st["target"]:
            log.info("Manual-AMD target %s: %.5f → %.5f (opposite-side draw)",
                     pair, st["target"], tgt)
            st["target"] = tgt

    # ── Trade entry — wrap parent + place real MT5 order ─────────────────────

    def _maybe_open(self, pair, t):
        was_active = pair in self.active
        self._current_pair = pair            # so _pyramid_lots sizes THIS pair
        super()._maybe_open(pair, t)

        if was_active or pair not in self.active:
            return   # nothing new opened

        st  = self.active[pair]
        self._apply_manual_target(pair, st)  # full-manual-AMD TP override (if set)
        leg = st["legs"][0]
        lots = round(leg["units"] / config.LOT_UNITS, 2)
        lots = max(lots, config.MIN_LOT_SIZE)

        res = mt.market_order(
            pair, lots, st["direction"],
            sl=leg["stop"], tp=st["target"],
            comment=f"ict_{st.get('im_scenario', '')}",
        )
        if res and res["ok"]:
            ticket = res.get("ticket") or self._recover_ticket(pair)
            if not ticket:
                # Broker accepted the order but returned no id and we can't match
                # an open position — we cannot manage what we can't reference.
                # Drop our tracking (so the pair isn't frozen) and warn: there may
                # be an untracked position with a broker-side SL/TP still on it.
                log.error("Order for %s reported OK but no ticket — possible untracked position", pair)
                _notify(
                    f"⚠️ ORDER UNCERTAIN\n"
                    f"{pair} order was accepted but MT5 returned no ticket.\n"
                    f"There may be an UNTRACKED position (its SL/TP are still set) —\n"
                    f"check the terminal manually. Bot dropped it from tracking."
                )
                del self.active[pair]
                return
            leg["ticket"] = ticket
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
        if self._manual_halt:
            return                           # /halt pauses new risk (adds too)
        self._current_pair = pair            # so _pyramid_lots sizes THIS pair
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
            ticket = res.get("ticket") or self._recover_ticket(pair)
            if not ticket:
                # No ticket to manage the add by — revert the leg rather than
                # keep a phantom. Any real broker fill keeps its own SL/TP.
                log.error("Pyramid %s leg %d reported OK but no ticket — reverting leg",
                          pair, new_leg["leg_idx"])
                st["legs"].pop()
                return
            new_leg["ticket"] = ticket
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

    def _tracked_tickets(self) -> set:
        """Every broker ticket currently tracked across all active legs."""
        return {leg.get("ticket")
                for st in self.active.values()
                for leg in st["legs"]
                if leg.get("ticket")}

    def _recover_ticket(self, pair: str):
        """Best-effort recovery of a just-opened position's ticket.

        MT5's order_send can return TRADE_RETCODE_DONE while `res.order` comes
        back 0/None. Without a ticket the leg is unmanageable (can't trail,
        close, or detect broker-close) and would otherwise be kept forever as a
        phantom. Here we look for an open position on this symbol stamped with
        our magic number that we're not already tracking — very likely the fill
        we just placed. Returns its ticket, or None if none can be matched.
        """
        tracked = self._tracked_tickets()
        candidates = [p for p in (mt.positions(pair) or [])
                      if getattr(p, "magic", 0) == mt.MT5_MAGIC
                      and p.ticket not in tracked]
        if not candidates:
            return None
        # Most recently opened wins (fallback: highest ticket id).
        best = max(candidates, key=lambda p: (getattr(p, "time", 0), p.ticket))
        return best.ticket

    def _sync_closed_positions(self, now):
        """Remove legs that MT5 has already closed (SL or TP hit by broker)."""
        for pair in list(self.active.keys()):
            st = self.active[pair]
            open_tickets = {p.ticket for p in (mt.positions(pair) or [])}

            live_legs = []
            for leg in st["legs"]:
                ticket = leg.get("ticket")
                if ticket is None:
                    # Phantom leg with no broker ticket — try one last recovery,
                    # else drop it. Keeping it (the old behaviour) froze the pair
                    # forever: it never matched an open ticket AND was never
                    # counted as closed. Prevented at source in _maybe_open /
                    # _maybe_pyramid; this is the defensive backstop.
                    recovered = self._recover_ticket(pair)
                    if recovered:
                        leg["ticket"] = recovered
                        live_legs.append(leg)
                        log.info("Recovered phantom %s leg → ticket %s", pair, recovered)
                    else:
                        log.warning("Dropping phantom %s leg (no ticket, unrecoverable)", pair)
                    continue
                if ticket in open_tickets:
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

    # ── Stale-feed guard ──────────────────────────────────────────────────────

    @staticmethod
    def _forex_market_open(now: datetime) -> bool:
        """Rough forex market hours in UTC. Closed over the weekend gap.

        Week opens Sunday ~21:00 UTC and closes Friday ~21:00 UTC. During that
        gap bars legitimately don't advance, so the stale-feed alert is suppressed.
        """
        wd = now.weekday()          # Mon=0 … Sat=5, Sun=6
        h  = now.hour
        if wd == 5:                 # Saturday: closed all day
            return False
        if wd == 6 and h < 21:      # Sunday before 21:00 UTC: still closed
            return False
        if wd == 4 and h >= 21:     # Friday after 21:00 UTC: closed
            return False
        return True

    def _feed_fresh(self, now: datetime) -> bool:
        """Return True if the MT5 feed is live; alert + return False if stale.

        Compares the age of the latest completed EURUSD M5 bar against
        STALE_FEED_MAX_MINUTES. Alerts on Telegram once when the feed goes stale
        and once when it recovers. Suppressed entirely over the weekend gap.
        """
        if not config.STALE_FEED_GUARD_ENABLED:
            return True
        if not self._forex_market_open(now):
            self._feed_stale = False    # weekend gap — reset, no alert
            return True

        bars = mt.get_bars("EURUSD", "5T", 1)
        if not bars:
            age_min = None              # no bars at all → treat as stale
        else:
            # bar.time is the bar OPEN epoch (UTC); +300s = its close.
            last_close = bars[-1].time + 300
            age_min = (now.timestamp() - last_close) / 60.0

        stale = (age_min is None) or (age_min > config.STALE_FEED_MAX_MINUTES)

        if stale and not self._feed_stale:
            self._feed_stale = True
            detail = "no bars returned" if age_min is None else f"last bar {age_min:.0f} min old"
            log.warning("FEED STALE — %s — holding, no trades until recovery", detail)
            _notify(
                f"⚠️ FEED STALE\n"
                f"MT5 data has stopped updating ({detail}).\n"
                f"Bot is HOLDING — no new trades until the feed recovers.\n"
                f"Check the VPS terminal + broker connection."
            )
        elif not stale and self._feed_stale:
            self._feed_stale = False
            log.info("Feed recovered (last bar %.0f min old) — resuming", age_min or 0)
            _notify(
                "✅ FEED RECOVERED\n"
                "MT5 data is flowing again. Bot resuming normal operation."
            )
        return not stale

    @staticmethod
    def _current_session(now: datetime):
        """Which session are we in, by New York time? (mirrors the engine's
        _is_london / _is_ny / _is_pm windows). Returns london / ny / ny_pm / None."""
        import pytz
        ny = now.astimezone(pytz.timezone("America/New_York"))
        h = ny.hour
        if 2 <= h < 5:
            return "london"
        if 7 <= h < 10:
            return "ny"
        if config.NY_PM_ENABLED and 13 <= h < 16:
            return "ny_pm"
        return None

    def _session_template(self, day_key, sess) -> str:
        """Start-of-session brief, fired at the top of each session (London / NY
        AM / NY PM): account + per-pair structure + open positions + commands."""
        head = {"london": "LONDON", "ny": "NEW YORK AM", "ny_pm": "NEW YORK PM"}.get(
            sess, str(sess).upper())
        return self.read_brief(header=f"{head} SESSION START - {day_key}")

    # ── Main loop ─────────────────────────────────────────────────────────────

    def run(self):
        """Block until interrupted: wake on each M5 bar close, run strategy."""
        log.info("=" * 60)
        log.info("ICT live loop started — pairs: %s", ", ".join(config.PAIRS))
        log.info("Account: %.2f ZAR  leverage 1:%s", self.equity,
                 mt.account().leverage if mt.account() else "?")
        log.info("DEMO mode until smoke test confirmed — see LIVE_SETUP.md")
        log.info("=" * 60)

        _feed_timeout = (config.STALE_FEED_MAX_MINUTES * 60
                         if config.STALE_FEED_GUARD_ENABLED else None)
        while True:
            try:
                # Timeout so a frozen feed wakes us to run the stale check instead
                # of blocking forever inside wait_for_bar.
                mt.wait_for_bar("5T", timeout_seconds=_feed_timeout)
                now = datetime.now(timezone.utc)
                if not self._feed_fresh(now):
                    continue   # feed stale — alerted, skip this cycle (no trading)
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

        # Semi-auto: pull any new Telegram commands (lot / bias / levels / hold /
        # close / halt). Passing self enables the action commands. poll() never
        # raises, so a Telegram hiccup can't interrupt trading.
        telegram_control.poll(self.inputs, trader=self)

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

        # Session-start template: fire once at the start of EACH session
        # (London / NY AM / NY PM), prompting the trader for that session's plan.
        sess = self._current_session(now)
        if sess and (day_key, sess) not in self._templated:
            self._templated.add((day_key, sess))
            _notify(self._session_template(day_key, sess))

        # New entry checks for each tradeable pair (skipped entirely while halted).
        if not self._manual_halt:
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

"""Semi-auto session inputs for the live engine.

Holds the trader's per-day manual overrides (set via Telegram — see
live/telegram_control.py):

  - day lot per pair          → base lot; the sizing multipliers still stack on it
  - direction bias per pair   → "long" | "short"  (filter: bot still needs its setup)
  - buy-side / sell-side liquidity levels per pair → full manual AMD
    (sweep one side = manipulation, target the other = distribution)

Persisted to data/session_inputs.json, scoped to a single UTC trading day. On a
new day the store auto-expires so yesterday's levels never leak into today.

This module is pure state — no MT5, no network — so it is unit-testable offline.
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone

_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "session_inputs.json",
)
_LOCK = threading.Lock()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


class SessionInputs:
    """Per-day, per-pair manual overrides. Thread-safe writes; auto-expiring."""

    def __init__(self, path: str = _PATH):
        self._path = path
        self._day = _today()
        self._pairs: dict[str, dict] = {}   # pair -> {lot, bias, buy, sell}
        self.load()

    # ── persistence ──────────────────────────────────────────────────────────

    def load(self) -> None:
        try:
            with open(self._path) as f:
                d = json.load(f)
            if d.get("day") == _today():
                self._day = d["day"]
                self._pairs = d.get("pairs", {}) or {}
                return
        except (FileNotFoundError, ValueError, KeyError, TypeError):
            pass
        self._day = _today()
        self._pairs = {}

    def save(self) -> None:
        with _LOCK:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w") as f:
                json.dump({"day": self._day, "pairs": self._pairs}, f, indent=2)
            os.replace(tmp, self._path)

    def _rollover(self) -> None:
        """Wipe inputs at the UTC day boundary so stale levels never carry over."""
        if self._day != _today():
            self._day = _today()
            self._pairs = {}
            self.save()

    def _p(self, pair: str) -> dict:
        return self._pairs.setdefault(pair, {})

    # ── setters (each returns a human ack string for Telegram) ────────────────

    def set_lot(self, pair: str, lot: float) -> str:
        self._rollover()
        self._p(pair)["lot"] = float(lot)
        self.save()
        return f"{pair}: day lot {float(lot):.2f} (base — sizing multipliers still stack)"

    def set_bias(self, pair: str, bias: str) -> str:
        self._rollover()
        bias = bias.lower()
        if bias in ("off", "auto", "both"):
            self._p(pair).pop("bias", None)
            self.save()
            return f"{pair}: direction filter cleared (auto — both directions)"
        if bias not in ("long", "short"):
            return f"bad direction '{bias}' — use long | short | both"
        self._p(pair)["bias"] = bias
        self.save()
        return f"{pair}: hunting {bias.upper()}S only (bot still needs its own setup)"

    def set_mm(self, pair: str, model: str, auto: bool = False) -> str:
        self._rollover()
        model = model.lower()
        if model in ("off", "none", "clear"):
            self._p(pair).pop("mm", None)
            self._p(pair).pop("mm_auto", None)
            self.save()
            return f"{pair}: Market Maker model OFF"
        if model in ("buy", "sell"):
            self._p(pair)["mm"] = model
            self._p(pair)["mm_auto"] = bool(auto)
            self.save()
            if auto:
                return (f"{pair}: Market Maker {model.upper()} model — AUTO-HUNT ARMED.\n"
                        f"It hunts {model} entries on the M30→M1 IFVG cascade (PD array "
                        f"inside the gap + internal AMD + structure), stop beyond the "
                        f"internal manipulation, targeting liquidity. PERSISTENT — takes "
                        f"the first entry then adds down the distribution, and re-enters "
                        f"after a close. Bypasses the autonomous gates (you gave the bias). "
                        f"/mm {pair} off to stop.")
            return (f"{pair}: Market Maker {model.upper()} model — WATCH (alerts only, "
                    f"with SMT read). Add 'auto' to let it hunt+execute: /mm {pair} {model} auto")
        return "usage: /mm EURUSD buy|sell [auto] | off"

    def mm(self, pair: str):
        self._rollover()
        return self._pairs.get(pair, {}).get("mm")

    def mm_auto(self, pair: str) -> bool:
        self._rollover()
        return bool(self._pairs.get(pair, {}).get("mm_auto"))

    def clear_mm_auto(self, pair: str) -> None:
        """Consume the one-shot auto-entry permission (leaves watch on)."""
        self._rollover()
        self._pairs.get(pair, {}).pop("mm_auto", None)
        self.save()

    _TRAIL_TF = {"m15": "15T", "15": "15T", "15m": "15T",
                 "m5": "5T", "5": "5T", "5m": "5T",
                 "m1": "1T", "1": "1T", "1m": "1T"}
    _TRAIL_TF_LBL = {"15T": "M15", "5T": "M5", "1T": "M1"}

    def set_trail(self, pair: str, tf: str, tier: str | None = None,
                  buf: str | float | None = None) -> str:
        """Structure trail: follow the latest intact swing on M15/M5/M1
        (short-term STH/STL or intermediate ITH/ITL) with a pip buffer."""
        self._rollover()
        tf = (tf or "").lower()
        if tf in ("off", "none", "clear"):
            self._p(pair).pop("trail", None)
            self.save()
            return f"{pair}: structure trail OFF"
        if tf not in self._TRAIL_TF:
            return "usage: /trail EURUSD m15|m5|m1 st|it [pips] | off"
        tier = (tier or "st").lower()
        if tier in ("st", "sth", "stl", "short", "s"):
            tier_k = "st"
        elif tier in ("it", "ith", "itl", "inter", "i"):
            tier_k = "it"
        else:
            return "tier must be st (STH/STL) or it (ITH/ITL)"
        try:
            b = float(buf) if buf is not None else 2.0
        except (TypeError, ValueError):
            return f"bad buffer '{buf}' — use a pip number, e.g. 3"
        if b < 0:
            return "buffer must be >= 0 pips"
        self._p(pair)["trail"] = {"tf": self._TRAIL_TF[tf], "tier": tier_k, "buf": b}
        self.save()
        tfl = self._TRAIL_TF_LBL[self._TRAIL_TF[tf]]
        tl = "ITH/ITL" if tier_k == "it" else "STH/STL"
        return (f"{pair}: structure trail ON — {tfl} {tl}, {b:g}-pip buffer.\n"
                f"Stop follows the latest intact swing (up for longs / down for "
                f"shorts) and only ever tightens. /trail {pair} off to stop.")

    def trail(self, pair: str):
        self._rollover()
        return self._pairs.get(pair, {}).get("trail")

    def set_hold(self, pair: str, on: bool = True) -> str:
        self._rollover()
        if on:
            self._p(pair)["hold"] = True
            self.save()
            return (f"{pair}: HOLD on — trade runs across the session handover "
                    f"(London→NY, NY AM→PM); managed by stop/target/trail only")
        self._p(pair).pop("hold", None)
        self.save()
        return f"{pair}: hold off — normal session-handover management"

    def set_levels(self, pair: str, buy: list | None, sell: list | None) -> str:
        self._rollover()
        p = self._p(pair)
        if buy is not None:
            p["buy"] = sorted(float(x) for x in buy)
        if sell is not None:
            p["sell"] = sorted(float(x) for x in sell)
        self.save()
        return (f"{pair}: buy-side {p.get('buy', [])} | sell-side {p.get('sell', [])}\n"
                f"(full manual AMD — sweep one side, target the other)")

    def clear(self, pair: str | None = None) -> str:
        self._rollover()
        if pair:
            self._pairs.pop(pair, None)
            msg = f"{pair}: back to full auto"
        else:
            self._pairs = {}
            msg = "all pairs back to full auto"
        self.save()
        return msg

    # ── getters ──────────────────────────────────────────────────────────────

    def day_lot(self, pair: str):
        self._rollover()
        return self._pairs.get(pair, {}).get("lot")

    def bias(self, pair: str):
        self._rollover()
        return self._pairs.get(pair, {}).get("bias")

    def buy_levels(self, pair: str) -> list:
        self._rollover()
        return self._pairs.get(pair, {}).get("buy", [])

    def sell_levels(self, pair: str) -> list:
        self._rollover()
        return self._pairs.get(pair, {}).get("sell", [])

    def hold(self, pair: str) -> bool:
        self._rollover()
        return bool(self._pairs.get(pair, {}).get("hold"))

    def has_levels(self, pair: str) -> bool:
        return bool(self.buy_levels(pair) or self.sell_levels(pair))

    def status_text(self) -> str:
        self._rollover()
        if not self._pairs:
            return "Semi-auto: none set — full auto on all pairs."
        lines = [f"Semi-auto inputs — {self._day} (UTC):"]
        for pair, d in self._pairs.items():
            bits = []
            if d.get("lot") is not None:
                bits.append(f"lot {d['lot']:.2f}")
            if d.get("bias"):
                bits.append(f"{d['bias']} only")
            if d.get("buy"):
                bits.append(f"buy {d['buy']}")
            if d.get("sell"):
                bits.append(f"sell {d['sell']}")
            if d.get("hold"):
                bits.append("HOLD across sessions")
            if d.get("trail"):
                tr = d["trail"]
                _tfl = self._TRAIL_TF_LBL.get(tr.get("tf"), tr.get("tf"))
                _tl = "ITH/ITL" if tr.get("tier") == "it" else "STH/STL"
                bits.append(f"trail {_tfl} {_tl} {tr.get('buf'):g}p")
            if d.get("mm"):
                bits.append(f"MM {d['mm']} {'AUTO' if d.get('mm_auto') else 'watch'}")
            lines.append(f"  {pair}: {', '.join(bits) if bits else 'auto'}")
        return "\n".join(lines)

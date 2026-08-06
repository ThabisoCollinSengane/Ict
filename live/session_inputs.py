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
            lines.append(f"  {pair}: {', '.join(bits) if bits else 'auto'}")
        return "\n".join(lines)

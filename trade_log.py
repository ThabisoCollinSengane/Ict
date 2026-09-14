"""Persistent trade log using SQLite.

Works standalone (no QuantConnect dependencies).  Call write_trade() on every
leg close; call read_open_positions() on startup to recover state after a restart.

Schema:
  trades          — closed leg records (immutable after write)
  open_positions  — live state snapshot, upserted on every change, deleted on close
"""

import sqlite3
import json
import os
from datetime import datetime

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "data", "trade_log.db")


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS trades (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            logged_at   TEXT NOT NULL,
            pair        TEXT NOT NULL,
            leg_idx     INTEGER,
            direction   INTEGER,
            entry       REAL,
            exit        REAL,
            units       REAL,
            pnl         REAL,
            opened_at   TEXT,
            closed_at   TEXT,
            reason      TEXT,
            entry_type  TEXT,
            session_side TEXT,
            equity_after REAL
        );

        CREATE TABLE IF NOT EXISTS open_positions (
            pair        TEXT PRIMARY KEY,
            snapshot    TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_trades_pair ON trades(pair);
        CREATE INDEX IF NOT EXISTS idx_trades_closed ON trades(closed_at);
    """)
    conn.commit()


class TradeLog:
    """Thread-safe trade logger backed by SQLite."""

    def __init__(self, db_path: str = _DEFAULT_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path

    def write_trade(self, trade: dict, equity_after: float = None):
        """Append a closed leg record.  `trade` must have the same keys as
        backtester.trades entries (pair, leg_idx, direction, entry, exit,
        units, pnl, opened_at, closed_at, reason, entry_type, session_side).
        """
        now = datetime.utcnow().isoformat(timespec="seconds")
        with _connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO trades
                    (logged_at, pair, leg_idx, direction, entry, exit, units,
                     pnl, opened_at, closed_at, reason, entry_type, session_side,
                     equity_after)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                now,
                trade.get("pair"),
                trade.get("leg_idx"),
                trade.get("direction"),
                trade.get("entry"),
                trade.get("exit"),
                trade.get("units"),
                trade.get("pnl"),
                str(trade.get("opened_at", "")),
                str(trade.get("closed_at", "")),
                trade.get("reason"),
                trade.get("entry_type"),
                trade.get("session_side"),
                equity_after,
            ))

    def upsert_position(self, pair: str, state: dict):
        """Snapshot current open position state for recovery after restart."""
        now = datetime.utcnow().isoformat(timespec="seconds")
        with _connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO open_positions (pair, snapshot, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(pair) DO UPDATE SET
                    snapshot   = excluded.snapshot,
                    updated_at = excluded.updated_at
            """, (pair, json.dumps(state, default=str), now))

    def delete_position(self, pair: str):
        """Remove position snapshot when trade is fully closed."""
        with _connect(self.db_path) as conn:
            conn.execute("DELETE FROM open_positions WHERE pair = ?", (pair,))

    def read_open_positions(self) -> dict:
        """Return {pair: state_dict} for all positions that were open at last
        snapshot.  Used to restore state after an algorithm restart.
        """
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT pair, snapshot FROM open_positions"
            ).fetchall()
        return {row["pair"]: json.loads(row["snapshot"]) for row in rows}

    def recent_trades(self, n: int = 50) -> list[dict]:
        """Return the N most recent closed leg records as dicts."""
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT * FROM trades ORDER BY id DESC LIMIT ?", (n,)
            ).fetchall()
        return [dict(r) for r in rows]

    def equity_curve(self) -> list[tuple]:
        """Return [(closed_at, equity_after)] for equity curve plotting."""
        with _connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT closed_at, equity_after FROM trades "
                "WHERE equity_after IS NOT NULL ORDER BY id"
            ).fetchall()
        return [(r["closed_at"], r["equity_after"]) for r in rows]

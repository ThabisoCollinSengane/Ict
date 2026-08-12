"""Live trading runtime for Exness via the MetaTrader5 Python package.

This package is the EXECUTION layer only — the strategy logic lives in backtest.py
(reference) and the ict/ pure-logic modules. main.py is the QuantConnect LEAN port.

Modules:
    mt5_connector  — broker layer: connect/login, symbol resolution, bar fetch,
                     account info, order place/modify/close. No strategy logic.
    smoke_test     — demo-account connectivity check (zero strategy risk).
    run_live       — (next phase) the live loop that drives the strategy.
"""

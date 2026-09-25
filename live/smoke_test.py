"""Connectivity smoke test — run this FIRST on the VPS, on a DEMO account.

It proves the whole broker layer works end-to-end WITHOUT placing any real trade:
  1. connects to MT5 / Exness
  2. prints the account (balance, equity, currency, leverage)
  3. resolves every symbol the strategy needs (catches missing instruments + suffixes)
  4. pulls a few bars on each timeframe and prints the latest close
  5. prints a live bid/ask tick
  6. computes synthetic DXY from live constituent prices (sanity ≈ 90–115)

Credentials come from environment variables (preferred) or are passed inline:
    set MT5_LOGIN=12345678
    set MT5_PASSWORD=yourpassword
    set MT5_SERVER=Exness-MT5Trial14
    python -m live.smoke_test

If you've already logged in inside the MT5 terminal GUI, you can run it with no
env vars at all — it will attach to the signed-in account.
"""

import logging
import os
import sys

import live.mt5_connector as mt
from ict.dxy_synthetic import compute_dxy

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("smoke")

TFS = ("1T", "5T", "15T", "60T", "240T", "D", "W")


def main() -> int:
    login = os.environ.get("MT5_LOGIN")
    password = os.environ.get("MT5_PASSWORD")
    server = os.environ.get("MT5_SERVER")
    path = os.environ.get("MT5_TERMINAL_PATH")  # optional

    ok = mt.connect(login=int(login) if login else None,
                    password=password, server=server, terminal_path=path)
    if not ok:
        log.error("CONNECT FAILED — check terminal is running, creds, and server name.")
        return 1

    acc = mt.account()
    print("\n=== ACCOUNT ===")
    print(f"  login    {acc.login}")
    print(f"  server   {acc.server}")
    print(f"  balance  {acc.balance:.2f} {acc.currency}")
    print(f"  equity   {acc.equity:.2f} {acc.currency}")
    print(f"  free     {acc.margin_free:.2f} {acc.currency}")
    print(f"  leverage 1:{acc.leverage}")
    if acc.currency != "ZAR":
        print("  NOTE: account currency is not ZAR — sizing assumes USD_ZAR conversion; "
              "review config before live.")

    print("\n=== SYMBOL RESOLUTION ===")
    resolved = mt.resolve_all()
    for base in mt.ALL_SYMBOLS:
        print(f"  {base:8s} → {resolved.get(base, '*** MISSING ***')}")

    print("\n=== BARS (latest close per timeframe, EURUSD) ===")
    for tf in TFS:
        bars = mt.get_bars("EURUSD", tf, 5)
        if bars:
            print(f"  {tf:5s} {len(bars)} bars  last close {bars[-1].close:.5f}")
        else:
            print(f"  {tf:5s} *** no bars ***")

    print("\n=== LIVE TICK ===")
    for base in mt.TRADEABLE:
        q = mt.tick(base)
        print(f"  {base}: {q}" if q else f"  {base}: *** no tick ***")

    print("\n=== SYNTHETIC DXY (from live constituents) ===")
    prices = {}
    for base in mt.DXY_CONSTITUENTS:
        q = mt.tick(base)
        if q:
            prices[base] = (q[0] + q[1]) / 2.0
    dxy = compute_dxy(prices)
    if dxy:
        sane = "ok" if 80 <= dxy <= 120 else "*** out of expected range ***"
        print(f"  DXY ≈ {dxy:.3f}  ({sane})")
    else:
        print("  could not compute — missing a constituent (see resolution above)")

    print("\nSMOKE TEST COMPLETE — no orders were placed.")
    mt.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())

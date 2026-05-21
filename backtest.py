"""Pandas-based backtester for the ICT intermarket strategy.

Fetches free 5-minute forex data from Yahoo Finance for the last ~60 days,
runs the strategy through the same `ict/` modules used by the QC version,
and reports trades + summary stats. No QuantConnect dependency.

Usage:  python backtest.py
"""

import sys
from collections import namedtuple
from datetime import timedelta

import pandas as pd
import yfinance as yf

import config
from ict.killzones import can_open_new_trade
from ict.fvg import detect_new_fvg, nearest_unmitigated
from ict.order_block import detect_order_blocks, nearest_unmitigated_ob
from ict.liquidity import find_equal_highs, find_equal_lows
from ict.bias import htf_bias
from ict.dxy_synthetic import compute_dxy, compute_dxy_range
from ict.amd import detect_consolidation, detect_manipulation
from intermarket import resolve as resolve_intermarket
from news_filter import NewsCalendar
from risk import position_size, pip_size


YF_TICKERS = {
    "GBPUSD": "GBPUSD=X",
    "EURUSD": "EURUSD=X",
    "EURGBP": "EURGBP=X",
    "USDJPY": "USDJPY=X",
    "USDCAD": "USDCAD=X",
    "USDSEK": "USDSEK=X",
    "USDCHF": "USDCHF=X",
}

Bar = namedtuple("Bar", "Open High Low Close")
SynBar = namedtuple("SynBar", "Open High Low Close")


def fetch_data(period="60d", interval="5m"):
    out = {}
    for name, ticker in YF_TICKERS.items():
        df = yf.download(ticker, period=period, interval=interval,
                         progress=False, auto_adjust=False)
        if df is None or df.empty:
            print(f"  WARN: no data for {name} ({ticker})")
            continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close"]].dropna()
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        else:
            df.index = df.index.tz_convert("UTC")
        out[name] = df
        print(f"  {name}: {len(df)} bars, {df.index.min()} -> {df.index.max()}")
    return out


def resample(df_5m, rule):
    return df_5m.resample(rule).agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
    }).dropna()


def df_to_bars(df):
    return [Bar(r.Open, r.High, r.Low, r.Close) for r in df.itertuples(index=False)]


class Backtester:
    def __init__(self, data_5m):
        self.data_5m = data_5m
        self.tf_dfs = {}
        self.tf_bars = {}     # pre-built list[Bar] for fast slicing
        self.tf_index = {}    # pandas DatetimeIndex per (sym, tf) for searchsorted
        self.tf_pos = {}      # (sym, tf) -> dict[timestamp] -> position (for _bar_at)
        for sym, df in data_5m.items():
            for tf_name, rule in [("5T", None), ("15T", "15min"), ("60T", "60min"),
                                   ("240T", "240min"), ("D", "1D"), ("W", "1W")]:
                d = df if rule is None else resample(df, rule)
                self.tf_dfs[(sym, tf_name)] = d
                self.tf_bars[(sym, tf_name)] = df_to_bars(d)
                self.tf_index[(sym, tf_name)] = d.index

        self.equity = config.STARTING_CASH
        self.start_equity = self.equity
        self.active = {}
        self.pending = {}
        self.trades = []

        self.news = NewsCalendar()
        for path in ("data/news_events.csv", "./data/news_events.csv"):
            try:
                with open(path, "r") as f:
                    n = self.news.load_csv(f.read())
                    print(f"  News CSV: {n} events loaded from {path}")
                    break
            except Exception:
                continue
        else:
            print("  News CSV: not found (skipping news filter)")

    def bars_up_to(self, sym, tf, t):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return []
        pos = idx.searchsorted(t, side="right")
        if pos == 0:
            return []
        return self.tf_bars[(sym, tf)][:pos]

    def _bar_at(self, sym, tf, t):
        idx = self.tf_index.get((sym, tf))
        if idx is None:
            return None
        try:
            pos = idx.get_loc(t)
        except KeyError:
            return None
        return self.tf_bars[(sym, tf)][pos]

    def run(self):
        if "GBPUSD" not in self.data_5m:
            raise SystemExit("GBPUSD data missing")
        timestamps = self.data_5m["GBPUSD"].index

        warmup_end = timestamps[0] + pd.Timedelta(days=5)
        total = len(timestamps)
        print(f"  Iterating {total} 5-min bars...")

        for i, t in enumerate(timestamps):
            for pair in config.PAIRS:
                self._update_orders(pair, t)
            if t < warmup_end:
                continue

            # Cheap killzone gate: skip heavy entry logic if not in any killzone.
            now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
            in_kz = can_open_new_trade(now)
            for pair in config.PAIRS:
                if pair in self.active:
                    self._maybe_pyramid(pair, t)
                elif in_kz and pair not in self.pending:
                    self._maybe_open(pair, t)

            if i % 1000 == 0 and i > 0:
                print(f"    bar {i}/{total} ({t}) - active={len(self.active)} "
                      f"pending={len(self.pending)} trades={len(self.trades)} "
                      f"equity={self.equity:.0f}")

        # Close any remaining positions at last available 5m close.
        last_t = timestamps[-1]
        for pair in list(self.active.keys()):
            last_close = self.data_5m[pair].iloc[-1].Close
            self._force_close(pair, last_close, last_t, "end_of_data")

    def _update_orders(self, pair, t):
        bar = self._bar_at(pair, "5T", t)
        if bar is None:
            return

        # Position exits.
        if pair in self.active:
            st = self.active[pair]
            direction = st["direction"]
            target = st["target"]
            for leg in list(st["legs"]):
                sl = leg["stop"]
                if direction > 0:
                    sl_hit = bar.Low <= sl
                    tp_hit = bar.High >= target
                else:
                    sl_hit = bar.High >= sl
                    tp_hit = bar.Low <= target
                if sl_hit:                       # worst-case: SL first
                    self._exit_leg(pair, leg, sl, t, "stop")
                elif tp_hit:
                    self._exit_leg(pair, leg, target, t, "target")
            if not self.active.get(pair, {}).get("legs"):
                self.active.pop(pair, None)

        # Pending limit entry fills.
        if pair in self.pending:
            pe = self.pending[pair]
            entry = pe["entry_price"]
            direction = pe["direction"]
            filled = (direction > 0 and bar.Low <= entry) or \
                     (direction < 0 and bar.High >= entry)
            age_min = (t - pe["placed_at"]).total_seconds() / 60.0
            if filled:
                self._fill_entry(pair, t)
            elif age_min > 25:               # cancel stale limit after 5 bars
                self.pending.pop(pair, None)

    def _fill_entry(self, pair, t):
        pe = self.pending.pop(pair)
        leg = {
            "entry": pe["entry_price"], "stop": pe["stop"],
            "units": pe["units"], "leg_idx": pe["leg_idx"], "opened_at": t,
        }
        if pair not in self.active:
            self.active[pair] = {
                "direction": pe["direction"],
                "target": pe["target"],
                "legs": [leg],
            }
        else:
            # Pyramid: promote prior leg to BE.
            prior = self.active[pair]["legs"][-1]
            prior["stop"] = prior["entry"]
            self.active[pair]["legs"].append(leg)

    def _exit_leg(self, pair, leg, exit_price, t, reason):
        st = self.active[pair]
        direction = st["direction"]
        pnl = (exit_price - leg["entry"]) * leg["units"] * direction
        self.equity += pnl
        self.trades.append({
            "pair": pair, "leg_idx": leg["leg_idx"], "direction": direction,
            "entry": leg["entry"], "exit": exit_price, "units": leg["units"],
            "pnl": pnl, "opened_at": leg["opened_at"], "closed_at": t,
            "reason": reason,
        })
        st["legs"].remove(leg)
        if not st["legs"]:
            self.active.pop(pair, None)

    def _force_close(self, pair, price, t, reason):
        for leg in list(self.active[pair]["legs"]):
            self._exit_leg(pair, leg, price, t, reason)

    def _sym_bias(self, sym, tf, t):
        bars = self.bars_up_to(sym, tf, t)
        return htf_bias(bars)

    def _dxy_bias_1h(self, t):
        rolls = {s: self.bars_up_to(s, "60T", t) for s in config.DXY_CONSTITUENTS}
        n = min((len(v) for v in rolls.values()), default=0)
        if n < config.SWING_LOOKBACK + 2:
            return 0
        series = []
        for i in range(-n, 0):
            close_px = {s: rolls[s][i].Close for s in config.DXY_CONSTITUENTS}
            high_px = {s: rolls[s][i].High for s in config.DXY_CONSTITUENTS}
            low_px = {s: rolls[s][i].Low for s in config.DXY_CONSTITUENTS}
            open_px = {s: rolls[s][i].Open for s in config.DXY_CONSTITUENTS}
            c = compute_dxy(close_px)
            o = compute_dxy(open_px)
            h, l = compute_dxy_range(high_px, low_px)
            if None in (c, o, h, l):
                continue
            series.append(SynBar(o, h, l, c))
        if len(series) < config.SWING_LOOKBACK + 2:
            return 0
        return htf_bias(series)

    def _find_target(self, pair, direction, t, price):
        candidates = []
        for tf in ("240T", "D", "W"):
            bars = self.bars_up_to(pair, tf, t)
            if len(bars) < 5:
                continue
            candidates += self._targets_in_series(bars, pair, direction, price)
        if direction > 0:
            candidates = [c for c in candidates if c > price]
        else:
            candidates = [c for c in candidates if c < price]
        if not candidates:
            return None
        return min(candidates, key=lambda x: abs(x - price))

    @staticmethod
    def _targets_in_series(bars, pair, direction, price):
        fvgs = []
        for i in range(2, len(bars)):
            g = detect_new_fvg(bars[: i + 1], pair)
            if g is not None:
                fvgs.append(g)
        for g in fvgs:
            for c in bars[g.bar_index + 1:]:
                if g.direction > 0 and c.Low <= g.top:
                    g.mitigated = True
                    break
                if g.direction < 0 and c.High >= g.bottom:
                    g.mitigated = True
                    break
        out = []
        tgt_fvg = nearest_unmitigated(fvgs, price, direction)
        if tgt_fvg is not None:
            out.append(tgt_fvg.mid)
        tgt_ob = nearest_unmitigated_ob(detect_order_blocks(bars), price, direction)
        if tgt_ob is not None:
            out.append(tgt_ob.mid)
        if direction > 0:
            out += find_equal_highs(bars, pair, lookback=200)
        else:
            out += find_equal_lows(bars, pair, lookback=200)
        return out

    def _maybe_open(self, pair, t):
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if not can_open_new_trade(now):
            return
        if self.news.is_blocked(now):
            return

        dxy_bias = self._dxy_bias_1h(t)
        eurgbp_bias = self._sym_bias(config.REF_EURGBP, "60T", t)
        signal = resolve_intermarket(dxy_bias, eurgbp_bias)
        if signal is None or signal.pair != pair:
            return

        if self._sym_bias(pair, "60T", t) != signal.direction:
            return
        if self._sym_bias(pair, "240T", t) != signal.direction:
            return

        bars15 = self.bars_up_to(pair, "15T", t)
        rng = detect_consolidation(bars15, pair)
        if rng is None:
            return
        sweep_dir = detect_manipulation(bars15, rng)
        if sweep_dir is None or sweep_dir != signal.direction:
            return
        sweep_price = rng.low if signal.direction > 0 else rng.high

        bars5 = self.bars_up_to(pair, "5T", t)
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != signal.direction:
            return

        cur_price = bars5[-1].Close
        target = self._find_target(pair, signal.direction, t, cur_price)
        if target is None:
            return

        pip = pip_size(pair)
        entry = fvg.mid
        stop = (sweep_price - pip) if signal.direction > 0 else (sweep_price + pip)
        risk_pips = abs(entry - stop) / pip
        reward_pips = abs(target - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return
        if risk_pips <= 0 or (reward_pips / risk_pips) < config.MIN_RR:
            return

        units = int(position_size(self.equity, entry, stop, pair))
        if units == 0:
            return

        self.pending[pair] = {
            "entry_price": entry, "stop": stop, "target": target,
            "direction": signal.direction, "units": units, "leg_idx": 1,
            "placed_at": t,
        }

    def _maybe_pyramid(self, pair, t):
        st = self.active[pair]
        if len(st["legs"]) >= config.MAX_LEGS:
            return
        if pair in self.pending:
            return
        now = t.to_pydatetime() if hasattr(t, "to_pydatetime") else t
        if self.news.is_blocked(now):
            return

        bars5 = self.bars_up_to(pair, "5T", t)
        fvg = detect_new_fvg(bars5, pair)
        if fvg is None or fvg.direction != st["direction"]:
            return

        cur_price = bars5[-1].Close
        pip = pip_size(pair)
        last_entry = st["legs"][-1]["entry"]
        favour_pips = (cur_price - last_entry) * st["direction"] / pip
        if favour_pips < 10:
            return

        entry = fvg.mid
        stop = st["legs"][-1]["entry"]
        units = int(position_size(self.equity, entry, stop, pair))
        if units == 0:
            return
        reward_pips = abs(st["target"] - entry) / pip
        if reward_pips < config.MIN_PIPS_TARGET:
            return

        self.pending[pair] = {
            "entry_price": entry, "stop": stop, "target": st["target"],
            "direction": st["direction"], "units": units,
            "leg_idx": len(st["legs"]) + 1, "placed_at": t,
        }


def summarize(bt):
    n = len(bt.trades)
    if n == 0:
        return {
            "trades": 0,
            "starting_equity": bt.start_equity,
            "ending_equity": round(bt.equity, 2),
            "pnl": round(bt.equity - bt.start_equity, 2),
        }
    df = pd.DataFrame(bt.trades)
    wins = df[df.pnl > 0]
    losses = df[df.pnl <= 0]
    win_rate = len(wins) / n * 100
    gp = wins.pnl.sum()
    gl = -losses.pnl.sum()
    pf = gp / gl if gl > 0 else float("inf")
    eq = bt.start_equity + df.pnl.cumsum()
    rmax = eq.cummax()
    dd = ((eq - rmax) / rmax * 100).min() if len(eq) else 0
    return {
        "trades": n,
        "win_rate_pct": round(win_rate, 1),
        "profit_factor": "inf" if pf == float("inf") else round(pf, 2),
        "starting_equity": bt.start_equity,
        "ending_equity": round(bt.equity, 2),
        "pnl": round(bt.equity - bt.start_equity, 2),
        "pnl_pct": round((bt.equity - bt.start_equity) / bt.start_equity * 100, 2),
        "max_drawdown_pct": round(dd, 2),
        "avg_win": round(wins.pnl.mean() if len(wins) else 0, 2),
        "avg_loss": round(losses.pnl.mean() if len(losses) else 0, 2),
    }


def main():
    print("Fetching 60d of 5-min forex data from yfinance...")
    data = fetch_data()
    if "GBPUSD" not in data or "EURUSD" not in data:
        print("ERROR: primary pairs missing")
        sys.exit(1)

    print("\nRunning backtest...")
    bt = Backtester(data)
    bt.run()

    print("\n=== Results ===")
    for k, v in summarize(bt).items():
        print(f"  {k:20s} {v}")

    if bt.trades:
        print("\n=== Trades ===")
        df = pd.DataFrame(bt.trades)
        cols = ["opened_at", "closed_at", "pair", "direction", "leg_idx",
                "entry", "exit", "units", "pnl", "reason"]
        # Show all trades (likely few given strict AMD gating).
        print(df[cols].to_string(index=False))


if __name__ == "__main__":
    main()

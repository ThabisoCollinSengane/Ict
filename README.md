# ICT Intermarket Strategy

Fully-autonomous day-trading algorithm written in Python for [QuantConnect](https://www.quantconnect.com/) (LEAN engine). Trades **GBPUSD** and **EURUSD** using ICT concepts gated by intermarket analysis (synthetic DXY + EURGBP relative strength) and a ForexFactory news filter.

Designed for hands-off execution — the algorithm analyses, sizes, enters, pyramids, and exits without manual intervention. Backtest and live-trade entirely in the QC cloud; no desktop required.

---

## Strategy in one paragraph

On each 5-minute bar inside a chosen ICT killzone (London Open / NY AM / London Close), the algorithm computes the **synthetic DXY** bias and **EURGBP** bias on 1H. The intermarket table picks one pair and one direction — never both pairs at once. The pair's own 4H + 1H bias must agree. It then waits for a **15m liquidity sweep** of the prior swing, a **5m Fair Value Gap** in trade direction, and a clear **HTF target** (FVG / Order Block / equal high or low on H4, Daily, or Weekly) at least **20 pips** away. Entry is a limit at the FVG midpoint, stop beyond the sweep, target the nearest valid HTF level. Up to **3 pyramid legs** are added on subsequent continuation FVGs, each leg trailing the previous to break-even. **High and medium impact USD/EUR/GBP news** within ±15 min blocks all new entries.

---

## Repo layout

```
.
├── main.py               QCAlgorithm entry — wires bars, drives entry/pyramid/exit
├── config.py             All tunable parameters
├── intermarket.py        DXY × EURGBP → (pair, direction) decision table
├── news_filter.py        ForexFactory weekly XML calendar parser + block check
├── risk.py               Position sizing + pyramiding TradeState
└── ict/
    ├── killzones.py      NY-time killzone gating
    ├── bias.py           BOS-based HTF bias
    ├── fvg.py            Fair Value Gap detection + mitigation
    ├── order_block.py    Order Block detection + mitigation
    ├── liquidity.py      Equal highs/lows + liquidity sweep detection
    └── dxy_synthetic.py  ICE-formula DXY from 6 constituent pairs
```

---

## Quickstart (QuantConnect cloud)

1. **Create a free account:** https://www.quantconnect.com/signup
2. **Create a new Python algorithm.**
3. **Upload all files** preserving the directory structure (drag-drop in the QC IDE).
4. **Hit Backtest.** Default period is set in `main.py` (`SetStartDate` / `SetEndDate`) — edit to taste.
5. **Read the Strategy Tester output.** Check: net profit, profit factor, max drawdown, total trades, Sharpe. Aim for PF ≥ 1.3 on out-of-sample data before going further.

### Going live (OANDA)

1. Open an **OANDA practice account** (free, demo money) and grab your API token.
2. In QC: *Live → Deploy → OANDA → paste token → choose v20 Practice → select this algorithm.*
3. Let it run 2–4 weeks on demo. Compare live stats to backtest.
4. Only fund with real money when demo confirms backtest characteristics.

---

## Configuration (`config.py`)

| Knob | Default | What it does |
|---|---|---|
| `RISK_PER_TRADE_PCT` | `1.0` | % of equity risked per leg |
| `MAX_LEGS` | `3` | Hard cap on pyramiding (initial + 2 adds) |
| `MIN_PIPS_TARGET` | `20` | Skip trade if nearest HTF target is closer than this |
| `MIN_RR` | `2.0` | Required reward:risk on initial entry |
| `KILLZONES` | London Open / NY AM / London Close | NY-time windows where entries are allowed |
| `NO_NEW_TRADES_LAST_MIN` | `15` | Skip new entries in the last N min of a killzone |
| `NEWS_BLOCK_MINUTES_BEFORE/AFTER` | `15 / 15` | Window around H/M USD/EUR/GBP events where entries are blocked |
| `TARGET_TF_MINUTES` | `(240, 1440, 10080)` | Timeframes scanned for HTF targets — H4, D, W |
| `SWING_LOOKBACK` | `20` | Bars used to define swing points for BOS |
| `FVG_MIN_SIZE_PIPS` | `3` | Ignore FVGs smaller than this |

---

## Intermarket decision table

| DXY 1H | EURGBP 1H | Decision        | Rationale                                   |
|--------|-----------|-----------------|---------------------------------------------|
| Bear   | Bull      | LONG EURUSD     | USD weak, EUR stronger leg → buy stronger   |
| Bear   | Bear      | LONG GBPUSD     | USD weak, GBP stronger leg → buy stronger   |
| Bull   | Bull      | SHORT GBPUSD    | USD strong, GBP weaker leg → sell weaker    |
| Bull   | Bear      | SHORT EURUSD    | USD strong, EUR weaker leg → sell weaker    |
| Neutral on either side | — | **No trade** | Confirmation incomplete                       |

---

## Known limitations / honest caveats

1. **Synthetic DXY** uses constituent pairs available on OANDA. It tracks ICE DXY within rounding; for a serious live deployment consider replacing with an actual DXY feed if your data plan supports it.
2. **Forex commission and spread** vary by broker. Default backtest uses QC defaults; tune `BrokerageModel` for your broker.
3. **News parsing** uses ForexFactory's free weekly XML. Schema can change without notice — if parsing breaks, check the format first (`news_filter.py`).
4. **No walk-forward / parameter optimisation** baked in. Do this manually for v1; if it becomes important, port to QC's optimiser.
5. **The 20-pip minimum target** is a hard filter. In ranging weeks it may produce few or zero trades — that's by design.
6. **Pyramiding** moves prior leg stops to entry only at the moment a new leg fires; intermediate trailing is not implemented.

---

## Verification checklist (before live $)

- [ ] Backtest compiles cleanly on QC with no warnings
- [ ] Backtest period covers ≥ 6 months including both trending and ranging regimes
- [ ] News-block log entries appear at expected times (NFP, FOMC, BoE, ECB)
- [ ] Average reward:risk in trade log ≥ `MIN_RR`
- [ ] Profit factor ≥ 1.3 out-of-sample
- [ ] Max drawdown within tolerance
- [ ] 30+ live demo trades match backtest stats within reasonable variance

---

## Roadmap (not in v1)

- Per-killzone trade-frequency cap
- Walk-forward parameter optimisation
- Replace synthetic DXY with native feed where data plan allows
- Telegram / Discord notifications on entry/exit/news-block
- Equity-curve circuit breaker (pause after N consecutive losses or % drawdown)

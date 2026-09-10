# Triple liquidity raid — EURUSD + GBPUSD vs DXY

Timeframe **60T**, sync window **4** bars, forward horizon **24** bars, MSS confirms within **6** bars.

**Bar coverage** (bars present in ALL THREE symbols): 2022: 5389 / 2023: 4293 / 2024: 5408 / 2025: 5396  
IS **9682** / OOS **10804**. An empty OOS bucket below usually means missing UDXUSD data for those years, not an absence of setups — check this line first.

`rev_rate` = share of events where price travelled FURTHER in the reversal direction than against it. `rev20` = share reaching 20+ pips our way. `single` = the same pair raided its own level while the trio did NOT align — the control that decides whether triple confirmation is worth anything. `trip+MSS` additionally requires structure to shift after the raid.

`n` counts PER-PAIR observations: one aligned trio contributes two rows (the EURUSD read and the GBPUSD read), so n = 2 x trios.

## short (pairs take HIGHS, DXY takes LOWS)

Aligned trios: **1541**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS    1444   52.3%    77.6%     48.6     41.3   40.2%
triple OOS   1638   50.5%    67.6%     32.8     32.3   37.5%
single IS    1056   50.6%    75.9%     46.7     43.8   44.0%
single OOS   1264   49.1%    67.4%     32.0     33.2   42.1%
trip+MSS IS    581   47.5%    74.4%     41.7     47.0  100.0%
trip+MSS OOS    615   50.2%    67.2%     34.4     33.8  100.0%
```

**Verdict: YELLOW** — positive but weak (+1.7pp IS / +1.4pp OOS)

## long  (pairs take LOWS,  DXY takes HIGHS)

Aligned trios: **1504**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS    1436   48.7%    75.7%     43.6     44.9   38.2%
triple OOS   1572   51.7%    71.1%     35.6     31.4   39.1%
single IS    1080   47.8%    72.8%     41.7     48.3   42.7%
single OOS   1202   52.3%    68.6%     33.7     30.7   43.3%
trip+MSS IS    548   50.0%    75.2%     46.5     46.8  100.0%
trip+MSS OOS    615   50.7%    69.9%     34.4     32.5  100.0%
```

**Verdict: RED** — no consistent lift (+0.9pp IS / -0.7pp OOS)

---

Measurement only. A GREEN earns an IS/OOS validation of a real lever; YELLOW/RED stands as the record of why nothing shipped.

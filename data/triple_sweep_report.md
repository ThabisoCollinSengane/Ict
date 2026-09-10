# Triple liquidity raid — EURUSD + GBPUSD vs DXY

Timeframe **60T**, sync window **4** bars, forward horizon **24** bars, MSS confirms within **6** bars.

**Bar coverage** (bars present in ALL THREE symbols): 2022: 5389 / 2023: 4293 / 2024: 5408 / 2025: 5396  
IS **9682** / OOS **10804**. An empty OOS bucket below usually means missing UDXUSD data for those years, not an absence of setups — check this line first.

`rev_rate` = share of events where price travelled FURTHER in the reversal direction than against it. `rev20` = share reaching 20+ pips our way. `single` = the same pair raided its own level while the trio did NOT align — the control that decides whether triple confirmation is worth anything. `trip+MSS` additionally requires structure to shift after the raid.

`n` counts PER-PAIR observations: one aligned trio contributes two rows (the EURUSD read and the GBPUSD read), so n = 2 x trios.

## short (pairs take HIGHS, DXY takes LOWS)

Aligned trios: **6**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS      12   41.7%    41.7%     17.5     72.0   33.3%
triple OOS      0   —
single IS      14   57.1%    57.1%     49.1     37.3   50.0%
single OOS     21   61.9%    76.2%     50.0     25.5   23.8%
trip+MSS IS      4   75.0%   100.0%     59.6     29.8  100.0%
trip+MSS OOS      0   —
```

**Verdict: RED** — no events in one or both splits

## long  (pairs take LOWS,  DXY takes HIGHS)

Aligned trios: **30**

```
bucket          n    rev%   rev20%   medFav   medAdv    MSS%
------------------------------------------------------------
triple IS      60   51.7%    75.0%     47.2     37.4   25.0%
triple OOS      0   —
single IS     101   43.6%    73.3%     44.2     56.5   23.8%
single OOS      0   —
trip+MSS IS     15   66.7%    86.7%     51.5     24.9  100.0%
trip+MSS OOS      0   —
```

**Verdict: RED** — no events in one or both splits

---

Measurement only. A GREEN earns an IS/OOS validation of a real lever; YELLOW/RED stands as the record of why nothing shipped.

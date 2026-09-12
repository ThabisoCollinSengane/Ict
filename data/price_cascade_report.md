# Pure-price draw cascade — daily taken → 3-day → 30-day → 60-day

Raw M1 price, independent of the strategy. Horizon after each sweep: **2.0 trading day(s)**. A daily sweep = price trades beyond the prior day's high/low; then we follow price and see which higher/lower pools it reaches. Pools 3d≤30d≤60d are ascending, so reach rates ARE the cascade. IS = 2022-23, OOS = 2024-25.

## All pairs combined

**In-sample 2022-23** — 1844 sweep events

| next pool | events with it ahead | reached it |
|---|---|---|
| 3-day | 1121 | 58% |
| 30-day | 1552 | 21% |
| 60-day | 1518 | 15% |
| weekly | 1153 | 25% |

_Conditional cascade (of those that reached the prior rung):_

take daily → **3-day** 58%· → **30-day** 49%· → **60-day** 70%

**Out-of-sample 2024-25** — 1793 sweep events

| next pool | events with it ahead | reached it |
|---|---|---|
| 3-day | 1080 | 61% |
| 30-day | 1609 | 20% |
| 60-day | 1669 | 13% |
| weekly | 1177 | 27% |

_Conditional cascade (of those that reached the prior rung):_

take daily → **3-day** 61%· → **30-day** 49%· → **60-day** 70%

## Per pair (full 4yr)

**EURUSD** — 1190 sweep events

| next pool | events with it ahead | reached it |
|---|---|---|
| 3-day | 737 | 59% |
| 30-day | 1048 | 20% |
| 60-day | 1065 | 13% |
| weekly | 760 | 26% |

_Conditional cascade (of those that reached the prior rung):_

take daily → **3-day** 59%· → **30-day** 48%· → **60-day** 65%

**GBPUSD** — 1208 sweep events

| next pool | events with it ahead | reached it |
|---|---|---|
| 3-day | 738 | 60% |
| 30-day | 1049 | 19% |
| 60-day | 1047 | 13% |
| weekly | 786 | 24% |

_Conditional cascade (of those that reached the prior rung):_

take daily → **3-day** 60%· → **30-day** 46%· → **60-day** 69%

**NZDUSD** — 1239 sweep events

| next pool | events with it ahead | reached it |
|---|---|---|
| 3-day | 726 | 59% |
| 30-day | 1064 | 22% |
| 60-day | 1075 | 16% |
| weekly | 784 | 28% |

_Conditional cascade (of those that reached the prior rung):_

take daily → **3-day** 59%· → **30-day** 54%· → **60-day** 76%

## Read

The cascade is REAL if reach rates step DOWN monotonically (near pools reached more than far) and IS/OOS agree. Compare the two splits above: 3-day 58%/61%, 30-day 21%/20%, 60-day 15%/13% (IS/OOS). A steep drop from 3-day to 60-day means price usually stops at the nearer draw — the strategy's exit-at-nearest design is correct, and the far pools are genuinely the NEXT cycle's target, not this move's.

_report generated on commit `c0f1c30`_

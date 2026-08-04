# Live structure + entries — GBPUSD

_all 14 GBPUSD entries over 60d · pips lot-independent · ZAR shown at the run's lot; ×3 for 0.03 lots, ÷2 for 0.01_

## Every entry (chronological)

| opened (UTC) | dir | model | scenario | draw | lot | pips | ZAR | result |
|---|---|---|---|---|---|---|---|---|
| 05-18 12:30 | long | breakout | 2b | 0 | 0.01 | -0.5 | -1 | stop |
| 05-26 13:00 | short | breakout | 1a_h4 | 0 | 0.01 | +9.5 | +18 | stop |
| 05-29 08:00 | short | judas | 1a_ip | 1 | 0.01 | -0.5 | -1 | stop |
| 06-09 11:15 | long | breakout | 2b_ip | 1 | 0.01 | -0.5 | -1 | stop |
| 06-18 08:00 | short | judas | 1a | 2 | 0.01 | +30.8 | +57 | target |
| 06-18 11:00 | short | breakout | 1a_h4 | 2 | 0.01 | -0.6 | -1 | session_handover |
| 06-19 12:45 | long | breakout | 2b_ip | 0 | 0.01 | -0.5 | -1 | stop |
| 06-22 07:30 | short | breakout | 1a_ip | 1 | 0.01 | -10.5 | -19 | stop |
| 06-24 12:30 | short | breakout | 1a_ip | 2 | 0.01 | -10.5 | -19 | stop |
| 07-02 07:45 | long | breakout | 2b | 0 | 0.01 | +9.5 | +18 | stop |
| 07-16 12:30 | short | breakout | 1a_ip | 0 | 0.01 | -10.5 | -19 | stop |
| 07-21 12:00 | short | judas | 1a | 2 | 0.01 | +34.5 | +64 | stop |
| 07-24 07:00 | long | breakout | 2b | 0 | 0.02 | -0.5 | -2 | stop |
| 07-27 11:45 | short | breakout | 1a_ip | 0 | 0.02 | +9.5 | +35 | stop |

## Per-day tally — the trending days (2+ entries) stand out

| day | entries | net pips | net ZAR | at 0.03 lots |
|---|---|---|---|---|
| 2026-05-18 | 1 | -0.5 | -1 | -3 |
| 2026-05-26 | 1 | +9.5 | +18 | +53 |
| 2026-05-29 | 1 | -0.5 | -1 | -3 |
| 2026-06-09 | 1 | -0.5 | -1 | -3 |
| 2026-06-18 ⭐ | 2 | +30.2 | +56 | +168 |
| 2026-06-19 | 1 | -0.5 | -1 | -3 |
| 2026-06-22 | 1 | -10.5 | -19 | -58 |
| 2026-06-24 | 1 | -10.5 | -19 | -58 |
| 2026-07-02 | 1 | +9.5 | +18 | +53 |
| 2026-07-16 | 1 | -10.5 | -19 | -58 |
| 2026-07-21 | 1 | +34.5 | +64 | +191 |
| 2026-07-24 | 1 | -0.5 | -2 | -3 |
| 2026-07-27 | 1 | +9.5 | +35 | +53 |

_⭐ = multi-entry (trending) day. Run `bash run_live_structure.sh --pair GBPUSD --date <YYYY-MM-DD>` on one to see its structure + the gate funnel passing all the way to entry._

## Setups that couldn't be taken (whole period)

Why setups did **not** become trades (counts):

| reason | count |
|---|---|
| no MSS (0/3 structure shift, need 2) | 47 |
| no HTF draw (0/3 cascade, not a breakout) | 15 |
| no MSS (1/3 structure shift, need 2) | 13 |

**Close calls — 15 setups that passed the structure shift but were blocked by a later gate:**

| time (UTC) | pair | dir | blocked by |
|---|---|---|---|
| 05-18 08:25 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 05-18 08:30 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:00 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:05 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:10 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:15 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:20 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:25 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-08 11:30 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 07-02 07:30 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 07-02 07:35 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 07-02 07:40 | GBPUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 07-27 11:00 | GBPUSD | short | no HTF draw (0/3 cascade, not a breakout) |
| 07-27 11:05 | GBPUSD | short | no HTF draw (0/3 cascade, not a breakout) |
| 07-27 11:10 | GBPUSD | short | no HTF draw (0/3 cascade, not a breakout) |


_report generated on commit `fcdf61e`_

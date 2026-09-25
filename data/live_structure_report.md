# Live structure + entries — EURUSD

_all 25 EURUSD entries over 60d · pips lot-independent · ZAR shown at the run's lot; ×3 for 0.03 lots, ÷2 for 0.01_

## Every entry (chronological)

| opened (UTC) | dir | model | scenario | draw | lot | pips | ZAR | result |
|---|---|---|---|---|---|---|---|---|
| 05-19 08:00 | short | judas | 3a | 1 | 0.01 | +9.6 | +18 | stop |
| 05-21 07:15 | short | breakout | 1b | 1 | 0.01 | -10.4 | -19 | stop |
| 05-21 12:00 | short | breakout | 3a | 1 | 0.01 | +9.6 | +18 | stop |
| 05-28 12:15 | long | breakout | 3b | 0 | 0.01 | +9.6 | +18 | stop |
| 06-01 13:05 | short | breakout | 1b_h4 | 1 | 0.01 | +9.6 | +18 | stop |
| 06-10 11:00 | short | judas | 1b | 1 | 0.01 | -10.4 | -19 | stop |
| 06-11 08:00 | short | judas | 3a | 1 | 0.01 | +9.6 | +18 | stop |
| 06-17 11:00 | short | breakout | 3a | 1 | 0.01 | +34.6 | +64 | stop |
| 06-22 13:00 | short | judas | 1b | 2 | 0.01 | -0.4 | -1 | stop |
| 06-23 07:30 | short | breakout | 3a | 1 | 0.01 | +33.9 | +70 | target |
| 06-23 11:50 | short | breakout | 1b | 1 | 0.01 | -10.4 | -19 | stop |
| 06-24 07:00 | short | breakout | 1b | 2 | 0.01 | +9.6 | +18 | stop |
| 06-25 11:00 | short | judas | 3a | 2 | 0.01 | -10.4 | -19 | stop |
| 06-26 12:55 | long | breakout | 2a | 1 | 0.01 | -10.4 | -19 | stop |
| 07-01 12:00 | short | breakout | 1b | 1 | 0.01 | +9.6 | +18 | stop |
| 07-10 13:00 | short | breakout | 3a | 2 | 0.01 | -10.4 | -19 | stop |
| 07-14 08:30 | long | breakout | 3b | 0 | 0.01 | -9.1 | -17 | session_handover |
| 07-14 12:15 | long | breakout | 2a | 0 | 0.01 | +35.3 | +65 | target |
| 07-20 12:00 | short | judas | 3a | 2 | 0.01 | +9.6 | +18 | stop |
| 07-23 08:10 | short | judas | 3a | 2 | 0.02 | +34.6 | +128 | stop |
| 07-24 12:30 | short | breakout | 3a | 1 | 0.02 | -10.4 | -38 | stop |
| 07-27 12:00 | short | breakout | 3a | 0 | 0.02 | +9.6 | +36 | stop |
| 07-30 07:15 | short | breakout | 1b | 0 | 0.02 | -10.2 | -38 | stop |
| 07-30 13:30 | long | breakout | 3b | 2 | 0.02 | +34.6 | +128 | stop |
| 07-31 11:00 | short | breakout | 3a | 0 | 0.02 | -3.9 | -15 | session_handover |

## Per-day tally — the trending days (2+ entries) stand out

| day | entries | net pips | net ZAR | at 0.03 lots |
|---|---|---|---|---|
| 2026-05-19 | 1 | +9.6 | +18 | +53 |
| 2026-05-21 ⭐ | 2 | -0.8 | -1 | -4 |
| 2026-05-28 | 1 | +9.6 | +18 | +53 |
| 2026-06-01 | 1 | +9.6 | +18 | +53 |
| 2026-06-10 | 1 | -10.4 | -19 | -58 |
| 2026-06-11 | 1 | +9.6 | +18 | +53 |
| 2026-06-17 | 1 | +34.6 | +64 | +192 |
| 2026-06-22 | 1 | -0.4 | -1 | -2 |
| 2026-06-23 ⭐ | 2 | +23.5 | +51 | +131 |
| 2026-06-24 | 1 | +9.6 | +18 | +53 |
| 2026-06-25 | 1 | -10.4 | -19 | -58 |
| 2026-06-26 | 1 | -10.4 | -19 | -58 |
| 2026-07-01 | 1 | +9.6 | +18 | +53 |
| 2026-07-10 | 1 | -10.4 | -19 | -58 |
| 2026-07-14 ⭐ | 2 | +26.2 | +48 | +145 |
| 2026-07-20 | 1 | +9.6 | +18 | +53 |
| 2026-07-23 | 1 | +34.6 | +128 | +192 |
| 2026-07-24 | 1 | -10.4 | -38 | -58 |
| 2026-07-27 | 1 | +9.6 | +36 | +53 |
| 2026-07-30 ⭐ | 2 | +24.4 | +90 | +136 |
| 2026-07-31 | 1 | -3.9 | -15 | -22 |

_⭐ = multi-entry (trending) day. Run `bash run_live_structure.sh --pair EURUSD --date <YYYY-MM-DD>` on one to see its structure + the gate funnel passing all the way to entry._

## Setups that couldn't be taken (whole period)

Why setups did **not** become trades (counts):

| reason | count |
|---|---|
| no MSS (0/3 structure shift, need 2) | 99 |
| no HTF draw (0/3 cascade, not a breakout) | 22 |
| 2a in London (chasing the spike) | 19 |
| no MSS (1/3 structure shift, need 2) | 18 |
| 2a_ip scenario gated (PF≤0.01) | 3 |

**Close calls — 8 distinct setups that passed the structure shift but were blocked by a later gate** (consecutive per-bar repeats collapsed):

| time (UTC) | pair | dir | blocked by |
|---|---|---|---|
| 06-16 08:00 | EURUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 06-26 07:30 | EURUSD | long | 2a in London (chasing the spike) |
| 07-02 12:30 | EURUSD | long | 2a_ip scenario gated (PF≤0.01) |
| 07-03 13:00 | EURUSD | short | no HTF draw (0/3 cascade, not a breakout) |
| 07-08 07:15 | EURUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 07-13 07:30 | EURUSD | long | 2a in London (chasing the spike) |
| 07-14 08:25 | EURUSD | long | no HTF draw (0/3 cascade, not a breakout) |
| 07-29 12:00 | EURUSD | short | no HTF draw (0/3 cascade, not a breakout) |


_report generated on commit `7c90903`_

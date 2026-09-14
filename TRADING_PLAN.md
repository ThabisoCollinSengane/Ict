# Personal trading plan — discretionary, on the algorithm's rails

Thabiso Collin Sengane · written 2026-09-14 · live from R1,000, Exness ZAR

**What this is.** I trade the setups by hand, because the evidence says my
context read beats the machine's filter (the Market Maker model measured a 2.98
profit factor and was rejected only because *a classifier* could not pick the
winners in advance — I can). But I run on the algorithm's rails for everything
the machine does better than me: sizing, stops, exits, and stopping.

**The split, stated once so I don't forget it:**

> My edge is **selection** — picking which of the day's setups is the real one.
> The machine's edge is **discipline** — executing without mood.
> The worst version of me reads the context right and gives it back through
> size, revenge, or skipping the boring ones.

Every number below is taken from the live engine config, not from memory.

---

# THE FIVE RULES

These are the whole plan. Everything after this page is the detail behind them.

### 1. I trade only what is on the card.

If the setup does not tick the card, there is no trade — no matter how it looks,
how long I have waited, or what I missed yesterday. **"Nothing today" is a
result, not a failure.** Outside the killzone there is no trade. Past my daily
cap there is no trade.

*This exists because the machine is never bored and I am.*

### 2. Size comes from the table. Never from the feeling.

Base lot is whatever my equity tier says. I may apply **one** 1.25× step, and
only for a named confirmation from the list. Nothing else changes my size —
not conviction, not a streak, not making back yesterday.

*This exists because sizing on feeling is the fastest way to give back an edge,
and the record says that feeling is mostly not informative.*

### 3. Stop and target are set before I enter, and I do not renegotiate them.

Stop goes beyond the intermediate swing, capped at 10 pips. Target is the
nearest qualifying draw at 30 pips or more. I trail on the ladder. **I take the
whole position off at the draw** — the continuation afterwards is a new trade
with a new entry, not a reason to hold.

*This exists because every single exit modification tested lost money: −49%,
−75%, and one version bankrupted the test account.*

### 4. I add only on the pyramid conditions. I never add to rescue.

An add requires: **+15 pips already in profit**, at least 30 pips of target
still remaining, and the higher timeframe still agreeing. Maximum 3 legs.
**If the trade is against me, there is no add. Ever.** That is averaging down
wearing a pyramid's clothes.

*This exists because the two look identical in the moment and opposite on the
account.*

### 5. The breakers are mine and they are not negotiable.

- **2 stop-outs, or −6% on the day → I am done for the day.**
- 5 losses in a row → done for the day.
- −10% from where the session opened → flat, day over.
- −15% from my equity peak → **10 calendar days off.**
- **Never a new trade in the same dollar direction as one that just stopped out.**

*This exists because revenge and tilt are the only things that can actually end
the account, and blocking correlated exposure alone lifted profit factor from
2.47 to 2.98 in testing.*

---

# THE DETAIL

## When I trade

| | |
|---|---|
| **Pairs** | GBPUSD, EURUSD, NZDUSD — nothing else |
| **London Open** | 03:00 – 05:00 New York time |
| **New York AM** | 07:00 – 10:00 New York time |
| **NZDUSD** | London Open only (NY AM was a confirmed drain) |
| **Hard block** | No new entry in the **last 15 minutes** of either killzone |
| **Daily cap** | **1 trade per pair**, **3 trades total**, per day |

The cap is part of Rule 1. Three is the ceiling, not the target — most days
should be one or zero.

## The setup card

Every box must tick before I click. No partial cards.

**Direction and pair**
- [ ] Dollar direction is clear (not flat) on H1 structure
- [ ] The pair is the one the dollar and EURGBP select
- [ ] **Golden rule:** short is GBPUSD, long is EURUSD — unless the cross
      explicitly says otherwise

**Structure**
- [ ] There is a consolidation / dealing range I can point at
- [ ] One side was swept and price closed **back inside** (the Judas)
- [ ] I am entering on a PD array — gap, order block or breaker — on the
      **retrace**, not on the sweep leg

**Quality — I want at least two of these four**
- [ ] The sweep ran **yesterday's high or low** *(55% / 53% vs 45% baseline)*
- [ ] The **H4 candle already swept and rejected** *(50.4% win rate, 137 trades)*
- [ ] My entry sits at an HTF gap's midpoint
- [ ] It is **Monday or Tuesday of NFP week**

**Target**
- [ ] At least **three different** sources agree at my target, within ~8 pips
      *(one source: PF 0.02 · two: 0.20 · **three: 6.70**)*
- [ ] The target is ≥ **30 pips** away and ≥ **1.2×** my stop
- [ ] It is the **nearest** qualifying draw — I am not reaching past it

**Nothing in the way**
- [ ] No opposing HTF gap sitting between my entry and my target
- [ ] No high-impact news in the window
- [ ] I hold no open position in the same dollar direction

> **If fewer than two quality boxes tick, or the target needs fewer than three
> sources — there is no trade.** That is the card doing its job.

## Size — Rule 2 in numbers

| Account equity | Lot | Per pip | 10-pip stop | 30-pip target |
|---|---|---|---|---|
| R1,000 – R3,000 | **0.02** | R3.70 | **−R37** | +R111 |
| R3,000 – R6,000 | **0.05** | R9.25 | −R92.50 | +R277 |
| R6,000+ | **0.09** | R16.65 | −R166.50 | +R499 |

**The 1.25× step.** One step only, and only for one of these:

- the sweep ran prior-day high/low
- H4 turtle soup already fired my way
- three or more sources agree at the target (4+ confluences)
- the trade follows the golden rule
- entry is at an HTF gap's midpoint

**Below R3,000 there is no step at all.** The multipliers are disabled under
R3,000 in the engine and they are disabled for me too. Risk on any single trade
never exceeds **8%** of the account.

> ⚠️ The account **cannot** size below 0.02 lots. If I draw down under R1,000 the
> tier table says 0.01 but the broker floor is 0.02 — so my worst day is about
> **R74 (two stops)**, not the R55 figure in the old notes. The −6% daily cap is
> what actually contains it.

## Exit — Rule 3 in numbers

| Trade progress | Where my stop goes |
|---|---|
| Entry | Beyond the intermediate swing, **capped at 10 pips** |
| **+10 pips** | Breakeven |
| **+20 pips** | Entry **+10** |
| **+40 pips** | Entry **+35** |
| **+60 pips** | Entry **+55** |
| every +20 after | lock **(milestone − 5)** |

**Target: the nearest qualifying draw, 30 pips minimum.** Aim at the **3-day**
pool — reached 58% and 61% of the time. The 30-day and 60-day pools are reached
about one time in five; they are extensions, not objectives.

**At the draw I am flat.** No trailing past it, no half-positions running on.

## Pyramiding — Rule 4 in numbers

An add is permitted only when **all four** are true:

1. Price is **≥ 15 pips** in profit on the existing position
2. **≥ 30 pips** of target still remains
3. The dollar still agrees **and** at least one higher timeframe still confirms
   the draw
4. I am on leg 1 or 2 — **maximum 3 legs**, each the same size

Each leg carries its **own** stop, placed structurally, capped at 10 pips.

> **An add is never a rescue.** If the trade is against me the answer is no.
> There is no version of this rule where being underwater permits another entry.

## The breakers — Rule 5 in numbers

| Trigger | Action |
|---|---|
| **−6% of the day's opening equity** | No new entries for the rest of the day |
| **2 stop-outs in a day** | Same — I close the laptop |
| **5 losses in a row** | Done for the day |
| **−10% from session open** | Close everything, day over |
| **−15% from equity peak** | **10 calendar days off.** No exceptions, no "just one" |
| Just stopped out | **No new trade in that same dollar direction** |

**On that last one:** EURUSD, GBPUSD and NZDUSD are one dollar bet wearing three
names. A long EURUSD and a short GBPUSD is the same position twice with two
spreads. Blocking that is measured to be worth roughly half a point of profit
factor.

---

# THE ROUTINE

## Before the session — 15 minutes

1. **Mark the daily gaps.** For each pair, note the nearest unfilled daily gap
   above and below price, and how far each is. A daily gap fills 90–96% of the
   time over a median 5–9 days — so this is my map of where price is likely to
   travel, **not** a direction signal on its own.
2. **Read the dollar.** H1 structure on the dollar index as of yesterday's
   close — the previous day's price action tells the story.
3. **Read the cross.** EURGBP decides which of EUR/GBP is the one to trade.
   The counters say the cross does more filtering work than the dollar does.
4. **Mark the range.** Yesterday's high/low, the Asian range, the previous
   session's high/low.
5. **Check the calendar.** High-impact news in the window = no trade.
6. **Write down what I expect** — one sentence, before price moves. This is how
   I find out later whether I actually read it right or told myself a story
   afterwards.

## During the session

- Watch for the card. Do not hunt for it.
- One trade per pair. Three total. Then stop looking.
- When it triggers: enter, set stop, set target, **walk away from the chart.**
- Manage only at the ladder levels. Nothing between them needs me.

## After the session — 10 minutes

Log every trade. The five fields that matter:

| Field | Why |
|---|---|
| Which quality boxes ticked | Builds the live version of the evidence tables |
| **Toward or away from the daily gap**, and how far | The one live open question — see below |
| Did I follow all five rules? **Yes / No** | This is the real score |
| If no — which one, and what was I feeling | The pattern is the point |
| Outcome in R (not rands) | Rands make small accounts feel like failures |

**Rule-following is scored separately from profit.** A losing trade that
followed all five rules is a **good** trade. A winning trade that broke one is a
**bad** trade that happened to pay — and that is the one that teaches the worst
habit.

## The one thing I am still collecting data on

Trades pointing **at** an unfilled daily gap won more often in both halves of the
backtest — +5.1 and +4.2 points. That is the right sign and the right size twice
over, which very little in this project managed. It could not be *proven*
because it needs roughly four times the data we have.

So I note it, and I do **not** force trades around it. After a few months of live
trades I will have something nobody had before: a real record of whether the
toward-the-gap setups are my signature moves.

---

# WHEN I BREAK A RULE

It will happen. What matters is what happens next.

1. **Write it down the same day** — which rule, what I was feeling, what it cost.
2. **No make-back trade.** The rule was broken; adding a second break does not
   repair the first.
3. **Two breaks in a week → one full week on demo.** Not as punishment — because
   two breaks means the rules are not yet automatic, and automatic is the whole
   point.

---

# REVIEW

- **Weekly:** rule-following score. Not P&L. The score.
- **Monthly:** compare my live win rate and profit factor against the algorithm's
  43.9% and 4.01. If I am below it after 50+ trades, the honest answer is that
  the machine should be running this and I should be supervising.
- **At 50 trades:** re-run the analysis on my own trade log and find out which of
  my quality boxes actually predicted anything — the same way the algorithm was
  tested, controls and both halves included.

---

*Baseline to measure myself against: the algorithm produced 736 trades over
2022–2025 — win rate 43.9%, profit factor 4.01, worst drawdown −13.24%, turning
R1,000 into R132,020 withdrawn plus R8,555 working capital.*

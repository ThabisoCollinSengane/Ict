# What four years of testing actually proved — a discretionary trader's notes

Written 2026-09-14, at the close of the research phase. Everything here is drawn
from the measured record in `CLAUDE.md`. Nothing is opinion or ICT orthodoxy
repeated back — every claim below is marked with what the evidence says and how
strong it is.

**How to read the confidence marks:**

| mark | means |
|---|---|
| ✅ **CONFIRMED** | held in 2022-23 AND 2024-25, at a similar size, on enough trades |
| ⚠️ **ONE PERIOD** | looked good in one half, did not survive the other — treat as unproven |
| 🔴 **NULL** | measured properly against a control and carries no edge |
| 💸 **COSTLY** | actually tested in the engine and lost real money |

The single most important framing: **most of what sounds true in ICT is
descriptively true and carries no directional information.** Price does go to the
gap. The gap does hold. Those are both real and both useless on their own,
because price does the same thing at any nearby level. What follows separates the
two.

---

## PART 1 — THE DOs

Things that held up in both halves of four years.

### ✅ 1. The AMD cycle is real, and you can see it in participation

Measured on tick volume across 275 trades, against each trade's own baseline:

| phase | volume vs baseline |
|---|---|
| Accumulation (the coil) | **0.66×** — dries up to two-thirds |
| Manipulation (the stop run) | **1.26×** — roughly doubles on the mean |
| Distribution | 1.22× — stays elevated |
| At the PD array (the fill) | **1.28×** — reacts hardest |

This is the institutional fingerprint, and it held on both pairs (GBPUSD spikes
harder than EURUSD — 1.93× vs 1.63× on the sweep). **When a range goes quiet and
then a sweep arrives on a violent bar, that is the real thing, not a fakeout.**

**But** — volume does NOT separate your winners from your losers. Tested
directly: winners and losers carry the same fingerprint, and the tiny 2022 edge
flips sign in 2024. Use volume to confirm you are *in* an AMD cycle. Do not use
it to judge whether *this* one will pay.

### ✅ 2. A sweep that runs prior-day high/low is your better setup

The one both-years-consistent setup-quality signal in the whole project:

| what the sweep ran | 2022 WR | 2024 WR |
|---|---|---|
| **PDH / PDL** | **55%** | **53%** |
| baseline (anything else) | ~45% | ~45% |

That is +8 to +10 points, in both years, on 115 trades. **If the stop-run took
yesterday's high or low, that setup is worth more size than one that swept a
random intraday level.** It is the one thing in this project that earned a real
position-size increase on merit.

### ✅ 3. The H4 turtle soup is a genuine timing confirmation

Price wicks beyond the prior 2-bar H4 range, then closes back inside. That is the
Judas swing one timeframe up — the manipulation has already fired.

| | trades | WR |
|---|---|---|
| **H4 turtle soup present** | 137 | **50.4%** |
| D1 turtle soup | 234 | 46.6% |
| no sweep | 427 | 45.4% |

Consistent in both halves. The **H4** one is the good one; the daily version is
weaker. **When the H4 candle has already run and rejected, your intraday entry in
that direction has better timing than one without it.**

### ✅ 4. The golden rule is real — and it is about *which pair*, not just direction

| | 2022-23 | 2024-25 |
|---|---|---|
| **SELL GBPUSD / BUY EURUSD** | WR 47.5% | WR 50.0% |
| against it | 39.7% | 42.2% |

+8 points in both halves, same size. GBP distributes harder on the downside, EUR
on the upside. **Short the weaker one, buy the stronger one.** When the dollar is
bid, sell GBPUSD. When it's offered, buy EURUSD.

The fuller version — the four-quadrant table in `CLAUDE.md` — uses EURGBP to pick
the pair, and the intermarket counters showed **EURGBP is the heavier filter**
(it rejected 97 setups where the dollar rejected 59). The cross does more work
than the dollar. That was never validated out-of-sample, so treat the quadrant as
a framework, not a proven edge — but the simple golden rule above IS proven.

### ✅ 5. Three independent confluences at your target, or don't take it

Scoring each target by how many *different* families agree within 8 pips
(fib / gap / order block / equal highs-lows / round number / PDH-PDL / weekly /
intermediate swings):

| confluences | trades | profit factor |
|---|---|---|
| 1 | 13 | **0.02** |
| 2 | 40 | **0.20** |
| **3** | 225 | **6.70** |
| 4 | 325 | 5.73 |
| 5 | 190 | 3.94 |

**The cliff between 2 and 3 is the finding.** One source can be found near any
price — that's noise. Three different frameworks pointing at the same level means
multiple desks are aiming there.

Note it does **not** keep improving above 4. More confirmation past that point
adds nothing.

### ✅ 6. Put your stop one structural tier up, not at the obvious swing

Moving the stop beyond the *intermediate* swing instead of the nearest
short-term swing was worth **+18% equity** with drawdown unchanged.

**The short-term swing is exactly what a minor liquidity run sweeps.** That's what
it's there for. If your stop sits at the obvious recent low, you are parked in
the pool. One tier up survives the sweep — and it costs you a little more on the
trades where you were simply wrong, which is the right trade-off.

### ✅ 7. The 3-day pool is the dependable draw. The 30/60-day one is not.

Pure price study, 3,637 sweep events, independent of any strategy:

| next pool after a prior-day sweep | reached within 2 days |
|---|---|
| **3-day high/low** | **58% / 61%** |
| weekly | 25% / 27% |
| 30-day | 21% / 20% |
| 60-day | 15% / 13% |

All three pairs agree. **Target the 3-day pool.** The 30 and 60-day pools are
reached about one time in five — they are extension targets, not objectives. This
is measured, both halves, rock solid.

### ✅ 8. Trail as you go on a long-running trade

Locking the stop progressively (breakeven at +10, +10 at +20, then every 20 pips
of progress lock 10 behind) was **+36% equity with drawdown up only 0.06%.** The
largest single improvement in the project after position sizing.

A trade that reaches +35 and reverses should not be a full loss.

### ✅ 9. Monday and Tuesday of NFP week

WR 62.5% / 52.1% vs 41.2% / 43.3% baseline. The only one of seven "narrative"
factors that passed both halves. The tight pre-NFP accumulation makes for a
clean sweep. (Wednesday to Friday of that week is already a known low-probability
window.)

---

## PART 2 — THE DON'Ts

Things that sound true, that most people believe, and that measure to nothing
when tested against a proper control.

**The method matters here.** For every one of these we asked: *what would an
identical but meaningless level do?* Usually it does exactly the same thing.

### 🔴 1. "Price is drawn to the fair value gap"

**True, and worthless as a direction.** Unfilled daily and H4 gaps get reached
90–95% of the time. And a band of **identical width, the same distance away, on
the opposite side of price** gets reached 90–95% of the time too.

Six separate comparisons, none differed by more than 0.8 points. On completely
random data, both read 93.5%.

**The gap being reached tells you nothing about which way to trade.** Holding a
bias toward a gap for days adds risk and time without adding expectancy. If you
find yourself saying "price has to come back and fill that gap" — it does, and so
does the level the same distance in the other direction.

### 🔴 2. "The gap held, so it's a support zone"

Price bounces at an HTF gap 64–70% of the time. It bounces at a mirror band the
same distance away 60–74% of the time.

The one cell that looked real (daily gaps, +9.7 points) collapsed to +3.5 in the
second half — and worse, **that branch lost money**: the favourable move after a
"respected" daily gap averaged 86 pips against 98 pips adverse.

**"It held at the gap" is a description of how price behaves at any level it
reaches, not evidence the gap did anything.**

### 🔴 3. "A broken gap inverts and becomes resistance" (the IFVG)

Tested twice, independently, both ways:
- As a standalone entry with a realistic 10-pip stop and costs: **profit factor
  0.80 / 0.76 — losing on every timeframe, both halves, two different target
  methods.** Win rate lands at ~33%, and a 2R target off a 10-pip stop needs more
  than 33% to break even before spread.
- As a re-test zone: hold rates look strong (63–78%) but the control does 61–75%.

**The full-body-close inversion is a real market-structure event that carries no
measurable edge on its own.** It may still be a useful *context* marker inside a
bigger setup — that's what the semi-auto MM model uses it for. It is not a trade
by itself.

### 🔴 4. "EURUSD and GBPUSD took highs while the dollar took lows — triple
confirmation"

1,541 of these over four years — about **1.5 per day.** Reversal rate: 47.5% to
52.3% in every bucket, both directions, both halves. A single-pair sweep with no
alignment does exactly the same.

**It is not a rare institutional fingerprint. It is what the dollar complex does
mechanically most days**, because the pairs are inverse to the dollar. You are
counting one event three times.

Adding the dollar/cross quadrant on top made it **worse** in all four cells.

### 🔴 5. "The daily open is a key level"

Tested against a deliberately meaningless level (a quarter of yesterday's range
from the open, side alternating by date). Lifts: +2.1/−4.4, −3.2/+3.7, −5.9/+0.2.
Small and sign-flipping.

**The daily open is not special.** Same for the session open: more confirmation at
the open read *better* in one half and *worse* in the other, perfectly mirrored.

### 🔴 6. "More confirmations = better trade"

Two separate findings say no:
- Past 3 confluences at the target, performance does not keep improving.
- The session-open confirmation count (0, 1 or 2 references confirming) was
  monotonically *better* with more confirmation in 2022-23 and monotonically
  *worse* in 2024-25. Perfect mirror images = noise.

**Waiting for a fourth and fifth confirmation costs you entry price and buys you
nothing.**

### 🔴 7. "If my stop was hit, I was early — the move came later"

This was your own standing claim and it was worth testing properly. From the bar
after each losing trade closed, which came first: the level we aimed at, or a
mirror level the same distance the *other* way?

**53.3% and 49.0%.** A coin flip in both halves.

**The losses were wrong-way trades, not early ones.** No stop placement, entry
timing or extra patience recovers them. This is worth internalising, because
"I was right but early" is the most comfortable story a trader can tell after a
loss, and here it is measurably false.

### 🔴 8. Day of week, seasonal lean, and "narrative" generally

Of seven contextual factors, one passed (NFP Mon/Tue), one was mildly **inverted**
(prior session's sweep agreeing with you was a small *negative*), one never fired
at all, and the rest flipped sign between halves.

---

## PART 3 — WHAT WENT WRONG WHEN WE TRIED TO IMPROVE THE ALGO

You asked specifically about this. Four patterns, each one tested repeatedly,
each one costly. **These translate directly to discretionary decisions.**

### 💸 1. Holding past your target destroyed money — three different ways

| attempt | result |
|---|---|
| Trail instead of exiting when price wicks the target | **−49% equity** |
| Same, better implementation | −49% |
| Take half at target, run the rest to the next draw | **−75% equity** |

Every single exit modification lost. The first version was so bad it bankrupted
the account in testing.

**Why: your target IS the end of the AMD cycle.** When price delivers to the
institutional draw, distribution has happened. Holding past it means sitting
through the consolidation/reversal where you have no edge. The next move belongs
to a *new* setup, not to your old one.

**Discretionary version: take the full position off at the draw.** The 100-200
pip continuation you occasionally see afterwards is real — and it is a new trade
with a new entry, not a reason to hold.

### 💸 2. Aiming further out destroyed money

Preferring a more distant liquidity pool over a nearer target: **drawdown went
from −13% to −22%** in both halves, win rate down 4-5 points.

The near target is the draw for *this* cycle. The far one is the draw for the
*next* cycle. Aiming at the far one means staying through the intermediate
consolidation where price pauses or reverses. This is the same lesson as #1 from
the other end, and the 3-day/30-day reach rates (58% vs 21%) are the arithmetic
behind it.

**Discretionary version: take the nearest target that gives you acceptable
reward-to-risk. Don't reach.**

### 💸 3. Trading *into* the pool destroyed money

The idea: instead of only fading the sweep, trade *toward* an untouched prior-day
high/low because price is drawn to it.

**Result: drawdown −16.7%, breaking the risk limit; win rate and profit factor
down in all three test periods.** Four separate attempts at "continuation instead
of reversal" failed the same way.

**Why: the pool is where the cycle ENDS.** Riding into it means buying exactly
where smart money is selling into the resting liquidity. Prior-day highs and lows
are correct as *targets*. They are wrong as *entries*.

### 💸 4. Filtering out "bad" setups destroyed money

This is the least intuitive one and the most important.

We identified a bucket of trades with a profit factor of **0.13** — catastrophically
losing in isolation. Removing them cost **R31 million** of compounded growth over
the test. A second attempt at merely *shrinking* them lost equity in all three
test periods while improving drawdown in none.

**Why: a setup that loses on simple arithmetic can still be positive to your
compounding**, because its occasional wins land at points where they compound
forward, and the slot it occupies would otherwise go to a lower-quality trade.

**Discretionary version: be very careful about deciding a setup type is bad and
cutting it.** The obvious filter is usually wrong. This is the single most
repeated failure in the whole project — four separate attempts, all costly.

### 💸 5. Sizing up broadly is leverage, not selection

Increasing size on the largest bucket (69% of trades) *lowered* profit factor and
*reduced* the trade count, because the bigger positions breached the per-trade
risk cap and got skipped.

**Every size increase that worked targeted a small, distinctive subset** —
15 trades, 91 trades, 122 trades out of 736. **A size bump is a selection tool. If
you apply it to most of your trades, you have just raised your lot size.**

---

## PART 4 — HOW NOT TO FOOL YOURSELF

These are method lessons, and honestly they may be the most transferable part.
I made every one of these mistakes during this work.

### 1. An unusually clean result is evidence of a bug before it's evidence of an edge

**Five separate studies produced beautiful, publishable findings that were
entirely artifacts of my own measurement.** In every single case the broken
version looked *better* than the truth. One of them — a "target quality" finding
I called the strongest result in the project — turned out to be reading
information from the future, and when fixed it didn't shrink, it **inverted**.

**If a pattern looks unusually clean, distrust it first.**

### 2. Always ask "what would a meaningless level do?"

This is the one that killed most of Part 2. "The gap gets reached 95% of the time"
sounds decisive until you check that a random band the same distance away gets
reached 95% too.

**Discretionary version: before you credit a level for what price did, ask
yourself what price does at levels generally.**

### 3. One good period proves nothing

Three times in this project a perfectly clean, ordered pattern in 2022-23
dissolved — or exactly reversed — in 2024-25. Not degraded. *Mirror image.*

**If you find something that works, you have not found something that works. You
have found something that worked in the period you looked at.** Check the other
period before you change your trading.

### 4. Don't let a confirmation be the thing you're trying to predict

Four times I measured "structure shifted my way" over the same window as "price
moved my way" — which are the same statement. The bucket scored 100% by
construction.

**Discretionary version: if your confirmation only becomes visible after the move
has already happened, it isn't a confirmation.**

### 5. Know how much data your question needs before you cut it

The final study needed roughly **four times** the entire four-year dataset to
answer its question. Every refinement made it worse by subdividing further.

**With 40 trades a quarter, you will never resolve a 5% win-rate difference. Don't
try. Spend your attention on the things where the effect is large enough to see.**

---

## PART 5 — YOUR EDGE VS THE ALGO'S

You raised this and it deserves a straight answer.

**There is direct evidence in this project that a human can beat the machine on
exactly this material.** The Market Maker model — dealing range, sweep of external
liquidity, entry at the inverted gap — was tested autonomously and came out
**genuinely profitable** (profit factor 2.98, roughly 5.5 setups a week). It was
not shipped for one reason:

> "Good timeframe cascades with a profit factor above 1 in both halves: **None.**
> Win rate 21% is uniform across every tag — cascade timeframe, pattern, pair,
> period. No robust subset to filter to. The edge is in a fat tail of rare large
> winners, **and the winners are unpredictable in advance.**"

**Unpredictable in advance *by a machine, from the tags it can measure*.** That is
precisely the gap a discretionary trader fills. You are reading context the
classifier cannot encode — how the sweep felt, what the dollar was doing into it,
whether the session had already shown its hand. The machine had to reject that
setup. You don't.

**So yes — you may well make more than the algo on this material.** That is a
reasonable expectation, not wishful thinking.

**What the algo has that you don't:**

- It takes the boring setup at 3:07am without being bored.
- It never revenge trades after two losses.
- It never skips the seventh consecutive small setup because the last six annoyed it.
- It stops at −6% on the day, every day, without negotiating.
- It sizes identically on the setup that "feels" great and the one that doesn't —
  and the record above says that feeling is mostly not informative.

**What you have that it doesn't:** context. The thing that made the MM model
unfilterable.

**The honest split:** your edge is in *selection* — picking which of the daily
setups is the real one. The machine's edge is in *discipline* — executing without
mood. The worst version of you is one who has the context read right and gives it
back through size, revenge, or skipping the boring ones.

So: **keep the circuit breakers as personal rules even when you're trading by
hand.** Two losses, stop for the day. No third trade after a stop-out on a
correlated pair — EURUSD, GBPUSD and NZDUSD are one dollar bet, and it was
blocking concurrent same-direction exposure that lifted the MM model's profit
factor from 2.47 to 2.98. That one is measured.

---

## THE ONE-PAGE VERSION

**Do:**
- Trade the pair the dollar and EURGBP select — sell the weaker, buy the stronger.
- Prefer sweeps that ran yesterday's high or low.
- Prefer setups where the H4 candle already swept and rejected.
- Need three *different* things agreeing at your target. Not more than that.
- Stop one structural tier beyond the obvious swing.
- Target the 3-day pool. Take the nearest target that clears your R:R.
- Trail as it runs. Take the whole position off at the draw.
- Mon/Tue of NFP week is a good window.

**Don't:**
- Don't hold past your target hoping for continuation.
- Don't reach for the further target.
- Don't trade *into* an untouched pool — that's where the cycle ends.
- Don't decide a setup type is bad and cut it.
- Don't wait for a fourth and fifth confirmation.
- Don't credit the gap for price arriving — it arrives everywhere.
- Don't tell yourself you were early. Measured: you were wrong.
- Don't take a fresh trade in the same dollar direction as one that just stopped out.

**And the meta-rule:** if something looks unusually clean, it's probably a
measurement artifact. That held five times out of six in this project.

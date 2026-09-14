"""Render the personal trading plan as a PDF.

    python scripts/build_trading_plan_pdf.py [output.pdf]

Pure reportlab, same convention as scripts/build_manual_pdf.py. Page 2 is THE
FIVE RULES alone — designed to be printed or screenshotted on its own.

Every number is read from the live config at build time, so the plan cannot
drift from the engine. If a value changes in config.py, rebuild and the plan
changes with it.
"""
import sys
sys.path.insert(0, ".")
import config as C
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/ICT_Trading_Plan.pdf"

NAVY  = colors.HexColor("#0B2545")
BLUE  = colors.HexColor("#13315C")
GREEN = colors.HexColor("#1B7A43")
RED   = colors.HexColor("#B23A2E")
AMBER = colors.HexColor("#B8860B")
GREY  = colors.HexColor("#5A6B7B")
LIGHT = colors.HexColor("#EDF3F8")
RULEC = colors.HexColor("#D5DEE6")
ZEBRA = colors.HexColor("#F7FAFC")

# ── values pulled live from config so the plan cannot drift ──────────────────
KZ        = C.KILLZONES
LAST_MIN  = C.NO_NEW_TRADES_LAST_MIN
PER_PAIR  = C.MAX_PAIR_TRADES_PER_DAY
PER_DAY   = C.MAX_TRADES_PER_DAY
STOP_CAP  = C.FIXED_STOP_PIPS
MIN_TGT   = C.MIN_PIPS_TARGET
MIN_RR    = C.MIN_RR
BE        = C.TRAIL_BE_PIPS
LOCK      = C.TRAIL_LOCK_PIPS
MSTEP     = C.MILESTONE_TRAIL_STEP
MBUF      = C.MILESTONE_TRAIL_BUFFER
PYR_FAV   = C.PYRAMID_MIN_FAVOUR_PIPS
MAX_LEGS  = C.MAX_LEGS
DD_HALT   = C.MAX_DRAWDOWN_HALT_PCT
DD_DAYS   = C.DRAWDOWN_PAUSE_DAYS
DAILY_CAP = C.MAX_DAILY_LOSS_PCT
CONSEC    = C.MAX_CONSECUTIVE_LOSSES
SESS_KILL = C.SESSION_DRAWDOWN_PCT
MAX_RISK  = C.MAX_RISK_PER_TRADE_PCT
SIZE_FLOOR= C.DRAW_SIZE_MIN_EQUITY
ZAR       = C.USD_ZAR
LOTFLOOR  = C.MIN_LOT_SIZE

styles = getSampleStyleSheet()
def S(n, **kw): styles.add(ParagraphStyle(n, parent=styles["Normal"], **kw))

S("Cover",   fontName="Helvetica-Bold", fontSize=26, textColor=NAVY, leading=30, spaceAfter=8)
S("CoverSub",fontName="Helvetica",      fontSize=12.5, textColor=GREY, leading=18)
S("H1",      fontName="Helvetica-Bold", fontSize=16.5, textColor=NAVY, leading=20,
             spaceBefore=13, spaceAfter=7)
S("H2",      fontName="Helvetica-Bold", fontSize=11.5, textColor=BLUE, leading=15,
             spaceBefore=11, spaceAfter=4)
S("Body",    fontName="Helvetica",      fontSize=9.6, leading=13.6, spaceAfter=5,
             textColor=colors.HexColor("#12222F"))
S("Small",   fontName="Helvetica",      fontSize=8.4, leading=11.6, textColor=GREY, spaceAfter=4)
S("Lead",    fontName="Helvetica",      fontSize=10.6, leading=15.4, spaceAfter=7,
             textColor=colors.HexColor("#12222F"))
S("Cell",    fontName="Helvetica",      fontSize=8.6, leading=11.4)
S("CellB",   fontName="Helvetica-Bold", fontSize=8.6, leading=11.4)
S("CellH",   fontName="Helvetica-Bold", fontSize=8.4, leading=11, textColor=colors.white)
S("RuleNo",  fontName="Helvetica-Bold", fontSize=21, textColor=colors.white, leading=24)
S("RuleTxt", fontName="Helvetica-Bold", fontSize=11.6, leading=15, textColor=NAVY, spaceAfter=3)
S("RuleSub", fontName="Helvetica",      fontSize=8.9, leading=12.4,
             textColor=colors.HexColor("#243444"))
S("RuleWhy", fontName="Helvetica-Oblique", fontSize=8.4, leading=11.4, textColor=GREY)
S("Check",   fontName="Helvetica",      fontSize=9.2, leading=14)

def P(t, s="Body"): return Paragraph(t, styles[s])
def rule(): return HRFlowable(width="100%", thickness=0.7, color=RULEC,
                              spaceBefore=5, spaceAfter=8)

def table(head, rows, widths, aligns=None, hl=None):
    data = [[Paragraph(h, styles["CellH"]) for h in head]]
    for i, r in enumerate(rows):
        st = "CellB" if hl and i in hl else "Cell"
        data.append([Paragraph(str(c), styles[st]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    cmds = [("BACKGROUND", (0, 0), (-1, 0), BLUE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.4, RULEC)]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    for col, a in enumerate(aligns or []):
        if a != "L":
            cmds.append(("ALIGN", (col, 0), (col, -1), "RIGHT" if a == "R" else "CENTER"))
    t.setStyle(TableStyle(cmds))
    return t

def note(text, col=GREY, w=16.2):
    t = Table([[Paragraph(text, styles["Small"])]], colWidths=[w*cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, col)]))
    return KeepTogether([Spacer(1, 3), t, Spacer(1, 5)])

def big_rule(n, title, body, why, col=NAVY):
    inner = [Paragraph(title, styles["RuleTxt"]), Paragraph(body, styles["RuleSub"]),
             Spacer(1, 3), Paragraph(why, styles["RuleWhy"])]
    t = Table([[Paragraph(str(n), styles["RuleNo"]), inner]],
              colWidths=[1.35*cm, 14.85*cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), col),
        ("VALIGN", (0, 0), (0, 0), "MIDDLE"), ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("VALIGN", (1, 0), (1, 0), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (1, 0), (1, 0), 9), ("RIGHTPADDING", (1, 0), (1, 0), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, RULEC)]))
    return KeepTogether([Spacer(1, 6), t])

def checks(items):
    rows = [[Paragraph("☐", styles["Check"]), Paragraph(i, styles["Check"])] for i in items]
    t = Table(rows, colWidths=[0.7*cm, 15.5*cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
    return t

def _page(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 7.6); canv.setFillColor(GREY)
    canv.drawString(2*cm, 1.25*cm, "Personal trading plan — discretionary, on the algorithm's rails")
    canv.drawRightString(A4[0] - 2*cm, 1.25*cm, f"{doc.page}")
    canv.setStrokeColor(RULEC); canv.line(2*cm, 1.6*cm, A4[0] - 2*cm, 1.6*cm)
    canv.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                          topMargin=1.7*cm, bottomMargin=2*cm,
                          title="Personal trading plan", author="T. C. Sengane")
    doc.addPageTemplates([PageTemplate(id="m",
        frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="n")],
        onPage=_page)])
    F = []

    # ── cover ───────────────────────────────────────────────────────────────
    F += [Spacer(1, 3.0*cm),
          P("Personal trading plan", "Cover"),
          P("Discretionary — running on the algorithm's rails", "CoverSub"),
          Spacer(1, 0.45*cm), rule(),
          P("I trade the setups by hand, because the evidence says my context read beats the "
            "machine's filter. But I run on the algorithm's rails for everything the machine does "
            "better than me: <b>sizing, stops, exits, and stopping.</b>", "Lead"),
          Spacer(1, 0.3*cm),
          note("<b>The split, stated once so I don't forget it.</b><br/><br/>"
               "My edge is <b>SELECTION</b> — picking which of the day's setups is the real one.<br/>"
               "The machine's edge is <b>DISCIPLINE</b> — executing without mood.<br/><br/>"
               "The worst version of me reads the context right and gives it back through size, "
               "revenge, or skipping the boring ones.", NAVY),
          Spacer(1, 0.4*cm),
          P(f"Live from R1,000 · Exness ZAR · GBPUSD, EURUSD, NZDUSD · "
            f"max {PER_PAIR} trade per pair, {PER_DAY} per day", "Small"),
          P("Every figure in this plan is read from the live engine config at build time, so the "
            "plan cannot drift from the algorithm.", "Small"),
          PageBreak()]

    # ── THE FIVE RULES (standalone page) ────────────────────────────────────
    F += [P("The five rules", "H1"),
          P("This page is the whole plan. Everything after it is the detail behind it.", "Lead")]

    F += [big_rule(1, "I trade only what is on the card.",
        "If the setup does not tick the card, there is no trade — no matter how it looks, how long "
        "I have waited, or what I missed yesterday. <b>“Nothing today” is a result, not a failure.</b> "
        "Outside the killzone there is no trade. Past my daily cap there is no trade.",
        "Because the machine is never bored, and I am.", NAVY)]

    F += [big_rule(2, "Size comes from the table. Never from the feeling.",
        f"Base lot is whatever my equity tier says. I may apply <b>one</b> 1.25× step, and only for a "
        f"named confirmation from the list. Nothing else changes my size — not conviction, not a "
        f"streak, not making back yesterday. Risk never exceeds <b>{MAX_RISK:.0f}%</b> on one trade.",
        "Because sizing on feeling is the fastest way to give back an edge — and the record says that "
        "feeling is mostly not informative.", BLUE)]

    F += [big_rule(3, "Stop and target are set before I enter, and I do not renegotiate them.",
        f"Stop beyond the intermediate swing, capped at <b>{STOP_CAP} pips</b>. Target is the nearest "
        f"qualifying draw at <b>{MIN_TGT} pips</b> or more. I trail on the ladder. "
        f"<b>I take the whole position off at the draw</b> — the continuation afterwards is a new "
        f"trade with a new entry, not a reason to hold.",
        "Because every single exit modification tested lost money: −49%, −75%, and one version "
        "bankrupted the test account.", GREEN)]

    F += [big_rule(4, "I add only on the pyramid conditions. I never add to rescue.",
        f"An add requires <b>+{PYR_FAV:.0f} pips already in profit</b>, at least {MIN_TGT} pips of "
        f"target still remaining, and the higher timeframe still agreeing. Maximum "
        f"<b>{MAX_LEGS} legs</b>. <b>If the trade is against me, there is no add. Ever.</b> That is "
        f"averaging down wearing a pyramid's clothes.",
        "Because the two look identical in the moment and opposite on the account.", AMBER)]

    F += [big_rule(5, "The breakers are mine and they are not negotiable.",
        f"<b>2 stop-outs, or −{DAILY_CAP:.0f}% on the day → I am done for the day.</b> "
        f"{CONSEC} losses in a row → done. −{SESS_KILL:.0f}% from session open → flat, day over. "
        f"−{DD_HALT:.0f}% from my equity peak → <b>{DD_DAYS} calendar days off.</b> "
        f"<b>Never a new trade in the same dollar direction as one that just stopped out.</b>",
        "Because revenge and tilt are the only things that can actually end the account — and "
        "blocking correlated exposure alone lifted profit factor from 2.47 to 2.98 in testing.", RED)]

    F += [PageBreak()]

    # ── WHEN ────────────────────────────────────────────────────────────────
    F += [P("The detail", "H1"), P("When I trade", "H2"),
          table(["", ""], [
              ["<b>Pairs</b>", "GBPUSD, EURUSD, NZDUSD — nothing else"],
              [f"<b>{KZ[0][0]}</b>", f"{KZ[0][1]} – {KZ[0][2]} New York time"],
              [f"<b>{KZ[1][0]}</b>", f"{KZ[1][1]} – {KZ[1][2]} New York time"],
              ["<b>NZDUSD</b>", "London Open only — NY AM was a confirmed drain"],
              ["<b>Hard block</b>", f"No new entry in the last <b>{LAST_MIN} minutes</b> of a killzone"],
              ["<b>Daily cap</b>", f"<b>{PER_PAIR} trade per pair</b>, <b>{PER_DAY} total</b>, per day"],
          ], [3.4*cm, 12.8*cm]),
          P("The cap is part of Rule 1. Three is the ceiling, not the target — most days should be "
            "one or zero.", "Small")]

    # ── CARD ────────────────────────────────────────────────────────────────
    F += [P("The setup card — Rule 1", "H2"),
          P("Every box must tick before I click. No partial cards.", "Body"),
          P("<b>Direction and pair</b>", "Body"),
          checks(["Dollar direction is clear (not flat) on H1 structure",
                  "The pair is the one the dollar and EURGBP select",
                  "<b>Golden rule:</b> short is GBPUSD, long is EURUSD — unless the cross says otherwise"]),
          Spacer(1, 4),
          P("<b>Structure</b>", "Body"),
          checks(["There is a consolidation / dealing range I can point at",
                  "One side was swept and price closed <b>back inside</b> (the Judas)",
                  "I am entering on a PD array — gap, order block or breaker — on the "
                  "<b>retrace</b>, not the sweep leg"]),
          Spacer(1, 4),
          P("<b>Quality — I want at least TWO of these four</b>", "Body"),
          checks([f"The sweep ran <b>yesterday's high or low</b>  <i>(55% / 53% vs 45% baseline, 115 trades)</i>",
                  "The <b>H4 candle already swept and rejected</b>  <i>(50.4% win rate, 137 trades)</i>",
                  "My entry sits at an HTF gap's midpoint",
                  "It is <b>Monday or Tuesday of NFP week</b>  <i>(62.5% / 52.1%)</i>"]),
          Spacer(1, 4),
          P("<b>Target</b>", "Body"),
          checks([f"At least <b>three different</b> sources agree at my target, within ~"
                  f"{C.TARGET_CONFLUENCE_TOL_PIPS} pips  <i>(one source: PF 0.02 · two: 0.20 · "
                  f"<b>three: 6.70</b>)</i>",
                  f"Target is ≥ <b>{MIN_TGT} pips</b> away and ≥ <b>{MIN_RR}×</b> my stop",
                  "It is the <b>nearest</b> qualifying draw — I am not reaching past it"]),
          Spacer(1, 4),
          P("<b>Nothing in the way</b>", "Body"),
          checks(["No opposing HTF gap sitting between my entry and my target",
                  "No high-impact news in the window",
                  "I hold no open position in the same dollar direction"]),
          note("<b>If fewer than two quality boxes tick, or the target needs fewer than three "
               "sources — there is no trade.</b> That is the card doing its job.", NAVY),
          PageBreak()]

    # ── SIZE ────────────────────────────────────────────────────────────────
    def pip(lot): return lot * 100000 * 0.0001 * ZAR
    F += [P("Size — Rule 2 in numbers", "H2"),
          table(["Account equity", "Lot", "Per pip", f"{STOP_CAP}-pip stop", f"{MIN_TGT}-pip target"], [
              ["R1,000 – R3,000", "<b>0.02</b>", f"R{pip(0.02):.2f}", f"<b>−R{pip(0.02)*STOP_CAP:.0f}</b>", f"+R{pip(0.02)*MIN_TGT:.0f}"],
              ["R3,000 – R6,000", "<b>0.05</b>", f"R{pip(0.05):.2f}", f"−R{pip(0.05)*STOP_CAP:.0f}", f"+R{pip(0.05)*MIN_TGT:.0f}"],
              ["R6,000+", "<b>0.09</b>", f"R{pip(0.09):.2f}", f"−R{pip(0.09)*STOP_CAP:.0f}", f"+R{pip(0.09)*MIN_TGT:.0f}"],
          ], [3.8*cm, 2.2*cm, 2.6*cm, 3.6*cm, 4.0*cm], ["L", "C", "C", "C", "C"]),
          P("<b>The 1.25× step — one only, and only for one of these:</b>", "Body"),
          checks(["the sweep ran prior-day high/low",
                  "H4 turtle soup already fired my way",
                  "four or more sources agree at the target",
                  "the trade follows the golden rule",
                  "entry is at an HTF gap's midpoint"]),
          P(f"<b>Below R{SIZE_FLOOR:,.0f} there is no step at all.</b> The multipliers are disabled "
            f"under R{SIZE_FLOOR:,.0f} in the engine and they are disabled for me too.", "Body"),
          note(f"⚠️ The account <b>cannot</b> size below {LOTFLOOR} lots. If I draw under R1,000 the "
               f"tier table says 0.01 but the broker floor is {LOTFLOOR} — so my worst day is about "
               f"<b>R{2*pip(0.02)*STOP_CAP:.0f} (two stops)</b>, not the R55 figure in the old notes. "
               f"The −{DAILY_CAP:.0f}% daily cap is what actually contains it.", AMBER)]

    # ── EXIT ────────────────────────────────────────────────────────────────
    F += [P("Exit — Rule 3 in numbers", "H2"),
          table(["Trade progress", "Where my stop goes"], [
              ["Entry", f"Beyond the intermediate swing, <b>capped at {STOP_CAP} pips</b>"],
              [f"<b>+{BE} pips</b>", "Breakeven"],
              [f"<b>+{LOCK} pips</b>", f"Entry <b>+{LOCK - BE}</b>"],
              [f"<b>+{LOCK+MSTEP} pips</b>", f"Entry <b>+{LOCK+MSTEP-MBUF}</b>"],
              [f"<b>+{LOCK+2*MSTEP} pips</b>", f"Entry <b>+{LOCK+2*MSTEP-MBUF}</b>"],
              [f"every +{MSTEP} after", f"lock <b>(milestone − {MBUF})</b>"],
          ], [4.6*cm, 11.6*cm], ["L", "L"]),
          P(f"<b>Target: the nearest qualifying draw, {MIN_TGT} pips minimum.</b> Aim at the "
            f"<b>3-day pool</b> — reached 58% and 61% of the time. The 30-day and 60-day pools are "
            f"reached about one time in five; they are extensions, not objectives.", "Body"),
          P("<b>At the draw I am flat.</b> No trailing past it, no half-position running on.", "Body")]

    # ── PYRAMID ─────────────────────────────────────────────────────────────
    F += [P("Pyramiding — Rule 4 in numbers", "H2"),
          P("An add is permitted only when <b>all four</b> are true:", "Body"),
          table(["#", "Condition"], [
              ["1", f"Price is <b>≥ {PYR_FAV:.0f} pips</b> in profit on the existing position"],
              ["2", f"<b>≥ {MIN_TGT} pips</b> of target still remains"],
              ["3", "The dollar still agrees <b>and</b> at least one higher timeframe still confirms the draw"],
              ["4", f"I am on leg 1 or 2 — <b>maximum {MAX_LEGS} legs</b>, each the same size"],
          ], [1.1*cm, 15.1*cm], ["C", "L"]),
          P(f"Each leg carries its <b>own</b> stop, placed structurally, capped at {STOP_CAP} pips.", "Body"),
          note("<b>An add is never a rescue.</b> If the trade is against me the answer is no. There is "
               "no version of this rule where being underwater permits another entry.", RED)]

    # ── BREAKERS ────────────────────────────────────────────────────────────
    F += [P("The breakers — Rule 5 in numbers", "H2"),
          table(["Trigger", "Action"], [
              [f"<b>−{DAILY_CAP:.0f}% of the day's opening equity</b>", "No new entries for the rest of the day"],
              ["<b>2 stop-outs in a day</b>", "Same — I close the laptop"],
              [f"<b>{CONSEC} losses in a row</b>", "Done for the day"],
              [f"<b>−{SESS_KILL:.0f}% from session open</b>", "Close everything, day over"],
              [f"<b>−{DD_HALT:.0f}% from equity peak</b>", f"<b>{DD_DAYS} calendar days off.</b> No exceptions, no “just one”"],
              ["<b>Just stopped out</b>", "<b>No new trade in that same dollar direction</b>"],
          ], [5.4*cm, 10.8*cm], ["L", "L"]),
          note("<b>On that last one:</b> EURUSD, GBPUSD and NZDUSD are one dollar bet wearing three "
               "names. A long EURUSD and a short GBPUSD is the same position twice, with two spreads. "
               "Blocking that is measured to be worth roughly half a point of profit factor.", NAVY),
          PageBreak()]

    # ── ROUTINE ─────────────────────────────────────────────────────────────
    F += [P("The routine", "H1"), P("Before the session — 15 minutes", "H2"),
          table(["#", "Step"], [
              ["1", "<b>Mark the daily gaps.</b> Nearest unfilled daily gap above and below price, per "
                    "pair, and how far each is. A daily gap fills 90–96% of the time over a median "
                    "5–9 days — this is my map of where price is likely to travel, <b>not</b> a "
                    "direction signal on its own."],
              ["2", "<b>Read the dollar.</b> H1 structure as of yesterday's close — the previous day's "
                    "price action tells the story."],
              ["3", "<b>Read the cross.</b> EURGBP decides which of EUR/GBP to trade. The counters say "
                    "the cross does more filtering work than the dollar."],
              ["4", "<b>Mark the range.</b> Yesterday's high/low, the Asian range, the previous "
                    "session's high/low."],
              ["5", "<b>Check the calendar.</b> High-impact news in the window = no trade."],
              ["6", "<b>Write down what I expect</b> — one sentence, before price moves. This is how I "
                    "find out later whether I read it right or told myself a story afterwards."],
          ], [1.0*cm, 15.2*cm], ["C", "L"])]

    F += [P("During the session", "H2"),
          checks(["Watch for the card. Do not hunt for it.",
                  f"{PER_PAIR} trade per pair. {PER_DAY} total. Then stop looking.",
                  "When it triggers: enter, set stop, set target, <b>walk away from the chart.</b>",
                  "Manage only at the ladder levels. Nothing between them needs me."])]

    F += [P("After the session — 10 minutes", "H2"),
          P("Log every trade. The five fields that matter:", "Body"),
          table(["Field", "Why"], [
              ["Which quality boxes ticked", "Builds the live version of the evidence tables"],
              ["<b>Toward or away from the daily gap</b>, and how far", "The one live open question — see below"],
              ["Did I follow all five rules? <b>Yes / No</b>", "This is the real score"],
              ["If no — which one, and what was I feeling", "The pattern is the point"],
              ["Outcome in <b>R</b>, not rands", "Rands make small accounts feel like failures"],
          ], [7.0*cm, 9.2*cm], ["L", "L"]),
          note("<b>Rule-following is scored separately from profit.</b> A losing trade that followed "
               "all five rules is a <b>good</b> trade. A winning trade that broke one is a <b>bad</b> "
               "trade that happened to pay — and that is the one that teaches the worst habit.", GREEN)]

    F += [P("The one thing I am still collecting data on", "H2"),
          P("Trades pointing <b>at</b> an unfilled daily gap won more often in both halves of the "
            "backtest — <b>+5.1 and +4.2 points</b>. Right sign, right size, twice over, which very "
            "little in this project managed. It could not be <i>proven</i> because it needs roughly "
            "four times the data we have.", "Body"),
          P("So I note it, and I do <b>not</b> force trades around it. After a few months of live "
            "trades I will have something nobody had before: a real record of whether the "
            "toward-the-gap setups are my signature moves.", "Body"),
          PageBreak()]

    # ── BREAKING A RULE + REVIEW ────────────────────────────────────────────
    F += [P("When I break a rule", "H1"),
          P("It will happen. What matters is what happens next.", "Lead"),
          table(["#", ""], [
              ["1", "<b>Write it down the same day</b> — which rule, what I was feeling, what it cost."],
              ["2", "<b>No make-back trade.</b> The rule was broken; adding a second break does not "
                    "repair the first."],
              ["3", "<b>Two breaks in a week → one full week on demo.</b> Not as punishment — because "
                    "two breaks means the rules are not yet automatic, and automatic is the whole point."],
          ], [1.0*cm, 15.2*cm], ["C", "L"]),
          P("Review", "H1"),
          table(["When", "What I look at"], [
              ["<b>Weekly</b>", "Rule-following score. Not P&amp;L. <b>The score.</b>"],
              ["<b>Monthly</b>", "My live win rate and profit factor against the algorithm's "
                                 "<b>43.9%</b> and <b>4.01</b>. If I am below it after 50+ trades, the "
                                 "honest answer is the machine should be running this and I should be "
                                 "supervising."],
              ["<b>At 50 trades</b>", "Re-run the analysis on my own trade log — which of my quality "
                                      "boxes actually predicted anything, tested the same way the "
                                      "algorithm was: controls, and both halves."],
          ], [3.2*cm, 13.0*cm], ["L", "L"]),
          Spacer(1, 0.5*cm), rule(),
          P("Baseline to measure myself against: the algorithm produced <b>736 trades</b> over "
            "2022–2025 — win rate <b>43.9%</b>, profit factor <b>4.01</b>, worst drawdown "
            "<b>−13.24%</b>, turning R1,000 into R132,020 withdrawn plus R8,555 working capital.",
            "Small")]

    doc.build(F)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()

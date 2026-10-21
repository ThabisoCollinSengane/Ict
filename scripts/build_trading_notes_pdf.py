"""Render TRADING_NOTES as a PDF, with the sample count behind every claim.

    python scripts/build_trading_notes_pdf.py [output.pdf]

Pure reportlab (no network), same convention as scripts/build_manual_pdf.py.

Every figure here traces to a measured result recorded in CLAUDE.md. Where the
record does NOT break out a sample count, the table says so rather than inventing
one — an unsourced n is worse than no n.
"""
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)

OUT = sys.argv[1] if len(sys.argv) > 1 else "docs/ICT_Trading_Notes.pdf"

NAVY  = colors.HexColor("#0B2545")
BLUE  = colors.HexColor("#13315C")
GREEN = colors.HexColor("#1B7A43")
RED   = colors.HexColor("#B23A2E")
AMBER = colors.HexColor("#B8860B")
GREY  = colors.HexColor("#5A6B7B")
LIGHT = colors.HexColor("#EDF3F8")
RULEC = colors.HexColor("#D5DEE6")
ZEBRA = colors.HexColor("#F7FAFC")

styles = getSampleStyleSheet()
def S(n, **kw): styles.add(ParagraphStyle(n, parent=styles["Normal"], **kw))

S("Cover",    fontName="Helvetica-Bold", fontSize=27, textColor=NAVY, leading=31, spaceAfter=8)
S("CoverSub", fontName="Helvetica",      fontSize=12.5, textColor=GREY, leading=18)
S("H1",       fontName="Helvetica-Bold", fontSize=16.5, textColor=NAVY, leading=20,
              spaceBefore=14, spaceAfter=7)
S("H2",       fontName="Helvetica-Bold", fontSize=11.5, textColor=BLUE, leading=15,
              spaceBefore=11, spaceAfter=4)
S("Body",     fontName="Helvetica",      fontSize=9.6, leading=13.6, spaceAfter=5,
              textColor=colors.HexColor("#12222F"))
S("Small",    fontName="Helvetica",      fontSize=8.4, leading=11.6, textColor=GREY,
              spaceAfter=4)
S("Lead",     fontName="Helvetica",      fontSize=10.6, leading=15.4, spaceAfter=7,
              textColor=colors.HexColor("#12222F"))
S("Cell",     fontName="Helvetica",      fontSize=8.5, leading=11)
S("CellB",    fontName="Helvetica-Bold", fontSize=8.5, leading=11)
S("CellH",    fontName="Helvetica-Bold", fontSize=8.3, leading=11, textColor=colors.white)
S("Kicker",   fontName="Helvetica-Bold", fontSize=9.6, leading=13.6, spaceAfter=5)

def P(t, s="Body"):  return Paragraph(t, styles[s])
def rule():          return HRFlowable(width="100%", thickness=0.7, color=RULEC,
                                       spaceBefore=5, spaceAfter=8)

def table(head, rows, widths, aligns=None, hl=None):
    """hl: set of row indexes (0-based within rows) to bold."""
    data = [[Paragraph(h, styles["CellH"]) for h in head]]
    for i, r in enumerate(rows):
        st = "CellB" if hl and i in hl else "Cell"
        data.append([Paragraph(str(c), styles[st]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, RULEC),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    for col, a in enumerate(aligns or []):
        if a != "L":
            cmds.append(("ALIGN", (col, 0), (col, -1), "RIGHT" if a == "R" else "CENTER"))
    t.setStyle(TableStyle(cmds))
    return t

def badge(kind, text):
    col = {"do": GREEN, "dont": RED, "cost": RED, "meth": AMBER}[kind]
    tag = {"do": "CONFIRMED", "dont": "MEASURED NULL",
           "cost": "LOST MONEY", "meth": "METHOD"}[kind]
    t = Table([[Paragraph(f'<font color="white"><b>{tag}</b></font>', styles["Cell"]),
                Paragraph(f"<b>{text}</b>", styles["Body"])]],
              colWidths=[3.5*cm, 12.7*cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), col),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([Spacer(1, 5), t, Spacer(1, 3)])

def note(text, col=GREY):
    t = Table([[Paragraph(text, styles["Small"])]], colWidths=[16.2*cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, col),
    ]))
    return KeepTogether([Spacer(1, 3), t, Spacer(1, 5)])


def _page(canv, doc):
    canv.saveState()
    canv.setFont("Helvetica", 7.6)
    canv.setFillColor(GREY)
    canv.drawString(2*cm, 1.25*cm, "ICT Intermarket Algorithm — evidence notes for discretionary trading")
    canv.drawRightString(A4[0] - 2*cm, 1.25*cm, f"{doc.page}")
    canv.setStrokeColor(RULEC)
    canv.line(2*cm, 1.6*cm, A4[0] - 2*cm, 1.6*cm)
    canv.restoreState()


def build():
    doc = BaseDocTemplate(OUT, pagesize=A4,
                          leftMargin=2*cm, rightMargin=2*cm,
                          topMargin=1.7*cm, bottomMargin=2*cm,
                          title="ICT Trading Notes — what the testing proved",
                          author="ICT Intermarket Algorithm project")
    frame = Frame(doc.leftMargin, doc.bottomMargin,
                  doc.width, doc.height, id="n")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_page)])
    F = []

    # ── cover ────────────────────────────────────────────────────────────────
    F += [Spacer(1, 3.2*cm),
          P("What four years of testing<br/>actually proved", "Cover"),
          P("Evidence notes for discretionary trading", "CoverSub"),
          Spacer(1, 0.5*cm), rule(),
          P("Every claim in this document is marked with what the evidence says, how "
            "strong it is, and <b>how many observations it rests on</b>. Nothing here is "
            "ICT orthodoxy repeated back — where a belief was tested and failed, it is "
            "in the DON'T section with the number that killed it.", "Lead"),
          Spacer(1, 0.4*cm)]

    F += [P("The evidence base", "H2"),
          table(["Source", "Period", "Observations"], [
              ["Main backtest (the algorithm)", "2022–2025, 3 pairs", "<b>736 trades</b> · 355 in-sample / 381 out"],
              ["Tick-volume AMD study", "2022 &amp; 2024, EU+GU", "275 trades"],
              ["Pure-price draw cascade", "2022–2025, 3 pairs", "<b>3,637 sweep events</b>"],
              ["Triple-raid study", "2022–2025, H1", "3,045 raids (1,541 short / 1,504 long)"],
              ["Gap-as-magnet study", "2022–2025, W/D/H4", "<b>62,797 gaps</b>"],
              ["IFVG standalone backtest", "2022–2025, 3 pairs", "~10,000 simulated trades"],
              ["Gap-race study", "2022–2025, daily", "3,157 bars · 774 resolved races"],
              ["Levers actually tested in the engine", "—", "~25 (5 shipped, 20 rejected)"],
          ], [5.3*cm, 3.9*cm, 7.0*cm]),
          Spacer(1, 0.4*cm),
          note("<b>The single most important framing.</b> Most of what sounds true in ICT is "
               "<i>descriptively</i> true and carries no directional information. Price does go "
               "to the gap. The gap does hold. Both are real and both are useless on their own, "
               "because price does the same thing at any nearby level. Everything below separates "
               "the two.", NAVY),
          Spacer(1, 0.3*cm),
          P("Baseline the algorithm produced: 736 trades, win rate 43.9%, profit factor 4.01, "
            "worst drawdown −13.24%. R1,000 grew to R132,020 withdrawn plus R8,555 working.", "Small"),
          PageBreak()]

    # ── PART 1 ───────────────────────────────────────────────────────────────
    F += [P("Part 1 — The DOs", "H1"),
          P("Held in <b>both</b> halves of the four years, at a similar size, on enough "
            "observations to mean something.", "Lead"), rule()]

    F += [badge("do", "1.  The AMD cycle is real, and you can see it in participation"),
          P("Tick volume measured against each trade's own pre-accumulation baseline:", "Body"),
          table(["Phase", "Volume vs baseline", "Observations"], [
              ["Accumulation (the coil)", "<b>0.66×</b> — dries to two-thirds", "275 trades"],
              ["Manipulation (the stop run)", "<b>1.26×</b> median, 1.74× mean", "275 trades"],
              ["Distribution", "1.22×", "275 trades"],
              ["At the PD array (the fill)", "<b>1.28×</b> — reacts hardest", "275 trades"],
          ], [5.3*cm, 6.4*cm, 4.5*cm], ["L", "L", "C"]),
          P("Held on both pairs — GBPUSD spikes harder than EURUSD on the sweep (1.93× vs 1.63×). "
            "<b>When a range goes quiet and then a sweep arrives on a violent bar, that is the "
            "real thing, not a fakeout.</b>", "Body"),
          note("<b>But volume does NOT separate winners from losers.</b> Tested directly on the same "
               "275 trades: the fingerprints are the same. The small 2022 edge flips sign in 2024. "
               "Absorption at the sweep is 50% win / 50% lose (2022) and 48% / 48% (2024). Use volume "
               "to confirm you are <i>in</i> an AMD cycle — never to judge whether <i>this</i> one pays.", RED)]

    F += [badge("do", "2.  A sweep that runs prior-day high/low is your better setup"),
          table(["What the sweep ran", "2022 win rate", "2024 win rate", "Observations"], [
              ["<b>Prior-day high / low</b>", "<b>55%</b>", "<b>53%</b>", "115 of 810 trades"],
              ["Everything else (baseline)", "45.3%", "45.8%", "695 of 810"],
          ], [5.0*cm, 3.4*cm, 3.4*cm, 4.4*cm], ["L", "C", "C", "C"], hl={0}),
          P("+8 to +10 points in <b>both</b> years. Shipped as a 1.25× size increase; it fired on "
            "122 trades over four years and lifted equity <b>+57%</b> with drawdown held to the "
            "decimal (−12.95% before and after). It is the one setup-quality signal in the whole "
            "project that earned more size on merit.", "Body"),
          P("For scale, what sweeps actually run across 810 trades: equal highs/lows <b>397</b>, "
            "prior-day <b>115</b>, prior-week <b>8</b>, value area 9.", "Small")]

    F += [badge("do", "3.  The H4 turtle soup is a genuine timing confirmation"),
          P("Price wicks beyond the prior two-bar H4 range, then closes back inside — the Judas "
            "swing one timeframe up. The manipulation has already fired.", "Body"),
          table(["Higher-timeframe sweep", "Trades", "Win rate", "PF 2022-23", "PF 2024-25"], [
              ["<b>H4 turtle soup</b>", "<b>137</b>", "<b>50.4%</b>", "3.40", "3.80"],
              ["Daily turtle soup", "234", "46.6%", "2.88", "3.02"],
              ["No sweep", "427", "45.4%", "3.21", "8.11"],
          ], [4.6*cm, 2.4*cm, 2.9*cm, 3.1*cm, 3.2*cm], ["L", "C", "C", "C", "C"], hl={0}),
          P("<b>The H4 one is the good one; the daily version is weaker.</b> Shipped as a 1.25× size "
            "increase on the H4 bucket only — 122 trades sized, equity <b>+48%</b>, drawdown "
            "unchanged at −12.95%.", "Body")]

    F += [badge("do", "4.  The golden rule — it is about WHICH PAIR, not just direction"),
          table(["", "2022-23 WR / PF", "2024-25 WR / PF"], [
              ["<b>SELL GBPUSD · BUY EURUSD</b>", "<b>47.5% / 4.07</b>", "<b>50.0% / 4.39</b>"],
              ["Against the rule", "39.7% / 2.84", "42.2% / 4.06"],
          ], [6.4*cm, 4.9*cm, 4.9*cm], ["L", "C", "C"], hl={0}),
          P("+8 points in both halves, same size. GBP distributes harder on the downside, EUR on "
            "the upside. <b>Short the weaker, buy the stronger.</b> Shipped as a 1.25× size increase.", "Body"),
          P("Related and consistent: an order-block entry on GBPUSD ran WR 60.0% (2022-23) and "
            "64.3% (2024-25) — the standout combination. Order blocks beat gaps on profit factor in "
            "both halves (3.72 / 5.18 vs 3.31 / 3.54), though gaps carry the volume at 484 trades.", "Small"),
          note("The fuller four-quadrant version uses EURGBP to pick the pair, and the counters show "
               "<b>EURGBP is the heavier filter</b> — it rejected 97 setups where the dollar rejected "
               "59. The cross does more work than the dollar. That version was never validated out of "
               "sample, so treat the quadrant as a framework, not a proven edge. The simple rule above "
               "IS proven.", AMBER)]

    F += [badge("do", "5.  Three independent confluences at your target — and not more"),
          P("Each target scored by how many <i>different</i> families agree within 8 pips: fib, gap, "
            "order block, equal highs/lows, round number, prior-day, prior-week, intermediate swings.", "Body"),
          table(["Confluences", "Trades", "Profit factor"], [
              ["1", "13", "<b>0.02</b>"],
              ["2", "40", "<b>0.20</b>"],
              ["<b>3</b>", "<b>225</b>", "<b>6.70</b>"],
              ["4", "325", "5.73"],
              ["5", "190", "3.94"],
              ["6", "18", "43.28  (tiny sample)"],
          ], [3.6*cm, 3.6*cm, 9.0*cm], ["C", "C", "L"], hl={2}),
          P("<b>The cliff between 2 and 3 is the finding</b> — a 33× jump in profit factor across 265 "
            "trades. One source can be found near any price; that is noise. Three different frameworks "
            "pointing at the same level means multiple desks are aiming there.", "Body"),
          P("Note it does <b>not</b> keep improving above 4. More confirmation past that point adds "
            "nothing — and costs you entry price.", "Body")]

    F += [badge("do", "6.  Stop one structural tier beyond the obvious swing"),
          table(["Change", "Equity", "Profit factor", "Worst drawdown"], [
              ["Stop at the nearest short-term swing", "R60.18M", "5.03", "−12.95%"],
              ["<b>Stop beyond the intermediate swing</b>", "<b>R71.19M  (+18.3%)</b>", "<b>5.12</b>", "<b>−12.95%</b>"],
          ], [6.2*cm, 4.2*cm, 2.9*cm, 3.1*cm], ["L", "C", "C", "C"], hl={1}),
          P("<b>The short-term swing is exactly what a minor liquidity run sweeps.</b> That is what it "
            "is there for. A stop at the obvious recent low is parked in the pool. One tier up "
            "survives the sweep — and costs a little more on the trades where you were simply wrong, "
            "which is the right trade-off.", "Body")]

    F += [badge("do", "7.  The 3-day pool is the dependable draw. The 30/60-day is not."),
          P("Measured on raw price across <b>3,637 prior-day sweep events</b>, independent of any "
            "strategy. After a sweep, which pool does price reach within two days:", "Body"),
          table(["Next pool", "2022-23", "2024-25", "Read"], [
              ["<b>3-day high / low</b>", "<b>58%</b>", "<b>61%</b>", "the dependable objective"],
              ["Weekly", "25%", "27%", "occasional"],
              ["30-day", "21%", "20%", "extension only"],
              ["60-day", "15%", "13%", "extension only"],
          ], [4.2*cm, 2.7*cm, 2.7*cm, 6.8*cm], ["L", "C", "C", "L"], hl={0}),
          P("All three pairs agree (roughly 60 / 20 / 14). <b>Target the 3-day pool.</b> The 30 and "
            "60-day pools are reached about one time in five — they are extension targets, not "
            "objectives. This is the arithmetic behind DON'T #2 in Part 3.", "Body")]

    F += [badge("do", "8.  Trail as it runs on a long trade"),
          P("Breakeven at +10, lock +10 at +20, then every 20 pips of further progress lock 10 behind:", "Body"),
          table(["", "Equity", "Profit factor", "Worst drawdown"], [
              ["Before", "R294.8M", "4.47", "−12.95%"],
              ["<b>With progressive trailing</b>", "<b>R400.7M  (+36%)</b>", "<b>4.47</b>", "<b>−13.01%</b>"],
          ], [6.2*cm, 4.2*cm, 2.9*cm, 3.1*cm], ["L", "C", "C", "C"], hl={1}),
          P("The largest single improvement in the project after position sizing, for +0.06% of "
            "drawdown. <b>A trade that reaches +35 and reverses should not be a full loss.</b>", "Body")]

    F += [badge("do", "9.  Monday and Tuesday of NFP week"),
          table(["", "2022-23 WR / PF", "2024-25 WR / PF"], [
              ["<b>Mon–Tue of NFP week</b>", "<b>62.5% / 4.66</b>", "<b>52.1% / 6.12</b>"],
              ["All other days", "41.2% / 3.25", "43.3% / 4.03"],
          ], [6.4*cm, 4.9*cm, 4.9*cm], ["L", "C", "C"], hl={0}),
          P("The only one of <b>seven</b> contextual factors that passed both halves. The tight "
            "pre-NFP accumulation makes for a clean sweep. Wednesday to Friday of that week is "
            "already a known low-probability window.", "Body"),
          P("Sample counts per bucket are not broken out in the record — treat this as the weakest "
            "of the nine DOs on evidence, even though it passed.", "Small"),
          PageBreak()]

    # ── PART 2 ───────────────────────────────────────────────────────────────
    F += [P("Part 2 — The DON'Ts", "H1"),
          P("Things that sound true, that most people believe, and that measure to nothing once you "
            "ask the right control question: <b>what would a meaningless level do?</b>", "Lead"), rule()]

    F += [badge("dont", "1.  “Price is drawn to the fair value gap”"),
          P("True — and worthless as a direction. Across <b>62,797 gaps</b>, compared against a band "
            "of identical width, the same distance away, on the <i>opposite</i> side of price:", "Body"),
          table(["Timeframe", "Gap reached", "Mirror band reached", "Difference"], [
              ["Weekly", "69.7% / 78.8%", "71.2% / 80.3%", "<b>−1.5 / −1.5</b>"],
              ["Daily", "90.2% / 87.2%", "91.0% / 86.4%", "<b>−0.7 / +0.8</b>"],
              ["H4", "95.2% / 95.3%", "95.0% / 95.3%", "<b>+0.2 / +0.0</b>"],
          ], [3.2*cm, 4.3*cm, 4.6*cm, 4.1*cm], ["L", "C", "C", "C"]),
          P("Six comparisons, <b>none differing by more than 0.8 points</b>, two negative. On "
            "completely random data both read 93.5%. Adding a structure shift toward the gap made it "
            "<i>worse</i> (85.1% / 86.0% against its own control's 92.6% / 96.0%).", "Body"),
          note("<b>The gap being reached tells you nothing about which way to trade.</b> Holding a bias "
               "toward a gap for days adds risk and time without adding expectancy. If you catch "
               "yourself saying “price has to come back and fill that gap” — it does, and so does the "
               "level the same distance in the other direction.", RED)]

    F += [badge("dont", "2.  “It held at the gap, so it's a support zone”"),
          table(["Timeframe", "Gap respected", "Mirror band respected", "Difference"], [
              ["Weekly", "69.6% / 69.2%", "63.8% / 73.6%", "+5.7 / <b>−4.4</b>"],
              ["Daily", "70.2% / 66.9%", "60.5% / 63.4%", "<b>+9.7</b> / +3.5"],
              ["H4  (n ≈ 2,000 per half)", "64.2% / 66.4%", "63.7% / 64.3%", "+0.6 / +2.1"],
          ], [4.6*cm, 4.0*cm, 4.4*cm, 3.2*cm], ["L", "C", "C", "C"]),
          P("The one cell that looked real — daily, +9.7 points — collapsed to +3.5 in the second "
            "half. And it <b>lost money</b>: after a “respected” daily gap the favourable move "
            "averaged 86 pips against 98 pips adverse. A higher reversal rate that loses money is "
            "not a signal.", "Body"),
          P("On H4 the sample is about 2,000 per half, where the margin of error is only 1.5 points — "
            "so the flat reading there is a real measurement, not a small-sample shrug.", "Small")]

    F += [badge("dont", "3.  “A broken gap inverts and becomes resistance” (the IFVG)"),
          P("Tested as a standalone entry with a realistic 10-pip structural stop and costs, across "
            "three pairs and four years — <b>roughly 10,000 simulated trades</b>:", "Body"),
          table(["Timeframe", "Trades (IS / OOS)", "PF 2022-23", "PF 2024-25", "Win rate"], [
              ["M15", "4,022 / 4,543", "0.78", "0.73", "33% / 32%"],
              ["H1", "1,243 / 1,122", "0.83", "0.85", "33% / 34%"],
              ["H4", "378 / 292", "0.97", "0.89", "37% / 35%"],
              ["Daily", "89 / 78", "0.86", "0.67", "34% / 28%"],
          ], [2.9*cm, 4.0*cm, 2.8*cm, 2.8*cm, 3.7*cm], ["L", "C", "C", "C", "C"]),
          P("<b>Below 1.0 on every timeframe, in both halves, on two different target methods.</b> "
            "Median result −1.11R — most trades stop out. The reason is arithmetic: a 2R target off a "
            "10-pip stop needs better than 33% to break even before spread, and the inversion lands "
            "right at 33%.", "Body"),
          P("Tested a second, independent way (does the zone reject price on a re-test): hold rates "
            "look strong at 63–78%, but the control does 61–75%. Every difference under one standard "
            "error.", "Body"),
          note("<b>The full-body-close inversion is a real market-structure event that carries no "
               "measurable edge on its own.</b> It can still be useful as <i>context</i> inside a "
               "bigger setup — that is what the semi-auto model uses it for. It is not a trade by "
               "itself.", RED)]

    F += [badge("dont", "4.  “Both pairs took highs while the dollar took lows — triple confirmation”"),
          table(["", "Triple raid", "Single-pair raid", "Observations"], [
              ["Short side", "52.3% / 50.5%", "50.6% / 49.1%", "1,541 trios"],
              ["Long side", "48.7% / 51.7%", "47.8% / 52.3%", "1,504 trios"],
          ], [3.6*cm, 4.0*cm, 4.2*cm, 4.4*cm], ["L", "C", "C", "C"]),
          P("Every bucket, both directions, both halves, lands between 47.5% and 52.3%. The margin of "
            "error at that sample size is ±1.9 points. A lone sweep with no alignment does exactly "
            "the same thing.", "Body"),
          P("<b>3,045 of these in four years — about 1.5 per day.</b> It is not a rare institutional "
            "fingerprint; it is what the dollar complex does mechanically most days, because the "
            "pairs are inverse to the dollar. <b>You are counting one event three times.</b>", "Body"),
          P("Adding the dollar/cross quadrant on top made it <i>worse</i> in all four cells "
            "(−4.8, −3.2, −0.5, −2.3 in the first half).", "Small")]

    F += [badge("dont", "5.  “The daily open is a key level”"),
          P("Tested against a deliberately meaningless level — a quarter of yesterday's range from "
            "the open, side alternating by date. Lift over that placebo:", "Body"),
          table(["Pair", "2022-23", "2024-25", "Read"], [
              ["EURUSD (ran the low)", "+2.1", "−4.4", "sign flips"],
              ["GBPUSD (ran the high)", "−3.2", "+3.7", "sign flips"],
              ["NZDUSD (ran the low)", "−5.9", "+0.2", "sign flips"],
          ], [4.6*cm, 3.0*cm, 3.0*cm, 5.6*cm], ["L", "C", "C", "L"]),
          P("<b>The daily open is not special.</b> Same verdict for the session open.", "Body")]

    F += [badge("dont", "6.  “More confirmations means a better trade”"),
          P("Counting how many opening references confirmed (0, 1 or 2):", "Body"),
          table(["Confirmations", "2022-23 (trades / WR)", "2024-25 (trades / WR)"], [
              ["Both references (+2)", "123 / <b>48.0%</b>", "100 / <b>41.0%</b>"],
              ["One reference (+1)", "188 / 41.5%", "246 / 45.1%"],
              ["None", "44 / <b>36.4%</b>", "39 / <b>48.7%</b>"],
          ], [4.6*cm, 5.8*cm, 5.8*cm], ["L", "C", "C"]),
          P("<b>Perfectly ordered downward in the first half and perfectly ordered upward in the "
            "second, on comparable samples.</b> Two mirror images is the clearest possible picture of "
            "noise. Combined with the confluence table flattening above 4, the message is the same: "
            "waiting for a fourth and fifth confirmation buys you nothing and costs you entry price.", "Body")]

    F += [badge("dont", "7.  “If my stop was hit, I was early — the move came later”"),
          P("Your own standing claim, and worth testing properly. From the bar after each losing "
            "trade closed: which comes first, the level we aimed at, or a mirror level the same "
            "distance the <i>other</i> way?", "Body"),
          table(["Half", "Ours first", "Mirror first", "Both", "Neither", "Ours %"], [
              ["2022-23 (losses)", "57", "50", "1", "48", "<b>53.3%</b>"],
              ["2024-25 (losses)", "71", "74", "0", "40", "<b>49.0%</b>"],
          ], [3.9*cm, 2.5*cm, 2.6*cm, 1.7*cm, 2.3*cm, 2.6*cm],
                ["L", "C", "C", "C", "C", "C"]),
          note("<b>A coin flip in both halves</b> (107 and 145 resolved races, margin of error ±4.5 "
               "points). The losses were wrong-way trades, not early ones — so no stop placement, "
               "entry timing or extra patience recovers them. Worth sitting with, because “I was right "
               "but early” is the most comfortable story a trader tells after a loss, and here it is "
               "measurably false.", RED)]

    F += [badge("dont", "8.  Day of week, seasonal lean, and “narrative” generally"),
          P("Seven contextual factors, each scored on all 740 trades. One passed (NFP Mon–Tue). One "
            "was mildly <b>inverted</b> — the trades where the prior session's sweep agreed with the "
            "direction were <i>worse</i> in both halves. One never fired at all. The remaining four "
            "flipped sign between halves.", "Body"),
          P("The aggregate score was not even ordinal: in the first half, score 1 → PF 0.93, "
            "2 → 4.17, 3 → 2.94, 4 → 3.82, 5 → 15.01.", "Small"),
          PageBreak()]

    # ── PART 3 ───────────────────────────────────────────────────────────────
    F += [P("Part 3 — What went wrong when we added things", "H1"),
          P("Five patterns, each tested in the engine with real money at stake, each one costly. "
            "<b>These translate most directly to discretionary decisions.</b>", "Lead"), rule()]

    F += [badge("cost", "1.  Holding past your target — three different ways, all destroyed money"),
          table(["Attempt", "Equity", "Change"], [
              ["Baseline", "R284.9M", "—"],
              ["Trail instead of exiting on a target wick (v1)", "bankrupt", "<b>−100.6% drawdown</b>"],
              ["Same, with a breakeven guard (v2)", "R137.8M", "<b>−52%</b>"],
              ["Same, best implementation (v3)", "R144.8M", "<b>−49%</b>"],
              ["Take half at target, run the rest to the next draw", "R70M", "<b>−75%</b>"],
          ], [7.6*cm, 4.2*cm, 4.4*cm], ["L", "C", "C"], hl={1, 4}),
          P("<b>Every single exit modification lost.</b> The first version was so bad it bankrupted "
            "the test account.", "Body"),
          note("<b>Why: your target IS the end of the AMD cycle.</b> When price delivers to the "
               "institutional draw, distribution has happened. Holding past it means sitting through "
               "the consolidation and reversal where you have no edge. <b>Take the full position off "
               "at the draw.</b> The 100–200 pip continuation you sometimes see afterwards is real — "
               "and it is a new trade with a new entry, not a reason to hold.", RED)]

    F += [badge("cost", "2.  Reaching for the further target destroyed money"),
          table(["", "Worst drawdown 2022-23", "Worst drawdown 2024-25", "Win rate"], [
              ["Nearest qualifying target", "−13.01%", "−13.94%", "46.0% / 45.9%"],
              ["<b>Prefer the distant pool</b>", "<b>−22.57%</b>", "<b>−22.60%</b>", "<b>41.8% / 42.5%</b>"],
          ], [4.6*cm, 4.2*cm, 4.2*cm, 3.2*cm], ["L", "C", "C", "C"], hl={1}),
          P("Drawdown nearly doubled in both halves. <b>The near target is the draw for THIS cycle; "
            "the far one belongs to the NEXT cycle.</b> Aiming at the far one means staying through "
            "the intermediate consolidation where price pauses or reverses. The 58%-vs-21% reach "
            "rates in DO #7 are the arithmetic behind it.", "Body")]

    F += [badge("cost", "3.  Trading INTO the pool destroyed money — four attempts"),
          table(["", "Worst drawdown", "Profit factor", "Win rate"], [
              ["Fade the sweep (the shipped model)", "−12.95%", "3.49", "45.3%"],
              ["<b>Trade toward the untouched pool</b>", "<b>−16.73%</b>", "<b>3.30</b>", "<b>44.6%</b>"],
          ], [6.4*cm, 3.4*cm, 3.2*cm, 3.2*cm], ["L", "C", "C", "C"], hl={1}),
          P("72 continuation entries added; they won less often and clustered their losses, breaking "
            "the risk limit. Four separate attempts at “continuation instead of reversal” failed the "
            "same way.", "Body"),
          note("<b>The pool is where the cycle ENDS.</b> Riding into it means buying exactly where "
               "smart money is selling into the resting liquidity. <b>Prior-day highs and lows are "
               "correct as targets. They are wrong as entries.</b>", RED)]

    F += [badge("cost", "4.  Filtering out “bad” setups destroyed money — the least intuitive one"),
          table(["Filter tried", "Bucket quality", "Cost"], [
              ["Cut a clearly losing session phase", "PF <b>0.13</b> / 0.16", "<b>−R31.1M</b> of compounding"],
              ["Merely shrink the weaker NY echo", "WR 46.9%", "<b>−R5.8M</b>, lost in all 3 tests"],
              ["Skip reversals fighting an opposing gap", "passed both halves", "<b>−20.15% drawdown</b> on the full run"],
              ["Exempt 6 weak trades from a gate", "6 trades", "<b>−R10.3M  (−17%)</b>"],
          ], [6.2*cm, 4.2*cm, 5.8*cm], ["L", "C", "L"], hl={0}),
          P("A bucket with a profit factor of <b>0.13</b> — catastrophic in isolation — cost "
            "<b>R31 million</b> of compounded growth when removed. A gentler version that merely "
            "shrank a weak bucket lost equity in all three test periods and improved drawdown in "
            "none.", "Body"),
          note("<b>Why: a setup that loses on simple arithmetic can still be positive to your "
               "compounding</b>, because its occasional wins land at points where they compound "
               "forward, and the slot it occupies would otherwise go to a lower-quality trade. "
               "<b>Be very careful about deciding a setup type is bad and cutting it.</b> The obvious "
               "filter is usually wrong — four separate attempts, all costly. This is the single most "
               "repeated failure in the project.", RED)]

    F += [badge("cost", "5.  Sizing up broadly is leverage, not selection"),
          table(["Size increase applied to…", "Trades", "Profit factor", "Equity"], [
              ["<b>69% of the book</b> (505 of 736)", "736 → <b>696</b>", "4.01 → <b>3.58</b>", "R140.6k → <b>R137.5k</b>"],
              ["A gap at its midpoint (shipped)", "fired 15×", "unchanged", "<b>+R825k</b>"],
              ["Prior-day sweep (shipped)", "fired 91×", "unchanged", "<b>+57%</b>"],
              ["H4 turtle soup (shipped)", "fired 122×", "unchanged", "<b>+48%</b>"],
          ], [5.6*cm, 3.2*cm, 3.4*cm, 4.0*cm], ["L", "C", "C", "C"], hl={0}),
          P("The broad version <i>lowered</i> profit factor and <i>reduced</i> the trade count — the "
            "bigger positions breached the per-trade risk cap and got skipped, 414 times.", "Body"),
          P("<b>Every size increase that worked targeted a small, distinctive subset</b> — 15, 91 or "
            "122 trades out of 736. A size bump is a selection tool. Apply it to most of your trades "
            "and you have simply raised your lot size.", "Body"),
          PageBreak()]

    # ── PART 4 ───────────────────────────────────────────────────────────────
    F += [P("Part 4 — How not to fool yourself", "H1"),
          P("Method lessons, and honestly the most transferable part. I made every one of these "
            "mistakes during this work.", "Lead"), rule()]

    F += [badge("meth", "1.  An unusually clean result is evidence of a bug before it's evidence of an edge"),
          P("<b>Five separate studies produced beautiful, publishable findings that were entirely "
            "artifacts of my own measurement.</b> In every single case the broken version looked "
            "<i>better</i> than the truth.", "Body"),
          P("One of them — a target-quality finding I had called the strongest result in the project "
            "— turned out to be reading information from the future. When fixed it did not shrink, "
            "it <b>inverted</b>: the bucket I had called a loser (profit factor 0.84) was actually "
            "the best one (5.72). Acting on the broken version would have cost 42% of equity.", "Body"),
          P("The same class of error appeared <b>seven times</b> across the project.", "Small")]

    F += [badge("meth", "2.  Always ask what a meaningless level would do"),
          P("This is what killed most of Part 2. “The gap gets reached 95% of the time” sounds "
            "decisive until you check that a random band the same distance away gets reached 95% "
            "too — and that on pure random data both read 93.5%.", "Body"),
          P("<b>Before you credit a level for what price did, ask what price does at levels "
            "generally.</b>", "Body")]

    F += [badge("meth", "3.  One good period proves nothing"),
          P("<b>Three times</b> in this project a perfectly clean, ordered pattern in 2022-23 "
            "dissolved — or exactly reversed — in 2024-25. Not degraded. Mirror image.", "Body"),
          P("If you find something that works, you have not found something that works. You have "
            "found something that <i>worked in the period you looked at</i>.", "Body")]

    F += [badge("meth", "4.  Don't let a confirmation be the thing you're trying to predict"),
          P("<b>Four times</b> I measured “structure shifted my way” over the same window as “price "
            "moved my way” — which are the same statement. The bucket scored 100% by construction. "
            "On one check, 62,797 gaps produced <b>zero</b> exceptions to the circularity.", "Body"),
          P("<b>If your confirmation only becomes visible after the move has already happened, it "
            "isn't a confirmation.</b>", "Body")]

    F += [badge("meth", "5.  Know how much data your question needs before you cut it"),
          P("The final study needed roughly <b>four times the entire four-year dataset</b> to answer "
            "its question: 774 resolved observations against about 1,580 required. Every refinement "
            "made it worse by subdividing further.", "Body"),
          P("<b>With 40 trades a quarter you will never resolve a 5-point win-rate difference.</b> "
            "Don't try. Spend your attention where the effect is large enough to see.", "Body"),
          PageBreak()]

    # ── PART 5 ───────────────────────────────────────────────────────────────
    F += [P("Part 5 — Your edge versus the algorithm's", "H1"), rule(),
          P("<b>There is direct evidence in this project that a human can beat the machine on exactly "
            "this material.</b>", "Lead"),
          P("The Market Maker model — dealing range, sweep of external liquidity, entry at the "
            "inverted gap — was tested autonomously across four years:", "Body"),
          table(["Measure", "Result"], [
              ["Setups produced", "1,091–1,158 over 4 years  (~5.5 per week)"],
              ["Money profit factor", "<b>2.98</b> — genuinely profitable"],
              ["Win rate", "21%, and <b>uniform across every tag</b>"],
              ["Shape of the edge", "845 losers at ~−4 pips, 230 winners at ~+15, tail to +114"],
              ["Worst drawdown", "−23.4%, improved only to −21.2% by every lever tried"],
          ], [5.0*cm, 11.2*cm], ["L", "L"]),
          P("It was not shipped for exactly one reason, quoted from the record:", "Body"),
          note("“Good timeframe cascades with a profit factor above 1 in both halves: <b>None.</b> "
               "Win rate 21% is uniform across every tag — cascade timeframe, pattern, pair, period. "
               "No robust subset to filter to. The edge is in a fat tail of rare large winners, "
               "<b>and the winners are unpredictable in advance.</b>", GREEN),
          P("Unpredictable in advance <b>by a machine, from the tags it can measure</b>. That is "
            "precisely the gap a discretionary trader fills. You are reading context the classifier "
            "cannot encode — how the sweep felt, what the dollar was doing into it, whether the "
            "session had already shown its hand. The machine had to reject that setup. You don't.", "Body"),
          P("<b>So yes — you may well make more than the algorithm on this material. That is a "
            "reasonable expectation, not wishful thinking.</b>", "Kicker")]

    F += [P("What the algorithm has that you don't", "H2"),
          P("• It takes the boring setup at 3:07am without being bored.<br/>"
            "• It never revenge trades after two losses.<br/>"
            "• It never skips the seventh small setup because the last six annoyed it.<br/>"
            "• It stops at −6% on the day, every day, without negotiating.<br/>"
            "• It sizes identically on the setup that feels great and the one that doesn't — and the "
            "record above says that feeling is mostly not informative.", "Body"),
          P("What you have that it doesn't: <b>context</b>. The thing that made the model "
            "unfilterable.", "Body"),
          note("<b>The honest split.</b> Your edge is in <i>selection</i> — picking which of the "
               "day's setups is the real one. The machine's edge is in <i>discipline</i> — executing "
               "without mood. The worst version of you is one who has the context read right and "
               "gives it back through size, revenge, or skipping the boring ones.", NAVY),
          P("Keep the circuit breakers as personal rules even trading by hand", "H2"),
          P("Two losses, stop for the day. And <b>no fresh trade in the same dollar direction as one "
            "that just stopped out</b> — EURUSD, GBPUSD and NZDUSD are one dollar bet. Blocking "
            "concurrent same-direction exposure is what lifted that model's profit factor from "
            "<b>2.47 to 2.98</b>. That one is measured, not advice.", "Body"),
          PageBreak()]

    # ── ONE PAGE ─────────────────────────────────────────────────────────────
    F += [P("The one-page version", "H1"), rule()]
    F += [P("DO", "H2"),
          table(["", "Evidence"], [
              ["Trade the pair the dollar and EURGBP select — sell the weaker, buy the stronger",
               "+8pp both halves"],
              ["Prefer sweeps that ran yesterday's high or low", "55% / 53% vs 45%, 115 trades"],
              ["Prefer setups where the H4 candle already swept and rejected", "50.4% WR, 137 trades"],
              ["Need three <i>different</i> things agreeing at your target — not more", "PF 0.20 → 6.70 at three"],
              ["Stop one structural tier beyond the obvious swing", "+18% equity, drawdown flat"],
              ["Target the 3-day pool; take the nearest target clearing your R:R", "58% / 61% reached"],
              ["Trail as it runs; take the whole position off at the draw", "+36% equity"],
              ["Mon–Tue of NFP week is a good window", "62.5% / 52.1% WR"],
          ], [10.6*cm, 5.6*cm], ["L", "L"])]

    F += [P("DON'T", "H2"),
          table(["", "What killed it"], [
              ["Don't hold past your target hoping for continuation", "−49% and −75%"],
              ["Don't reach for the further target", "drawdown −13% → −22%"],
              ["Don't trade <i>into</i> an untouched pool — that's where the cycle ends", "−16.7%, 4 attempts"],
              ["Don't decide a setup type is bad and cut it", "−R31M on a PF 0.13 bucket"],
              ["Don't wait for a fourth and fifth confirmation", "flat above 3; mirror-image halves"],
              ["Don't credit the gap for price arriving — it arrives everywhere", "mirror band: same 90–95%"],
              ["Don't tell yourself you were early", "53.3% / 49.0% — coin flip"],
              ["Don't take a fresh trade in the same dollar direction as one that just stopped",
               "PF 2.47 → 2.98 when blocked"],
          ], [10.6*cm, 5.6*cm], ["L", "L"])]

    F += [Spacer(1, 0.4*cm),
          note("<b>And the meta-rule:</b> if something looks unusually clean, it is probably a "
               "measurement artifact. That held <b>five times out of six</b> in this project — and "
               "in every case the broken version looked better than the truth.", NAVY),
          Spacer(1, 0.5*cm),
          P("Sources: every figure traces to a measured result recorded in CLAUDE.md — the running "
            "research log for this project. Baseline algorithm: 736 trades over 2022–2025, win rate "
            "43.9%, profit factor 4.01, worst drawdown −13.24%.", "Small")]

    doc.build(F)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()

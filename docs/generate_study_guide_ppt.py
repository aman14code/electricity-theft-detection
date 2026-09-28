"""
PowerGuard — Complete Deep Dive Study Guide PPT Generator
Creates a professional, content-rich PowerPoint presentation.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PPT = os.path.join(SCRIPT_DIR, "PowerGuard_Deep_Dive_Study_Guide.pptx")

# ─── Color Palette ────────────────────────────────────────
BLUE       = RGBColor(41, 128, 185)
DARK_BLUE  = RGBColor(23, 32, 42)
DARK       = RGBColor(44, 62, 80)
GREY       = RGBColor(100, 100, 100)
LIGHT_GREY = RGBColor(180, 180, 180)
WHITE      = RGBColor(255, 255, 255)
GREEN      = RGBColor(39, 174, 96)
RED        = RGBColor(231, 76, 60)
ORANGE     = RGBColor(243, 156, 18)
AMBER      = RGBColor(241, 196, 15)
TEAL       = RGBColor(26, 188, 156)
PURPLE     = RGBColor(142, 68, 173)
BG_DARK    = RGBColor(30, 39, 46)
BG_CARD    = RGBColor(45, 52, 54)
ACCENT     = RGBColor(52, 152, 219)


def add_bg(slide, color=BG_DARK):
    """Fill slide background with solid color."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_shape(slide, left, top, width, height, color, alpha=None):
    """Add a rounded rectangle shape."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def add_text_box(slide, left, top, width, height):
    """Add a text box and return its text frame."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    return txBox.text_frame


def set_text(tf, text, size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT, font_name="Calibri"):
    """Set text in a text frame."""
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    return p


def add_para(tf, text, size=14, bold=False, color=WHITE, align=PP_ALIGN.LEFT, space_before=Pt(4), space_after=Pt(2), font_name="Calibri"):
    """Add a paragraph to a text frame."""
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    p.font.name = font_name
    p.alignment = align
    p.space_before = space_before
    p.space_after = space_after
    return p


def add_bullet(tf, text, size=13, color=WHITE, level=0, bold=False):
    """Add a bullet point."""
    p = tf.add_paragraph()
    p.text = text
    p.font.size = Pt(size)
    p.font.color.rgb = color
    p.font.name = "Calibri"
    p.font.bold = bold
    p.level = level
    p.space_before = Pt(3)
    p.space_after = Pt(1)
    return p


# ═══════════════════════════════════════════════════════════
# SLIDE BUILDERS
# ═══════════════════════════════════════════════════════════

def slide_title(prs):
    """Slide 1: Title slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    add_bg(slide, RGBColor(15, 22, 36))

    # Accent line
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(2.6), Inches(10), Pt(4))
    shape.fill.solid(); shape.fill.fore_color.rgb = BLUE; shape.line.fill.background()

    # Title
    tf = add_text_box(slide, Inches(0.8), Inches(1.0), Inches(8.4), Inches(1.2))
    set_text(tf, "POWERGUARD", size=44, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

    # Subtitle
    tf2 = add_text_box(slide, Inches(0.8), Inches(1.8), Inches(8.4), Inches(0.8))
    set_text(tf2, "Electricity Theft Detection System", size=24, color=WHITE, align=PP_ALIGN.CENTER)

    # Tagline
    tf3 = add_text_box(slide, Inches(1.5), Inches(3.0), Inches(7), Inches(0.6))
    set_text(tf3, "Complete Deep Dive Study Guide", size=20, color=LIGHT_GREY, align=PP_ALIGN.CENTER)

    # Key stats boxes
    stats = [
        ("8", "Detection\nFactors"),
        ("5", "ML\nModels"),
        ("47+", "Engineered\nFeatures"),
        ("4", "Micro-\nservices"),
    ]
    for i, (num, label) in enumerate(stats):
        x = Inches(1.0 + i * 2.2)
        card = add_shape(slide, x, Inches(4.0), Inches(1.8), Inches(1.4), BG_CARD)
        tf = card.text_frame
        tf.word_wrap = True
        set_text(tf, num, size=36, bold=True, color=BLUE, align=PP_ALIGN.CENTER)
        add_para(tf, label, size=11, color=LIGHT_GREY, align=PP_ALIGN.CENTER)

    # Footer
    tf4 = add_text_box(slide, Inches(1), Inches(6.5), Inches(8), Inches(0.4))
    set_text(tf4, "ML + Heuristic Hybrid  |  SGCC Dataset  |  Ensemble Strategy  |  SHAP Explainability", 
             size=10, color=GREY, align=PP_ALIGN.CENTER)


def slide_problem(prs):
    """Slide 2: The Problem."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
    set_text(tf, "THE PROBLEM: Electricity Theft", size=28, bold=True, color=BLUE)

    # Left content
    tf2 = add_text_box(slide, Inches(0.5), Inches(1.2), Inches(4.5), Inches(4.5))
    set_text(tf2, "Non-Technical Loss (NTL)", size=18, bold=True, color=WHITE)
    add_bullet(tf2, "India loses ~Rs.1.5 lakh crore/year to theft", color=WHITE)
    add_bullet(tf2, "Globally: $96 billion problem", color=WHITE)
    add_bullet(tf2, "20-25% of total electricity generated is stolen", color=WHITE)
    add_para(tf2, "", size=6)
    add_para(tf2, "Why Can't Humans Find It?", size=16, bold=True, color=ORANGE)
    add_bullet(tf2, "Manual inspection covers only 2-5% of meters/year", color=LIGHT_GREY)
    add_bullet(tf2, "Skilled thieves make it visually undetectable", color=LIGHT_GREY)
    add_bullet(tf2, "Inspections cost Rs.500-2000 per visit", color=LIGHT_GREY)
    add_bullet(tf2, "Data spoofing leaves zero physical evidence", color=LIGHT_GREY)

    # Right card
    card = add_shape(slide, Inches(5.3), Inches(1.2), Inches(4.2), Inches(4.5), BG_CARD)
    tf3 = card.text_frame
    tf3.word_wrap = True
    set_text(tf3, "Our Solution", size=18, bold=True, color=GREEN)
    add_para(tf3, "", size=6)
    add_bullet(tf3, "Use smart meter telemetry data (already being collected)", color=WHITE)
    add_bullet(tf3, "6 dimensions: consumption, voltage, current, power factor, frequency, tamper", color=WHITE)
    add_bullet(tf3, "ML + rule-based heuristics to find anomalies", color=WHITE)
    add_bullet(tf3, "Explainable results operators can act on", color=WHITE)
    add_para(tf3, "", size=6)
    add_para(tf3, "Technical Loss vs NTL", size=14, bold=True, color=AMBER)
    add_bullet(tf3, "Technical: Heat in wires (physics, predictable)", size=12, color=LIGHT_GREY)
    add_bullet(tf3, "Non-Technical: Theft (anomalous patterns, ML detectable)", size=12, color=LIGHT_GREY)


def slide_6_dimensions(prs):
    """Slide 3: The 6 Input Dimensions."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
    set_text(tf, "THE 6 INPUT DIMENSIONS", size=28, bold=True, color=BLUE)

    dims = [
        ("1. Consumption", "kWh", "0.5-20", "How much electricity consumed", BLUE),
        ("2. Voltage", "Volts", "190-250V", "Electrical pressure in line", TEAL),
        ("3. Current", "Amps", "0.5-30A", "Flow of electrons through meter", GREEN),
        ("4. Power Factor", "0-1", "0.85-1.0", "Real/Apparent power ratio", ORANGE),
        ("5. Frequency", "Hz", "49.5-50.5", "Grid oscillation rate", PURPLE),
        ("6. Tamper Flag", "Bool", "false", "Hardware sensor trigger", RED),
    ]

    for i, (name, unit, normal, desc, color) in enumerate(dims):
        row = i // 3
        col = i % 3
        x = Inches(0.4 + col * 3.15)
        y = Inches(1.2 + row * 2.5)
        card = add_shape(slide, x, y, Inches(2.95), Inches(2.2), BG_CARD)
        tf2 = card.text_frame
        tf2.word_wrap = True
        set_text(tf2, name, size=14, bold=True, color=color)
        add_para(tf2, f"Unit: {unit}", size=11, color=LIGHT_GREY)
        add_para(tf2, f"Normal: {normal}", size=11, color=LIGHT_GREY)
        add_para(tf2, desc, size=12, color=WHITE, space_before=Pt(8))

    tf3 = add_text_box(slide, Inches(0.5), Inches(6.4), Inches(9), Inches(0.4))
    set_text(tf3, "Different theft techniques disturb different dimensions -- that's why we analyze all 6 together", 
             size=11, color=AMBER, align=PP_ALIGN.CENTER)


def slide_8_factors_overview(prs):
    """Slide 4: 8 Detection Factors Overview."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.7))
    set_text(tf, "THE 8 DETECTION FACTORS (Overview)", size=28, bold=True, color=BLUE)

    factors = [
        ("Consumption Drop", "25%", "Meter bypass during daytime", BLUE),
        ("Tamper Detection", "20%", "Physical hardware tampering", RED),
        ("Current Anomaly", "15%", "Current shunted around meter", TEAL),
        ("Voltage Anomaly", "10%", "Voltage manipulation", ORANGE),
        ("Power Factor", "10%", "Load manipulation via capacitors", PURPLE),
        ("Pattern Irregularity", "10%", "Day/night inversion, chaos", GREEN),
        ("Frequency Deviation", "5%", "Illegal grid tapping", AMBER),
        ("Flat-line Detection", "5%", "Spoofed/replayed data", LIGHT_GREY),
    ]

    for i, (name, weight, desc, color) in enumerate(factors):
        row = i // 2
        col = i % 2
        x = Inches(0.4 + col * 4.8)
        y = Inches(1.1 + row * 1.25)
        card = add_shape(slide, x, y, Inches(4.5), Inches(1.05), BG_CARD)
        tf2 = card.text_frame
        tf2.word_wrap = True
        set_text(tf2, f"{name}  [{weight}]", size=14, bold=True, color=color)
        add_para(tf2, desc, size=11, color=LIGHT_GREY)

    # Bottom note
    tf3 = add_text_box(slide, Inches(0.5), Inches(6.2), Inches(9), Inches(0.6))
    set_text(tf3, "Each factor scores 0.0 (clean) to 1.0 (theft). Combined via weighted average + boosting logic.", 
             size=12, color=AMBER, align=PP_ALIGN.CENTER)


def slide_factor_detail(prs, num, name, weight, detects, physics, formula, why_weight, color):
    """Slide template for individual factor deep dive."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    # Header
    tf = add_text_box(slide, Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    set_text(tf, f"FACTOR {num}: {name.upper()}  [Weight: {weight}]", size=24, bold=True, color=color)

    # Left: What & Physics
    tf2 = add_text_box(slide, Inches(0.5), Inches(1.0), Inches(4.5), Inches(5.0))
    set_text(tf2, f"What it detects:", size=14, bold=True, color=AMBER)
    add_para(tf2, detects, size=13, color=WHITE)
    add_para(tf2, "", size=6)
    add_para(tf2, "The Physics / Logic:", size=14, bold=True, color=AMBER)
    for line in physics:
        add_bullet(tf2, line, size=12, color=LIGHT_GREY)

    # Right: Formula & Why
    card = add_shape(slide, Inches(5.2), Inches(1.0), Inches(4.3), Inches(5.0), BG_CARD)
    tf3 = card.text_frame
    tf3.word_wrap = True
    set_text(tf3, "Algorithm:", size=14, bold=True, color=GREEN)
    for line in formula:
        add_para(tf3, line, size=11, color=WHITE)
    add_para(tf3, "", size=6)
    add_para(tf3, f"Why {weight} weight?", size=14, bold=True, color=ORANGE)
    add_para(tf3, why_weight, size=12, color=LIGHT_GREY)


def slide_factors_1_to_4(prs):
    """Slides 5-8: Factors 1-4 deep dive."""
    slide_factor_detail(prs, 1, "Consumption Drop", "25%",
        "Meter bypass during daytime hours",
        [
            "Zero kWh during 8AM-8PM is impossible",
            "People use ACs, fridges, lights during day",
            "Zero during peak hours = bypassed meter",
            "Also checks: avg < 30% of baseline",
        ],
        [
            "Filter to peak hours (8AM-8PM)",
            "Count zero-kWh readings",
            "Score = min(1.0, (zeros/total) x 5)",
            "If avg < 30% baseline -> floor at 0.7",
            "x5 multiplier: 20% zeros = score 1.0",
        ],
        "Strongest single indicator. Appears in 70%+ of confirmed theft cases.",
        BLUE)

    slide_factor_detail(prs, 2, "Current Anomaly", "15%",
        "Physical meter bypass (current shunted around meter)",
        [
            "Ohm's Law: P = V x I",
            "If voltage=220V, current=0.05A, but consumption>0",
            "-> Physically IMPOSSIBLE without bypass",
            "Current must flow through bypass wire",
        ],
        [
            "Find: current<0.1A AND voltage>200V",
            "  AND consumption>0",
            "Score = min(1.0, (count/total) x 4)",
            "Zero current + consumption>0.5 -> x8 boost",
            "Violates basic electrical physics",
        ],
        "Physics-based signal. Very hard to fake or explain away. Less common than consumption drops.",
        TEAL)

    slide_factor_detail(prs, 3, "Tamper Detection", "20%",
        "Physical tampering with meter hardware",
        [
            "Smart meters have accelerometers,",
            "  reed switches, case-open detectors",
            "Physical opening/shaking/magnet -> tamper flag",
            "Consecutive flags = sustained tampering",
            "Random faults are isolated (1-2 flags)",
        ],
        [
            "Score = min(1.0, tamper_ratio x 10)",
            "  -> 10% tamper rate = score 1.0",
            "",
            "Consecutive check:",
            "  5+ consecutive flags -> score 0.9",
            "  (deliberate, not random noise)",
        ],
        "Physical hardware signal. Very reliable but can have false positives (storms, accidents).",
        RED)

    slide_factor_detail(prs, 4, "Voltage Anomaly", "10%",
        "Voltage manipulation to reduce metered consumption",
        [
            "Thieves use 'voltage divider' devices",
            "Energy = V x I x t",
            "Lower voltage = lower recorded consumption",
            "Safe band: 190V-250V (India standard)",
            "Extreme (<170V or >270V) = deliberate",
        ],
        [
            "Count readings outside 190-250V",
            "Score = min(1.0, (outliers/total) x 3)",
            "",
            "Extreme voltage (<170V or >270V):",
            "  5x multiplier (deliberate manipulation)",
            "  vs grid fluctuation",
        ],
        "Voltage issues CAN be legitimate (grid problems during monsoon). Weighted lower for this reason.",
        ORANGE)


def slide_factors_5_to_8(prs):
    """Slides 9-12: Factors 5-8 deep dive."""
    slide_factor_detail(prs, 5, "Power Factor", "10%",
        "Load manipulation using capacitor banks",
        [
            "PF = Real Power / Apparent Power",
            "PF=1.0: perfect efficiency",
            "PF=0.3: 70% energy wasted as reactive",
            "Thieves use capacitors to create low PF",
            "Meter records less 'real power'",
        ],
        [
            "Count readings where PF < 0.5",
            "Score = min(1.0, (low_pf/total) x 3)",
            "",
            "Cross-reference:",
            "  PF<0.3 AND consumption<20% baseline",
            "  -> x5 multiplier (VERY strong signal)",
        ],
        "Low PF alone can be legitimate (old motors). Combined with low consumption = strong theft signal.",
        PURPLE)

    slide_factor_detail(prs, 6, "Pattern Irregularity", "10%",
        "Reversed, chaotic, or artificially manipulated patterns",
        [
            "Normal: peaks at 8AM and 7PM",
            "Theft: HIGH at 2AM, ZERO during day",
            "Stealing when inspectors aren't watching",
            "Also detects erratic/random patterns",
        ],
        [
            "CV = std / mean",
            "Score = min(1.0, (CV-0.5) / 1.5)",
            "",
            "Day/Night Inversion:",
            "  night_avg > 2x day_avg -> 0.6",
            "  day=0 but night>0 -> 0.85",
            "  mean=0 (active meter) -> 0.8",
        ],
        "Catches behavioral anomalies that physics-based measures miss.",
        GREEN)

    slide_factor_detail(prs, 7, "Frequency Deviation", "5%",
        "Grid-level anomalies from illegal high-power tapping",
        [
            "India grid: exactly 50 Hz (+/- 0.5 Hz)",
            "Most tightly controlled grid parameter",
            "Deviations: large illegal loads tapping in",
            "Or generator running unsynchronized",
        ],
        [
            "Normal band: 49.0 - 51.0 Hz",
            "Count readings outside band",
            "Score = min(1.0, (outliers/total) x 4)",
            "",
            "Weak individual signal",
            "Useful in combination with others",
        ],
        "Frequency affects entire grid, not just one meter. Weakest individual signal but adds value in ensemble.",
        AMBER)

    slide_factor_detail(prs, 8, "Flat-line Detection", "5%",
        "Spoofed/replayed meter data (hacked firmware)",
        [
            "Real consumption is NEVER perfectly constant",
            "Even a fridge has compressor cycles",
            "Same kWh for 24 hours = pre-recorded fake data",
            "Very specific attack (firmware hacking)",
        ],
        [
            "unique_ratio = unique_values / total",
            "Score = min(1.0, (1-unique_ratio)x2 - 0.5)",
            "",
            "Last-24 check:",
            "  <= 2 unique values in 24 readings",
            "  -> score floor at 0.9",
        ],
        "Very specific attack type. When present, extremely obvious. But rare (requires technical sophistication).",
        LIGHT_GREY)


def slide_weighted_scoring(prs):
    """Slide: How the 8 factors combine."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "WEIGHTED SCORING & BOOSTING LOGIC", size=28, bold=True, color=BLUE)

    # Formula
    card1 = add_shape(slide, Inches(0.4), Inches(1.0), Inches(9.2), Inches(1.4), BG_CARD)
    tf2 = card1.text_frame; tf2.word_wrap = True
    set_text(tf2, "The Formula:", size=16, bold=True, color=GREEN)
    add_para(tf2, "theft_prob = (drop x 0.25) + (tamper x 0.20) + (current x 0.15) + (voltage x 0.10)", size=12, color=WHITE)
    add_para(tf2, "           + (PF x 0.10) + (pattern x 0.10) + (freq x 0.05) + (flatline x 0.05)", size=12, color=WHITE)

    # Boosting rules
    card2 = add_shape(slide, Inches(0.4), Inches(2.6), Inches(4.3), Inches(2.4), BG_CARD)
    tf3 = card2.text_frame; tf3.word_wrap = True
    set_text(tf3, "Boost Rule 1: Multi-Measure Agreement", size=13, bold=True, color=ORANGE)
    add_para(tf3, "If 3+ factors score above 0.5:", size=12, color=WHITE)
    add_para(tf3, "  theft_prob = min(1.0, theft_prob x 1.3)", size=12, color=AMBER)
    add_para(tf3, "", size=4)
    add_para(tf3, "Why? Multiple independent detectors agreeing means real probability is HIGHER than weighted average.", size=11, color=LIGHT_GREY)

    card3 = add_shape(slide, Inches(5.0), Inches(2.6), Inches(4.6), Inches(2.4), BG_CARD)
    tf4 = card3.text_frame; tf4.word_wrap = True
    set_text(tf4, "Boost Rule 2: High-Confidence Floor", size=13, bold=True, color=RED)
    add_para(tf4, "If ANY factor >= 0.9:", size=12, color=WHITE)
    add_para(tf4, "  theft_prob = max(0.40, theft_prob)", size=12, color=AMBER)
    add_para(tf4, "", size=4)
    add_para(tf4, "Why? One factor screaming 'theft' at 0.9 should NEVER be washed out by 7 clean factors.", size=11, color=LIGHT_GREY)

    # Threshold
    card4 = add_shape(slide, Inches(0.4), Inches(5.2), Inches(9.2), Inches(1.0), BG_CARD)
    tf5 = card4.text_frame; tf5.word_wrap = True
    set_text(tf5, "Decision Threshold: anomaly_flag = true if probability >= 30%", size=14, bold=True, color=GREEN)
    add_para(tf5, "Why 30% (not 50%)?  Missing a thief costs Rs.50,000+/year. A false alarm costs Rs.500 (one inspection). 100:1 cost ratio.", size=12, color=LIGHT_GREY)


def slide_worked_example(prs):
    """Slide: Worked example of scoring."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "WORKED EXAMPLE: Scoring a Suspicious Meter", size=24, bold=True, color=BLUE)

    card = add_shape(slide, Inches(0.4), Inches(1.0), Inches(9.2), Inches(5.5), BG_CARD)
    tf2 = card.text_frame; tf2.word_wrap = True
    set_text(tf2, "Factor Scores:", size=16, bold=True, color=AMBER)
    
    examples = [
        ("Consumption Drop:   0.80 x 0.25 = 0.200", WHITE),
        ("Tamper Detection:    0.90 x 0.20 = 0.180", WHITE),
        ("Current Anomaly:     0.70 x 0.15 = 0.105", WHITE),
        ("Voltage Anomaly:     0.30 x 0.10 = 0.030", LIGHT_GREY),
        ("Power Factor:        0.20 x 0.10 = 0.020", LIGHT_GREY),
        ("Pattern Irregular:   0.40 x 0.10 = 0.040", LIGHT_GREY),
        ("Frequency Deviat:    0.10 x 0.05 = 0.005", LIGHT_GREY),
        ("Flat-line:           0.00 x 0.05 = 0.000", LIGHT_GREY),
    ]
    for text, color in examples:
        add_para(tf2, text, size=13, color=color, font_name="Consolas")

    add_para(tf2, "", size=4)
    add_para(tf2, "Weighted Sum = 0.580  (58%)", size=15, bold=True, color=WHITE)
    add_para(tf2, "", size=4)
    add_para(tf2, "Boost Rule 1:  3 factors > 0.5 (drop, tamper, current) -> x1.3", size=13, color=ORANGE)
    add_para(tf2, "  0.580 x 1.3 = 0.754  (75.4%)", size=14, bold=True, color=RED)
    add_para(tf2, "", size=4)
    add_para(tf2, "Result: 75.4% -> CRITICAL RISK -> Immediate field investigation", size=14, bold=True, color=RED)


def slide_feature_engineering(prs):
    """Slide: Feature Engineering."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "FEATURE ENGINEERING: 47+ Features in 6 Categories", size=24, bold=True, color=BLUE)

    categories = [
        ("Statistical (14)", "mean, std, CV, skewness, kurtosis,\npercentiles (p10/25/75/90), IQR,\nrange, min, max, median", BLUE),
        ("Temporal (10)", "weekday/weekend ratio, seasonal Q1-Q4,\nmonth-over-month changes, trend ratio,\nautocorrelation (lag-1, lag-7)", TEAL),
        ("Anomaly (9)", "zero-day count/ratio, sudden drops,\nflatline days, unique ratio,\nvolatility index, below-baseline ratio", RED),
        ("Comparative (3)", "zone z-score deviation,\nzone percentile rank,\nratio-to-zone average", ORANGE),
        ("Metadata (6)", "consumer type (one-hot x3),\nbaseline kWh, sanctioned load,\nconsumption-to-sanctioned ratio", PURPLE),
        ("Advanced (5)", "entropy, last/first 30-day ratio,\nmax consecutive below-threshold,\nweekday/weekend means", GREEN),
    ]

    for i, (cat, feats, color) in enumerate(categories):
        row = i // 3
        col = i % 3
        x = Inches(0.3 + col * 3.2)
        y = Inches(1.1 + row * 2.7)
        card = add_shape(slide, x, y, Inches(3.0), Inches(2.4), BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, cat, size=13, bold=True, color=color)
        add_para(tf2, feats, size=10, color=LIGHT_GREY, space_before=Pt(6))

    tf3 = add_text_box(slide, Inches(0.5), Inches(6.5), Inches(9), Inches(0.3))
    set_text(tf3, "Raw '10 kWh today' is not enough. ML models need rich, multi-dimensional feature views.", 
             size=11, color=AMBER, align=PP_ALIGN.CENTER)


def slide_class_imbalance(prs):
    """Slide: Class Imbalance."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "CLASS IMBALANCE: 91.5% Honest vs 8.5% Theft", size=24, bold=True, color=BLUE)

    # Problem
    card1 = add_shape(slide, Inches(0.4), Inches(1.0), Inches(9.2), Inches(1.2), BG_CARD)
    tf2 = card1.text_frame; tf2.word_wrap = True
    set_text(tf2, "The Problem: Accuracy Paradox", size=16, bold=True, color=RED)
    add_para(tf2, "A model that ALWAYS predicts 'Honest' gets 91.5% accuracy but catches ZERO thieves. Useless!", size=13, color=WHITE)

    # 3 solutions
    solutions = [
        ("SMOTE", "Creates synthetic thief samples\nMath: x_new = x_i + lambda x (x_zi - x_i)\nBalances to 50/50 training set", GREEN),
        ("Class Weights", "Model penalizes missing thief 6.25x more\nweight = n_total / (2 x n_theft)\nForces model to 'care about' thieves", ORANGE),
        ("Threshold Tuning", "Find threshold that maximizes F1-score\nUsually ~0.35-0.45 (not default 0.50)\nLower = catch more thieves", PURPLE),
    ]

    for i, (title, desc, color) in enumerate(solutions):
        x = Inches(0.3 + i * 3.2)
        card = add_shape(slide, x, Inches(2.5), Inches(3.0), Inches(3.5), BG_CARD)
        tf3 = card.text_frame; tf3.word_wrap = True
        set_text(tf3, f"Solution {i+1}: {title}", size=14, bold=True, color=color)
        add_para(tf3, desc, size=11, color=LIGHT_GREY, space_before=Pt(8))


def slide_5_models(prs):
    """Slide: The 5 ML Models."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "THE 5 ML MODELS", size=28, bold=True, color=BLUE)

    models = [
        ("Random Forest", "300 trees voting\nmax_depth=20, class_weight=balanced\nStrength: Feature importance", BLUE),
        ("XGBoost", "300 sequential boosted trees\nL1/L2 regularization, scale_pos_weight\nStrength: Best for tabular data", TEAL),
        ("DNN", "128->64->32 neural network\nDropout 40%, BatchNorm, Early Stop\nStrength: Non-linear patterns", GREEN),
        ("LSTM", "2 stacked layers (128->64)\nMemory gates, dropout 0.3\nStrength: Time-series sequences", ORANGE),
        ("Isolation Forest", "200 trees, unsupervised\nNo labels needed, contamination=0.1\nStrength: Catches novel theft", RED),
    ]

    for i, (name, desc, color) in enumerate(models):
        if i < 3:
            x = Inches(0.2 + i * 3.3)
            y = Inches(1.1)
        else:
            x = Inches(1.7 + (i - 3) * 3.3)
            y = Inches(3.7)
        card = add_shape(slide, x, y, Inches(3.1), Inches(2.3), BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, name, size=15, bold=True, color=color)
        add_para(tf2, desc, size=11, color=LIGHT_GREY, space_before=Pt(6))


def slide_ensemble(prs):
    """Slide: Ensemble Strategy."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "ENSEMBLE STRATEGY: Combining 5 Models", size=26, bold=True, color=BLUE)

    # Soft Voting
    card1 = add_shape(slide, Inches(0.4), Inches(1.1), Inches(4.4), Inches(3.0), BG_CARD)
    tf2 = card1.text_frame; tf2.word_wrap = True
    set_text(tf2, "Soft Voting (Simple Average)", size=15, bold=True, color=GREEN)
    add_para(tf2, "P_ensemble = (P_RF + P_XGB + P_DNN + P_LSTM + P_ISO) / 5", size=11, color=WHITE, space_before=Pt(8))
    add_para(tf2, "", size=4)
    add_para(tf2, "Example:", size=12, bold=True, color=AMBER)
    add_para(tf2, "RF: 0.72  XGB: 0.68  DNN: 0.81", size=11, color=LIGHT_GREY)
    add_para(tf2, "LSTM: 0.55  ISO: 0.60", size=11, color=LIGHT_GREY)
    add_para(tf2, "Ensemble = 0.672 (67.2%)", size=13, bold=True, color=WHITE)

    # Stacking
    card2 = add_shape(slide, Inches(5.1), Inches(1.1), Inches(4.4), Inches(3.0), BG_CARD)
    tf3 = card2.text_frame; tf3.word_wrap = True
    set_text(tf3, "Stacking (Meta-Learner)", size=15, bold=True, color=PURPLE)
    add_para(tf3, "Logistic Regression learns optimal weights for each model's prediction:", size=12, color=WHITE, space_before=Pt(8))
    add_para(tf3, "P = sigmoid(w1*P_RF + w2*P_XGB + w3*P_DNN + w4*P_LSTM + w5*P_ISO + b)", size=10, color=AMBER, space_before=Pt(6))
    add_para(tf3, "", size=4)
    add_para(tf3, "If XGBoost is consistently more reliable, meta-learner automatically gives it higher weight.", size=11, color=LIGHT_GREY)

    # Why ensemble
    card3 = add_shape(slide, Inches(0.4), Inches(4.4), Inches(9.2), Inches(2.0), BG_CARD)
    tf4 = card3.text_frame; tf4.word_wrap = True
    set_text(tf4, "Why Not Just Use the Best Model?", size=15, bold=True, color=ORANGE)
    add_para(tf4, "Every model has blind spots. RF can't capture complex interactions. XGBoost may overfit. DNN is a black box. LSTM is overkill for non-temporal patterns. Isolation Forest has false positives.", size=12, color=WHITE)
    add_para(tf4, "The ensemble lets models COVER for each other's weaknesses.", size=13, bold=True, color=GREEN, space_before=Pt(6))


def slide_explainability(prs):
    """Slide: SHAP & Heuristic Explainability."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "EXPLAINABILITY: SHAP + Heuristic Breakdown", size=24, bold=True, color=BLUE)

    # Problem
    card0 = add_shape(slide, Inches(0.4), Inches(1.0), Inches(9.2), Inches(1.0), BG_CARD)
    tf0 = card0.text_frame; tf0.word_wrap = True
    set_text(tf0, 'The Black-Box Problem: Inspector asks "WHY 90% theft?" -- "Because neural network said so" is NOT acceptable.', size=13, color=RED)

    # SHAP
    card1 = add_shape(slide, Inches(0.4), Inches(2.2), Inches(4.4), Inches(3.8), BG_CARD)
    tf2 = card1.text_frame; tf2.word_wrap = True
    set_text(tf2, "Solution 1: SHAP Values", size=15, bold=True, color=GREEN)
    add_para(tf2, "Game-theory math (Shapley values) breaks down which feature caused the high score:", size=12, color=WHITE, space_before=Pt(6))
    add_para(tf2, "anom_zero_day_ratio:  +0.23  (UP)", size=11, color=AMBER, font_name="Consolas")
    add_para(tf2, "stat_cv:             +0.18  (UP)", size=11, color=AMBER, font_name="Consolas")
    add_para(tf2, "comp_zone_deviation: +0.15  (UP)", size=11, color=AMBER, font_name="Consolas")
    add_para(tf2, "meta_baseline_kwh:   -0.05  (down)", size=11, color=LIGHT_GREY, font_name="Consolas")

    # Heuristic Breakdown
    card2 = add_shape(slide, Inches(5.1), Inches(2.2), Inches(4.4), Inches(3.8), BG_CARD)
    tf3 = card2.text_frame; tf3.word_wrap = True
    set_text(tf3, "Solution 2: 8-Measure Breakdown", size=15, bold=True, color=ORANGE)
    add_para(tf3, "The heuristic ALWAYS runs to provide visual breakdown on dashboard:", size=12, color=WHITE, space_before=Pt(6))
    bars = [
        ("Consumption Drop:  80%", BLUE),
        ("Tamper Detection:  90%", RED),
        ("Current Anomaly:   70%", TEAL),
        ("Voltage Anomaly:   30%", LIGHT_GREY),
        ("Power Factor:      20%", LIGHT_GREY),
    ]
    for text, color in bars:
        add_para(tf3, text, size=11, color=color, font_name="Consolas")
    add_para(tf3, "", size=4)
    add_para(tf3, "Physical explanation operators can understand and act on.", size=11, color=GREEN)


def slide_training_pipeline(prs):
    """Slide: Training Pipeline."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "TRAINING PIPELINE: 7 Phases", size=28, bold=True, color=BLUE)

    phases = [
        ("Phase 1", "Load SGCC Dataset", "42,372 consumers x 1,035 days\n91.5% honest / 8.5% theft"),
        ("Phase 2", "Preprocessing", "Forward/backward fill missing values\nWinsorize at 5th/95th percentile\nEngineer 47-65 features"),
        ("Phase 3", "Class Imbalance", "SMOTE (k=5 neighbors)\nCost-sensitive class weights"),
        ("Phase 4", "Train 5 Models", "RF(300) + XGBoost(300) + DNN\n+ LSTM + Isolation Forest"),
        ("Phase 5", "Ensemble", "Soft Voting + Stacking\nOptimal threshold tuning"),
        ("Phase 6", "Evaluation", "Accuracy, Precision, Recall, F1\nAUC-ROC, PR-AUC, 5-Fold CV"),
        ("Phase 7", "SHAP", "TreeExplainer on Random Forest\nTop 15 features by importance"),
    ]

    colors = [BLUE, TEAL, RED, GREEN, PURPLE, ORANGE, AMBER]
    for i, (phase, title, desc) in enumerate(phases):
        if i < 4:
            x = Inches(0.2 + i * 2.45)
            y = Inches(1.1)
        else:
            x = Inches(0.2 + (i - 4) * 3.27)
            y = Inches(3.8)
        w = Inches(2.25) if i < 4 else Inches(3.07)
        h = Inches(2.4) if i < 4 else Inches(2.5)
        card = add_shape(slide, x, y, w, h, BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, f"{phase}: {title}", size=12, bold=True, color=colors[i])
        add_para(tf2, desc, size=10, color=LIGHT_GREY, space_before=Pt(6))


def slide_theft_scenarios(prs):
    """Slide: 6 Theft Scenarios."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "6 SYNTHETIC THEFT SCENARIOS", size=28, bold=True, color=BLUE)

    scenarios = [
        ("Meter Tampering", "Consumption x 0.1-0.4\nAdjusted calibration", RED),
        ("Bypass", "Zero consumption blocks\nCopper wire around CT", ORANGE),
        ("Billing Irregularity", "30-70% readings replaced\nBribed reader / hacked billing", AMBER),
        ("Unauthorized Tap", "Sudden drop to near-zero\nDirect grid connection", PURPLE),
        ("Flat-line Spoof", "Constant value forever\nHacked meter firmware", TEAL),
        ("Gradual Decay", "Exponential decay to 5%\nDeliberate mechanical degradation", GREEN),
    ]

    for i, (name, desc, color) in enumerate(scenarios):
        row = i // 3
        col = i % 3
        x = Inches(0.3 + col * 3.2)
        y = Inches(1.1 + row * 2.7)
        card = add_shape(slide, x, y, Inches(3.0), Inches(2.4), BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, f"{i+1}. {name}", size=14, bold=True, color=color)
        add_para(tf2, desc, size=11, color=LIGHT_GREY, space_before=Pt(8))

    tf3 = add_text_box(slide, Inches(0.5), Inches(6.5), Inches(9), Inches(0.3))
    set_text(tf3, "Each starts at random point (20-80% through timeline), maintains realistic seasonality before theft", 
             size=11, color=AMBER, align=PP_ALIGN.CENTER)


def slide_evaluation(prs):
    """Slide: Evaluation Metrics."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "EVALUATION METRICS", size=28, bold=True, color=BLUE)

    # Metrics
    metrics = [
        ("Precision", "TP / (TP+FP)", "Of all 'theft' predictions,\nhow many correct?", GREEN),
        ("Recall", "TP / (TP+FN)", "Of all actual thieves,\nhow many caught?", ORANGE),
        ("F1-Score", "2*(P*R)/(P+R)", "Harmonic mean of\nPrecision & Recall", PURPLE),
        ("AUC-ROC", "Area under curve", "Discrimination ability\nacross all thresholds", BLUE),
    ]

    for i, (name, formula, desc, color) in enumerate(metrics):
        x = Inches(0.3 + i * 2.45)
        card = add_shape(slide, x, Inches(1.1), Inches(2.25), Inches(2.3), BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, name, size=14, bold=True, color=color)
        add_para(tf2, formula, size=11, color=AMBER, font_name="Consolas")
        add_para(tf2, desc, size=11, color=LIGHT_GREY, space_before=Pt(6))

    # Confusion matrix
    card_cm = add_shape(slide, Inches(0.4), Inches(3.7), Inches(9.2), Inches(2.8), BG_CARD)
    tf3 = card_cm.text_frame; tf3.word_wrap = True
    set_text(tf3, "Confusion Matrix & 5-Fold Cross-Validation", size=15, bold=True, color=AMBER)
    add_para(tf3, "TN (True Negative)  = Honest correctly identified", size=12, color=GREEN)
    add_para(tf3, "TP (True Positive)   = Thief correctly caught!", size=12, color=GREEN)
    add_para(tf3, "FP (False Positive)  = False alarm (wasted inspection, cost: Rs.500)", size=12, color=ORANGE)
    add_para(tf3, "FN (False Negative) = MISSED thief! (cost: Rs.50,000+/year)", size=12, color=RED)
    add_para(tf3, "", size=4)
    add_para(tf3, "5-Fold Stratified CV: Split data into 5 parts, train on 4, test on 1. Rotate 5 times. Report mean +/- std.", size=12, color=LIGHT_GREY)


def slide_architecture(prs):
    """Slide: System Architecture."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "SYSTEM ARCHITECTURE: 4 Microservices", size=26, bold=True, color=BLUE)

    services = [
        ("React Frontend", "Vite, Dashboard, Port 5173\n7 pages + JWT auth\nRecharts visualization", BLUE, Inches(0.3)),
        ("Node.js API", "Express, Port 5000\nAuth, CRUD, Stats\nOrchestrates ML calls", GREEN, Inches(2.7)),
        ("FastAPI ML Service", "Python, Port 8000\n8-Measure Heuristic\nEnsemble Model", ORANGE, Inches(5.1)),
        ("MongoDB", "Port 27017\nMeters, Readings, Alerts\nCompound Indexes", TEAL, Inches(7.5)),
    ]

    for name, desc, color, x in services:
        card = add_shape(slide, x, Inches(1.1), Inches(2.2), Inches(2.5), BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, name, size=13, bold=True, color=color)
        add_para(tf2, desc, size=10, color=LIGHT_GREY, space_before=Pt(6))

    # Arrows (represented as text)
    tf_arrows = add_text_box(slide, Inches(0.3), Inches(3.8), Inches(9.4), Inches(0.5))
    set_text(tf_arrows, "Frontend  --(REST/JSON)-->  Backend  --(HTTP POST)-->  ML Service  |  Backend  --(Mongoose)-->  MongoDB", 
             size=11, color=AMBER, align=PP_ALIGN.CENTER)

    # Triple fallback
    card_fb = add_shape(slide, Inches(0.4), Inches(4.5), Inches(9.2), Inches(2.0), BG_CARD)
    tf3 = card_fb.text_frame; tf3.word_wrap = True
    set_text(tf3, "Triple-Layer Fallback (System NEVER Fails)", size=15, bold=True, color=RED)
    add_para(tf3, "Layer 1: ML Ensemble (ensemble_model.pkl) -> Highest accuracy", size=12, color=GREEN)
    add_para(tf3, "Layer 2: Python Heuristic (8-measure rules) -> No model file needed", size=12, color=ORANGE)
    add_para(tf3, "Layer 3: JavaScript Fallback (same algorithm in JS) -> Zero external dependencies", size=12, color=AMBER)
    add_para(tf3, "Availability > DRY principle for critical infrastructure", size=11, color=LIGHT_GREY, space_before=Pt(6))


def slide_risk_levels(prs):
    """Slide: Risk Classification."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, BG_DARK)

    tf = add_text_box(slide, Inches(0.5), Inches(0.3), Inches(9), Inches(0.6))
    set_text(tf, "RISK CLASSIFICATION: 4 Tiers", size=28, bold=True, color=BLUE)

    tiers = [
        ("LOW", "0% - 29%", "No action needed", GREEN),
        ("MEDIUM", "30% - 49%", "Inspect within 30 days", AMBER),
        ("HIGH", "50% - 74%", "Inspect within 7 days", ORANGE),
        ("CRITICAL", "75% - 100%", "Immediate investigation", RED),
    ]

    for i, (level, range_str, action, color) in enumerate(tiers):
        x = Inches(0.3 + i * 2.45)
        card = add_shape(slide, x, Inches(1.2), Inches(2.25), Inches(2.5), BG_CARD)
        tf2 = card.text_frame; tf2.word_wrap = True
        set_text(tf2, level, size=24, bold=True, color=color, align=PP_ALIGN.CENTER)
        add_para(tf2, range_str, size=16, color=WHITE, align=PP_ALIGN.CENTER, space_before=Pt(10))
        add_para(tf2, action, size=12, color=LIGHT_GREY, align=PP_ALIGN.CENTER, space_before=Pt(8))

    # Data flow
    card2 = add_shape(slide, Inches(0.4), Inches(4.2), Inches(9.2), Inches(2.3), BG_CARD)
    tf3 = card2.text_frame; tf3.word_wrap = True
    set_text(tf3, "Data Flow: Button Click to Result", size=15, bold=True, color=BLUE)
    flow_steps = [
        "1. User clicks 'Analyze Anomalies' on a meter",
        "2. Frontend sends POST /api/analyze/:meterId (JWT attached)",
        "3. Backend verifies ownership, fetches 30 days of readings (~720 hourly)",
        "4. Backend computes stats (mean/std/min/max for all 6 dimensions)",
        "5. Backend POSTs to ML Service with 15s timeout",
        "6. ML Service runs ensemble (or heuristic fallback), returns 8 scores",
        "7. If anomaly -> Alert created in MongoDB -> Red banner + 8 progress bars",
    ]
    for step in flow_steps:
        add_para(tf3, step, size=10, color=LIGHT_GREY)


def slide_summary(prs):
    """Slide: Summary."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_bg(slide, RGBColor(15, 22, 36))

    # Accent line
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.8), Inches(10), Pt(3))
    shape.fill.solid(); shape.fill.fore_color.rgb = BLUE; shape.line.fill.background()

    tf = add_text_box(slide, Inches(0.5), Inches(0.2), Inches(9), Inches(0.6))
    set_text(tf, "SUMMARY", size=32, bold=True, color=BLUE, align=PP_ALIGN.CENTER)

    card = add_shape(slide, Inches(0.5), Inches(1.2), Inches(9), Inches(4.5), BG_CARD)
    tf2 = card.text_frame; tf2.word_wrap = True
    set_text(tf2, "What We Built:", size=18, bold=True, color=AMBER)
    
    points = [
        "PowerGuard: full-stack ML-powered electricity theft detection system",
        "Analyzes 6-dimensional smart meter telemetry in real-time",
        "8-measure weighted heuristic engine with per-factor explainability",
        "5-model ML ensemble (RF + XGBoost + DNN + LSTM + Isolation Forest)",
        "Trained on SGCC dataset (42,372 consumers) with SMOTE for class imbalance",
        "47+ engineered features across 6 categories",
        "SHAP explainability for transparent, actionable predictions",
        "4-service microservice architecture (React + Node.js + FastAPI + MongoDB)",
        "Triple-layer fallback ensuring zero downtime",
        "4-tier risk classification with one-click bulk analysis",
    ]
    for p in points:
        add_bullet(tf2, p, size=12, color=WHITE)

    # Interview tip
    tf3 = add_text_box(slide, Inches(0.5), Inches(6.0), Inches(9), Inches(0.6))
    set_text(tf3, "For every component: What? -> Why? -> How? -> Alternatives? -> Trade-offs? -> What would I change?", 
             size=11, color=AMBER, align=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════════

def main():
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Build all slides
    slide_title(prs)          # 1
    slide_problem(prs)        # 2
    slide_6_dimensions(prs)   # 3
    slide_8_factors_overview(prs)  # 4
    slide_factors_1_to_4(prs)     # 5-8
    slide_factors_5_to_8(prs)     # 9-12
    slide_weighted_scoring(prs)   # 13
    slide_worked_example(prs)     # 14
    slide_feature_engineering(prs)  # 15
    slide_class_imbalance(prs)    # 16
    slide_5_models(prs)           # 17
    slide_ensemble(prs)           # 18
    slide_explainability(prs)     # 19
    slide_training_pipeline(prs)  # 20
    slide_theft_scenarios(prs)    # 21
    slide_evaluation(prs)         # 22
    slide_architecture(prs)       # 23
    slide_risk_levels(prs)        # 24
    slide_summary(prs)            # 25

    prs.save(OUT_PPT)
    sz = os.path.getsize(OUT_PPT) / 1024
    print(f"[OK] PowerPoint generated successfully!")
    print(f"     File: {OUT_PPT}")
    print(f"     Size: {sz:.0f} KB")
    print(f"     Slides: 25")


if __name__ == "__main__":
    main()

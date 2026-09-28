"""
Convert comprehensive_study_guide.md -> PDF
Uses fpdf2 with Unicode TTF font support.
"""

import os, re
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(SCRIPT_DIR, "comprehensive_study_guide.md")
OUT_PDF = os.path.join(SCRIPT_DIR, "Comprehensive_Deep_Dive_Study_Guide.pdf")

# ---------- helpers ----------

def sanitize(text):
    """Replace problematic Unicode with ASCII equivalents."""
    MAP = {
        "\u2014": "--", "\u2013": "-", "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2192": "->", "\u2190": "<-", "\u2265": ">=", "\u2264": "<=",
        "\u2248": "~", "\u00d7": "x", "\u00f7": "/",
        "\u03c3": "sigma", "\u03a3": "SUM", "\u03bb": "lambda",
        "\u03b8": "theta", "\u03a9": "Omega",
        "\u2081": "1", "\u2082": "2", "\u2083": "3", "\u2084": "4", "\u2085": "5",
        "\u2098": "m", "\u2096": "k", "\u1d62": "i",
        "\u2500": "-", "\u2550": "=", "\u2551": "|",
        "\u2554": "+", "\u2557": "+", "\u255a": "+", "\u255d": "+",
        "\u251c": "+", "\u2524": "+", "\u250c": "+", "\u2510": "+",
        "\u2514": "+", "\u2518": "+", "\u2502": "|",
        "\u25b6": ">", "\u25c0": "<", "\u25bc": "v",
        "\u2588": "#", "\u2591": ".",
        "\u20b9": "Rs.",
        "\u2022": "*",  # bullet
        "\u2716": "X", "\u2714": "OK",
    }
    for old, new in MAP.items():
        text = text.replace(old, new)
    # Remove any remaining non-latin-1 chars
    emoji_re = re.compile(
        "["
        "\U0001F300-\U0001F9FF"
        "\U00002702-\U000027B0"
        "\U0000FE00-\U0000FE0F"
        "\U0001FA00-\U0001FAFF"
        "\U00002600-\U000026FF"
        "\U0000200D"
        "\U00002B50"
        "]+", flags=re.UNICODE
    )
    text = emoji_re.sub("", text)
    # Final pass: remove anything outside latin-1
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def strip_md_inline(text):
    """Remove markdown bold/italic/code/link markers."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    return text


# ---------- PDF class ----------

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 7, sanitize("PowerGuard -- Complete Deep Dive Study Guide"), align="C")
        self.ln(3)
        self.set_draw_color(41, 128, 185)
        self.set_line_width(0.4)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, f"Page {self.page_no()}/{{nb}}", align="C")


# ---------- rendering helpers ----------

def render_code(pdf, lines):
    pdf.ln(1)
    y0 = pdf.get_y()
    lh = 4.2
    needed = len(lines) * lh + 6
    if y0 + needed > pdf.h - 18:
        pdf.add_page()
        y0 = pdf.get_y()
    pdf.set_fill_color(243, 243, 243)
    pdf.rect(12, y0, pdf.w - 24, min(needed, pdf.h - y0 - 18), "F")
    pdf.set_font("Courier", "", 7.5)
    pdf.set_text_color(40, 40, 40)
    pdf.set_xy(15, y0 + 2)
    for ln in lines:
        if pdf.get_y() > pdf.h - 18:
            pdf.add_page()
            pdf.set_fill_color(243, 243, 243)
            pdf.set_font("Courier", "", 7.5)
            pdf.set_text_color(40, 40, 40)
        pdf.cell(0, lh, sanitize(ln[:130]), ln=True)
        pdf.set_x(15)
    pdf.ln(2)


def render_table(pdf, rows):
    if not rows:
        return
    pdf.ln(1)
    ncols = max(len(r) for r in rows)
    if ncols == 0:
        return
    avail = pdf.w - 24
    col_w = max(10, avail / ncols)  # Ensure minimum column width
    # If columns would overflow, limit number of visible columns
    max_visible = int(avail / 10)
    if ncols > max_visible:
        ncols = max_visible
        col_w = avail / ncols
    for ri, row in enumerate(rows):
        if pdf.get_y() > pdf.h - 18:
            pdf.add_page()
        if ri == 0:
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.set_fill_color(41, 128, 185)
            pdf.set_text_color(255, 255, 255)
        else:
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(30, 30, 30)
            if ri % 2 == 0:
                pdf.set_fill_color(240, 248, 255)
            else:
                pdf.set_fill_color(255, 255, 255)
        pdf.set_x(12)
        for ci in range(ncols):
            t = sanitize(strip_md_inline(row[ci] if ci < len(row) else ""))
            pdf.cell(col_w, 5.5, t[:55], border=1, fill=True)
        pdf.ln()
    pdf.ln(2)


def render_blockquote(pdf, lines):
    pdf.ln(1)
    text = " ".join(l for l in lines if not l.startswith("[!"))
    text = sanitize(strip_md_inline(text))
    y0 = pdf.get_y()
    pdf.set_x(18)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(70, 70, 70)
    pdf.multi_cell(pdf.w - 30, 5, text)
    pdf.set_draw_color(149, 165, 166)
    pdf.set_line_width(0.8)
    pdf.line(14, y0, 14, pdf.get_y())
    pdf.ln(1)


# ---------- main ----------

def build_pdf():
    with open(MD_FILE, "r", encoding="utf-8") as f:
        raw = f.read()

    lines = raw.split("\n")

    pdf = PDF("P", "mm", "A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()

    # -- title page --
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(41, 128, 185)
    pdf.ln(30)
    pdf.cell(0, 15, "PowerGuard", align="C", ln=True)
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 10, "Complete Deep Dive Study Guide", align="C", ln=True)
    pdf.ln(8)
    pdf.set_draw_color(41, 128, 185)
    pdf.set_line_width(0.6)
    pdf.line(60, pdf.get_y(), pdf.w - 60, pdf.get_y())
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Electricity Theft Detection System", align="C", ln=True)
    pdf.cell(0, 8, "ML + Heuristic Hybrid Approach", align="C", ln=True)
    pdf.ln(20)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, "8 Detection Factors  |  5 ML Models  |  47+ Engineered Features", align="C", ln=True)
    pdf.cell(0, 6, "SGCC Dataset  |  Ensemble Strategy  |  SHAP Explainability", align="C", ln=True)

    pdf.add_page()

    # -- Parse content --
    in_code = False
    code_buf = []
    table_buf = []
    bq_buf = []
    in_bq = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith("```") or line.strip().startswith("````"):
            if in_code:
                render_code(pdf, code_buf)
                code_buf = []
                in_code = False
            else:
                if in_bq:
                    render_blockquote(pdf, bq_buf)
                    bq_buf = []; in_bq = False
                in_code = True
            i += 1; continue

        if in_code:
            code_buf.append(line)
            i += 1; continue

        # Tables
        if "|" in line and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.match(r"^[-:]+$", c) for c in cells):
                i += 1; continue
            table_buf.append(cells)
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("|"):
                i += 1; continue
            else:
                render_table(pdf, table_buf)
                table_buf = []
                i += 1; continue

        # Blockquotes
        if line.strip().startswith("> ") or line.strip() == ">":
            bq_buf.append(line.strip().lstrip("> ").strip())
            in_bq = True
            i += 1; continue
        elif in_bq:
            render_blockquote(pdf, bq_buf)
            bq_buf = []; in_bq = False
            # fall through

        # H1
        if line.startswith("# ") and not line.startswith("## "):
            t = sanitize(strip_md_inline(line[2:].strip()))
            pdf.set_font("Helvetica", "B", 20)
            pdf.set_text_color(41, 128, 185)
            pdf.ln(5)
            pdf.multi_cell(0, 9, t)
            pdf.ln(3)
            i += 1; continue

        # H2
        if line.startswith("## "):
            t = sanitize(strip_md_inline(line[3:].strip()))
            pdf.set_font("Helvetica", "B", 15)
            pdf.set_text_color(44, 62, 80)
            pdf.ln(6)
            pdf.multi_cell(0, 8, t)
            pdf.set_draw_color(41, 128, 185)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y() + 1, pdf.w - 10, pdf.get_y() + 1)
            pdf.ln(4)
            i += 1; continue

        # H3
        if line.startswith("### "):
            t = sanitize(strip_md_inline(line[4:].strip()))
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(52, 73, 94)
            pdf.ln(4)
            pdf.multi_cell(0, 7, t)
            pdf.ln(2)
            i += 1; continue

        # H4
        if line.startswith("#### "):
            t = sanitize(strip_md_inline(line[5:].strip()))
            pdf.set_font("Helvetica", "BI", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.ln(3)
            pdf.multi_cell(0, 6, t)
            pdf.ln(1)
            i += 1; continue

        # HR
        if line.strip() == "---":
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.15)
            pdf.line(10, pdf.get_y(), pdf.w - 10, pdf.get_y())
            pdf.ln(2)
            i += 1; continue

        # Blank
        if line.strip() == "":
            pdf.ln(2)
            i += 1; continue

        # Normal text
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        t = line.strip()

        # Bullets
        if t.startswith("- ") or t.startswith("* "):
            t = "  * " + t[2:]

        t = sanitize(strip_md_inline(t))
        pdf.set_x(10)  # Reset X to left margin
        pdf.multi_cell(0, 5.2, t)
        i += 1

    # Flush
    if in_bq and bq_buf:
        render_blockquote(pdf, bq_buf)
    if in_code and code_buf:
        render_code(pdf, code_buf)

    pdf.output(OUT_PDF)
    sz = os.path.getsize(OUT_PDF) / 1024
    print(f"[OK] PDF generated successfully!")
    print(f"     File: {OUT_PDF}")
    print(f"     Size: {sz:.0f} KB | Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()

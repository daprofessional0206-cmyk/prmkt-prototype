# shared/exports.py
from __future__ import annotations
from typing import Iterable, Optional
import os
import re

from fpdf import FPDF

# -------- Font setup --------
HERE = os.path.dirname(__file__)
FONT_DIR = os.path.join(HERE, "fonts", "dejavu")  # you already created this

_REG_SPACES = re.compile(r"[ \t\u00A0\u2000-\u200D\u202F\u205F\u3000]+")

def _ensure_fonts(pdf: FPDF) -> None:
    """
    Register DejaVu fonts once per FPDF instance.
    """
    pdf.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"), uni=True)
    bold = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
    ital = os.path.join(FONT_DIR, "DejaVuSans-Oblique.ttf")
    if os.path.exists(bold):
        pdf.add_font("DejaVu", "B", bold, uni=True)
    if os.path.exists(ital):
        pdf.add_font("DejaVu", "I", ital, uni=True)

def _clean_line(s: str) -> str:
    """
    FPDF can choke on some zero-width / exotic spaces; normalize them.
    """
    if not s:
        return ""
    s = s.replace("\r", "")
    # normalize all “odd” spaces to a single space
    s = _REG_SPACES.sub(" ", s)
    return s

def text_to_pdf_bytes(text: str, title: Optional[str] = None) -> bytes:
    """
    Render plain text to a simple A4 PDF with sane margins and Unicode font.
    """
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(True, margin=14)
    pdf.set_margins(left=14, top=16, right=14)
    pdf.add_page()

    _ensure_fonts(pdf)
    pdf.set_font("DejaVu", size=12)

    # Optional title
    if title:
        pdf.set_font("DejaVu", "B", size=14)
        pdf.multi_cell(w=pdf.epw, h=7, txt=_clean_line(title))
        pdf.ln(3)
        pdf.set_font("DejaVu", size=12)

    # Effective printable width (A4: ~210mm - margins)
    # FPDF exposes epw (effective page width) in recent versions:
    try:
        eff_w = pdf.epw  # type: ignore[attr-defined]
    except Exception:
        eff_w = pdf.w - pdf.l_margin - pdf.r_margin

    for raw_line in (text or "").split("\n"):
        line = _clean_line(raw_line)
        if line.strip() == "":
            pdf.ln(4)
        else:
            pdf.multi_cell(w=eff_w, h=6, txt=line)

    raw = pdf.output(dest="S")
    # FPDF<2.7 returns str; newer returns bytes/bytearray
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw)
    return raw.encode("latin-1")

# ---------- small helper used by Content Engine ----------
def join_variants(variants: Iterable[str], divider: Optional[str] = None) -> str:
    """
    Utility: merge A/B/C variants for exporting. Adds a friendly divider.
    """
    joined: list[str] = []
    for i, v in enumerate(variants, start=1):
        title = f"Variant {i}"
        block = f"{title}\n{'-'*len(title)}\n{v.strip()}"
        joined.append(block)
    if divider is None:
        divider = "\n\n" + ("-" * 60) + "\n\n"
    return divider.join(joined)

# shared/exports.py
from __future__ import annotations
from io import BytesIO
from typing import Iterable
import unicodedata

from fpdf import FPDF

try:
    from docx import Document  # python-docx
except Exception:  # pragma: no cover
    Document = None


# -------- helpers --------

_REPLACEMENTS = {
    "“": '"', "”": '"', "„": '"',
    "‘": "'", "’": "'", "‚": "'",
    "—": "-", "–": "-", "-": "-",
    "•": "-", "·": "-", "●": "-",
    "\u00A0": " ",  # nbsp
}

def _replace_chars(s: str) -> str:
    if not s:
        return s
    for bad, good in _REPLACEMENTS.items():
        s = s.replace(bad, good)
    return s

def _pdf_safe(text: str) -> str:
    """
    Make text safe for core FPDF fonts:
    - replace common Unicode punctuation
    - normalize and drop codepoints outside latin-1
    """
    if not text:
        return ""
    text = _replace_chars(text)
    # NFKD then encode latin-1 (drop non-latin), then back to str
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "ignore").decode("latin-1")


# -------- public API --------

def text_to_pdf_bytes(text: str, title: str | None = None) -> bytes:
    """
    Convert plain text to a lightweight PDF (A4).
    Uses core Helvetica (latin-1) for maximum compatibility.
    """
    safe = _pdf_safe(text)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=15, top=15, right=15)
    pdf.add_page()

    if title:
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(w=0, h=8, txt=_pdf_safe(title))
        pdf.ln(2)

    pdf.set_font("Helvetica", size=11)

    # Split into lines and write as wrapped paragraphs
    for raw_line in safe.splitlines():
        line = raw_line.rstrip()
        if line.strip() == "":
            pdf.ln(6)
        else:
            # 0 width means “use remaining line width”
            pdf.multi_cell(w=0, h=6, txt=line)

    # Return bytes (latin-1 string per FPDF API)
    return pdf.output(dest="S").encode("latin-1")


def text_to_docx_bytes(text: str, title: str | None = None) -> bytes:
    """
    Convert text to a .docx document.
    Requires python-docx.
    """
    if Document is None:
        raise ImportError(
            "DOCX export requires the 'python-docx' package. "
            "Add 'python-docx' to requirements.txt and reinstall."
        )

    doc = Document()
    if title:
        doc.add_heading(title, level=1)

    # Keep the text readable in Word (don’t drop Unicode here)
    for line in text.splitlines():
        if line.strip() == "":
            doc.add_paragraph()
        else:
            doc.add_paragraph(line)

    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()


def text_to_txt_bytes(text: str) -> bytes:
    return (text or "").encode("utf-8")


def iter_to_pdf_bytes(lines: Iterable[str], title: str | None = None) -> bytes:
    """Optional: build PDF from an iterable of lines."""
    return text_to_pdf_bytes("\n".join(lines), title=title)

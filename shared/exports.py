# shared/exports.py
from __future__ import annotations

from io import BytesIO
from typing import Iterable

# ----- PDF (fpdf2) -----
# fpdf2 handles UTF-8; we also guard against "unbreakable long tokens" by inserting soft breaks.
from fpdf import FPDF

def _soft_wrap_text(text: str, max_token: int = 80) -> str:
    """
    Insert zero-width spaces into very long tokens so fpdf2 can wrap them.
    """
    import re
    def wrap_token(tok: str) -> str:
        if len(tok) <= max_token:
            return tok
        # break token every max_token chars
        parts = [tok[i:i+max_token] for i in range(0, len(tok), max_token)]
        return "\u200b".join(parts)  # zero-width space
    return " ".join(wrap_token(t) for t in re.split(r"(\s+)", text))

def text_to_pdf_bytes(text: str, title: str = "Presence Document") -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_title(title)

    # Basic fonts that exist in fpdf core (latin1). For broader unicode support, fpdf2 recommends TTF.
    pdf.set_font("Helvetica", size=12)

    # Left margin = 15mm, effective width = 210 - 2*15 = 180mm
    effective_width = 180

    for line in text.splitlines():
        safe = _soft_wrap_text(line.strip())
        if not safe:
            pdf.ln(6)
            continue
        # multi_cell(width, height, text)
        pdf.multi_cell(w=effective_width, h=6, txt=safe, align="L")

    out = pdf.output(dest="S").encode("latin1", "replace")
    return out

# ----- DOCX (python-docx) -----
# Note: requires python-docx in requirements.txt
def text_to_docx_bytes(text: str, title: str = "Presence Document") -> bytes:
    from docx import Document
    from docx.shared import Pt

    doc = Document()
    doc.core_properties.title = title

    for line in text.splitlines():
        p = doc.add_paragraph()
        run = p.add_run(line)
        run.font.size = Pt(11)

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()

# ----- CSV/TSV helpers if you need to export tabular things later -----
def rows_to_tsv_bytes(rows: Iterable[Iterable[str]]) -> bytes:
    from csv import writer
    bio = BytesIO()
    w = writer(bio, delimiter="\t", lineterminator="\n")
    for r in rows:
        w.writerow(list(r))
    return bio.getvalue()

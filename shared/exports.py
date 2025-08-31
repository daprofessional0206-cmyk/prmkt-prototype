# shared/exports.py
from __future__ import annotations
from io import BytesIO

def text_to_pdf_bytes(text: str) -> bytes:
    # fpdf safe rendering
    from fpdf import FPDF
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_margins(12, 12, 12)
    pdf.set_font("Helvetica", size=11)

    # Hard-wrap long unbroken sequences to avoid "not enough horizontal space"
    def _chunks(s: str, n: int):
        for i in range(0, len(s), n):
            yield s[i:i+n]

    for raw in text.splitlines():
        line = raw.replace("\t", "    ").strip("\u200b")
        if not line:
            pdf.ln(5)
            continue
        if len(line) > 180 and " " not in line:
            for part in _chunks(line, 80):
                pdf.multi_cell(w=190, h=6, txt=part)
        else:
            pdf.multi_cell(w=190, h=6, txt=line)
    out = BytesIO()
    pdf.output(out)
    return out.getvalue()

def text_to_docx_bytes(text: str) -> bytes:
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    for para in text.split("\n\n"):
        p = doc.add_paragraph(para.strip())
        p_format = p.paragraph_format
        p_format.space_after = Pt(6)
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# shared/exports.py
from __future__ import annotations
from typing import Optional
import io

def text_to_txt_bytes(text: str) -> bytes:
    return text.encode("utf-8")

def text_to_docx_bytes(text: str) -> bytes:
    try:
        from docx import Document  # python-docx
    except Exception as e:
        raise ImportError(
            "DOCX export requires the 'python-docx' package. "
            "Add 'python-docx' to requirements.txt and reinstall. "
            f"Underlying import error: {e!r}"
        )
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def text_to_pdf_bytes(text: str) -> bytes:
    """Lightweight PDF via fpdf. If unavailable, raise a clear error."""
    try:
        from fpdf import FPDF
    except Exception as e:
        raise ImportError(
            "PDF export requires the 'fpdf' package. "
            "Add 'fpdf' to requirements.txt and reinstall. "
            f"Underlying import error: {e!r}"
        )
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.splitlines():
        pdf.multi_cell(0, 8, line)
    bio = io.BytesIO()
    pdf.output(bio)
    return bio.getvalue()

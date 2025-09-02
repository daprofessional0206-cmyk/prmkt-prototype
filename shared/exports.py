# shared/exports.py
from __future__ import annotations
from typing import Iterable, Optional
from io import BytesIO
from pathlib import Path

def _import_fpdf():
    try:
        from fpdf import FPDF  # type: ignore
        return FPDF
    except Exception as e:
        raise RuntimeError(
            "PDF export requires the 'fpdf2' package. Add 'fpdf2' to requirements.txt and reinstall."
        ) from e

def _dejavu_path() -> Optional[Path]:
    here = Path(__file__).parent
    p = here / "fonts" / "dejavu" / "DejaVuSans.ttf"
    return p if p.exists() else None

def _normalize_text(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")

# --- TXT → PDF bytes (now accepts optional title=) ---
def text_to_pdf_bytes(text: str, title: Optional[str] = None) -> bytes:
    FPDF = _import_fpdf()
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Use DejaVu (Unicode) if provided; else Arial + latin-1 replacement
    djv = _dejavu_path()
    if djv:
        pdf.add_font("DejaVu", "", str(djv))
        pdf.set_font("DejaVu", size=12)
        encode_none = False
    else:
        pdf.set_font("Arial", size=12)
        text = text.encode("latin-1", "replace").decode("latin-1")
        if title:
            title = title.encode("latin-1", "replace").decode("latin-1")
        encode_none = True

    pdf.set_left_margin(12)
    pdf.set_right_margin(12)

    # Optional heading
    if title:
        pdf.set_font_size(14)
        pdf.multi_cell(w=0, h=7, txt=title)
        pdf.ln(2)
        pdf.set_font_size(12)

    for line in _normalize_text(text):
        if line.strip() == "":
            pdf.ln(4)
            continue
        pdf.multi_cell(w=0, h=6, txt=line)

    out_str = pdf.output(dest="S")
    return out_str.encode("latin-1") if encode_none else out_str.encode("latin-1")

# --- TXT → DOCX bytes ---
def text_to_docx_bytes(text: str) -> bytes:
    try:
        from docx import Document  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "DOCX export requires the 'python-docx' package. Add 'python-docx' to requirements.txt and reinstall."
        ) from e

    doc = Document()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    for para in text.split("\n\n"):
        doc.add_paragraph(para.strip() if para else "")
    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# --- Join A/B/C variants with a neat divider ---
def join_variants(variants: Iterable[str], divider: Optional[str] = None) -> str:
    blocks: list[str] = []
    for i, v in enumerate(variants, start=1):
        title = f"Variant {i}"
        header = f"{title}\n{'-' * len(title)}"
        blocks.append(f"{header}\n{v.strip()}")
    if divider is None:
        divider = "\n\n" + ("-" * 60) + "\n\n"
    return divider.join(blocks)

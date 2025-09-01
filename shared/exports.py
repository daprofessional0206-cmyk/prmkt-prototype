# shared/exports.py
from __future__ import annotations
from typing import Iterable, Optional
from io import BytesIO
from pathlib import Path

# ---- internal helpers (import lazily so import-time never crashes) ----
def _import_fpdf():
    try:
        from fpdf import FPDF  # type: ignore
        return FPDF
    except Exception as e:
        raise RuntimeError(
            "PDF export requires the 'fpdf' package. Add 'fpdf2' to requirements.txt and reinstall."
        ) from e

def _dejavu_path() -> Optional[Path]:
    """
    Return path to DejaVuSans.ttf if present at shared/fonts/dejavu/DejaVuSans.ttf
    """
    here = Path(__file__).parent
    p = here / "fonts" / "dejavu" / "DejaVuSans.ttf"
    return p if p.exists() else None

def _normalize_text(text: str) -> list[str]:
    # Normalize to unix newlines, keep empty lines (they become spacing)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")

# ---- public: TXT → PDF bytes (Unicode safe when font exists) ----
def text_to_pdf_bytes(text: str) -> bytes:
    FPDF = _import_fpdf()
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Try Unicode font first
    djv = _dejavu_path()
    if djv:
        pdf.add_font("DejaVu", "", str(djv))
        pdf.set_font("DejaVu", size=11)
        encode_none = False
    else:
        # Fallback to core Latin-1 font and replace unsupported chars
        pdf.set_font("Arial", size=11)
        text = text.encode("latin-1", "replace").decode("latin-1")
        encode_none = True  # output() already returns latin-1 str

    # Left/right margins ~12mm; MultiCell width 0 = remaining printable width
    pdf.set_left_margin(12)
    pdf.set_right_margin(12)

    for line in _normalize_text(text):
        if line.strip() == "":
            pdf.ln(4)   # vertical spacer
            continue
        # width=0 means full available width (prevents the “not enough space” error)
        pdf.multi_cell(w=0, h=6, txt=line)

    # Return bytes; FPDF.output() returns latin-1 str
    out_str = pdf.output(dest="S")
    return out_str.encode("latin-1") if encode_none else out_str.encode("latin-1")

# ---- public: TXT → DOCX bytes ----
def text_to_docx_bytes(text: str) -> bytes:
    try:
        from docx import Document  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "DOCX export requires the 'python-docx' package. Add 'python-docx' to requirements.txt and reinstall."
        ) from e

    doc = Document()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split into paragraphs on blank lines
    paragraphs = [p.strip() for p in text.split("\n\n")]
    for p in paragraphs:
        doc.add_paragraph(p if p else "")

    bio = BytesIO()
    doc.save(bio)
    return bio.getvalue()

# ---- public: join multiple variants with readable separators ----
def join_variants(variants: Iterable[str], divider: Optional[str] = None) -> str:
    blocks: list[str] = []
    for i, v in enumerate(variants, start=1):
        title = f"Variant {i}"
        header = f"{title}\n{'-' * len(title)}"
        blocks.append(f"{header}\n{v.strip()}")
    if divider is None:
        divider = "\n\n" + ("-" * 60) + "\n\n"
    return divider.join(blocks)

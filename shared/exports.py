# shared/exports.py
"""
Export helpers for Presence:
- Text → PDF bytes
- Text → DOCX bytes
- DataFrame → CSV bytes
- History(list[dict]) → JSON bytes
- JSON text → list[dict] (safe import)

All functions return BYTES so you can feed them directly to st.download_button.
"""

from __future__ import annotations

from io import BytesIO
from typing import List, Dict, Any, Iterable
import json

# Optional libs (we raise friendly errors if missing)
try:
    import importlib
    _rl_pagesizes = importlib.import_module("reportlab.lib.pagesizes")
    _rl_pdfgen_canvas = importlib.import_module("reportlab.pdfgen.canvas")
    letter = getattr(_rl_pagesizes, "letter")
    canvas = _rl_pdfgen_canvas
except Exception as _e_pdf:
    letter = None  # type: ignore
    canvas = None  # type: ignore
    _REPORTLAB_ERR = _e_pdf
else:
    _REPORTLAB_ERR = None

try:
    import importlib
    _docx_mod = importlib.import_module("docx")
    Document = getattr(_docx_mod, "Document")
except Exception as _e_docx:
    Document = None  # type: ignore
    _DOCX_ERR = _e_docx
else:
    _DOCX_ERR = None

# -----------------------------------------------------------------------------
# Core text exporters
# -----------------------------------------------------------------------------
def text_to_pdf_bytes(text: str, title: str | None = None, margin: int = 40) -> bytes:
    """
    Convert plain text into a simple multi-page PDF (letter size).
    Each line becomes one line of text (no wrapping).
    """
    if canvas is None or letter is None:
        raise RuntimeError(
            "PDF export requires the 'reportlab' package. "
            "Add 'reportlab' to requirements.txt and reinstall.\n"
            f"Underlying import error: {repr(_REPORTLAB_ERR)}"
        )

    buf = BytesIO()
    pdf = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    y = height - margin
    if title:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(margin, y, title)
        y -= 22
        pdf.setFont("Helvetica", 11)

    for raw_line in (text or "").splitlines():
        line = raw_line.replace("\t", "    ")
        pdf.drawString(margin, y, line)
        y -= 15
        if y < margin:
            pdf.showPage()
            y = height - margin

    pdf.save()
    buf.seek(0)
    return buf.getvalue()


def text_to_docx_bytes(text: str, title: str | None = None) -> bytes:
    """
    Convert plain text into a simple .docx document.
    """
    if Document is None:
        raise RuntimeError(
            "DOCX export requires the 'python-docx' package. "
            "Add 'python-docx' to requirements.txt and reinstall.\n"
            f"Underlying import error: {repr(_DOCX_ERR)}"
        )

    doc = Document()
    if title:
        p = doc.add_paragraph()
        run = p.add_run(title)
        run.bold = True
    for line in (text or "").splitlines():
        doc.add_paragraph(line if line.strip() else "")  # preserve blank lines

    buf = BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

# -----------------------------------------------------------------------------
# Data helpers
# -----------------------------------------------------------------------------
def df_to_csv_bytes(df) -> bytes:
    """
    Convert a pandas DataFrame to CSV bytes (UTF-8, no index).
    """
    # Lazy import to avoid hard dependency if not used
    import pandas as pd  # noqa: F401
    csv_text = df.to_csv(index=False)
    return csv_text.encode("utf-8")


def history_to_json_bytes(items: List[Dict[str, Any]]) -> bytes:
    """
    Convert a history list[dict] to pretty JSON bytes.
    """
    return json.dumps(items or [], ensure_ascii=False, indent=2).encode("utf-8")


def json_text_to_history(json_text: str) -> List[Dict[str, Any]]:
    """
    Parse JSON text back into a list[dict]. Returns [] on any failure.
    """
    try:
        data = json.loads(json_text)
        if isinstance(data, list):
            # ensure all items are dict-like
            return [x for x in data if isinstance(x, dict)]
        return []
    except Exception:
        return []

# -----------------------------------------------------------------------------
# Tiny convenience
# -----------------------------------------------------------------------------
def safe_filename(base: str, ext: str) -> str:
    """
    Sanitize a base name and append the extension (e.g., ".pdf").
    """
    bad = '/\\:*?"<>|'
    clean = "".join(c for c in (base or "export") if c not in bad).strip()
    if not clean:
        clean = "export"
    if not ext.startswith("."):
        ext = "." + ext
    return clean + ext

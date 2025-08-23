# shared/exports.py
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from docx import Document

def text_to_pdf_bytes(text: str) -> bytes:
    """Convert plain text into a simple PDF (bytes)."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40
    for line in text.splitlines():
        pdf.drawString(40, y, line)
        y -= 15
        if y < 40:
            pdf.showPage()
            y = height - 40
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()

def text_to_docx_bytes(text: str) -> bytes:
    """Convert plain text into a simple Word .docx (bytes)."""
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

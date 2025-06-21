from fpdf import FPDF
from docx import Document
from io import BytesIO
import streamlit as st

# === PDF Export ===
def export_text_to_pdf(text: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    # Write PDF to buffer
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    # Convert to bytes before passing
    st.download_button(
        label="⬇️ Download PDF",
        data=buffer.getvalue(),
        file_name="corrected_output.pdf",
        mime="application/pdf"
    )

# === DOCX Export ===
def export_text_to_docx(text: str):
    doc = Document()
    doc.add_paragraph(text)

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    # Convert to bytes before passing
    st.download_button(
        label="⬇️ Download DOCX",
        data=buffer.getvalue(),
        file_name="corrected_output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
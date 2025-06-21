import PyPDF2

def extract_text_from_pdf(file):
    """
    Extracts and returns plain text from a PDF file.
    """
    try:
        reader = PyPDF2.PdfReader(file)
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text.strip())
        return "\n".join(full_text).strip()
    except Exception as e:
        return f"❌ Failed to extract text from PDF: {e}"
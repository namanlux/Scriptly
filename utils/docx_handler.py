import docx
from io import BytesIO
import logging

def extract_text_from_docx(file):
    """
    Extracts and returns plain text from a .docx Word file.
    """
    try:
        # Ensure compatibility with Streamlit's file uploader
        file_data = BytesIO(file.read()) if hasattr(file, 'read') else file
        doc = docx.Document(file_data)
        full_text = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(full_text)
    except Exception as e:
        logging.error(f"❌ Failed to extract text from Word file: {e}")
        return ""
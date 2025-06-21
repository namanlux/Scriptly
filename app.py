import streamlit as st
from utils.grammar_corrector import correct_text
from utils.pdf_handler import extract_text_from_pdf
from utils.docx_handler import extract_text_from_docx
from fpdf import FPDF
from docx import Document
from io import BytesIO
import difflib
import html
import base64

st.set_page_config(page_title="Scriptly - AI Grammar Assistant", layout="wide", page_icon="📝")

# === Inject custom background and button styles ===
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF6EC;
    }

    div.stButton > button {
        background-color: #FAF6EC;
        color: black;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    div.stButton > button:hover {
        background-color: #f2eee6;
        color: black;
    }

    div.stDownloadButton > button {
        background-color: #FAF6EC;
        color: black;
        border: 1px solid #ccc;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }

    div.stDownloadButton > button:hover {
        background-color: #f2eee6;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# === Display Centered Logo ===
def center_logo(path, width="180px"):
    with open(path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        st.markdown(
            f"""
            <div style="display:flex; justify-content:center; margin-top:10px;">
                <img src="data:image/png;base64,{encoded}" style="width:{width};"/>
            </div>
            """,
            unsafe_allow_html=True,
        )

center_logo("assets/scriptly_logo.png")

# === Title and Description ===
st.title("Scriptly: Your AI Grammar Assistant")
st.markdown("Fix grammar, get clean summaries, and see improvements side-by-side.")

# === Upload Section ===
st.subheader("📄 Upload a file (PDF or DOCX)")
uploaded_file = st.file_uploader("Drag and drop file here", type=["pdf", "docx"])
user_text = ""

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        user_text = extract_text_from_pdf(uploaded_file)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        user_text = extract_text_from_docx(uploaded_file)
    st.success("✅ File loaded successfully!")

# === Text Area ===
st.markdown("🔍 **Tip:** For best results, input text should be between **150 and 200 words**.")
if not uploaded_file:
    user_text = st.text_area("Type Or paste your text here", height=250)

# === Highlight Differences ===
def highlight_differences(original, corrected):
    if isinstance(original, tuple):
        original = original[0]
    if isinstance(corrected, tuple):
        corrected = corrected[0]

    diff = list(difflib.ndiff(original.split(), corrected.split()))
    html_diff = ""
    for token in diff:
        if token.startswith("- "):
            html_diff += f"<span style='background-color:#ffdddd;color:red;'> {html.escape(token[2:])} </span>"
        elif token.startswith("+ "):
            html_diff += f"<span style='background-color:#ddffdd;color:green;'> {html.escape(token[2:])} </span>"
        elif token.startswith("  "):
            html_diff += f"{html.escape(token[2:])} "
    return html_diff

# === Grammar Correction ===
if st.button("✅ Correct Grammar and Show Summary"):
    if user_text.strip():
        corrected_text, summary = correct_text(user_text)

        st.subheader("📌 Corrected Version")
        st.text_area("Corrected Text", value=corrected_text, height=250)

        st.subheader("🪞 See What Changed")
        diff_html = highlight_differences(user_text, corrected_text)
        st.markdown(
            f"""
            <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; font-family:monospace; font-size:15px;">
                {diff_html}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("🧠 Summary")
        st.success(summary)

        st.subheader("⬇️ Export Corrected Version")
        col1, col2 = st.columns(2)

        with col1:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in corrected_text.split("\n"):
                pdf.multi_cell(0, 10, line)
            pdf_buffer = BytesIO()
            pdf_bytes = pdf.output(dest="S").encode("latin1")
            pdf_buffer.write(pdf_bytes)
            pdf_buffer.seek(0)
            st.download_button("⬇️ Download PDF", data=pdf_buffer, file_name="corrected_output.pdf", mime="application/pdf")

        with col2:
            doc = Document()
            doc.add_paragraph(corrected_text)
            doc_buffer = BytesIO()
            doc.save(doc_buffer)
            doc_buffer.seek(0)
            st.download_button("⬇️ Download DOCX", data=doc_buffer, file_name="corrected_output.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.warning("⚠️ Please enter or upload some text first.")

st.markdown("---")
st.markdown("Made with ❤️ for quality writing.")
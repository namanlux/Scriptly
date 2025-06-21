from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline
)
import torch
import textwrap

# ========== Model Setup ==========

# Grammar correction model (efficient + stylistic)
GRAMMAR_MODEL = "pszemraj/flan-t5-large-grammar-synthesis"
grammar_tokenizer = AutoTokenizer.from_pretrained(GRAMMAR_MODEL)
grammar_model = AutoModelForSeq2SeqLM.from_pretrained(
    GRAMMAR_MODEL,
    torch_dtype=torch.float16,
    device_map="auto"
)
grammar_model.eval()

# Summarization pipeline (improved fallback handling)
try:
    summarizer = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device=0 if torch.cuda.is_available() else -1
    )
except Exception as e:
    summarizer = None  # Summary fallback
    print("⚠️ Summarizer pipeline not available:", e)

# ========== Core Function ==========
def correct_text(text: str, max_tokens: int = 512):
    """
    Apply grammar + style correction.
    Supports long inputs by chunking intelligently.
    Returns both corrected text and summary.
    """
    chunks = textwrap.wrap(text, width=700, break_long_words=False, break_on_hyphens=False)
    results = []

    for chunk in chunks:
        inputs = grammar_tokenizer(chunk, return_tensors="pt", truncation=True, max_length=max_tokens).to(grammar_model.device)
        with torch.no_grad():
            outputs = grammar_model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.0,
                do_sample=False,
            )
        corrected = grammar_tokenizer.decode(outputs[0], skip_special_tokens=True)
        results.append(corrected)

    corrected_text = "\n".join(results)
    summary = summarize_text(corrected_text)
    return corrected_text, summary

# ========== Summary Function ==========
def summarize_text(text: str, max_length: int = 120, min_length: int = 30) -> str:
    """
    Generates a summary from given text using BART.
    """
    if not summarizer:
        return "⚠️ Summarizer unavailable."

    try:
        summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print("❌ Summary error:", e)
        return "⚠️ Could not generate summary."
import os
import re

def clean_text(text: str) -> str:
    """
    Basic text cleaner: trims whitespace, normalizes spaces, and removes extra punctuation.
    """
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"[‘’]", "'", text)
    return text


def ensure_dir(path: str):
    """
    Ensures a directory exists.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def count_tokens(text: str, tokenizer):
    """
    Counts the number of tokens using a given tokenizer.
    """
    return len(tokenizer(text)["input_ids"])


def print_sample_dataset(df, n=5):
    """
    Nicely print first few samples of a dataset DataFrame.
    """
    print("📊 Sample Dataset Entries:")
    print(df.head(n).to_string(index=False))


def truncate_text(text: str, max_words=50):
    """
    Truncates text to a specific word limit.
    """
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")
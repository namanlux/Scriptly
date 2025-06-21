import os
import pandas as pd
import warnings
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    TrainingArguments,
    Trainer
)

# === Config ===
BASE_MODEL = "google/flan-t5-large"
RAW_DATA_DIR = "datasets_raw"
LOG_DIR = "train_model/logs"
CHECKPOINT_DIR = "train_model/checkpoints"


def load_dataset():
    print("📂 Loading CSVs from:", RAW_DATA_DIR)
    all_dfs = []
    for file in os.listdir(RAW_DATA_DIR):
        if file.endswith(".csv"):
            path = os.path.join(RAW_DATA_DIR, file)
            try:
                df = pd.read_csv(path)[["input_text", "target_text"]]
                df = df.dropna(subset=["input_text", "target_text"])
                all_dfs.append(df)
                print(f"✅ Loaded: {file} ({len(df)} rows)")
            except Exception as e:
                warnings.warn(f"⚠️ Skipped {file} due to error: {e}")

    if not all_dfs:
        raise ValueError("❌ No valid datasets found in 'datasets_raw/'.")

    merged_df = pd.concat(all_dfs, ignore_index=True)
    print(f"📊 Total merged rows: {len(merged_df)}")

    # Rename for tokenizer compatibility
    merged_df = merged_df.rename(columns={"input_text": "source", "target_text": "target"})

    # Train/test split
    train_df, val_df = train_test_split(merged_df, test_size=0.2, random_state=42)
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)

    return {"train": train_dataset, "validation": val_dataset}


def train():
    print("🚀 Starting training pipeline...")

    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL)

    # Tokenizer function
    def tokenize_function(example):
        return tokenizer(
            example["source"],
            text_target=example["target"],
            truncation=True,
            padding="max_length",
            max_length=128,
        )

    # Load and tokenize datasets
    dataset = load_dataset()
    tokenized_datasets = {
        split: dataset[split].map(tokenize_function, batched=True)
        for split in dataset
    }

    # Training setup
    training_args = TrainingArguments(
        output_dir=CHECKPOINT_DIR,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=4,  # Effective batch size = 4
        num_train_epochs=3,
        logging_dir=LOG_DIR,
        overwrite_output_dir=True,
        report_to="none"
    )

    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
    )

    trainer.train()
    print("✅ Training finished!")


if __name__ == "__main__":
    train()
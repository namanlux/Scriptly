import os
import pandas as pd

RAW_DIR = "train_model/datasets_raw"
OUTPUT_FILE = "train_model/dataset.csv"
EXPECTED_COLS = ["Category", "input_text", "target_text"]

def normalize_columns(df):
    rename_map = {
        "input": "input_text",
        "source": "input_text",
        "original": "input_text",
        "output": "target_text",
        "target": "target_text",
        "corrected": "target_text",
    }
    df = df.rename(columns=rename_map)

    # Ensure all required columns
    if "input_text" in df.columns and "target_text" in df.columns:
        if "Category" not in df.columns:
            df["Category"] = "general"
        return df[EXPECTED_COLS]
    return None

def clean_and_merge():
    all_dfs = []
    for file in os.listdir(RAW_DIR):
        if file.endswith(".csv"):
            path = os.path.join(RAW_DIR, file)
            try:
                df = pd.read_csv(path)
                df = normalize_columns(df)
                if df is not None:
                    df = df.dropna().drop_duplicates()
                    all_dfs.append(df)
                    print(f"✅ Cleaned: {file} ({len(df)} rows)")
                else:
                    print(f"❌ Skipped (Invalid columns): {file}")
            except Exception as e:
                print(f"⚠️ Failed to load {file}: {e}")

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n📦 Merged dataset saved to: {OUTPUT_FILE} ({len(final_df)} total rows)")
    else:
        print("⚠️ No valid datasets to merge.")

if __name__ == "__main__":
    print("🔧 Fixing and merging datasets...")
    clean_and_merge()
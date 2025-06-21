import os
import pandas as pd
from tqdm import tqdm

RAW_DIR = "train_model/datasets_raw"
OUTPUT_FILE = "train_model/dataset.csv"
REQUIRED_COLUMNS = ["Category", "input_text", "target_text"]

def normalize_columns(df: pd.DataFrame, source: str) -> pd.DataFrame:
    df = df.copy()
    
    # Try to guess or rename input/target columns
    lower_cols = [col.lower() for col in df.columns]

    if len(df.columns) >= 3:
        df.columns = df.columns[:3]  # Use only first 3 if more
        df = df.iloc[:, :3]          # Trim extras
        df.columns = REQUIRED_COLUMNS
    elif "input_text" in lower_cols and "target_text" in lower_cols:
        if "category" not in lower_cols:
            df["Category"] = "General"
        df = df[REQUIRED_COLUMNS]
    else:
        raise ValueError(f"⚠️ Can't normalize columns in {source}")

    return df.dropna()

def main():
    print(f"🚀 Merging all CSVs in {RAW_DIR}...\n")
    all_dfs = []

    for file in tqdm(os.listdir(RAW_DIR)):
        if file.endswith(".csv"):
            path = os.path.join(RAW_DIR, file)
            try:
                df = pd.read_csv(path)
                df = normalize_columns(df, file)
                all_dfs.append(df)
                print(f"✅ Added {file} with {len(df)} rows")
            except Exception as e:
                print(f"❌ Skipped {file} — {e}")

    if all_dfs:
        merged = pd.concat(all_dfs, ignore_index=True)
        merged.to_csv(OUTPUT_FILE, index=False)
        print(f"\n🎉 Done! Final dataset saved as '{OUTPUT_FILE}' with {len(merged)} rows.")
    else:
        print("❌ No datasets merged — all files invalid.")

if __name__ == "__main__":
    main()
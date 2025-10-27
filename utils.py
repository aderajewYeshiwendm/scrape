import pandas as pd
import os
from datetime import datetime

def save_to_csv(df: pd.DataFrame, handle: str, folder: str):
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    path = f"{folder}/{handle}_followers_{timestamp}.csv"
    df.to_csv(path, index=False)
    print(f"Saved {len(df):,} followers → {path}")
    return path
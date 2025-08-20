from __future__ import annotations
from pathlib import Path
import io
import pandas as pd

def ensure_sample_dataset():
    p = Path("data")
    p.mkdir(exist_ok=True)
    csv = p / "sample_dataset.csv"
    if not csv.exists():
        csv.write_text("date,channel\n2025-08-01,LinkedIn\n2025-08-03,Email\n2025-08-05,Instagram\n", encoding="utf-8")

def load_csv(path: str):
    try:
        return pd.read_csv(path)
    except Exception:
        return None

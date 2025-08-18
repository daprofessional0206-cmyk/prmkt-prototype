# shared/data.py — dataset utils
from __future__ import annotations
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
SAMPLE_CSV = DATA_DIR / "sample_dataset.csv"

def ensure_sample_dataset():
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    if not SAMPLE_CSV.exists():
        SAMPLE_CSV.write_text(
            "date,channel,post_type,headline,copy,clicks,impressions,engagement_rate\n"
            "2025-08-01,LinkedIn,post,Acme RoboHub 2.0 Launch,Fast setup & SOC2 Type II,124,6500,3.1\n"
            "2025-08-03,Email,newsletter,Why customers switch to Acme,Save 30% with faster onboarding,410,17800,2.2\n"
            "2025-08-05,Instagram,reel,Behind-the-scenes of RoboHub,Meet the team that builds speed,980,45900,1.6\n"
        )

def load_csv(nrows: int | None = None) -> pd.DataFrame:
    df = pd.read_csv(SAMPLE_CSV)
    if nrows:
        df = df.head(nrows)
    return df

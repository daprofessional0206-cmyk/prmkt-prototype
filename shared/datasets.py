# shared/datasets.py
from __future__ import annotations

from pathlib import Path
from typing import Optional
import pandas as pd
import streamlit as st


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLE_CSV = DATA_DIR / "sample_dataset.csv"


def ensure_sample_dataset() -> None:
    """Create/overwrite a tiny CSV so preview always works."""
    DATA_DIR.mkdir(exist_ok=True)
    if not SAMPLE_CSV.exists():
        SAMPLE_CSV.write_text(
            "date,channel,post_type,headline,copy,clicks,impressions,engagement_rate\n"
            "2025-08-01,LinkedIn,post,Acme RoboHub 2.0 Launch,Fast setup & SOC2 Type II,124,6500,3.1\n"
            "2025-08-03,Email,newsletter,Why customers switch to Acme,Save 30% with faster onboarding,410,17800,2.2\n"
            "2025-08-05,Instagram,reel,Behind-the-scenes of RoboHub,Meet the team that builds speed,980,45900,1.6\n"
        )


@st.cache_data(show_spinner=False)
def load_csv(path: Path, nrows: Optional[int] = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if nrows:
        df = df.head(int(nrows))
    return df

# pages/99_Admin_Settings.py
from __future__ import annotations
import io
import pandas as pd
import streamlit as st

from shared import state

# Optional dataset helpers (won't crash if missing)
try:
    from shared.datasets import ensure_sample_dataset, load_csv  # type: ignore
except Exception:  # helpers absent? make no-ops
    def ensure_sample_dataset() -> None: ...
    def load_csv(path: str) -> pd.DataFrame | None:
        try:
            return pd.read_csv(path)
        except Exception:
            return None

st.set_page_config(page_title="Admin Settings", page_icon="🛠️", layout="wide")
st.title("Admin Settings")

# --- OpenAI status ---
openai_ok = state.has_openai()
st.write(f"**OpenAI:** {'✅ Connected' if openai_ok else '❌ Missing key'}")
st.caption(
    "Set your key as Streamlit secret `openai_api_key` (preferred) or environment variable `OPENAI_API_KEY`. "
    "After updating secrets, use **Manage app → Reboot → Clear cache**."
)

with st.expander("How to set the key (quick reference)"):
    st.markdown(
        """
**Streamlit Cloud:**
1. Click **⋮ → Manage app** (top-right) → **Secrets**
2. Add:
```yaml
openai_api_key: sk-...
    """
)

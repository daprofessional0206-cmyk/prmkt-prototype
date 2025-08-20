from __future__ import annotations
import io
import pandas as pd
import streamlit as st
from shared import ui, state, history
# optional dataset helpers
try:
    from shared.datasets import ensure_sample_dataset, load_csv
except Exception:
    def ensure_sample_dataset(): ...
    def load_csv(path: str): return None

st.set_page_config(page_title="Admin Settings", page_icon="🛠️", layout="wide")
ui.inject_css()
ui.page_title("Admin Settings")

state.init()

# --- OpenAI status ---
openai_ok = state.has_openai()
st.write(f"**OpenAI:** {'✅ Connected' if openai_ok else '❌ Missing key'}")
st.caption("Set your key as Streamlit secret **openai_api_key** (preferred) or environment variable **OPENAI_API_KEY**.")

with st.expander("How to set the key (quick reference)"):
    st.markdown(
        """
**Streamlit Cloud:**
1. Click **⋯ → Manage app** (top-right) → **Secrets**
2. Add:
```yaml
openai_api_key: sk-...

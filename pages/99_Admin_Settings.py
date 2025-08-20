# pages/99_Admin_Settings.py
from __future__ import annotations
import streamlit as st

from shared import state
from shared.llm import is_openai_ready

# If you kept helper functions in shared/datasets.py, import them here:
try:
    from shared.datasets import ensure_sample_dataset, load_csv  # optional; ignore if you removed them
except Exception:
    def ensure_sample_dataset() -> None: ...
    def load_csv(path: str): return None

state.init()
st.set_page_config(page_title="Admin Settings", layout="wide")
st.title("⚙️ Admin Settings")

ok = is_openai_ready()
st.markdown(f"**OpenAI status:** {'✅ Connected' if ok else '❌ Missing key'}")

st.info(
    "Set your OpenAI key as a Streamlit secret (`openai_api_key`) or environment variable `OPENAI_API_KEY`. "
    "Then reboot the app."
)

with st.expander("Sample dataset (optional)"):
    ensure_sample_dataset()
    st.success("Sample dataset ensured.")

import streamlit as st
import io
import pandas as pd
from shared.llm import is_openai_ready
from shared.datasets import ensure_sample_dataset, load_csv

# --- OpenAI key check --------------------------------------------------------
openai_ok = is_openai_ready()
st.write(f"**OpenAI:** {'✅ Connected' if openai_ok else '❌ Missing key'}")

st.caption(
    "Set your key as Streamlit secret `openai_api_key` (preferred) or "
    "environment variable `OPENAI_API_KEY`. After updating secrets, use "
    "**Manage app → Reboot → Clear cache**."
)

with st.expander("How to set the key (quick reference)"):
    st.markdown(
        """
        **Streamlit Cloud:**
        1. Click **⋮ → Manage app** (top-right) → **Secrets**
        2. Add:
        ```yaml
        openai_api_key: sk-...
        ```
        """
    )

# --- Dataset tools (optional) ------------------------------------------------
st.subheader("Dataset Tools (optional)")

left, right = st.columns([2, 1])
with left:
    st.write(
        "If your project includes a sample dataset helper, you can prepare it here. "
        "This safely no-ops if helpers are not present."
    )
with right:
    if st.button("Ensure sample dataset"):
        ensure_sample_dataset()
        st.success("Sample dataset ensured (or already present).")

with st.expander("Preview a CSV (local path)"):
    path = st.text_input("CSV path (e.g., data/sample_dataset.csv)", value="data/sample_dataset.csv")
    if st.button("Preview CSV"):
        df = load_csv(path)
        if df is None:
            st.warning("Could not load CSV (missing file or reader unavailable).")
        else:
            st.dataframe(df.head(50), use_container_width=True)

st.subheader("Upload a CSV (session memory)")
uploaded = st.file_uploader("Upload CSV to preview (not persisted on Cloud)", type=["csv"])
if uploaded is not None:
    try:
        df_up = pd.read_csv(io.BytesIO(uploaded.getvalue()))
        st.success(f"Loaded '{uploaded.name}' — showing first 50 rows.")
        st.dataframe(df_up.head(50), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")

# --- History management ------------------------------------------------------
st.subheader("History")

c1, c2 = st.columns(2)
with c1:
    try:
        from shared.history import get_history  # type: ignore
        count = len(get_history())
    except Exception:
        count = len(st.session_state.get("history", []))
    st.write(f"Items in history: **{count}**")

with c2:
    if st.button("Clear history", type="primary"):
        st.session_state["history"] = []
        st.success("History cleared.")

# --- App info ----------------------------------------------------------------
st.subheader("App Info")
st.write("Presence — multi-page prototype (Phase 3.2)")
st.caption("If changes don’t show up on Cloud, Manage app → Reboot and Clear cache.")

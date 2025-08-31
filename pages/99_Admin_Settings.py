# pages/99_Admin_Settings.py
from __future__ import annotations
import streamlit as st
import io, pandas as pd
from shared import ui, state, history

ui.page_title("Admin & Settings", "Keys, dataset utilities, and maintenance.")
state.init()

# OpenAI
st.subheader("OpenAI")
st.write(f"Connected: {'✅' if state.has_openai() else '❌ (offline templates)'}")
st.caption("Keys live in Streamlit secrets, not in code.")

# Dataset tools (optional; safe no-ops if not present)
st.subheader("Dataset tools (optional)")
with st.expander("Upload a CSV to preview (session only)"):
    uploaded = st.file_uploader("CSV", type=["csv"])
    if uploaded:
        try:
            df = pd.read_csv(io.BytesIO(uploaded.getvalue()))
            st.dataframe(df.head(50), use_container_width=True)
        except Exception as e:
            st.error(f"Failed: {e}")

# History maintenance
st.subheader("History maintenance")
c1, c2 = st.columns(2)
with c1:
    st.write(f"Items in history: **{len(history.get_history())}**")
with c2:
    if st.button("Clear history", type="primary"):
        st.session_state["history"] = []
        st.success("History cleared.")

st.caption("Presence — multi-page prototype (Phase 3 Stabilize Pack)")

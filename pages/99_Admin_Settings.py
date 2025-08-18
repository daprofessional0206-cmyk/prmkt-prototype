# pages/99_Admin_Settings.py
from __future__ import annotations
import streamlit as st
from shared import state, ui
from shared.data import ensure_sample_dataset, load_csv

state.init()
ui.title("Admin & Settings")

st.write("Version:", "v2.0 scaffold")
if st.button("Reset Streamlit cache"):
    st.cache_data.clear()
    st.success("Cache cleared. Refresh the page.")

if st.button("Recreate sample dataset"):
    ensure_sample_dataset()
    st.success("Sample dataset ensured.")

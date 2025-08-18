# pages/04_Optimizer_Tests.py — scaffold
from __future__ import annotations
import streamlit as st
from shared import state, ui
from shared.history import add as add_history

state.init()
ui.title("Optimizer & Adaptive Tests")

text = st.text_area("Paste copy to optimize", height=140)

col1, col2 = st.columns(2)
with col1:
    if st.button("Suggest improvements"):
        if not text.strip():
            st.warning("Paste some copy first.")
        else:
            # simple placeholder suggestion
            suggestions = "- Use stronger verbs.\n- Shorten first sentence.\n- Add a concrete benefit near the CTA."
            st.markdown("**Suggestions**")
            st.write(suggestions)
            add_history("Optimizer", {"text": text}, suggestions, tags=["Optimizer"])

with col2:
    if st.button("Generate A/B rewrites"):
        if not text.strip():
            st.warning("Paste some copy first.")
        else:
            rewrites = ["Variant A:\n" + text, "Variant B:\n" + text.replace(" ", "  ")]
            st.markdown("**Rewrites**")
            st.write("\n\n".join(rewrites))
            add_history("Testing", {"text": text}, rewrites, tags=["Testing"])

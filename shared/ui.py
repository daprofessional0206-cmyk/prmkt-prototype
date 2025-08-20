from __future__ import annotations
import streamlit as st

def inject_css():
    st.markdown(
        """
        <style>
        .stButton>button { height: 42px; }
        .note { background: #0f172a; color: #e2e8f0; padding: 0.8rem 1rem; border-radius: 8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def page_title(title: str, subtitle: str = ""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

def page_link(script_path: str, label: str):
    st.link_button(label, f"/{script_path.split('/')[-1].replace('.py','')}")

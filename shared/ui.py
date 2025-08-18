from __future__ import annotations
import streamlit as st

def title(text: str, subtitle: str | None = None):
    st.title(text)
    if subtitle:
        st.caption(subtitle)

def divider():
    st.markdown("<hr style='border:1px solid #202431;margin:1rem 0;'/>", unsafe_allow_html=True)

def status_ok(msg: str): st.success(msg)
def status_info(msg: str): st.info(msg)

def page_link(path: str, label: str):
    if hasattr(st, "page_link"):
        st.page_link(path, label=label)
    else:
        st.write(f"→ **{label}** (open from sidebar)")

def card(title: str, body: str, link_path: str):
    with st.container(border=True):
        st.subheader(title)
        st.caption(body)
        page_link(link_path, "Open")

def footer(text: str):
    divider()
    st.caption(text)

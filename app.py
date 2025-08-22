# app.py
from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

# Local shared modules (already in your repo)
from shared import state, history  # type: ignore

# Optional dataset helpers (present as shared/datasets.py in your repo)
try:
    from shared.datasets import load_csv, ensure_sample_dataset  # type: ignore
    HAS_DATASET_HELPERS = True
except Exception:
    HAS_DATASET_HELPERS = False


# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Presence — PR & Marketing OS",
    page_icon="📣",
    layout="wide",
)
st.write("")  # small top spacing

# -----------------------------------------------------------------------------
# App state & OpenAI status
# -----------------------------------------------------------------------------
state.init()  # safe no-op if already initialized

st.title("Presence — PR & Marketing OS (Prototype)")

openai_ok = state.has_openai()
st.write(
    f"**OpenAI:** {'✅ Connected' if openai_ok else '❌ Missing key'}"
)
st.caption(
    "Set your key as Streamlit secret `openai_api_key` (preferred) or env var `OPENAI_API_KEY`."
    " After updating secrets, use **Manage app → Reboot → Clear cache**."
)

# -----------------------------------------------------------------------------
# Active company banner
# -----------------------------------------------------------------------------
co = state.get_company()
with st.container():
    if co and getattr(co, "name", "").strip():
        parts = []
        if getattr(co, "name", None):
            parts.append(f"**{co.name}**")
        if getattr(co, "industry", None):
            parts.append(f"{co.industry}")
        if getattr(co, "size", None):
            parts.append(f"{co.size}")
        banner_text = " · ".join(parts) if parts else "Company profile set"
        st.success(f"Active company: {banner_text}")
        st.caption("Tip: add brand rules in Company Profile so all tools align to your voice.")
    else:
        st.warning("No company selected yet. Open **Company Profile** to set one.")

st.divider()

# -----------------------------------------------------------------------------
# Sample Data Preview (optional)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("**Sample Data Preview**")
    if HAS_DATASET_HELPERS:
        try:
            ensure_sample_dataset()
            df = load_csv("data/sample_dataset.csv")
            n = st.number_input("Preview rows", 1, 25, 5, step=1)
            if df is not None:
                st.dataframe(df.head(int(n)), use_container_width=True, height=220)
            else:
                st.caption("No sample dataset found.")
        except Exception:
            st.caption("Dataset helpers present but preview failed.")
    else:
        st.caption("Dataset helpers not available.")

# -----------------------------------------------------------------------------
# Main tiles (copy) — simple overview
# -----------------------------------------------------------------------------
st.markdown("Phase 3.2 • Multi-page UI with: Company Profile, Strategy Ideas, Content Engine, Optimizer Tests, History & Insights")

col1, col2, col3 = st.columns(3)
with col1:
    st.header("🏢 Company Profile")
    st.write("Set your **name, industry, size, goals**, and **brand rules** once; all tools use them.")
    st.page_link("pages/01_Company_Profile.py", label="Open Company Profile →")

with col2:
    st.header("💡 Strategy Ideas")
    st.write("Brainstorm **campaign angles & PR ideas**. Generates multiple variants fast.")
    st.page_link("pages/02_Strategy_Ideas.py", label="Open Strategy Ideas →")

with col3:
    st.header("📰 Content Engine")
    st.write("Create **press releases, ads, posts, landing pages, blogs** with brand-safe copy.")
    st.page_link("pages/03_Content_Engine.py", label="Open Content Engine →")

st.divider()

# -----------------------------------------------------------------------------
# Quick links (safe routes; no 404 pop-ups)
# -----------------------------------------------------------------------------
st.subheader("Open a tool")
st.page_link("pages/01_Company_Profile.py",    label="Company Profile →",           icon="🏢")
st.page_link("pages/02_Strategy_Ideas.py",     label="Strategy Ideas →",            icon="💡")
st.page_link("pages/03_Content_Engine.py",     label="Content Engine →",            icon="📰")
st.page_link("pages/04_Optimizer_Tests.py",    label="Optimizer Tests →",           icon="🧪")
st.page_link("pages/05_History_Insights.py",   label="History & Insights →",        icon="📊")

# New Phase-3.4/3.5 pages
st.page_link("pages/07_PR_Intelligence.py",    label="PR Intelligence (v1) →",      icon="🛰️")
st.page_link("pages/08_Creator_Intelligence.py", label="Creator Intelligence (v1) →", icon="🎥")

st.page_link("pages/99_Admin_Settings.py",     label="Admin Settings →",            icon="🛠️")

st.divider()

# -----------------------------------------------------------------------------
# Recent Activity (safe rendering of history entries)
# -----------------------------------------------------------------------------
st.subheader("Recent activity")

def _fmt_ts(ts: Any) -> str:
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(float(ts)).strftime("%Y-%m-%d %H:%M")
        if isinstance(ts, str):
            # ISO string or similar
            return ts.split(".")[0].replace("T", " ")
    except Exception:
        pass
    return "—"

def _print_entry(it: Dict[str, Any]) -> None:
    etype = it.get("type", "item")
    ts = _fmt_ts(it.get("ts") or it.get("time"))
    tags = it.get("tags") or []
    with st.container():
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{etype.capitalize()}**  ·  {ts}")
        with c2:
            if tags:
                st.caption(" · ".join([str(t) for t in tags]))
        # input
        payload = it.get("input") or it.get("payload") or {}
        if isinstance(payload, (dict, list)):
            with st.expander("Input", expanded=False):
                st.json(payload)
        elif isinstance(payload, str) and payload.strip():
            with st.expander("Input", expanded=False):
                st.code(payload)
        # output
        out = it.get("output") or it.get("result")
        if out:
            with st.expander("Output", expanded=True):
                if isinstance(out, (dict, list)):
                    st.json(out)
                else:
                    st.write(out)

# load last N
try:
    items: List[Dict[str, Any]] = history.get_history()  # type: ignore
except Exception:
    items = st.session_state.get("history", [])

if not items:
    st.caption("Nothing yet. Generate something in Strategy Ideas or Content Engine.")
else:
    max_items = min(5, len(items))
    for it in list(reversed(items))[:max_items]:
        _print_entry(it)
        st.markdown("---")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.caption("Presence — multi-page prototype (Phase 3.2)")
st.caption("If changes don’t show up on Cloud, use **Manage app → Reboot → Clear cache**.")

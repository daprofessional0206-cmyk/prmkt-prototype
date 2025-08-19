# app.py — Presence (Phase 3.2 Home)

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

# Local shared modules (created earlier)
from shared import state, history

# ──────────────────────────────────────────────────────────────────────────────
# App config + light CSS
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Presence — PR & Marketing OS (Prototype)",
    page_icon="📣",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.0rem; padding-bottom: 2.2rem; }
      .stTextArea textarea { font-size: 0.95rem; line-height: 1.45; }
      .stDownloadButton button { width: 100%; }
    </style>
    """,
    unsafe_allow_html=True,
)

def divider() -> None:
    st.markdown("<hr style='border:1px solid #202431; margin: 1rem 0;'/>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# Sample dataset (optional mini-preview in sidebar)
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
SAMPLE_CSV = DATA_DIR / "sample_dataset.csv"

@st.cache_data(show_spinner=False)
def load_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.head(nrows) if nrows else df

def ensure_sample_dataset() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    if not SAMPLE_CSV.exists():
        SAMPLE_CSV.write_text(
            "date,channel,post_type,headline,copy,clicks,impressions,engagement_rate\n"
            "2025-08-01,LinkedIn,post,Acme RoboHub 2.0 Launch,Fast setup & SOC2 Type II,124,6500,3.1\n"
            "2025-08-03,Email,newsletter,Why customers switch to Acme,Save 30% with faster onboarding,410,17800,2.2\n"
            "2025-08-05,Instagram,reel,Behind-the-scenes of RoboHub,Meet the team that builds speed,980,45900,1.6\n"
        )

ensure_sample_dataset()

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar: status + dataset preview
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("⚙️ App Status")
    st.caption("Presence — multi-page prototype (Phase 3.2)")

    # Secrets / API status
    if state.has_openai():
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Offline (using templates)")

    divider()

    st.subheader("📁 Sample Data Preview")
    rows = st.number_input("Preview rows", 1, 20, 5, key="sb_preview_rows")
    st.caption(f"Dataset: `{SAMPLE_CSV.name}`")
    try:
        st.dataframe(load_csv(SAMPLE_CSV, nrows=int(rows)), use_container_width=True)
        if st.button("Reset sample data", key="btn_reset_sample"):
            if SAMPLE_CSV.exists():
                SAMPLE_CSV.unlink()
            ensure_sample_dataset()
            st.rerun()
    except Exception as e:
        st.warning(f"Could not load dataset preview: {e!s}")

    divider()
    st.caption("Use the navigation in the left sidebar to open pages.")

# ──────────────────────────────────────────────────────────────────────────────
# Home content
# ──────────────────────────────────────────────────────────────────────────────
st.title("📣 Presence — PR & Marketing OS (Prototype)")
st.caption("Phase 3.2 · Multi-page UI ready: Company Profile, Strategy Ideas, Content Engine, Optimizer Tests, History & Insights")

company = state.get_company()
st.success(
    f"Active company: **{company.get('name','(set in Company Profile)')}** · "
    f"{company.get('industry','—')} · {company.get('size','—')}"
)
if state.get_brand_rules().strip():
    st.caption("Brand rules loaded ✅")
else:
    st.caption("Tip: add brand rules in **Company Profile** so all tools align to your voice.")

divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.header("🏢 Company Profile")
    st.write("Set your **name**, **industry**, **size**, **goals**, and **brand rules** once; all tools use them.")
    st.page_link("pages/01_Company_Profile.py", label="Open Company Profile →", icon="🏢")

with col2:
    st.header("💡 Strategy Ideas")
    st.write("Brainstorm **campaign angles** & **PR ideas**. Generates multiple variants fast.")
    st.page_link("pages/02_Strategy_Ideas.py", label="Open Strategy Ideas →", icon="💡")

with col3:
    st.header("📝 Content Engine")
    st.write("Create **press releases, ads, posts, landing pages** with brand-safe copy.")
    st.page_link("pages/03_Content_Engine.py", label="Open Content Engine →", icon="📝")

divider()

col4, col5 = st.columns(2)
with col4:
    st.header("🧪 Optimizer Tests")
    st.write("Run **A/B/C** style variations by tone, length, CTA and compare quickly.")
    st.page_link("pages/04_Optimizer_Tests.py", label="Open Optimizer Tests →", icon="🧪")

with col5:
    st.header("📊 History & Insights")
    st.write("Filter/search **everything generated**. Export or clear in one click.")
    st.page_link("pages/05_History_Insights.py", label="Open History & Insights →", icon="📊")

divider()

st.subheader("Recent activity")
items = history.get_history()
if not items:
    st.caption("No history yet. Generate content or strategies to see them here.")
else:
    for it in items[:5]:
        st.markdown(f"**{it['kind']}** — {it['ts']}")
        if it.get("tags"):
            st.caption(", ".join(it["tags"]))
        st.json(it["input"])
        st.divider()

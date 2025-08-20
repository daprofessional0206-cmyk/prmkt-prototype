from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import streamlit as st

from shared import ui, state, history


# ----------------- page config -----------------
st.set_page_config(
    page_title="Presence — PR & Marketing OS (Prototype)",
    page_icon="📣",
    layout="wide",
)
APP_VERSION = "v3.2"
st.sidebar.caption(f"Build: {APP_VERSION}")

ui.inject_css()

# ----------------- top banner -----------------
ui.page_title(
    "Presence — PR & Marketing OS (Prototype)",
    "Phase 3.2 • Multi-page UI with: Company Profile, Strategy Ideas, Content Engine, Optimizer Tests, History & Insights",
)

co = state.get_company()
if co.name or co.industry or co.size:
    st.success(f"Active company: **{co.name or '—'}** · **{co.size or '—'}**")
else:
    st.info("Tip: fill **Company Profile** so tools can tailor output to your brand/voice.")

# ----------------- product tiles -----------------
with st.container():
    cols = st.columns(3)
    with cols[0]:
        st.header("🏢 Company Profile")
        st.write("Set your **name, industry, size, goals**, and brand rules once; all tools use them.")
        st.page_link("pages/01_Company_Profile.py",  label="Open Company Profile →",   icon="🏢")
    with cols[1]:
        st.header("💡 Strategy Ideas")
        st.write("Brainstorm **campaign angles & PR ideas**. Generates multiple variants fast.")
        st.page_link("pages/02_Strategy_Ideas.py",   label="Open Strategy Ideas →",    icon="💡")
    with cols[2]:
        st.header("📝 Content Engine")
        st.write("Create **press releases, ads, posts, landing pages, blogs** with brand-safe copy.")
        st.page_link("pages/03_Content_Engine.py",   label="Open Content Engine →",   icon="📝")

cols = st.columns(2)
with cols[0]:
    st.header("🧪 Optimizer Tests")
    st.write("Test different **tones/lengths/styles** to optimize messaging.")
    st.page_link("pages/04_Optimizer_Tests.py",  label="Open Optimizer Tests →",   icon="📈")
with cols[1]:
    st.header("📊 History & Insights")
    st.write("View/export/import all generated content, strategies, and tests.")
    st.page_link("pages/05_History_Insights.py",  label="Open History & Insights →",   icon="📊")

# ----------------- OpenAI status -----------------
st.divider()
ok = state.has_openai()
st.caption(
    f"OpenAI: {'✅ Connected' if ok else '❌ Missing key'} · "
    "Set `openai_api_key` in **Manage app → Secrets** or environment `OPENAI_API_KEY`."
)

# ----------------- sample dataset preview (optional) -----------------
st.sidebar.write("### Sample Data Preview")
csv_path = Path("data/sample_dataset.csv")
if csv_path.exists():
    try:
        n = st.sidebar.number_input("Preview rows", 1, 30, 5)
        df = pd.read_csv(csv_path)
        st.sidebar.dataframe(df.head(int(n)), use_container_width=True)
        if st.sidebar.button("Start over (reset sample data)"):
            csv_path.unlink(missing_ok=True)
            st.sidebar.success("Removed. Reboot app to recreate if your dataset helper does that.")
    except Exception as e:
        st.sidebar.error(f"Could not read sample dataset: {e}")
else:
    st.sidebar.info("`data/sample_dataset.csv` not found (optional).")

# ----------------- recent activity -----------------
st.divider()
st.subheader("🕑 Recent activity")
items = history.get_history(5)
if not items:
    st.caption("No history yet. Generate something in Strategy Ideas or Content Engine.")
else:
    for it in items:
        with st.expander(f"{it['ts']} · {it.get('kind','—')} · {', '.join(it.get('tags',[]))}"):
            st.json(it["payload"])
            st.write(it["result"])
# ── Footer ────────────────────────────────────────────────────────────────────
import streamlit as st  # safe if already imported
st.caption("Presence — multi-page prototype (Phase 3.2 • build v3.2)")

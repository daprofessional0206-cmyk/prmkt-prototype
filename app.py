# app.py — Presence (Phase 3.2 Home)

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

# Local shared modules (created earlier)
from shared import state, history
from shared.llm import is_openai_ready

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

    st.subheader("App Status")
    st.write("Presence — multi-page prototype (Phase 3.2)")
    st.write(f"OpenAI: {'✅ Connected' if is_openai_ready() else '❌ Missing key'}")

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

# === Recent activity (safe renderer) =========================================
import json
from datetime import datetime

try:
    # prefer central helpers if available
    from shared.history import get_history  # type: ignore
except Exception:
    def get_history():
        return st.session_state.get("history", [])

st.markdown("### History (last 20)")

def _normalize_for_view(it: dict) -> dict:
    """
    Handle legacy/malformed rows gracefully (no KeyErrors).
    Accepts old shapes like {'type':..., 'input':..., 'result':...}.
    """
    if not isinstance(it, dict):
        return {
            "kind": "unknown",
            "payload": {},
            "output": it,
            "tags": [],
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }

    kind = it.get("kind") or it.get("type") or "unknown"
    payload = it.get("payload") or it.get("input") or it.get("data") or {}
    output = it.get("output") if "output" in it else it.get("result")
    tags = it.get("tags", [])
    created = it.get("created_at") or it.get("ts") or datetime.utcnow().isoformat(timespec="seconds") + "Z"
    return {
        "kind": kind,
        "payload": payload if isinstance(payload, dict) else {"value": payload},
        "output": output,
        "tags": tags if isinstance(tags, list) else [str(tags)],
        "created_at": created,
    }

items = get_history()[:20]
if not items:
    st.caption("No history yet.")
else:
    for idx, raw in enumerate(items, start=1):
        it = _normalize_for_view(raw)
        title = f"{idx}. {it['kind']} • {it['created_at']}"
        with st.expander(title, expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Input")
                try:
                    st.json(it["payload"])
                except Exception:
                    st.write(it["payload"])
                if it.get("tags"):
                    st.caption("Tags")
                    st.write(", ".join(map(str, it["tags"])))
            with c2:
                st.caption("Output")
                out = it.get("output")
                if out is None:
                    st.write("—")
                elif isinstance(out, (list, tuple)):
                    for j, v in enumerate(out, start=1):
                        st.markdown(f"**Variant {j}**")
                        st.write(v if isinstance(v, str) else json.dumps(v, indent=2))
                elif isinstance(out, dict):
                    st.json(out)
                else:
                    st.write(str(out))

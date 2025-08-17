# app.py — Presence v2.0 (Phase 2 complete)

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────────────────────────
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import pandas as pd
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# App config + light CSS
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Presence — PR & Marketing AI Prototype",
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

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────
def divider() -> None:
    st.markdown("<hr style='border: 1px solid #202431; margin: 1.1rem 0;'/>", unsafe_allow_html=True)

def bulletize(text: str) -> List[str]:
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ──────────────────────────────────────────────────────────────────────────────
# Sample dataset utilities (Phase 2 / Steps 2–4)
# ──────────────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
SAMPLE_CSV = DATA_DIR / "sample_dataset.csv"

@st.cache_data(show_spinner=False)
def load_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if nrows:
        df = df.head(nrows)
    return df

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
# Optional OpenAI client (auto-detect via secrets)
# ──────────────────────────────────────────────────────────────────────────────
OPENAI_OK = False
client = None
MODEL = "gpt-4o-mini"  # fast & frugal

if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        OPENAI_OK = True
    except Exception:
        OPENAI_OK = False

# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class Company:
    name: str
    industry: str
    size: str
    goals: str

@dataclass
class ContentBrief:
    content_type: str
    tone: str
    length: str
    platform: str
    audience: str
    cta: str
    topic: str
    bullets: List[str]
    language: str = "English"
    variants: int = 1
    brand_rules: str = ""

# Session state
if "history" not in st.session_state:
    st.session_state["history"] = []  # list[dict]
if "next_id" not in st.session_state:
    st.session_state["next_id"] = 1   # for stable IDs in history

def add_history(kind: str, payload: dict, output):
    item = {
        "id": st.session_state["next_id"],
        "ts": now_iso(),
        "kind": kind,      # "strategy", "content", "Variants"
        "input": payload,  # dict
        "output": output,  # str or list[str]
        "tags": [],        # editable in UI
    }
    st.session_state["next_id"] += 1
    st.session_state.history.insert(0, item)
    st.session_state.history = st.session_state.history[:20]

# ──────────────────────────────────────────────────────────────────────────────
# LLM prompts and generators
# ──────────────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert PR & Marketing copywriter.
Write clear, compelling, brand-safe copy. Keep facts generic unless provided.
Match the requested tone, audience, and length. If brand rules are provided,
respect them and avoid banned words. If a language is specified, write in it.
Return only the copy, no preface.
"""

def make_prompt(br: ContentBrief, co: Company) -> str:
    bullets = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "(no bullets provided)"
    rules = br.brand_rules.strip() or "(none provided)"
    return f"""
Generate {br.variants} distinct variant(s) of a {br.length.lower()} {br.content_type.lower()}.

Language: {br.language}.
Audience: {br.audience}. Tone: {br.tone}.
Company: {co.name} ({co.industry}, size: {co.size}).
Topic / Offer: {br.topic}

Key points:
{bullets}

Call to action: {br.cta}

Brand rules (follow & avoid banned words):
{rules}

Constraints:
- Brand-safe, factual from provided info only.
- Strong opening, clear structure, crisp CTA.
- If multiple variants are requested, make them clearly different.
"""

def llm_copy(prompt: str, temperature: float = 0.6, max_tokens: int = 900) -> str:
    if not OPENAI_OK or client is None:
        raise RuntimeError("OpenAI is not configured.")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()

def offline_press_release(br: ContentBrief, co: Company) -> str:
    bullets_md = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "- (add key benefits)"
    cta_line = br.cta or "Contact us to learn more."
    return f"""FOR IMMEDIATE RELEASE

{co.name} Announces {br.topic}

[City, Date] – {co.name} introduces {br.topic} for {br.audience.lower()} in {co.industry.lower()}.
Key points:
{bullets_md}

This {br.length.lower()} release follows tone “{br.tone}” and brand guidance where provided.

{cta_line}
"""

def offline_generic_copy(br: ContentBrief, co: Company) -> str:
    bullets_md = "\n".join([f"• {b}" for b in br.bullets]) if br.bullets else "• Add 2–3 benefits"
    cta_line = br.cta or "Get started today."
    opening = {
        "Ad": "Attention, innovators!",
        "Social Post": "Quick update:",
        "Landing Page": "Welcome—here’s how we help:",
        "Email": "Hi there,",
        "Press Release": "FOR IMMEDIATE RELEASE",
    }.get(br.content_type, "Here’s something useful:")
    return f"""{opening}

{co.name} presents **{br.topic}** for {br.audience.lower()}.
Tone: {br.tone}. Length: {br.length.lower()}. Language: {br.language}.

What you’ll get:
{bullets_md}

Next step: **{cta_line}**
"""

# ──────────────────────────────────────────────────────────────────────────────
# Sidebar: Dataset preview + App status
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("📁 Dataset preview")
    st.caption("Preview the sample dataset used in Phase 2.")

    preview_rows = st.number_input(
        "Preview rows", min_value=1, max_value=50, value=5, step=1, key="sb_preview_rows"
    )

    if st.button("Start over (reset sample data)", key="btn_reset_sample"):
        if SAMPLE_CSV.exists():
            SAMPLE_CSV.unlink()
        ensure_sample_dataset()
        st.rerun()

    st.caption(f"Dataset: `{SAMPLE_CSV.name}`")
    try:
        df_preview = load_csv(SAMPLE_CSV, nrows=int(preview_rows))
        st.dataframe(df_preview, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load dataset preview: {e!s}")

    divider()
    st.subheader("⚙️ App Status")
    if OPENAI_OK:
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Not configured (offline templates)")
    st.caption("Add `OPENAI_API_KEY` in Streamlit Cloud → App → Secrets to enable online LLM.")
st.divider()

# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.title("💡 Presence — PR & Marketing AI (v2 Prototype)")
st.caption("Strategy ideas, multi-variant content drafts, brand rules, language, and history with filters/tagging.")
divider()

# ──────────────────────────────────────────────────────────────────────────────
# 1) Company Profile
# ──────────────────────────────────────────────────────────────────────────────
st.header("1️⃣  Company Profile")
col1, col2, col3 = st.columns([2, 1.4, 1.2])

with col1:
    company_name = st.text_input("Company Name", value="Acme Innovations", key="cp_name")
with col2:
    industry     = st.text_input("Industry / Sector", value="Robotics, Fintech, Retail…", key="cp_industry")
with col3:
    size         = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"], index=1, key="cp_size")

goals = st.text_area(
    "Business Goals (one or two sentences)",
    value="Increase qualified demand, accelerate sales cycles, reinforce brand trust…",
    height=90,
    key="cp_goals",
)

company = Company(
    name=company_name or "Acme Innovations",
    industry=industry or "Technology",
    size=size,
    goals=goals,
)

divider()

# ──────────────────────────────────────────────────────────────────────────────
# 2) Quick Strategy Idea
# ──────────────────────────────────────────────────────────────────────────────
st.header("2️⃣  Quick Strategy Idea")
if st.button("Generate Strategy Idea", key="btn_idea"):
    prompt = f"""
Propose a practical PR/Marketing initiative for {company.name} ({company.industry}, size: {company.size}).
Goals: {company.goals or "(not specified)"}.
Output a brief, 4–6 bullet plan with headline, rationale, primary channel, and success metrics.
""".strip()
    try:
        idea = llm_copy(prompt, temperature=0.5, max_tokens=350) if OPENAI_OK else (
            f"""**Campaign Idea: “Momentum Now”**
- **Rationale:** Convert in-market demand with fast, helpful education.
- **Primary channel:** Organic social + email drips; PR angle for thought-leadership.
- **Tactics:** Rapid Q&A posts, 2 customer mini-stories, founder AMAs, and one simple ROI calculator.
- **Measurement:** CTR to calculator, demo requests, and 30-day retention of new leads.
- **Notes:** Align tone to {company.size.lower()} buyers in {company.industry.lower()}."""
        )
        st.success("Strategy idea created.")
        st.markdown(idea)
        add_history("strategy", asdict(company), idea)
    except Exception as e:
        st.error(str(e))

divider()

# ──────────────────────────────────────────────────────────────────────────────
# 3) Content Engine — AI Copy (A/B/C)
# ──────────────────────────────────────────────────────────────────────────────
st.header("3️⃣  Content Engine — AI Copy (A/B/C)")

left, right = st.columns([1, 1])

with left:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad", "Social Post", "Landing Page", "Email"],
        key="ce_type",
    )
    platform = st.selectbox(
        "Platform (for Social/Ad)",
        ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"],
        key="ce_platform",
    )
    topic = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0", key="ce_topic")
    bullets_raw = st.text_area(
        "Key Points (bullets, one per line)",
        value="2× faster setup\nSOC 2 Type II\nSave 30% cost",
        height=120,
        key="ce_bullets",
    )

with right:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"], key="ce_tone")
    length = st.selectbox("Length", ["Short", "Medium", "Long"], key="ce_length")
    audience = st.text_input("Audience (who is this for?)", value="Decision-makers", key="ce_audience")
    cta = st.text_input("Call to Action", value="Book a demo", key="ce_cta")

st.subheader("Brand rules (optional)")
brand_rules = st.text_area(
    "Paste brand do’s/don’ts or banned words (optional)",
    value="Avoid superlatives like 'best-ever'. Use 'customers' not 'clients'.",
    height=110,
    key="ce_brand_rules",
)

col_lang, col_var = st.columns([2, 1])
with col_lang:
    language = st.selectbox(
        "Language",
        ["English", "Spanish", "French", "German", "Hindi", "Japanese"],
        index=0,
        key="ce_language",
    )
with col_var:
    variants = st.number_input("Variants (A/B/C)", min_value=1, max_value=3, value=1, step=1, key="ce_variants")

brief = ContentBrief(
    content_type=content_type,
    tone=tone,
    length=length,
    platform=platform,
    audience=audience or "Decision-makers",
    cta=cta,
    topic=topic,
    bullets=bulletize(bullets_raw),
    language=language,
    variants=int(variants),
    brand_rules=brand_rules or "",
)

issues = []
if not brief.topic.strip():
    issues.append("Add a topic/product name.")
if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

if st.button("Generate Variants (A/B/C)", key="btn_generate_variants", use_container_width=True):
    if not brief.topic.strip():
        st.warning("Please enter a topic / offer first.")
    else:
        try:
            prompt = make_prompt(brief, company)
            outputs: List[str] = []

            if OPENAI_OK:
                raw = llm_copy(prompt, temperature=0.65, max_tokens=1200)
                # Expecting multiple variants separated by blank lines; if your model returns a delimiter, you can split on that.
                # Simple fallback: split by two newlines; if fewer chunks than requested, duplicate last.
                chunks = [seg.strip() for seg in raw.split("\n\n--\n\n") if seg.strip()]
                if not chunks:
                    chunks = [seg.strip() for seg in raw.split("\n\n") if seg.strip()]
                while len(chunks) < brief.variants:
                    chunks.append(chunks[-1])
                outputs = chunks[:brief.variants]
            else:
                # Offline fallback: one generic template (duplicate if variants > 1)
                base = (
                    offline_press_release(brief, company)
                    if brief.content_type == "Press Release"
                    else offline_generic_copy(brief, company)
                )
                outputs = [base for _ in range(brief.variants)]

            add_history("Variants", {"company": asdict(company), "brief": asdict(brief)}, outputs)
            st.success("Draft(s) created!")

            for idx, draft in enumerate(outputs, start=1):
                st.markdown(f"#### Variant {idx}")
                st.markdown(draft)
                fname = f"variant_{idx}_{brief.content_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    label=f"Download Variant {idx} (.txt)",
                    data=draft.encode("utf-8"),
                    file_name=fname,
                    mime="text/plain",
                    key=f"btn_dl_{idx}"
                )
                st.divider()

        except Exception as e:
            st.error(f"Error while generating: {e}")

divider()

# ──────────────────────────────────────────────────────────────────────────────
# 4) History — filters, search, tagging, export/import (Phase 2 Step 6.5)
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("🕘 History (last 20)"):
    hist: list[dict] = st.session_state.get("history", [])
    if not hist:
        st.caption("No items yet.")
    else:
        kinds = sorted({h.get("kind", "content") for h in hist})
        all_tags = sorted({t for h in hist for t in h.get("tags", [])})

        c1, c2, c3 = st.columns([1.2, 1.5, 1.2])
        with c1:
            kind_filter = st.multiselect("Filter by type", options=kinds, default=kinds, key="hist_kind_filter")
        with c2:
            tag_filter = st.multiselect("Filter by tag(s)", options=all_tags, default=[], key="hist_tag_filter")
        with c3:
            text_query = st.text_input("Search text", value="", key="hist_search")

        def match_item(h: dict) -> bool:
            if h.get("kind") not in kind_filter:
                return False
            tags = set(h.get("tags", []))
            if tag_filter and not set(tag_filter).issubset(tags):
                return False
            if text_query.strip():
                q = text_query.strip().lower()
                out = h.get("output")
                out_str = "\n\n".join(out) if isinstance(out, list) else (out or "")
                inp_str = json.dumps(h.get("input", {}), ensure_ascii=False)
                if q not in out_str.lower() and q not in inp_str.lower():
                    return False
            return True

        filtered = [h for h in hist if match_item(h)]

        e1, e2 = st.columns([1, 1])
        with e1:
            st.download_button(
                "Export history (.json)",
                data=json.dumps(hist, ensure_ascii=False, indent=2).encode("utf-8"),
                file_name=f"presence_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="btn_export_history",
            )
        with e2:
            uploaded = st.file_uploader("Import history (.json)", type=["json"], key="uploader_hist")
            if uploaded is not None:
                try:
                    imported = json.loads(uploaded.read().decode("utf-8"))
                    if isinstance(imported, list):
                        for it in imported:
                            if "id" not in it:
                                it["id"] = st.session_state["next_id"]
                                st.session_state["next_id"] += 1
                            if "tags" not in it:
                                it["tags"] = []
                        st.session_state["history"] = imported[:20]
                        st.success("History imported.")
                        st.rerun()
                    else:
                        st.error("JSON must be a list of history items.")
                except Exception as e:
                    st.error(f"Import failed: {e}")

        st.caption(f"Showing {len(filtered)} of {len(hist)} item(s).")
        st.divider()

        for i, item in enumerate(filtered, start=1):
            hid = item.get("id", i)
            st.markdown(f"**{i}. {item.get('kind','content')}** · {item.get('ts','')}")
            with st.expander("Open"):
                st.code(json.dumps(item.get("input", {}), ensure_ascii=False, indent=2))
                out = item.get("output")
                if isinstance(out, list):
                    for idx, v in enumerate(out, start=1):
                        st.markdown(f"**Variant {idx}**")
                        st.markdown(v)
                        st.divider()
                else:
                    st.markdown(out or "")

                t1, t2, t3, t4 = st.columns([1, 1, 1, 2])
                with t1:
                    if st.button("👍 Good", key=f"tag_good_{hid}"):
                        tags = set(item.get("tags", [])); tags.add("good")
                        item["tags"] = sorted(tags)
                        st.success("Tagged: good"); st.rerun()
                with t2:
                    if st.button("📝 Needs review", key=f"tag_review_{hid}"):
                        tags = set(item.get("tags", [])); tags.add("needs review")
                        item["tags"] = sorted(tags)
                        st.info("Tagged: needs review"); st.rerun()
                with t3:
                    if st.button("✅ Approved", key=f"tag_ok_{hid}"):
                        tags = set(item.get("tags", [])); tags.add("approved")
                        item["tags"] = sorted(tags)
                        st.success("Tagged: approved"); st.rerun()
                with t4:
                    cur = ", ".join(item.get("tags", []))
                    new_tags_str = st.text_input("Edit tags (comma-separated)", value=cur, key=f"edit_tags_{hid}")
                    if st.button("Save tags", key=f"save_tags_{hid}"):
                        cleaned = [t.strip() for t in new_tags_str.split(",") if t.strip()]
                        item["tags"] = sorted(set(cleaned))
                        st.success("Tags saved"); st.rerun()

            divider() 
            
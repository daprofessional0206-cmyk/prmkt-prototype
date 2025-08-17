# app.py — Presence (Phase 2 up to Step 6.2)

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Streamlit MUST be imported before any code that uses `st`
# ──────────────────────────────────────────────────────────────────────────────
import streamlit as st

# Standard libs
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional
from pathlib import Path

# Data
import pandas as pd

# ──────────────────────────────────────────────────────────────────────────────
# App wide config
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Presence — PR & Marketing AI Prototype",
    page_icon="📣",
    layout="wide",
)

# Small CSS polish
st.markdown(
    """
    <style>
      .block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; }
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
    """Thin horizontal divider to separate sections."""
    st.markdown(
        "<hr style='border: 1px solid #202431; margin: 1.1rem 0;'/>",
        unsafe_allow_html=True,
    )

def bulletize(text: str) -> List[str]:
    """Split multi-line textarea into cleaned bullets (max 15)."""
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
    """Create/overwrite small sample CSV so preview always works."""
    DATA_DIR.mkdir(exist_ok=True)
    if not SAMPLE_CSV.exists():
        SAMPLE_CSV.write_text(
            "date,channel,post_type,headline,copy,clicks,impressions,engagement_rate\n"
            "2025-08-01,LinkedIn,post,Acme RoboHub 2.0 Launch,Fast setup & SOC2 Type II,124,6500,3.1\n"
            "2025-08-03,Email,newsletter,Why customers switch to Acme,Save 30% with faster onboarding,410,17800,2.2\n"
            "2025-08-05,Instagram,reel,Behind-the-scenes of RoboHub,Meet the team that builds speed,980,45900,1.6\n"
        )

# Ensure preview dataset exists
ensure_sample_dataset()

# ──────────────────────────────────────────────────────────────────────────────
# Optional OpenAI client (auto-detect)
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

# Session history
if "history" not in st.session_state:
    st.session_state["history"] = []  # type: ignore

def add_history(kind: str, payload: dict, output: str):
    st.session_state.history.insert(
        0,
        {"ts": now_iso(), "kind": kind, "input": payload, "output": output},
    )
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
# Sidebar: Dataset preview + App status (Phase 2 / Steps 3–4)
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.subheader("📁 Dataset preview")
    st.caption("Preview the dataset to understand its structure and contents.")

    preview_rows = st.number_input(
        "Preview rows", min_value=1, max_value=50, value=5, step=1, key="sb_preview_rows"
    )

    if st.button("Reset sample data", key="btn_reset_sample"):
        # Overwrite sample and rerun safely (no experimental API)
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

# ──────────────────────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────────────────────
st.title("💡 PR & Marketing AI Platform — v1 Prototype")
st.caption("A focused prototype for strategy ideas and content drafts (press releases, ads, posts, emails, etc.)")
divider()

# ──────────────────────────────────────────────────────────────────────────────
# 1) Company Profile
# ──────────────────────────────────────────────────────────────────────────────
st.header("1️⃣  Company Profile")
col1, col2, col3 = st.columns([2, 1.4, 1.2])

with col1:
    company_name = st.text_input("Company Name", value="Acme Innovations", key="cp_name")
with col2:
    industry = st.text_input("Industry / Sector", value="Robotics, Fintech, Retail…", key="cp_industry")
with col3:
    size = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"], index=1, key="cp_size")

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

# Phase 2 additions
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

# Hints
issues = []
if not brief.topic.strip():
    issues.append("Add a topic/product name.")
if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

# Generate button (UNIQUE KEY)
if st.button("Generate A/B/C Variants", key="btn_generate_variants", use_container_width=True):
    if not brief.topic.strip():
        st.warning("Please enter a topic / offer first.")
    else:
        try:
            # Build LLM prompt once
            prompt = make_prompt(brief, company)
            outputs: List[str] = []

            if OPENAI_OK:
                # Ask model to return variants separated clearly
                # (We keep it simple and split on '\n\n---\n\n' if present,
                #  else present the single block as Variant A.)
                raw = llm_copy(prompt, temperature=0.65, max_tokens=1200)
                chunks = [seg.strip() for seg in raw.split("\n---\n") if seg.strip()]
                if len(chunks) < brief.variants:
                    # If the model didn’t clearly separate, duplicate splits safely
                    while len(chunks) < brief.variants:
                        chunks.append(raw.strip())
                outputs = chunks[: brief.variants]
            else:
                # Offline templates
                template = (
                    offline_press_release(brief, company)
                    if brief.content_type == "Press Release"
                    else offline_generic_copy(brief, company)
                )
                # Make up to N “variants” by slightly labeling them
                labels = ["Variant A", "Variant B", "Variant C"]
                outputs = [f"### {labels[i]}\n\n{template}" for i in range(brief.variants)]

            st.success("Draft(s) created!")
            for idx, draft in enumerate(outputs, start=1):
                st.markdown(f"#### Variant {idx}")
                st.markdown(draft)

                # unique download key per variant
                fname = f"variant_{idx}_{brief.content_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                st.download_button(
                    label=f"Download Variant {idx} (.txt)",
                    data=draft.encode("utf-8"),
                    file_name=fname,
                    mime="text/plain",
                    key=f"btn_dl_v{idx}",
                )
                divider()

            # Save to session history
            add_history(
                "content",
                {"company": asdict(company), "brief": asdict(brief)},
                "\n\n---\n\n".join(outputs),
            )

        except Exception as e:
            st.error(str(e))

divider()

# ──────────────────────────────────────────────────────────────────────────────
# 4) History
# ──────────────────────────────────────────────────────────────────────────────
with st.expander("🕘 History (last 20)"):
    if not st.session_state.history:
        st.caption("No items yet.")
    else:
        for i, item in enumerate(st.session_state.history, start=1):
            st.markdown(f"**{i}. {item['kind']}** · {item['ts']}")
            with st.expander("View"):
                st.code(json.dumps(item["input"], indent=2))
                st.markdown(item["output"])
            divider()

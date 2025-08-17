# app.py
from __future__ import annotations

# IMPORTANT: Streamlit must be imported BEFORE any line that uses `st`
import streamlit as st

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional

# Phase 2: dataset utils
from pathlib import Path
import pandas as pd
# --- simple helpers (place these right after imports) ---
def divider():
    """Thin horizontal divider to separate sections."""
    st.markdown(
        "<hr style='border: 1px solid #202431; margin: 1.1rem 0;'/>",
        unsafe_allow_html=True,
    )

def now_iso() -> str:
    """UTC timestamp for history items / filenames."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def bulletize(text: str) -> list[str]:
    """Split textarea lines into bullets (trim, drop empties, cap list)."""
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]


# ============ Phase 2: Dataset utils ============
DATA_DIR = Path(__file__).parent / "data"
SAMPLE_CSV = DATA_DIR / "sample_dataset.csv"

@st.cache_data(show_spinner=False)
def load_csv(path: Path, nrows: int | None = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if nrows:
        df = df.head(nrows)
    return df

def ensure_sample_dataset() -> None:
    """Create a tiny sample CSV if it doesn't exist, so preview always works."""
    DATA_DIR.mkdir(exist_ok=True)
    if not SAMPLE_CSV.exists():
        SAMPLE_CSV.write_text(
            "date,channel,post_type,headline,copy,clicks,impressions,engagement_rate\n"
            "2025-08-01,LinkedIn,post,Acme RoboHub 2.0 Launch,Fast setup & SOC2 Type II,124,6500,0.023\n"
            "2025-08-03,Email,newsletter,Why customers switch to Acme,Save 30% with faster onboarding,201,11890,0.017\n"
            "2025-08-05,Instagram,reel,Behind-the-scenes of RoboHub,Meet the team that builds speed,342,24010,0.028\n"
        )

# ============ Optional OpenAI ============
OPENAI_OK = False
MODEL = "gpt-4o-mini"
client = None
if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        OPENAI_OK = True
    except Exception:
        OPENAI_OK = False

SYSTEM_PROMPT = """You are an expert PR & Marketing copywriter.
Write clear, compelling, brand-safe copy. Keep facts generic unless provided.
Return only the copy, no preface.
"""

def llm_copy(prompt: str, temperature: float = 0.6, max_tokens: int = 600) -> str:
    if not OPENAI_OK or client is None:
        raise RuntimeError("OpenAI is not configured.")
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()

# ============ Data models ============
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

# ============ Session state ============
if "history" not in st.session_state:
    st.session_state["history"] = []

# ============ Guardrails ============
import time

def require_secrets_if_online(online_flag: bool):
    if online_flag:
        if "OPENAI_API_KEY" not in st.secrets or not st.secrets["OPENAI_API_KEY"]:
            st.error("🔐 Missing OpenAI API key. Add it in Streamlit Cloud → App settings → Secrets.")
            st.stop()

def require_inputs(company: str, topic: str, bullets: list[str]):
    problems = []
    if not company.strip():
        problems.append("Company name is required.")
    if not topic.strip():
        problems.append("Topic / Product / Offer is required.")
    if len(bullets) == 0:
        problems.append("Add at least one key point (1 per line).")
    if any(len(b) > 220 for b in bullets):
        problems.append("Each bullet should be ≤ 220 characters.")
    if problems:
        st.warning("Please fix these:\n\n- " + "\n- ".join(problems))
        st.stop()

def throttle(seconds: int = 8):
    now = time.time()
    last = st.session_state.get("last_gen", 0)
    if now - last < seconds:
        wait = int(seconds - (now - last))
        st.info(f"⏳ Please wait {wait}s before generating again.")
        st.stop()
    st.session_state["last_gen"] = now

# ============ Generators ============
def offline_press_release(br: ContentBrief, co: Company) -> str:
    bullets_md = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "- (add key benefits)"
    cta_line = br.cta or "Contact us to learn more."
    return f"""FOR IMMEDIATE RELEASE

{co.name} Unveils {br.topic}: {br.tone} Impact for {co.industry}

[City, Date] – {co.name} announces {br.topic}, advancing {co.industry.lower()} leaders with {br.length.lower()}-format benefits.
This launch supports our goal to: {co.goals or "deliver measurable value and growth."}

Key points:
{bullets_md}

Why it matters for {br.audience.lower()}:
- Reduces friction and speeds outcomes
- Improves confidence with clear, compliant communication
- Scales across {br.platform.lower()} channels

{cta_line}
"""

def offline_generic_copy(br: ContentBrief, co: Company) -> str:
    bullets_md = "\n".join([f"• {b}" for b in br.bullets]) if br.bullets else "• Add 2–3 benefits customers care about."
    cta_line = br.cta or "Get started today."
    opening = {
        "Ad": "Attention, innovators!",
        "Social Post": "Quick update:",
        "Landing Page": "Welcome—here’s how we help:",
        "Email": "Hi there,",
    }.get(br.content_type, "Here’s something useful:")
    return f"""{opening}

{co.name} presents **{br.topic}** for {br.audience.lower()}.
Tone: {br.tone}. Length: {br.length.lower()}.

What you’ll get:
{bullets_md}

Next step: **{cta_line}**
"""

def make_prompt(br: ContentBrief, co: Company) -> str:
    bullets = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "(no bullets provided)"
    return f"""
Write a {br.length.lower()} {br.content_type.lower()} for platform "{br.platform}".
Audience: {br.audience}. Tone: {br.tone}.
Company: {co.name} ({co.industry}, size: {co.size}).
Topic / Offer: {br.topic}

Key points:
{bullets}

Call to action: {br.cta}

Constraints:
- Be brand-safe and factual from given info only.
- Strong opening, clear structure, and a crisp CTA.
"""

def add_history(kind: str, payload: dict, output: str):
    st.session_state.history.insert(0, {"ts": now_iso(), "kind": kind, "input": payload, "output": output})
    st.session_state.history = st.session_state.history[:15]

# ============ Sidebar ============

with st.sidebar:
    # Dataset preview (Phase 2 – Step 4)
    st.subheader("▦ Dataset preview")
    ensure_sample_dataset()

    cols = st.columns([1, 1])
    with cols[0]:
        nrows = st.number_input("Preview rows", min_value=1, max_value=50, value=5, step=1, key="sb_preview_rows")
    with cols[1]:
        if st.button("Reset sample data"):
            # nuke cache + recreate file
            if SAMPLE_CSV.exists():
                SAMPLE_CSV.unlink()
            st.cache_data.clear()
            ensure_sample_dataset()
            st.success("Sample dataset recreated.")

    try:
        df_preview = load_csv(SAMPLE_CSV, nrows=nrows)
        st.caption(f"Dataset: `{SAMPLE_CSV.name}`")
        st.dataframe(df_preview, use_container_width=True, height=220)
    except Exception as e:
        st.warning(f"Could not load dataset preview: {e}")

    divider()
    st.subheader("⚙️ App Status")
    if OPENAI_OK:
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Not configured (offline templates)")

# ============ Header ============
st.title("💡 PR & Marketing AI Platform — v1 Prototype")
st.caption("A focused prototype for strategy ideas and content drafts (press releases, ads, posts, emails, etc.)")

divider()

# ============ Section 1 — Company Profile ============
st.header("1️⃣  Company Profile")

col1, col2, col3 = st.columns([2, 1.4, 1.2])
with col1:
    company_name = st.text_input("Company Name", key="cp_name", placeholder="Acme Innovations")
with col2:
    industry = st.text_input("Industry / Sector", key="cp_industry", placeholder="Robotics, Fintech, Retail…")
with col3:
    size = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"], index=1, key="cp_size")

goals = st.text_area(
    "Business Goals (one or two sentences)",
    key="cp_goals",
    placeholder="Increase qualified demand, accelerate sales cycles, reinforce brand trust…",
    height=80,
)

company = Company(
    name=company_name or "Acme Innovations",
    industry=industry or "Technology",
    size=size,
    goals=goals,
)

divider()

# ============ Section 2 — Strategy Idea ============
st.header("2️⃣  Quick Strategy Idea")
if st.button("Generate Strategy Idea", key="btn_idea"):
    base_prompt = f"""
Propose a practical PR/Marketing initiative for {company.name} ({company.industry}, size: {company.size}).
Goals: {company.goals or "(not specified)"}.
Output a brief, 4–6 bullet plan with headline, rationale, primary channel, and success metrics.
""".strip()
    try:
        idea = llm_copy(base_prompt, temperature=0.5, max_tokens=350) if OPENAI_OK else (
            f"""**Campaign Idea: “Momentum Now”**
- **Rationale:** Convert in-market demand with fast, helpful education.
- **Primary channel:** Organic social + email drips; PR angle for thought-leadership.
- **Tactics:** Rapid Q&A posts, 2 customer mini-stories, founder AMAs, and one simple ROI calculator.
- **Measurement:** CTR to calculator, demo requests, and 30-day retention of new leads.
- **Notes:** Align copy tone to {company.size.lower()} buyers in {company.industry.lower()}."""
        )
        st.success("Strategy idea created.")
        st.markdown(idea)
        add_history("strategy", asdict(company), idea)
    except Exception as e:
        st.error(str(e))

divider()

# ============ Section 3 — Content Engine ============
st.header("3️⃣  Content Engine — AI Copy Generator")

left, right = st.columns([1, 1])
with left:
    content_type = st.selectbox("Content Type", ["Press Release", "Ad", "Social Post", "Landing Page", "Email"], key="ce_type")
    platform = st.selectbox("Platform (for Social/Ad)", ["Generic", "LinkedIn", "Instagram", "X/Twitter", "YouTube", "Search Ad"], key="ce_platform")
    topic = st.text_input("Topic / Product / Offer", key="ce_topic", placeholder="Launch of Acme RoboHub 2.0")
    bullets_raw = st.text_area("Key Points (bullets, one per line)", key="ce_bullets",
                               placeholder="2× faster setup\nSOC 2 Type II\nSave 30% cost", height=110)
with right:
    tone = st.selectbox("Tone", ["Neutral", "Professional", "Friendly", "Bold", "Conversational"], key="ce_tone")
    length = st.selectbox("Length", ["Short", "Medium", "Long"], key="ce_length")
    audience = st.text_input("Audience (who is this for?)", key="ce_audience", placeholder="Decision-makers")
    cta = st.text_input("Call to Action", key="ce_cta", placeholder="Book a demo")

brief = ContentBrief(
    content_type=content_type,
    tone=tone,
    length=length,
    platform=platform,
    audience=audience or "Decision-makers",
    cta=cta,
    topic=topic,
    bullets=bulletize(bullets_raw),
)

issues = []
if not brief.topic.strip():
    issues.append("Add a topic/product name.")

if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

if st.button("Generate Content", key="btn_generate", use_container_width=True):
    # Guardrails
    throttle(8)
    require_inputs(company.name, brief.topic, brief.bullets)
    require_secrets_if_online(OPENAI_OK)
    try:
        if OPENAI_OK:
            prompt = make_prompt(brief, company)
            draft = llm_copy(prompt, temperature=0.65, max_tokens=900)
        else:
            draft = offline_press_release(brief, company) if brief.content_type == "Press Release" else offline_generic_copy(brief, company)

        st.success("Draft created!")
        st.markdown(draft)

        add_history("content", {"company": asdict(company), "brief": asdict(brief)}, draft)

        fname = f"{brief.content_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        st.download_button("Download .txt", data=draft.encode("utf-8"), file_name=fname, mime="text/plain")

        if not issues:
            st.info("Looks good for a first draft. Tweak tone/CTA and regenerate if needed.")
    except Exception as e:
        st.error(str(e))

divider()

with st.expander("🕘 History (last 15)"):
    if not st.session_state.history:
        st.caption("No items yet.")
    else:
        for i, item in enumerate(st.session_state.history, start=1):
            st.markdown(f"**{i}. {item['kind']}** · {item['ts']}")
            with st.expander("View"):
                st.code(json.dumps(item["input"], indent=2))
                st.markdown(item["output"])
            divider()


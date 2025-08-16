# app.py
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional

import streamlit as st # --- App Config (branding & theme) ---
st.set_page_config(
    page_title="PR & Marketing Prototype",
    page_icon="📢",
    layout="centered"
)

st.title("📢 PR & Marketing AI Prototype")
st.caption("Phase 1 Demo – Generate PR copy, marketing content, and track history")


# --------- Optional OpenAI (auto-detect via st.secrets) ----------
OPENAI_OK = False
MODEL = "gpt-4o-mini"  # fast & inexpensive; change if you prefer
client = None
if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        OPENAI_OK = True
    except Exception:
        OPENAI_OK = False


# ============ Page & simple CSS polish ============
st.set_page_config(
    page_title="PR & Marketing AI Prototype",
    page_icon="💡",
    layout="wide",
)

# Small layout pad tweak
st.markdown(
    """
<style>
    .block-container { padding-top: 1.2rem; padding-bottom: 3rem; }
    .stTextArea textarea { font-size: 0.95rem; line-height: 1.45; }
    .stDownloadButton button { width: 100%; }
</style>
""",
    unsafe_allow_html=True,
)


# ============ Utilities ============

def divider():
    st.markdown("<hr style='border: 1px solid #202431; margin: 1.1rem 0;'/>", unsafe_allow_html=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bulletize(text: str) -> List[str]:
    """Split textarea lines into bullets (drop empties, trim, max 15)."""
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]


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


# in-memory session history
if "history" not in st.session_state:
    st.session_state["history"] = []  # type: ignore  # optional




def add_history(kind: str, payload: dict, output: str):
    st.session_state.history.insert(
        0,
        {
            "ts": now_iso(),
            "kind": kind,
            "input": payload,
            "output": output,
        },
    )
    # keep it light
    st.session_state.history = st.session_state.history[:15]


# ============ Generators ============

SYSTEM_PROMPT = """You are an expert PR & Marketing copywriter. 
Write clear, compelling, brand-safe copy. Keep facts generic unless provided. 
Match the requested tone, audience, and length. Include a strong call to action when asked.
Return only the copy, no preface or commentary.
"""


def llm_copy(prompt: str, temperature: float = 0.6, max_tokens: int = 600) -> str:
    """Generate with OpenAI if available, else raise."""
    if not OPENAI_OK or client is None:
        raise RuntimeError("OpenAI is not configured.")

    try:
        # Chat Completions (OpenAI 1.x)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        raise RuntimeError(f"OpenAI error: {e}")


def offline_press_release(br: ContentBrief, co: Company) -> str:
    """Template press release when offline."""
    bullets_md = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "- (add key benefits)"
    cta_line = br.cta if br.cta else "Contact us to learn more."

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
    """Generic offline copy for non-press types."""
    bullets_md = "\n".join([f"• {b}" for b in br.bullets]) if br.bullets else "• Add 2–3 benefits customers care about."
    cta_line = br.cta if br.cta else "Get started today."

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


# ============ Sidebar Status ============

with st.sidebar:
    st.subheader("🔧 App Status")
    if OPENAI_OK:
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Not configured (offline templates)")

    st.caption("Tip: Add an API key in `.streamlit/secrets.toml` to enable higher-quality AI outputs.")
    divider()
    st.markdown("**Version**: v1.0 (Phase 1)")
    st.caption("Light theme polish, stable widget keys, offline/online modes, and downloads.")


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
    industry = st.text_input("Industry / Sector", key="cp_industry", placeholder="Robotics, Fintech, Retail...")
with col3:
    size = st.selectbox("Company Size", ["Small", "Mid-market", "Enterprise"], index=1, key="cp_size")

goals = st.text_area(
    "Business Goals (one or two sentences)",
    key="cp_goals",
    placeholder="Increase qualified demand, accelerate sales cycles, reinforce brand trust…",
    height=90,
)

company = Company(
    name=company_name or "Acme Innovations",
    industry=industry or "Technology",
    size=size,
    goals=goals,
)

divider()

# ============ Section 2 — Strategy Idea (Optional) ============

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
    topic = st.text_input("Topic / Product / Offer", key="ce_topic", placeholder="Launch of Acme RoboHub 2.0")
    bullets_raw = st.text_area(
        "Key Points (bullets, one per line)",
        key="ce_bullets",
        placeholder="2× faster setup\nSOC 2 Type II\nSave 30% cost",
        height=120,
    )

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

# Lightweight QA nudges (no blocking)
issues = []
if not brief.topic.strip():
    issues.append("Add a topic/product name.")
if brief.content_type == "Press Release" and "press" not in brief.content_type.lower():
    pass  # kept for parity/future rules
if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

if st.button("Generate Content", key="btn_generate", use_container_width=True):
    if not brief.topic.strip():
        st.warning("Please enter a topic / offer first.")
    else:
        try:
            if OPENAI_OK:
                prompt = make_prompt(brief, company)
                draft = llm_copy(prompt, temperature=0.65, max_tokens=900)
            else:
                draft = (
                    offline_press_release(brief, company)
                    if brief.content_type == "Press Release"
                    else offline_generic_copy(brief, company)
                )

            st.success("Draft created!")
            st.markdown(draft)

            # Save to session history
            add_history(
                "content",
                {"company": asdict(company), "brief": asdict(brief)},
                draft,
            )

            # Download button
            fname = f"{brief.content_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            st.download_button(
                "Download .txt",
                data=draft.encode("utf-8"),
                file_name=fname,
                mime="text/plain",
            )

            # Small “looks good” nudges
            if not issues:
                st.info("Looks good for a first draft. Tweak tone/CTA and regenerate if needed.")
        except Exception as e:
            st.error(str(e))

divider()

# ============ History ============

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

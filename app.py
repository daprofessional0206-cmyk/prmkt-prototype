# app.py
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import streamlit as st
import pandas as pd

# ---------------- App Config ----------------
st.set_page_config(
    page_title="Presence — PR & Marketing Prototype",
    page_icon="📢",
    layout="wide",
)

# ---------------- Small CSS polish ----------------
st.markdown(
    """
<style>
    .block-container { padding-top: 1.0rem; padding-bottom: 2.5rem; }
    .stTextArea textarea { font-size: 0.95rem; line-height: 1.45; }
    .stDownloadButton button { width: 100%; }
    .brand-ok { color: #16a34a; font-weight: 600; }
    .brand-warn { color: #b45309; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- Data constants (Phase 2) ----------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_CSV = DATA_DIR / "sample_dataset.csv"


def ensure_sample_dataset() -> None:
    """Create a small demo CSV if missing."""
    if SAMPLE_CSV.exists():
        return
    rows = [
        {"date": "2025-08-01", "channel": "LinkedIn", "post_type": "post",
         "headline": "Acme RoboHub 2.0 Launch", "copy": "Fast setup • SOC 2 Type II • Save 30%"},
        {"date": "2025-08-03", "channel": "Email", "post_type": "newsletter",
         "headline": "Why customers switch to Acme", "copy": "Cut onboarding time in half"},
        {"date": "2025-08-05", "channel": "Instagram", "post_type": "reel",
         "headline": "Behind-the-scenes", "copy": "Meet the team building speed"},
        {"date": "2025-08-08", "channel": "X/Twitter", "post_type": "thread",
         "headline": "RoboHub 2.0 tips", "copy": "3 ways to launch in hours"},
    ]
    pd.DataFrame(rows).to_csv(SAMPLE_CSV, index=False)


@st.cache_data(show_spinner=False)
def load_csv(path: Path, nrows: Optional[int] = None) -> pd.DataFrame:
    df = pd.read_csv(path)
    if nrows:
        return df.head(int(nrows))
    return df


# ---------- OpenAI (auto-detect via st.secrets) ----------
OPENAI_OK = False
MODEL = "gpt-4o-mini"  # fast & affordable
client = None
if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
    try:
        from openai import OpenAI

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        OPENAI_OK = True
    except Exception:
        OPENAI_OK = False


# ---------------- Helpers & guardrails ----------------
def divider():
    st.markdown("<hr style='border: 1px solid #202431; margin: 0.9rem 0;'/>", unsafe_allow_html=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def bulletize(text: str) -> List[str]:
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]


def throttle(seconds: int = 8):
    """Prevent accidental double runs."""
    now = time.time()
    last = st.session_state.get("last_gen", 0)
    if now - last < seconds:
        wait = int(seconds - (now - last))
        st.info(f"⏳ Please wait {wait}s before generating again.")
        st.stop()
    st.session_state["last_gen"] = now


def require_inputs(company: str, topic: str, bullets: List[str]):
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


# ---------------- Data classes ----------------
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
    language: str


# ---------------- Session: history ----------------
if "history" not in st.session_state:
    st.session_state["history"] = []  # type: ignore


def add_history(kind: str, payload: dict, output: dict):
    st.session_state.history.insert(
        0, {"ts": now_iso(), "kind": kind, "input": payload, "output": output}
    )
    st.session_state.history = st.session_state.history[:20]


# ---------------- LLM prompts ----------------
SYSTEM_PROMPT = """You are Presence, an expert PR & Marketing copywriter.
- Write clear, compelling, brand-safe copy.
- Use only facts provided; do not invent specifics.
- Match requested tone, audience, length, and language.
- Include a strong CTA when requested.
Return only the copy for each variant, with headings 'Variant A/B/C'.
"""

def make_prompt(br: ContentBrief, co: Company, variants: int = 3) -> str:
    bullets = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "(no bullets)"
    return f"""
Generate {variants} distinct variants (A,B,C) of a {br.length.lower()} {br.content_type.lower()} for platform "{br.platform}".
Language: {br.language}. Audience: {br.audience}. Tone: {br.tone}.
Company: {co.name} ({co.industry}, size: {co.size}).
Topic/Offer: {br.topic}
Key points:
{bullets}
Call to action: {br.cta or "(none specified)"}
Constraints:
- Strong opening, clear structure, crisp CTA.
- Brand-safe, no false claims, no placeholders like [COMPANY].
- Keep within reasonable length for the content type.
Output format:
## Variant A
...copy...
## Variant B
...copy...
## Variant C
...copy...
""".strip()


def llm_variants(prompt: str, temperature: float = 0.65, max_tokens: int = 1200) -> str:
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
    return resp.choices[0].message.content.strip()


def offline_variants(br: ContentBrief, co: Company) -> str:
    """Fallback when OpenAI not configured."""
    bullets_md = "\n".join([f"• {b}" for b in br.bullets]) or "• Add 2–3 customer benefits."
    def one(lead: str):
        return f"""{lead}

{co.name} — **{br.topic}** ({br.platform})
Audience: {br.audience} | Tone: {br.tone} | Length: {br.length}

Why it matters:
{bullets_md}

Next step: **{br.cta or "Get started today."}**
"""
    return "\n\n".join([
        "## Variant A\n" + one("Here’s a fast win:"),
        "## Variant B\n" + one("Quick update:"),
        "## Variant C\n" + one("Heads-up:"),
    ])


# ---------------- Ensure data exists BEFORE UI ----------------
ensure_sample_dataset()

# ---------------- Sidebar ----------------
with st.sidebar:
    st.subheader("📂 Dataset preview")
    preview_rows = st.number_input(
        "Preview rows", min_value=1, max_value=50, value=5, step=1, key="sb_preview_rows"
    )

    if st.button("Reset sample data", key="btn_reset_sample"):
        try:
            if SAMPLE_CSV.exists():
                SAMPLE_CSV.unlink()
            ensure_sample_dataset()
            try:
                st.cache_data.clear()
            except Exception:
                pass
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Reset failed: {e}")

    try:
        df_preview = load_csv(SAMPLE_CSV, nrows=preview_rows)
        st.caption(f"Dataset: `{SAMPLE_CSV.name}`")
        st.dataframe(df_preview, use_container_width=True, height=220)
    except Exception as e:
        st.warning(f"Could not load dataset preview: {e}")

    st.divider()
    st.subheader("⚙️ App Status")
    if OPENAI_OK:
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Not configured (offline mode)")

# ---------------- Header ----------------
st.title("📢 Presence — PR & Marketing AI Prototype")
st.caption("Phase 2+3: Dataset tools • Multi-variant generator • Guardrails • Brand checks • Language")

divider()

# ---------------- Section 1: Company Profile ----------------
st.header("1️⃣ Company Profile")
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
    height=90,
)

company = Company(
    name=company_name or "Acme Innovations",
    industry=industry or "Technology",
    size=size,
    goals=goals,
)

divider()

# ---------------- Section 2: Strategy Idea (quick) ----------------
st.header("2️⃣ Quick Strategy Idea")
if st.button("Generate Strategy Idea", key="btn_idea"):
    base_prompt = f"""
Propose a practical PR/Marketing initiative for {company.name} ({company.industry}, size: {company.size}).
Goals: {company.goals or "(not specified)"}.
Output a brief, 4–6 bullet plan with headline, rationale, primary channel, and success metrics.
""".strip()
    try:
        idea = llm_variants(base_prompt, temperature=0.5, max_tokens=350) if OPENAI_OK else (
            """**Campaign Idea: “Momentum Now”**
- **Rationale:** Convert in-market demand with fast, helpful education.
- **Primary channel:** Organic social + email; PR angle for thought-leadership.
- **Tactics:** Rapid Q&A posts, 2 customer mini-stories, founder AMAs, ROI calculator.
- **Measurement:** CTR to calculator, demo requests, retention of new leads.
- **Notes:** Align copy tone to segment & channel."""
        )
        st.success("Strategy idea created.")
        st.markdown(idea)
        add_history("strategy", asdict(company), {"idea": idea})
    except Exception as e:
        st.error(str(e))

divider()

# ---------------- Section 3: Content Engine (A/B/C variants) ----------------
st.header("3️⃣ Content Engine — AI Copy (A/B/C)")

left, right = st.columns([1, 1])
with left:
    content_type = st.selectbox(
        "Content Type", ["Press Release", "Ad", "Social Post", "Landing Page", "Email"], key="ce_type",
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
    language = st.selectbox("Language", ["English", "Hindi", "Gujarati"], index=0, key="ce_lang")

st.markdown("### Brand rules (optional)")
brand_rules = st.text_area(
    "Paste brand do's/don'ts or banned words (optional)",
    key="brand_rules",
    placeholder="Example: Do use confident tone. Don’t mention competitors. Avoid words: cheap, disrupt, revolutionary.",
    height=80,
)

# Build structured brief
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
)

# Light suggestions
issues = []
if not brief.topic.strip():
    issues.append("Add a topic/product name.")
if not brief.bullets:
    issues.append("Add at least one key point.")
if issues:
    with st.expander("Suggested fixes"):
        for i in issues:
            st.write("•", i)

# --- Generate button ---
if st.button("Generate A/B/C Variants", key="btn_generate", use_container_width=True):
    # Guardrails
    require_inputs(company.name, brief.topic, brief.bullets)
    throttle(7)

    try:
        # Prompt + brand rules injection
        base_prompt = make_prompt(brief, company, variants=3)
        if brand_rules.strip():
            base_prompt += f"\n\nExtra brand constraints:\n{brand_rules.strip()}\n"

        if OPENAI_OK:
            raw = llm_variants(base_prompt, temperature=0.65, max_tokens=1100)
        else:
            raw = offline_variants(brief, company)

        # Try to split into variants by headings
        parts = []
        current = []
        current_title = None
        for line in raw.splitlines():
            if line.strip().lower().startswith("## variant"):
                if current_title is not None:
                    parts.append((current_title, "\n".join(current).strip()))
                current_title = line.strip().replace("##", "").strip()
                current = []
            else:
                current.append(line)
        if current_title is not None:
            parts.append((current_title, "\n".join(current).strip()))

        if not parts:
            parts = [("Variant A", raw.strip())]

        st.success("Drafts created!")
        tabs = st.tabs([title for title, _ in parts])
        downloads_bundle = []

        for t, (title, body) in zip(tabs, parts):
            with t:
                st.markdown(f"#### {title}")
                st.markdown(body)
                fname = f"{title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
                st.download_button(f"Download {title}", data=body.encode("utf-8"), file_name=fname, mime="text/plain", key=f"dl_{title}")
                downloads_bundle.append((fname, body))

        # Save to history (store all variants together)
        add_history(
            "content_variants",
            {"company": asdict(company), "brief": asdict(brief), "brand_rules": brand_rules},
            {"variants": [{"title": t, "text": b} for t, b in parts]},
        )

        # Small “looks good” hint
        if not issues:
            st.info("Looks good for a first pass. Adjust tone/CTA or add brand rules and regenerate if needed.")

    except Exception as e:
        st.error(str(e))

divider()

# ---------------- History ----------------
with st.expander("🕘 History (last 20)"):
    if not st.session_state.history:
        st.caption("No items yet.")
    else:
        for i, item in enumerate(st.session_state.history, start=1):
            st.markdown(f"**{i}. {item['kind']}** · {item['ts']}")
            with st.expander("View"):
                st.code(json.dumps(item["input"], indent=2))
                out = item["output"]
                if isinstance(out, dict) and "variants" in out:
                    for v in out["variants"]:
                        st.markdown(f"**{v['title']}**")
                        st.markdown(v["text"])
                        st.markdown("---")
                else:
                    st.markdown(str(out))
            divider()



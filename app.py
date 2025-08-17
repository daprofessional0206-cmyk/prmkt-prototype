# app.py — Presence (v2.0 Prototype)
from __future__ import annotations

# ============= Streamlit must be first =============
import streamlit as st

# ============= Std libs =============
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pathlib import Path

# ============= Data =============
import pandas as pd

# ========= App config & small CSS polish =========
st.set_page_config(
    page_title="Presence — PR & Marketing AI (v2 Prototype)",
    page_icon="📣",
    layout="wide",
)
st.markdown(
    """
    <style>
      .block-container { padding-top: 0.8rem; padding-bottom: 2.2rem; }
      .stTextArea textarea { font-size: 0.96rem; line-height: 1.46; }
      .stDownloadButton button { width: 100%; }
      .stSelectbox, .stNumberInput, .stTextInput { font-size: 0.98rem; }
      .tagchip {
        display:inline-block; background:#223; color:#9ad;
        padding:2px 8px; margin:0 4px 4px 0; border-radius:12px;
        font-size:12px; border:1px solid #334;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============= Helpers =============
def divider() -> None:
    st.markdown("<hr style='border: 1px solid #202431; margin: 1.0rem 0;'/>", unsafe_allow_html=True)

def bulletize(text: str) -> List[str]:
    lines = [ln.strip("•- \t") for ln in text.splitlines() if ln.strip()]
    return lines[:15]

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def export_history_json() -> str:
    return json.dumps(st.session_state.get("history", []), ensure_ascii=False, indent=2)

def import_history_json(text: str) -> None:
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("History JSON must be a list.")
    # keep max 20; normalize structure
    st.session_state["history"] = data[:20]

def collect_all_tags(items: List[Dict[str, Any]]) -> List[str]:
    bag = set()
    for it in items:
        for t in it.get("tags", []):
            bag.add(t)
    return sorted(bag)

# ============= Phase 2 — dataset utils (preview/reset) =============
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

# ============= Optional OpenAI client (safe/offline) =============
OPENAI_OK = False
client = None
MODEL = "gpt-4o-mini"

if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        OPENAI_OK = True
    except Exception:
        OPENAI_OK = False

# ============= Data classes =============
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

# ============= Session state =============
if "history" not in st.session_state:
    st.session_state["history"] = []
if "history_filter_kind" not in st.session_state:
    st.session_state["history_filter_kind"] = ["Variants"]
if "history_filter_tags" not in st.session_state:
    st.session_state["history_filter_tags"] = []
if "history_search" not in st.session_state:
    st.session_state["history_search"] = ""

def add_history(kind: str, payload: dict, output: Any, tags: Optional[List[str]] = None):
    item = {
        "ts": now_iso(),
        "kind": kind,              # e.g., "strategy", "Variants"
        "tags": tags or [],        # user tags
        "input": payload,          # saved input payload
        "output": output,          # text or list[str]
    }
    st.session_state.history.insert(0, item)
    st.session_state.history = st.session_state.history[:20]

# ============= LLM prompt/generators =============
SYSTEM_PROMPT = """You are an expert PR & Marketing copywriter.
Write clear, compelling, brand-safe copy. Use only provided facts.
Match tone, audience, length; follow brand rules; use requested language.
Return only the copy, no preface or commentary.
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
    bullets_md = "\n".join([f"- {b}" for b in br.bullets]) if br.bullets else "- Add 2–3 benefits"
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
    bullets_md = "\n".join([f"• {b}" for b in br.bullets]) if br.bullets else "• Add key benefits"
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

# ============= Sidebar: dataset preview & app status =============
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

    st.caption(f"Dataset: `sample_dataset.csv`")
    try:
        df_preview = load_csv(SAMPLE_CSV, nrows=int(preview_rows))
        st.dataframe(df_preview, use_container_width=True)
    except Exception as e:
        st.warning(f"Could not load dataset preview: {e!s}")

    divider()
    st.subheader("🔧 App Status")
    if OPENAI_OK:
        st.success("OpenAI: Connected")
    else:
        st.info("OpenAI: Not configured (offline templates)")

# ============= Header =============
st.title("💡 Presence — PR & Marketing AI (v2 Prototype)")
st.caption("Strategy ideas, multi-variant content drafts, brand rules, language, and history with filters/tagging.")
divider()

# ============= 1) Company Profile =============
st.header("1️⃣  Company Profile")
c1, c2, c3 = st.columns([2, 1.4, 1.2])
with c1:
    company_name = st.text_input("Company Name", value="Acme Innovations", key="cp_name")
with c2:
    industry = st.text_input("Industry / Sector", value="Robotics, Fintech, Retail…", key="cp_industry")
with c3:
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

# ============= 2) Quick Strategy Idea =============
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
        add_history("strategy", asdict(company), idea, tags=["strategy"])
    except Exception as e:
        st.error(str(e))
divider()

# ============= 3) Content Engine — AI Copy (A/B/C) =============
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
        height=110,
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
    height=105,
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

# --- Generate button (unique key) ---
if st.button("Generate Variants (A/B/C)", key="btn_generate_variants", use_container_width=True):
    if not brief.topic.strip():
        st.warning("Please enter a topic / offer first.")
    else:
        try:
            outputs: List[str] = []
            if OPENAI_OK:
                raw = llm_copy(make_prompt(brief, company), temperature=0.65, max_tokens=1200)
                chunks = [seg.strip() for seg in raw.split("\n\n--\n\n") if seg.strip()]
                while len(chunks) < brief.variants:
                    chunks.append(chunks[-1])
                outputs = chunks[:brief.variants]
            else:
                # Offline templates
                if brief.content_type == "Press Release":
                    base = offline_press_release(brief, company)
                else:
                    base = offline_generic_copy(brief, company)
                outputs = [base for _ in range(brief.variants)]

            # Save to History (6.3) with auto tags
            auto_tags = [brief.content_type, brief.language]
            add_history("Variants", asdict(brief), outputs, tags=auto_tags)

            st.success("Draft(s) created!")

            # Show outputs + downloads (6.4)
            for idx, draft in enumerate(outputs, start=1):
                st.markdown(f"### Variant {idx}")
                st.markdown(draft)
                fname = f"variant_{idx}_{brief.content_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                st.download_button(
                    label=f"Download Variant {idx} (.txt)",
                    data=draft.encode("utf-8"),
                    file_name=fname,
                    mime="text/plain",
                    key=f"btn_dl_{idx}",
                )
                divider()
        except Exception as e:
            st.error(f"Error while generating: {e}")

divider()

# ============= 4) History (filters + tags + import/export) =============
with st.expander("🕘 History (last 20)", expanded=False):
    # Filters row
    col_kind, col_tags, col_search = st.columns([1.2, 1.6, 1.2])

    kinds_available = sorted({it.get("kind", "") for it in st.session_state.history} - {""}) or ["strategy", "Variants"]
    with col_kind:
        selected_kinds = st.multiselect(
            "Filter by type",
            options=kinds_available,
            default=st.session_state.history_filter_kind or kinds_available,
            key="hist_kind",
        )
        st.session_state.history_filter_kind = selected_kinds

    all_tags = collect_all_tags(st.session_state.history)
    with col_tags:
        selected_tags = st.multiselect(
            "Filter by tag(s)",
            options=all_tags,
            default=st.session_state.history_filter_tags,
            key="hist_tags",
        )
        st.session_state.history_filter_tags = selected_tags

    with col_search:
        search_text = st.text_input("Search text", value=st.session_state.history_search, key="hist_search")
        st.session_state.history_search = search_text.strip()

    # Export / Clear / Import row
    cA, cB, cC = st.columns([0.9, 0.9, 2])
    with cA:
        if st.download_button(
            "Export history (.json)",
            data=export_history_json().encode("utf-8"),
            file_name=f"presence_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            key="btn_export_history",
        ):
            pass
    with cB:
        if st.button("🗑️ Clear history", key="btn_clear_history"):
            st.session_state.history = []
            st.rerun()
    with cC:
        st.caption("Import history (.json)")
        up = st.file_uploader("Drag and drop file here", type=["json"], key="hist_uploader")
        if up is not None:
            try:
                import_history_json(up.read().decode("utf-8"))
                st.success("History imported.")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

    # Apply filters
    items = st.session_state.history
    if selected_kinds:
        items = [it for it in items if it.get("kind") in selected_kinds]
    if selected_tags:
        items = [it for it in items if any(t in it.get("tags", []) for t in selected_tags)]
    if search_text:
        q = search_text.lower()
        def match(it: Dict[str, Any]) -> bool:
            hay = json.dumps(it, ensure_ascii=False).lower()
            return q in hay
        items = [it for it in items if match(it)]

    st.caption(f"Showing {len(items)} of {len(st.session_state.history)} item(s).")
    divider()

    if not items:
        st.caption("No items yet.")
    else:
        for i, item in enumerate(items, start=1):
            kind = item.get("kind", "?")
            ts = item.get("ts", "")
            tags_str = "".join([f"<span class='tagchip'>{t}</span>" for t in item.get("tags", [])])
            st.markdown(f"**{i}. {kind}** · {ts}  {tags_str}", unsafe_allow_html=True)

            with st.expander("Open"):
                st.markdown("**Input**")
                st.code(json.dumps(item.get("input", {}), indent=2, ensure_ascii=False))
                st.markdown("**Output**")
                out = item.get("output")
                if isinstance(out, list):
                    for j, d in enumerate(out, start=1):
                        st.markdown(f"**Variant {j}**")
                        st.markdown(d)
                        st.markdown("---")
                else:
                    st.markdown(out if out else "_(empty)_")

            divider()

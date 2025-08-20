# pages/03_Content_Engine.py
from __future__ import annotations
import time
import streamlit as st

# --- soft imports -------------------------------------------------------------
try:
    from shared import state  # type: ignore
except Exception:
    class _State:
        def init(self): st.session_state.setdefault("company", {}); st.session_state.setdefault("brand_rules","")
        def get_company(self): return st.session_state["company"]
        def get_brand_rules(self): return st.session_state.get("brand_rules","")
    state = _State()  # type: ignore

try:
    from shared.llm import llm_copy, is_openai_ready  # type: ignore
except Exception:
    def is_openai_ready() -> bool: return False
    def llm_copy(prompt: str) -> str:
        return "Draft:\n• Opening line tailored to the audience.\n• Benefit/feature #1\n• Benefit/feature #2\n• Clear CTA"

try:
    from shared.history import add as add_history  # type: ignore
except Exception:
    def add_history(kind: str, payload: dict, output: str, tags=None):
        tags = tags or []
        st.session_state.setdefault("history", [])
        st.session_state["history"].append(
            {"kind": kind, "payload": payload, "output": output, "tags": tags, "ts": time.time()}
        )

# --- helpers ------------------------------------------------------------------
def throttle(key: str, seconds: float) -> bool:
    now = time.time()
    last = st.session_state.get(key, 0.0)
    remain = seconds - (now - last)
    if remain > 0:
        st.info(f"Please wait {int(remain)}s before generating again.")
        return True
    st.session_state[key] = now
    return False

def make_prompt(content_type: str, tone: str, length: str, language: str, company: dict, rules: str) -> str:
    return (
        f"Write a {content_type} in {language} with {tone.lower()} tone and {length.lower()} length.\n"
        f"Company: {company.get('name','(Company)')} | {company.get('industry','(Industry)')} | size {company.get('size','Mid-market')}.\n"
        f"Business goals: {company.get('goals','(Goals)')}.\n"
        f"Brand rules (must follow): {rules or '(none)'}.\n"
        "Return a clean draft. No disclaimers."
    )

# --- page ---------------------------------------------------------------------
st.set_page_config(page_title="Content Engine", page_icon="🧾", layout="wide")
state.init()
st.title("Content Engine")
st.caption("Generate press releases, ads, landing pages, blogs, and social posts.")

company = state.get_company()
rules = state.get_brand_rules()

with st.expander("View current brand rules"):
    st.code(rules or "(none)")

col1, col2, col3, col4 = st.columns([2,2,2,1])
with col1:
    content_type = st.selectbox(
        "Content Type",
        ["Press Release", "Ad Copy", "Landing Page", "Blog Post", "Social Post"],
        index=0,
    )
with col2:
    tone = st.selectbox("Tone", ["Neutral", "Bold", "Friendly", "Professional"], index=0)
with col3:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=0)
with col4:
    n_variants = st.number_input("Variants (A/B/C)", 1, 4, 1, step=1)

lang = st.selectbox("Language", ["English", "Hindi", "Spanish", "French"], index=0)

if throttle("content_cooldown", 4):
    st.stop()

if st.button("Generate A/B/C Variants", type="primary", use_container_width=True):
    if not is_openai_ready():
        st.warning("OpenAI key missing — showing template output.")

    drafts = []
    for i in range(int(n_variants)):
        prompt = make_prompt(content_type, tone, length, lang, company, rules)
        try:
            draft = llm_copy(prompt)
        except Exception as e:
            draft = f"(Fallback) Unable to reach LLM.\n\n{e}"
        drafts.append((prompt, draft))

    st.success("Draft(s) created!")
    for i, (p, d) in enumerate(drafts, start=1):
        st.markdown(f"### Variant {i}")
        st.markdown(d)
        add_history("variants", {"prompt": p, "content_type": content_type, "tone": tone, "length": length, "language": lang}, d, tags=[content_type, lang, tone])

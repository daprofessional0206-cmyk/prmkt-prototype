# app.py
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="PR & Marketing AI Prototype", page_icon="🧠", layout="wide")
import streamlit as st

# Thin separator between major sections
def divider():
    st.markdown("<hr style='border: 1px solid #202431; margin: 1.25rem 0;'/>", unsafe_allow_html=True)

# Slightly reduce global top padding
st.markdown("""
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 3rem; }
    </style>
""", unsafe_allow_html=True)


# ---------- helpers ----------
def ss_get(name, default):
    if name not in st.session_state:
        st.session_state[name] = default
    return st.session_state[name]

def bulletize(text):
    lines = [ln.strip("-• ").strip() for ln in text.splitlines() if ln.strip()]
    return [f"• {ln}" for ln in lines][:10]

# ---------- header ----------
st.title("🧠 PR & Marketing AI Platform — v0 Prototype")
st.caption("Stable baseline: unique Streamlit element keys + safe defaults (no undefined variables).")

# ---------- 1) Company Profile ----------
with st.container():
    st.header("1️⃣ Company Profile")

    company_name = st.text_input(
        "Company Name",
        value=ss_get("company_name", ""),
        key="cp_company_name",
    )
    industry = st.text_input(
        "Industry / Sector",
        value=ss_get("industry", ""),
        key="cp_industry",
    )
    size = st.selectbox(
        "Company Size",
        ["Small Business", "Mid-Size", "Enterprise"],
        index=["Small Business", "Mid-Size", "Enterprise"].index(ss_get("company_size", "Small Business")),
        key="cp_company_size",
    )
    goals = st.text_area(
        "Business Goals (comma separated)",
        value=ss_get("business_goals", "Grow pipeline, Improve brand awareness"),
        key="cp_goals",
        height=90,
    )

# ---------- 2) Strategy Idea (offline mock) ----------
with st.container():
    st.header("2️⃣ Strategy Suggestion (mock, offline)")
    if st.button("Generate Strategy Idea", key="btn_strategy"):
        goal_list = [g.strip() for g in goals.split(",") if g.strip()]
        st.info(
            f"**Draft idea** for **{company_name or 'your company'}** in **{industry or 'your industry'}**:\n\n"
            "- Launch a 4-week content sprint targeting top buyer pains.\n"
            "- Mix PR (2 press notes), social (8 posts), and 1 gated asset.\n"
            f"- Primary goals: {', '.join(goal_list) or 'brand awareness'}.\n"
            "- Include 1 customer story and 1 analyst/partner quote."
        )

# ----------------------------------------------------------
# 3️⃣ Content Engine — AI Copy Generator (live)
# ----------------------------------------------------------
import os
import json
from openai import OpenAI

st.header("3️⃣ Content Engine — AI Copy Generator (live)")

# Read API key from Streamlit secrets or env var
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))

# UI controls
content_type = st.selectbox("Content Type", ["Press Release","Ad Copy","LinkedIn Post","Tweet / X","Email","Landing Page"], index=0)
tone         = st.selectbox("Tone", ["Neutral","Friendly","Professional","Bold","Playful","Urgent"], index=0)
length       = st.selectbox("Length", ["Short","Medium","Long"], index=0)
platform     = st.selectbox("Platform (for Social/Ad)", ["Generic","LinkedIn","Instagram","Facebook","Twitter / X","YouTube","Google Ads"], index=0)
audience     = st.text_input("Audience (who is this for?)", value="Decision-makers")
cta          = st.selectbox("Call to Action", ["Book a demo","Sign up","Learn more","Buy now","Contact sales"], index=0)

topic        = st.text_input("Topic / Product / Offer", value="Launch of Acme RoboHub 2.0")
bullets      = st.text_area("Key Points (bullets, one per line)",
                            value="• 2× faster setup\n• SOC 2 Type II\n• Save 30% cost")

def _model_name():
    """
    Choose a lightweight, inexpensive model by default.
    You can change this to a larger model later.
    """
    return "gpt-4o-mini"  # good balance of quality/cost

def generate_copy():
    if not OPENAI_API_KEY:
        return None, "No API key found. Add OPENAI_API_KEY to Streamlit secrets or your environment."

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Build a clean JSON-friendly brief the model can follow
    brief = {
        "content_type": content_type,
        "tone": tone,
        "length": length,
        "platform": platform,
        "audience": audience,
        "call_to_action": cta,
        "topic": topic,
        "key_points": [ln.strip("• ").strip() for ln in bullets.splitlines() if ln.strip()]
    }

    system_msg = (
        "You are an expert PR/Marketing copywriter. "
        "Write clear, on-brand copy using the brief. "
        "Keep it factual, avoid hallucinations, and include a crisp CTA. "
        "Return ONLY the copy text (no explanations)."
    )

    user_msg = (
        "Brief (JSON):\n"
        f"{json.dumps(brief, ensure_ascii=False, indent=2)}"
    )

    try:
        resp = client.chat.completions.create(
            model=_model_name(),
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user",    "content": user_msg}
            ],
            temperature=0.7,
        )
        text = resp.choices[0].message.content.strip()
        return text, None
    except Exception as e:
        return None, f"OpenAI error: {e}"

if st.button("Generate Content", use_container_width=True):
    with st.spinner("Generating copy…"):
        text, err = generate_copy()
    if err:
        st.error(err)
    else:
        st.success("Draft created!")
        st.write(text)
        st.download_button(
            "Download .txt",
            data=text.encode("utf-8"),
            file_name=f"{content_type.lower().replace(' ','_')}.txt",
            mime="text/plain",
        )


# Lightweight lint (kept from your earlier version)
problems = []
if not topic:
    problems.append("Topic missing — add a topic/product name.")
if content_type == "Press Release" and "Press Release" not in topic:
    pass

if problems:
    st.warning("Fix these:")
    for p in problems:
        st.write("• " + p)
else:
    st.success("Looks good for a first draft.")


# app.py
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="PR & Marketing AI Prototype", page_icon="🧠", layout="wide")

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

# ---------- 3) Content Engine — AI Copy Generator (offline) ----------
with st.container():
    st.header("3️⃣ Content Engine — AI Copy Generator (offline)")

    col1, col2, col3 = st.columns(3)

    with col1:
        content_type = st.selectbox(
            "Content Type",
            ["Press Release", "LinkedIn Post", "Twitter/X Post", "Blog Intro", "Email (Outbound)"],
            index=["Press Release", "LinkedIn Post", "Twitter/X Post", "Blog Intro", "Email (Outbound)"].index(
                ss_get("content_type", "Press Release")
            ),
            key="ce_content_type",
        )
        platform = st.selectbox(
            "Platform (for Social/Ad)",
            ["Generic", "LinkedIn", "Twitter/X", "Facebook", "Instagram", "YouTube"],
            index=["Generic", "LinkedIn", "Twitter/X", "Facebook", "Instagram", "YouTube"].index(
                ss_get("platform", "Generic")
            ),
            key="ce_platform",
        )

    with col2:
        tone = st.selectbox(
            "Tone",
            ["Neutral", "Professional", "Friendly", "Bold", "Urgent"],
            index=["Neutral", "Professional", "Friendly", "Bold", "Urgent"].index(ss_get("tone", "Neutral")),
            key="ce_tone",
        )
        audience = st.text_input(
            "Audience (who is this for?)",
            value=ss_get("audience", "Decision-makers"),
            key="ce_audience",
        )

    with col3:
        length = st.selectbox(
            "Length",
            ["Short", "Medium", "Long"],
            index=["Short", "Medium", "Long"].index(ss_get("length", "Short")),
            key="ce_length",
        )
        cta = st.selectbox(
            "Call to Action",
            ["Book a demo", "Contact sales", "Download whitepaper", "Learn more", "Subscribe"],
            index=["Book a demo", "Contact sales", "Download whitepaper", "Learn more", "Subscribe"].index(
                ss_get("cta", "Book a demo")
            ),
            key="ce_cta",
        )

    topic = st.text_input(
        "Topic / Product / Offer",
        value=ss_get("topic", "Launch of Acme RoboHub 2.0"),
        key="ce_topic",
    )
    key_points = st.text_area(
        "Key Points (bullets, one per line)",
        value=ss_get("key_points", "2× faster setup\nSOC 2 Type II\nSave 30% cost"),
        key="ce_keypoints",
        height=120,
    )

    if st.button("Generate Content", key="btn_generate"):
        bullets = bulletize(key_points)

        # very simple text template (offline)
        now = datetime.utcnow().strftime("%Y-%m-%d")
        body = [
            f"[{content_type}] for {platform} — {now}",
            f"Company: {company_name or 'Your company'}",
            f"Industry: {industry or 'N/A'} | Size: {size}",
            f"Audience: {audience} | Tone: {tone} | Length: {length}",
            "",
            f"Topic: {topic}",
            "",
            "Key Points:",
            *bullets,
            "",
            f"CTA: {cta}",
        ]
        st.success("Draft created below (offline template).")
        st.code("\n".join(body))

        # simple checks (no crashes if empty)
        problems = []
        if not topic:
            problems.append("Topic missing — add a topic/product name.")
        if content_type == "Press Release" and "Press Release" not in topic:
            # this is just a gentle nudge; not required
            pass

        if problems:
            st.warning("Fix these:")
            for p in problems:
                st.write("• " + p)
        else:
            st.success("Looks good for a first draft.")

st.markdown("---")
st.caption("Prototype v0 — stable inputs (unique keys), safe defaults, and offline content generation.")

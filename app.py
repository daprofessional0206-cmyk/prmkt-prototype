import streamlit as st
from datetime import date

# ------------------------------
# Page setup
# ------------------------------
st.set_page_config(page_title="PR & Marketing AI Prototype", layout="wide")
st.title("🧠 PR & Marketing AI Platform — v0.1")
st.caption("v0.1 adds a no-API AI Copy Generator. We’ll plug in live data + LLMs next.")

# ------------------------------
# Company Profile
# ------------------------------
st.header("1️⃣ Company Profile")
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        company_name = st.text_input("Company Name", placeholder="Acme Robotics")
    with col2:
        industry = st.text_input("Industry / Sector", placeholder="Consumer Electronics")
    with col3:
        company_size = st.selectbox("Company Size", ["Small Business", "Mid-size", "Large MNC"])

    goals = st.text_area("Business Goals", placeholder="Grow qualified leads, launch new product, improve brand trust")
    unique = st.text_area("Unique Value / Proof", placeholder="99.9% uptime, ISO-27001, 2x faster onboarding")
    primary_audience = st.text_input("Primary Audience", placeholder="IT Directors at mid-size SaaS companies")

    if st.button("Save Profile"):
        st.success(f"Profile saved for **{company_name or 'Company'}** in **{industry or 'Sector'}**.")

# ------------------------------
# Strategy Brain (placeholder)
# ------------------------------
st.header("2️⃣ Strategy Brain")
with st.container(border=True):
    strategy_notes = st.text_area("Notes or context for your PR/Marketing strategy (optional)")
    if st.button("Generate Strategy Idea"):
        st.info("💡 Try a 2-week campaign using LinkedIn posts + short blog + email follow-ups. Focus on 1 key proof point.")

# ------------------------------
# Simple AI Copy Generator (no API)
# ------------------------------
st.header("3️⃣ Content Engine — AI Copy Generator (offline)")
with st.container(border=True):

    colA, colB, colC = st.columns(3)
    with colA:
        content_type = st.selectbox("Content Type", ["Press Release", "Social Post", "Blog Intro", "Ad Copy"])
    with colB:
        tone = st.selectbox("Tone", ["Neutral", "Friendly", "Confident", "Bold", "Formal"])
    with colC:
        length = st.selectbox("Length", ["Short", "Medium", "Long"])

    colD, colE, colF = st.columns(3)
    with colD:
        platform = st.selectbox("Platform (for Social/Ad)", ["Generic", "LinkedIn", "Twitter/X", "Instagram", "Facebook"])
    with colE:
        audience = st.text_input("Audience (who is this for?)", value=primary_audience or "Decision-makers")
    with colF:
        call_to_action = st.text_input("Call to Action", value="Book a demo")

    topic = st.text_input("Topic / Product / Offer", placeholder="Launch of Acme RoboHub 2.0")
    key_points = st.text_area("Key Points (bullets, one per line)", placeholder="• 2x faster setup\n• SOC 2 Type II\n• Saves 30% cost")

    def style_with_tone(text: str, tone: str):
        # lightweight stylistic tweaks
        t = tone.lower()
        if t == "friendly":
            prefix = "Hey there — "
        elif t == "confident":
            prefix = "Here’s the bottom line: "
        elif t == "bold":
            prefix = "Big news: "
        elif t == "formal":
            prefix = "Announcement: "
        else:
            prefix = ""
        return prefix + text

    def choose_length(length: str, short: str, medium: str, long: str):
        if length == "Short":
            return short
        if length == "Long":
            return long
        return medium

    def bullet_join(lines):
        pts = [l.strip("•- ").strip() for l in lines.split("\n") if l.strip()]
        return pts

    def gen_press_release():
        pts = bullet_join(key_points)
        headline = f"{company_name or 'Our Company'} Announces {topic or 'a New Offering'}"
        sub = choose_length(
            length,
            f"{industry or 'Industry'} milestone delivering value to {audience or 'customers'}.",
            f"{(company_name or 'The company')} unveils {topic or 'new solution'} for {audience or 'the market'}, highlighting {', '.join(pts[:2]) if pts else 'key benefits'}.",
            f"{(company_name or 'The company')} today announced {topic or 'a new solution'}, designed for {audience or 'customers'} and engineered to deliver {', '.join(pts[:3]) if len(pts)>=3 else 'measurable outcomes'} in {industry or 'its category'}."
        )
        body_intro = choose_length(
            length,
            f"{company_name or 'The company'} today announced {topic or 'a new solution'} for {audience or 'customers'}.",
            f"{company_name or 'The company'} today announced {topic or 'a new solution'}, purpose-built for {audience or 'customers'} in {industry or 'the industry'}.",
            f"{company_name or 'The company'} today announced {topic or 'a new solution'}, built for {audience or 'customers'} operating in {industry or 'the industry'}. The release aligns with our goals to {goals or 'drive growth and trust'}."
        )
        benefits = pts or ["Performance improvements", "Security/compliance", "Lower total cost"]
        quotes = f"“{topic or 'This launch'} reflects our commitment to real impact,” said the {(company_name or 'Company')} team."
        cta_line = f"To learn more, {call_to_action or 'contact us'} at our website."

        result = f"""PRESS RELEASE
Headline: {headline}
Subhead: {sub}

{body_intro}

Key Benefits:
- {"\n- ".join(benefits)}

Quote:
{quotes}

About {(company_name or 'the company')}:
{(unique or 'We deliver reliable, secure, and scalable solutions.')} Founded {date.today().year-5}, serving {company_size or 'growing teams'} in {industry or 'multiple industries'}.

CTA:
{cta_line}
"""
        return style_with_tone(result, tone)

    def gen_social():
        pts = bullet_join(key_points)
        tagline = choose_length(
            length,
            f"{topic or 'New launch'} is here.",
            f"{topic or 'New launch'} for {audience or 'you'} — built to deliver results.",
            f"{topic or 'New launch'} for {audience or 'teams'}: {', '.join(pts[:3]) if pts else 'speed, security, savings'}."
        )
        hash_base = [industry, company_name, "launch", "AI", "growth"]
        hashtags = " ".join([f"#{h.replace(' ', '')}" for h in hash_base if h])

        if platform == "LinkedIn":
            style_hint = "Tailored for professionals. Keep it value-driven."
        elif platform == "Twitter/X":
            style_hint = "Short, punchy, with 1–2 hashtags."
        elif platform == "Instagram":
            style_hint = "Add an eye-catching visual. Keep lines short."
        elif platform == "Facebook":
            style_hint = "Conversational. Add a friendly CTA."
        else:
            style_hint = "Generic social style."

        body = f"{tagline}\n{(' • '.join(pts[:3])) if pts else ''}\n{hashtags}\n\n{call_to_action or 'Learn more'} → {company_name or 'our site'}"
        return style_with_tone(f"{body}\n\n({style_hint})", tone)

    def gen_blog_intro():
        pts = bullet_join(key_points)
        hook = choose_length(
            length,
            f"{audience or 'teams'} are under pressure to do more with less.",
            f"{audience or 'teams'} face tighter budgets and higher expectations. {topic or 'This post'} explains a clearer path.",
            f"In every conversation with {audience or 'leaders'}, the same theme shows up: pressure to move faster without risking quality or security. {topic or 'In this post'}, we break down a practical way forward."
        )
        section = f"Why it matters: {', '.join(pts) if pts else 'Speed, security, and savings now define winning teams.'}"
        promise = f"By the end, you’ll know how {company_name or 'we'} help {audience or 'teams'} get measurable results."
        return style_with_tone(f"{hook}\n\n{section}\n\n{promise}\n\nCTA: {call_to_action or 'Book a demo'}", tone)

    def gen_ad_copy():
        pts = bullet_join(key_points)
        headline = choose_length(
            length,
            f"{topic or 'Upgrade fast.'}",
            f"{topic or 'Upgrade performance.'}",
            f"{topic or 'Upgrade performance without the risk.'}"
        )
        body = choose_length(
            length,
            f"{', '.join(pts[:2]) if pts else 'Faster setup. Lower cost.'}",
            f"{', '.join(pts[:3]) if pts else 'Faster setup, compliance, and cost savings.'}",
            f"{', '.join(pts[:4]) if pts else 'Faster setup, tighter security, lower cost, proven ROI.'}"
        )
        line = f"{headline}\n{body}\n{call_to_action or 'Start now'}"
        return style_with_tone(line, tone)

    def generate_copy():
        if content_type == "Press Release":
            return gen_press_release()
        if content_type == "Social Post":
            return gen_social()
        if content_type == "Blog Intro":
            return gen_blog_intro()
        if content_type == "Ad Copy":
            return gen_ad_copy()
        return "Select a content type."

    if st.button("Generate Content"):
        output = generate_copy()
        st.success("Generated content:")
        st.code(output, language="markdown")

# ------------------------------
# Brand Check (placeholder)
# ------------------------------
st.header("4️⃣ Brand Check")
with st.container(border=True):
    content_to_check = st.text_area("Paste content to check brand basics")
    if st.button("Run Brand Check"):
        problems = []
        if len(content_to_check) < 40:
            problems.append("Very short — add more detail for credibility.")
        if call_to_action and call_to_action.lower() not in content_to_check.lower():
            problems.append("CTA missing — include your call to action.")
        if (company_name or "").lower() not in content_to_check.lower():
            problems.append("Company not mentioned — add company name once.")

        if problems:
            st.warning("Fix these:")
            for p in problems:
                st.write("• " + p)
        else:
            st.success("Looks good for a first draft.")

st.markdown("---")
st.caption("Next: save to JSON, live news hooks, multi-language, and optional LLM APIs.")
# ==============================
# Content Engine — AI Copy Generator (offline, +language +download)
# ==============================
import io

st.subheader("3️⃣  Content Engine — AI Copy Generator (offline)")
st.caption("Now supports language output and download.")

col1, col2, col3 = st.columns(3)
with col1:
    content_type = st.selectbox("Content Type", [
        "Press Release", "Ad Copy", "LinkedIn Post", "Tweet/X Post", "Blog Intro"
    ])
with col2:
    tone = st.selectbox("Tone", ["Neutral", "Friendly", "Professional", "Bold"])
with col3:
    length = st.selectbox("Length", ["Short", "Medium", "Long"])

colp1, colp2, colp3 = st.columns(3)
with colp1:
    platform = st.selectbox("Platform (for Social/Ad)", ["Generic", "LinkedIn", "X/Twitter", "Instagram", "YouTube"])
with colp2:
    audience = st.selectbox("Audience (who is this for?)", ["Decision-makers", "Buyers", "Developers", "General"])
with colp3:
    cta_choice = st.selectbox("Call to Action", ["Book a demo", "Learn more", "Sign up", "Contact us"])

# NEW: language output
language = st.selectbox("Language", ["English", "Hindi", "Gujarati"])

topic = st.text_input("Topic / Product / Offer", placeholder="Launch of Acme RoboHub 2.0")
bullets = st.text_area("Key Points (bullets, one per line)",
                       placeholder="• 2x faster setup\n• SOC 2 Type II\n• Saves 30% cost")

def translate_text(lang: str, text: str) -> str:
    """
    Quick, rule-based translation-ish mapping for demo.
    (Not accurate translation — just enough to prove the UI/flow.
    We’ll replace with a real LLM later.)
    """
    if lang == "English":
        return text
    # very simple word swaps to demonstrate multi-language output
    mapping_hi = {
        "Press Release": "प्रेस विज्ञप्ति",
        "Book a demo": "डेमो बुक करें",
        "Learn more": "और जानें",
        "Sign up": "साइन अप करें",
        "Contact us": "हमसे संपर्क करें",
        "Key Points": "मुख्य बिंदु"
    }
    mapping_gu = {
        "Press Release": "પ્રેસ રિલીઝ",
        "Book a demo": "ડેમો બુક કરો",
        "Learn more": "વધુ જાણો",
        "Sign up": "સાઇન અપ કરો",
        "Contact us": "અમારો સંપર્ક કરો",
        "Key Points": "મુખ્ય મુદ્દા"
    }
    mp = mapping_hi if lang == "Hindi" else mapping_gu
    for k, v in mp.items():
        text = text.replace(k, v)
    return text

def make_draft():
    # Build a simple, offline draft
    lines = []
    title_map = {
        "Press Release": "Press Release",
        "Ad Copy": "Ad Copy",
        "LinkedIn Post": "LinkedIn Post",
        "Tweet/X Post": "Tweet/X Post",
        "Blog Intro": "Blog Intro"
    }
    title = f"{title_map.get(content_type, content_type)} — {topic}".strip(" —")
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")
    lines.append(f"Tone: {tone} | Length: {length} | Audience: {audience} | CTA: {cta_choice}")
    lines.append(f"Platform: {platform}")
    lines.append("")

    if bullets.strip():
        lines.append("Key Points:")
        # normalize bullet list
        pts = [b.strip("•- ").strip() for b in bullets.splitlines() if b.strip()]
        for p in pts:
            lines.append(f"• {p}")
        lines.append("")

    # pretend generated body (rule-based skeleton)
    body = []
    if content_type == "Press Release":
        body.append(f"{topic} — announced today, designed for {audience.lower()}.")
        body.append("It improves speed, reliability, and cost for modern teams.")
        body.append("For details and a walkthrough, see the link below.")
    elif content_type == "Ad Copy":
        body.append(f"Introducing {topic}. Faster. Smarter. Better.")
        body.append("Get the edge you need — without the complexity.")
    elif content_type == "LinkedIn Post":
        body.append(f"We’re excited to share {topic}! 🚀")
        body.append("Built for real-world teams who value impact over noise.")
    elif content_type == "Tweet/X Post":
        body.append(f"{topic}: speed, trust, and savings — in one place. #New")
    else:
        body.append(f"{topic} sets a new baseline for performance and simplicity.")
        body.append("Here’s why it matters and how you can get started…")

    lines.extend(body)
    lines.append("")
    lines.append(f"➡ {cta_choice}")
    draft = "\n".join(lines)

    # apply the quick language mapping
    return translate_text(language, draft)

if st.button("Generate Content"):
    draft_text = make_draft()
    st.text_area("Generated Content", draft_text, height=300)

    # NEW: Download options
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            "Download .txt",
            data=draft_text.encode("utf-8"),
            file_name="ai_copy.txt",
            mime="text/plain"
        )
    with col_dl2:
        md = f"```text\n{draft_text}\n```"
        st.download_button(
            "Download .md",
            data=md.encode("utf-8"),
            file_name="ai_copy.md",
            mime="text/markdown"
        )

# lightweight checks (kept from earlier logic, optional)
problems = []
if not topic:
    problems.append("Topic missing — add a topic/product name.")
if content_type == "Press Release" and "Press Release" not in topic:
    # just a gentle nudge for demo
    pass

if problems:
    st.warning("Fix these:")
    for p in problems:
        st.write("• " + p)
else:
    st.success("Looks good for a first draft.")

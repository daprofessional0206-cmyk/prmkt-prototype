# shared/llm.py
from __future__ import annotations

from typing import Dict, Any, List
import streamlit as st

# We only import the OpenAI client when a key exists to avoid hard failure locally.
_CLIENT = None
_MODEL = "gpt-4o-mini"  # fast & frugal; adjust if you prefer


def is_openai_ready() -> bool:
    """True if an API key is supplied in Streamlit secrets."""
    return bool(st.secrets.get("OPENAI_API_KEY"))


@st.cache_resource(show_spinner=False)
def _get_client():
    """Lazily create an OpenAI client (cached)."""
    from openai import OpenAI
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


SYSTEM_PROMPT = """You are an expert PR & Marketing copywriter.
Write clear, compelling, brand-safe copy. Keep facts generic unless provided.
Follow brand rules if present. If a language is specified, write in it.
Return only the copy, no preface.
"""


def build_prompt(company: Dict[str, str], brief: Dict[str, Any]) -> str:
    """
    brief keys expected:
      content_type, platform, topic, bullets(list[str]),
      tone, length, audience, cta, language, variants, brand_rules
    """
    bullets = brief.get("bullets") or []
    bullets_md = "\n".join([f"- {b}" for b in bullets]) if bullets else "(no bullets provided)"
    brand_rules = (brief.get("brand_rules") or "").strip() or "(none provided)"

    return f"""
Generate {brief.get('variants', 1)} distinct variant(s) of a {brief['length'].lower()} {brief['content_type'].lower()}.

Language: {brief.get('language','English')}.
Audience: {brief.get('audience','Decision-makers')}. Tone: {brief.get('tone','Professional')}.
Company: {company.get('name')} ({company.get('industry')}, size: {company.get('size')}).
Topic / Offer: {brief.get('topic')}

Key points:
{bullets_md}

Call to action: {brief.get('cta')}

Brand rules (follow & avoid banned words):
{brand_rules}

Separator rule:
- Separate each variant with a line that contains exactly three hyphens:
---
"""


def _parse_variants(raw: str, expected: int) -> List[str]:
    # Split by our separator line '---'
    parts = [p.strip() for p in raw.split("\n---\n") if p.strip()]
    if len(parts) < expected:
        # fallback split by big paragraph gaps
        alt = [p.strip() for p in raw.split("\n\n") if p.strip()]
        if len(alt) >= expected:
            parts = alt[:expected]
    # pad if still short
    while len(parts) < expected and parts:
        parts.append(parts[-1])
    if not parts:
        parts = ["(No content returned)"]
    return parts[:expected]


def _offline_variant(company: Dict[str, str], brief: Dict[str, Any], style: int) -> str:
    """A richer offline fallback that produces believable copy."""
    topic = brief.get("topic") or "your offering"
    tone = brief.get("tone", "Professional")
    cta = brief.get("cta", "Get started today.")
    audience = brief.get("audience", "Decision-makers")
    bullets = brief.get("bullets") or []
    bullets_md = "\n".join([f"• {b}" for b in bullets]) if bullets else "• Add 2–3 benefits customers care about."

    if brief.get("content_type") == "Press Release":
        openers = [
            f"FOR IMMEDIATE RELEASE\n\n{company['name']} Introduces {topic} for {audience}",
            f"FOR IMMEDIATE RELEASE\n\n{company['name']} Unveils {topic}: Built for {audience}",
            f"FOR IMMEDIATE RELEASE\n\n{company['name']} Announces {topic} — A {tone.lower()} step forward",
        ]
        return f"""{openers[style % len(openers)]}

[{company.get('industry','Industry')}, {company.get('size','Company')}]

Key highlights:
{bullets_md}

Next steps: {cta}
"""

    # Generic content (Ad, Social, Landing, Email)
    headlines = [
        f"{topic}: Faster results for {audience}",
        f"Meet {topic} — built for {audience}",
        f"{topic} that {audience} actually use",
    ]
    body = f"""Tone: {tone}. What you’ll get:
{bullets_md}

Call to action: {cta}"""
    return f"**{headlines[style % len(headlines)]}**\n\n{body}"


def _offline_generate(company: Dict[str, str], brief: Dict[str, Any]) -> List[str]:
    variants = int(brief.get("variants", 1)) or 1
    return [_offline_variant(company, brief, i) for i in range(variants)]


def generate_copy(company: Dict[str, str], brief: Dict[str, Any], temperature: float = 0.65) -> List[str]:
    """
    Returns a list of `variants` strings.
    Uses OpenAI if available, otherwise rich offline fallback.
    """
    variants = int(brief.get("variants", 1)) or 1

    if not is_openai_ready():
        return _offline_generate(company, brief)

    try:
        client = _get_client()
        prompt = build_prompt(company, brief)
        resp = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=1100,
        )
        raw = (resp.choices[0].message.content or "").strip()
        if not raw:
            # If model returns empty (rare), use offline
            return _offline_generate(company, brief)
        return _parse_variants(raw, expected=variants)
    except Exception:
        # Any API error: gracefully fall back
        return _offline_generate(company, brief)

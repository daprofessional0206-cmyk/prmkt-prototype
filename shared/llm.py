from __future__ import annotations
import os
import streamlit as st

# Optional OpenAI import (graceful if missing)
try:
    from openai import OpenAI
except Exception:  # library not installed or incompatible
    OpenAI = None  # type: ignore


def is_openai_ready() -> bool:
    return bool(st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")) and OpenAI is not None


def _client():
    if not is_openai_ready():
        return None
    key = st.secrets.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
    # New OpenAI SDK client (>=1.0)
    return OpenAI(api_key=key)


def _chat(system: str, user: str, n: int = 1):
    """
    Return (messages, error_text). messages is a list[str] with n completions.
    On any issue it returns ([], 'error message').
    """
    try:
        cl = _client()
        if cl is None:
            return [], "OpenAI not configured or SDK unavailable."

        model = st.secrets.get("openai_model") or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        resp = cl.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            n=n,
            temperature=0.7,
        )
        outs = []
        for ch in resp.choices:
            txt = ch.message.content if hasattr(ch.message, "content") else ch.message.get("content", "")
            outs.append(txt or "")
        return outs, ""
    except Exception as e:
        return [], f"{type(e).__name__}: {e}"


def strategy(goals: str, company, tone: str, length: str):
    system = "You are a senior PR & marketing strategist. Produce one focused, practical initiative."
    user = f"""
Company: {company.name or '—'} (Industry: {company.industry or '—'}, Size: {company.size or '—'})
Goals: {goals or company.goals or '—'}
Tone: {tone}; Length: {length}
Brand rules (if any): {company.brand_rules or '—'}

Return a crisp idea with: Objective, Core concept, Channels, Why it fits the brand.
"""
    outs, err = _chat(system, user, n=1)
    if outs:
        return outs[0], ""
    # fallback text
    fallback = (
        "Objective: Raise awareness among ICP this quarter.\n"
        "Concept: Signature PR hook aligned with brand positioning.\n"
        "Channels: Press outreach • Social • Blog • Email.\n"
        "Why it fits: Matches voice and solves a key audience pain."
    )
    return fallback, err or "LLM unavailable."


def variants(content_type: str, n_variants: int, company, tone: str, length: str, lang: str):
    system = "You are a precise PR/marketing copywriter. Follow brand rules and format tightly."
    user = f"""
Content: {content_type}
Company: {company.name or '—'} (Industry: {company.industry or '—'}, Size: {company.size or '—'})
Tone: {tone}; Length: {length}; Language: {lang}
Brand rules (if any): {company.brand_rules or '—'}

Return {n_variants} numbered variants separated by clear headings.
"""
    outs, err = _chat(system, user, n=n_variants)
    if outs:
        return outs, ""
    # fallback
    fb = [
        "Draft:\n• Opening line tailored to the audience.\n• Benefit/feature #1\n• Benefit/feature #2\n• Clear CTA",
    ]
    return fb, err or "LLM unavailable."

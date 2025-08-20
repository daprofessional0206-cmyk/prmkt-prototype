# shared/llm.py
from __future__ import annotations

import os
from typing import Optional, Tuple, List, Any

# Streamlit is optional at import time (so this module works in tests, too)
try:
    import streamlit as st  # type: ignore
except Exception:  # pragma: no cover
    st = None  # type: ignore

# OpenAI SDK v1
try:
    from openai import OpenAI
    from openai.types.chat import ChatCompletion
except Exception as e:  # pragma: no cover
    OpenAI = None  # type: ignore


# --------------------------- Key / Client helpers ---------------------------

def _get_api_key() -> Optional[str]:
    """Return OpenAI API key from Streamlit secrets or environment."""
    # 1) Streamlit secrets (preferred)
    if st is not None:
        try:
            key = st.secrets.get("openai_api_key")  # type: ignore[attr-defined]
            if key:
                return str(key)
        except Exception:
            pass

    # 2) Environment variables
    for name in ("OPENAI_API_KEY", "openai_api_key"):
        key = os.environ.get(name)
        if key:
            return key

    return None


def is_openai_ready() -> bool:
    """Quick health check: is an API key available and SDK import OK?"""
    return OpenAI is not None and _get_api_key() is not None


def _client() -> Any:
    """Create an OpenAI client or raise a clear error."""
    if OpenAI is None:
        raise RuntimeError(
            "OpenAI SDK not available. Make sure 'openai' is in requirements.txt."
        )
    key = _get_api_key()
    if not key:
        raise RuntimeError(
            "OpenAI API key not found. Set Streamlit secret 'openai_api_key' "
            "or env var OPENAI_API_KEY."
        )
    return OpenAI(api_key=key)


# ------------------------------- Core call ---------------------------------

def _chat(
    prompt: str,
    *,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_tokens: int = 600,
    system: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """
    Execute a chat completion. Returns (text, error).
    If error is not None, text may contain a short fallback/explanation.
    """
    try:
        client = _client()
        sys_msg = system or (
            "You are a helpful marketing & PR writing assistant. "
            "Return clear, concise copy in plain text."
        )

        resp: ChatCompletion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
        )

        # Current SDK returns message content here:
        text = (resp.choices[0].message.content or "").strip()
        if not text:
            return "", "Empty response from model."
        return text, None

    except Exception as e:
        # Do not raise — pages should keep running and show a clear message.
        return (
            f"[LLM error] {e}\n"
            "Tip: Check OpenAI key in Admin Settings → Secrets (or environment).",
            str(e),
        )


# ----------------------- Page-friendly convenience -------------------------

def llm_copy(
    *,
    content_type: str,
    topic: str,
    audience: str,
    tone: str,
    length: str,
    language: str = "English",
    brand_rules: str = "",
    company: Optional[dict] = None,
    bullets: Optional[List[str]] = None,
    cta: Optional[str] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    variants: int = 1,
    max_tokens: int = 700,
) -> Tuple[List[str], Optional[str]]:
    """
    High-level helper used by pages. Returns (list_of_variants, error).

    It builds a consistent prompt that respects brand rules and company context
    and generates the requested number of variants.
    """
    bullets = bullets or []
    company = company or {}

    # Build a single prompt for determinism; variants generated in a loop
    prompt = (
        f"Language: {language}\n"
        f"Content type: {content_type}\n"
        f"Topic/Offer: {topic}\n"
        f"Audience: {audience}\n"
        f"Tone: {tone}\n"
        f"Desired length: {length}\n"
        f"Brand rules (do/don'ts, banned words):\n{brand_rules.strip()}\n\n"
        f"Company context:\n"
        f"  - Name: {company.get('name','(Company)')}\n"
        f"  - Industry: {company.get('industry','(Industry)')}\n"
        f"  - Size: {company.get('size','(Size)')}\n"
        f"  - Goals: {company.get('goals','(Goals)')}\n"
        f"\nKey points:\n"
        + "\n".join([f"  - {b}" for b in bullets])
        + ("\n" if bullets else "")
        + (f"\nCall to action: {cta}\n" if cta else "")
        + "\nInstructions:\n"
          "- Write *brand-safe* copy that follows the rules above.\n"
          "- Be specific and avoid generic platitudes.\n"
          "- Do not include preambles like 'Here is...'; output only the copy.\n"
    )

    outputs: List[str] = []
    last_error: Optional[str] = None
    for _ in range(max(1, variants)):
        text, err = _chat(
            prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if err:
            last_error = err
        outputs.append(text)

    return outputs, last_error

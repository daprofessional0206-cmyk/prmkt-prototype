# shared/llm.py — clean OpenAI client wrapper (no hardcoded keys)

from __future__ import annotations
import os
from typing import Optional, Dict, Any

import streamlit as st

# Try OpenAI 1.x client
try:
    from openai import OpenAI  # pip install openai>=1.0.0
    _HAS_OPENAI = True
except Exception:
    OpenAI = None  # type: ignore
    _HAS_OPENAI = False


_DEFAULT_MODEL = "gpt-4o-mini"
_DEFAULT_SYSTEM = (
    "You are an expert PR & Marketing copywriter. "
    "Write clear, compelling, brand-safe copy. Keep facts generic unless provided. "
    "Match the requested tone, audience, and length. Return only the copy."
)


def _get_api_key() -> Optional[str]:
    # Prefer Streamlit secrets > env var
    if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
        return st.secrets["OPENAI_API_KEY"]
    return os.getenv("OPENAI_API_KEY")


def has_key() -> bool:
    return bool(_get_api_key())


def online() -> bool:
    """True if OpenAI client can be constructed."""
    return _HAS_OPENAI and has_key()


def _get_client() -> Any:
    """Memoize client in session to avoid recreating."""
    if "openai_client" not in st.session_state:
        api_key = _get_api_key()
        if not api_key or not _HAS_OPENAI:
            raise RuntimeError("OpenAI not available: missing key or package.")
        st.session_state["openai_client"] = OpenAI(api_key=api_key)
    return st.session_state["openai_client"]


def health() -> Dict[str, Any]:
    return {
        "openai_installed": _HAS_OPENAI,
        "has_key": has_key(),
        "online": online(),
        "model_default": st.secrets.get("OPENAI_MODEL", _DEFAULT_MODEL) if hasattr(st, "secrets") else _DEFAULT_MODEL,
    }


def generate(
    prompt: str,
    system: Optional[str] = None,
    temperature: float = 0.6,
    max_tokens: int = 900,
    model: Optional[str] = None,
) -> str:
    """
    Core text generation. Raises clean RuntimeError if anything fails
    (so callers can show a friendly error).
    """
    if not online():
        raise RuntimeError("OpenAI is not configured (no key or package missing).")

    _model = model or st.secrets.get("OPENAI_MODEL", _DEFAULT_MODEL)
    _system = system or _DEFAULT_SYSTEM

    try:
        client = _get_client()
        resp = client.chat.completions.create(
            model=_model,
            messages=[
                {"role": "system", "content": _system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            raise RuntimeError("OpenAI returned empty content.")
        return content
    except Exception as e:
        # Bubble up so the UI can show a clear message instead of silently falling back
        raise RuntimeError(f"OpenAI error: {e!s}") from e

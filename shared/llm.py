# shared/llm.py
from __future__ import annotations

import os
from typing import Optional, Tuple, Any

# Streamlit is optional here—module still works without it (e.g., in tests)
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None  # noqa: N816

# OpenAI SDK (>=1.0)
try:
    from openai import OpenAI
except Exception as e:  # pragma: no cover
    OpenAI = None  # type: ignore
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -------------------------- Config --------------------------

DEFAULT_MODEL = "gpt-4o-mini"

def _get_api_key() -> Optional[str]:
    """
    Returns an API key from Streamlit secrets or the environment.
    Priority: st.secrets["OPENAI_API_KEY"] -> os.environ["OPENAI_API_KEY"]
    """
    # 1) Streamlit Cloud / local secrets
    if st is not None:
        try:
            if "OPENAI_API_KEY" in st.secrets and st.secrets["OPENAI_API_KEY"]:
                return str(st.secrets["OPENAI_API_KEY"])
        except Exception:
            pass

    # 2) Environment variable
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key or None


def _make_client() -> Tuple[Optional[Any], bool, str]:
    """
    Try to construct the OpenAI client. Returns (client, ok_flag, reason_if_not_ok).
    """
    if OpenAI is None:
        return None, False, "openai SDK not installed or failed to import"

    api_key = _get_api_key()
    if not api_key:
        return None, False, "OPENAI_API_KEY not found in secrets or environment"

    try:
        client = OpenAI(api_key=api_key)
        return client, True, ""
    except Exception as e:
        return None, False, f"failed to initialize OpenAI client: {e!s}"


_client, OPENAI_OK, _WHY_NOT = _make_client()


# ------------------------ Public API ------------------------

SYSTEM_PROMPT = (
    "You are an expert PR & Marketing copywriter. Write clear, compelling, "
    "brand-safe copy. Keep facts generic unless provided. Match requested tone, "
    "audience, and length. If brand rules are provided, follow them and avoid "
    "banned words. Return only the copy, no preface."
)


def llm_copy(
    prompt: str,
    *,
    temperature: float = 0.6,
    max_tokens: int = 900,
    model: str = DEFAULT_MODEL,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """
    Generate copy with OpenAI. If the client isn't available, returns an
    offline placeholder so the app still functions.

    Other modules import this exactly as:
        from shared.llm import OPENAI_OK, llm_copy
    """
    # Offline fallback if no working client
    if not OPENAI_OK or _client is None:
        return (
            "Draft:\n"
            "• Opening line tailored to the audience.\n"
            "• Benefit/feature #1\n"
            "• Benefit/feature #2\n"
            "• Clear CTA.\n"
            "\n"
            "_[Offline template shown because OpenAI is not configured.]_"
        )

    try:
        resp = _client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = (resp.choices[0].message.content or "").strip()
        return text or "(empty response)"
    except Exception as e:
        # Graceful fallback on any runtime error
        msg = str(e)
        return (
            "Draft:\n"
            "• Opening line tailored to the audience.\n"
            "• Benefit/feature #1\n"
            "• Benefit/feature #2\n"
            "• Clear CTA.\n"
            f"\n_[Fallback used due to LLM error: {msg}]_"
        )


def status_text() -> str:
    """
    Small helper you can show in a sidebar if you want:
        st.caption(status_text())
    """
    if OPENAI_OK:
        return f"OpenAI: Connected ({DEFAULT_MODEL})"
    return f"OpenAI: Not configured — {_WHY_NOT}"

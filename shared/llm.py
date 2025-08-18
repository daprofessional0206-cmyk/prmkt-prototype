# shared/llm.py — LLM wrapper + offline fallbacks
from __future__ import annotations
import streamlit as st
from typing import Optional

_MODEL = "gpt-4o-mini"

def is_openai_ready() -> bool:
    try:
        return bool(st.secrets.get("OPENAI_API_KEY"))
    except Exception:
        return False

def llm_copy(prompt: str, temperature: float = 0.6, max_tokens: int = 900) -> str:
    if not is_openai_ready():
        raise RuntimeError("OpenAI not configured")
    from openai import OpenAI
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    resp = client.chat.completions.create(
        model=_MODEL,
        messages=[{"role":"system","content":"You are a helpful marketing copywriter."},
                  {"role":"user","content":prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (resp.choices[0].message.content or "").strip()

# offline fallbacks
def offline_press_release(topic: str, bullets: list[str], cta: str) -> str:
    bullets_md = "\n".join(f"- {b}" for b in bullets) if bullets else "- (add bullets)"
    return f"FOR IMMEDIATE RELEASE\n\n{topic}\n\nKey points:\n{bullets_md}\n\n{cta}\n"

def offline_generic_copy(topic: str, bullets: list[str], cta: str) -> str:
    bullets_md = "\n".join(f"• {b}" for b in bullets) if bullets else "• Add bullets"
    return f"{topic}\n\n{bullets_md}\n\nNext step: {cta}"

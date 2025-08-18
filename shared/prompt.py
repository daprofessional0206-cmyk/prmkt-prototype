# shared/prompts.py — prompt builders
from __future__ import annotations
from .types import ContentBrief, Company

SYSTEM_PROMPT = """You are an expert PR & Marketing copywriter..."""

def make_prompt(br: ContentBrief, co: Company) -> str:
    bullets = "\n".join(f"- {b}" for b in br.bullets) if br.bullets else "(no bullets)"
    rules = br.brand_rules.strip() or "(none)"
    return f"""
Generate {br.variants} distinct variant(s) of a {br.length.lower()} {br.content_type.lower()}.

Language: {br.language}. Audience: {br.audience}. Tone: {br.tone}.
Company: {co.name} ({co.industry}, size: {co.size}).
Topic / Offer: {br.topic}

Key points:
{bullets}

Call to action: {br.cta}

Brand rules:
{rules}
""".strip()

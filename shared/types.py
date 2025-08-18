from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class Company:
    name: str
    industry: str
    size: str
    goals: str

    def asdict(self):
        return asdict(self)

@dataclass
class ContentBrief:
    content_type: str
    tone: str
    length: str
    platform: str
    audience: str
    cta: str
    topic: str
    bullets: List[str]
    language: str = "English"
    variants: int = 1
    brand_rules: str = ""

    @staticmethod
    def defaults() -> "ContentBrief":
        return ContentBrief(
            content_type="Press Release",
            tone="Neutral",
            length="Short",
            platform="Generic",
            audience="Decision-makers",
            cta="Book a demo",
            topic="Launch of Acme RoboHub 2.0",
            bullets=["2× faster setup", "SOC 2 Type II", "Save 30% cost"],
            language="English",
            variants=1,
            brand_rules="",
        )

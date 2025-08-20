from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass
class Company:
    name: str = ""
    industry: str = ""
    size: str = ""
    goals: str = ""
    brand_rules: str = ""

    def asdict(self):
        return asdict(self)

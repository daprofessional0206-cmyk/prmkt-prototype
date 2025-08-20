# shared/__init__.py
"""
Re-export common submodules so pages can do:
    from shared import state, ui
and it will work reliably.
"""

# Core modules
from . import state       # noqa: F401
from . import history     # noqa: F401
from . import llm         # noqa: F401
from . import ui          # noqa: F401

# Your data helper was renamed to datasets.py — export it as `data`
try:
    from . import datasets as data  # noqa: F401
except Exception:
    # If a different name exists, fall back silently
    try:
        from . import data  # type: ignore  # noqa: F401
    except Exception:
        pass

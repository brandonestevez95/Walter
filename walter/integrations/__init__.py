"""
Walter integrations package
"""

from . import gitbook
from . import llm

try:
    from . import agol
    HAS_AGOL = True
except ImportError:
    HAS_AGOL = False

__all__ = ["gitbook", "llm"]
if HAS_AGOL:
    __all__.append("agol") 
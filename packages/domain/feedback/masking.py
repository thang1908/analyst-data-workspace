"""Pure P0 masking for the non-privileged feedback boundary."""
from __future__ import annotations

import re

_EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_PHONE_PATTERN = re.compile(r"(?<!\d)(?:\+?84|0)\d{8,10}(?!\d)")


def mask_pii(content_raw: str) -> str:
    """Return display-safe content without retaining raw PII in item text."""
    without_email = _EMAIL_PATTERN.sub("[EMAIL]", content_raw)
    return _PHONE_PATTERN.sub("[PHONE]", without_email)

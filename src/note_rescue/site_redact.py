from __future__ import annotations

import re

from .privacy import EMAIL_PATTERN, PID_PATTERN

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"
)
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def redact_text(text: str, replacement: str = "[REDACTED]") -> str:
    text = EMAIL_PATTERN.sub(replacement, text)
    text = PID_PATTERN.sub(replacement, text)
    text = PHONE_PATTERN.sub(replacement, text)
    text = SSN_PATTERN.sub(replacement, text)
    return text


def scan_for_leaks(text: str) -> list[str]:
    issues = []
    if EMAIL_PATTERN.search(text):
        issues.append("email address")
    if PID_PATTERN.search(text):
        issues.append("UCSD PID pattern")
    if PHONE_PATTERN.search(text):
        issues.append("phone number")
    if SSN_PATTERN.search(text):
        issues.append("SSN-like pattern")
    return issues

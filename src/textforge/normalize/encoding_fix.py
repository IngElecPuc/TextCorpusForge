from __future__ import annotations

try:
    from ftfy import fix_text
except Exception:  # pragma: no cover
    fix_text = None


def fix_recoverable_encoding(text: str) -> str:
    if fix_text is None:
        return text
    return fix_text(text)

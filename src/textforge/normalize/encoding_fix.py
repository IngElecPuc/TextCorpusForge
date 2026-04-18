from __future__ import annotations

try:
    from ftfy import fix_text
except ImportError:  # pragma: no cover
    def fix_text(text: str) -> str:
        return text


def fix_recoverable_encoding(text: str) -> str:
    return fix_text(text)

from __future__ import annotations

import re


_INLINE_RE = re.compile(r"[ \t\u00A0]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\u00A0", " ")
    lines = []
    for line in text.split("\n"):
        line = _INLINE_RE.sub(" ", line).strip()
        lines.append(line)
    text = "\n".join(lines)
    text = _MULTI_NL_RE.sub("\n\n", text)
    return text.strip()


def normalize_segment_line(text: str) -> str:
    return _INLINE_RE.sub(" ", text.replace("\u00A0", " ")).strip()

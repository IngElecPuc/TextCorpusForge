from __future__ import annotations


def strip_protocol_markers(text: str) -> str:
    return text.replace("<<", "").replace(">>", "")

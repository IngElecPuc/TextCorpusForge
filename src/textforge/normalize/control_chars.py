from __future__ import annotations


def remove_control_characters(text: str) -> str:
    allowed = {"\n", "\t", "\r"}
    return "".join(ch for ch in text if ch.isprintable() or ch in allowed)

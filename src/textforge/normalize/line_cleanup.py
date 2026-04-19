from __future__ import annotations

from textforge.normalize.control_chars import remove_control_characters
from textforge.normalize.encoding_fix import fix_recoverable_encoding
from textforge.normalize.unicode_norm import normalize_unicode
from textforge.normalize.whitespace import normalize_segment_line


def canonicalize_segment(text: str) -> str:
    text = fix_recoverable_encoding(text)
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = normalize_segment_line(text)
    return text

from __future__ import annotations

from dataclasses import dataclass, field

from textforge.schemas.common import BaseRecord


@dataclass(slots=True)
class SegmentRecord(BaseRecord):
    segment_id: str = ""
    lang: str = ""
    text_raw: str = ""
    text_norm: str = ""
    sequence_index: int = 0
    segment_key: str = ""
    segment_key_numeric: int | None = None
    speaker: str | None = None
    is_dialogue: bool = False
    can_concat_left: bool = True
    can_concat_right: bool = True
    casing_profile: str = "mixed"
    num_chars: int = 0
    num_words: int = 0
    quality_flags: list[str] = field(default_factory=list)

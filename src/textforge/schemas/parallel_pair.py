from __future__ import annotations

from dataclasses import dataclass, field

from textforge.schemas.common import BaseRecord


@dataclass(slots=True)
class ParallelPairRecord(BaseRecord):
    pair_id: str = ""
    pair_index: int = 0
    src_lang: str = ""
    tgt_lang: str = ""
    src_text_raw: str = ""
    tgt_text_raw: str = ""
    src_text_norm: str = ""
    tgt_text_norm: str = ""
    src_segment_keys: list[str] = field(default_factory=list)
    tgt_segment_keys: list[str] = field(default_factory=list)
    src_sequence_indices: list[int] = field(default_factory=list)
    tgt_sequence_indices: list[int] = field(default_factory=list)
    alignment_type: str = ""
    src_words: int = 0
    tgt_words: int = 0
    length_ratio: float = 0.0
    quality_flags: list[str] = field(default_factory=list)

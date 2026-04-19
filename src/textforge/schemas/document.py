from __future__ import annotations

from dataclasses import dataclass

from textforge.schemas.common import BaseRecord


@dataclass(slots=True)
class DocumentRecord(BaseRecord):
    document_id: str = ""
    src_lang: str | None = None
    tgt_lang: str | None = None
    split_hint: str = "train"
    is_parallel: bool = False
    segment_count_src: int = 0
    segment_count_tgt: int = 0
    pair_count: int = 0
    total_chars_src: int = 0
    total_chars_tgt: int = 0
    total_words_src: int = 0
    total_words_tgt: int = 0

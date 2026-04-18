from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from textforge.schemas.common import BaseRecord


@dataclass(slots=True)
class ParallelPairRecord(BaseRecord):
    pair_id: str = ""
    src_lang: str = ""
    tgt_lang: str = ""
    src_text_raw: str = ""
    tgt_text_raw: str = ""
    src_text_norm: str = ""
    tgt_text_norm: str = ""
    src_words: int = 0
    tgt_words: int = 0
    length_ratio: float = 0.0
    quality_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

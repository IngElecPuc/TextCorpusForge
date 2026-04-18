from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from textforge.schemas.common import BaseRecord


@dataclass(slots=True)
class DocumentRecord(BaseRecord):
    doc_id: str = ""
    lang: str = ""
    text_raw: str = ""
    text_norm: str = ""
    num_chars: int = 0
    num_words: int = 0
    quality_flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

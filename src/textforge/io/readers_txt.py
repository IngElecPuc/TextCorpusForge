from __future__ import annotations

from pathlib import Path
from typing import Iterator

from textforge.normalize.encoding_fix import fix_recoverable_encoding
from textforge.normalize.unicode_norm import normalize_unicode
from textforge.normalize.whitespace import normalize_whitespace
from textforge.normalize.control_chars import remove_control_characters
from textforge.schemas.document import DocumentRecord
from textforge.utils.hashing import stable_hash


def iter_txt_documents(root: str | Path, source: str, domain: str, lang: str = "") -> Iterator[DocumentRecord]:
    root = Path(root)
    for path in root.rglob("*.txt"):
        raw = path.read_text(encoding="utf-8", errors="replace")
        norm = canonicalize_text(raw)
        yield DocumentRecord(
            doc_id=stable_hash(f"{source}:{path}"),
            source=source,
            domain=domain,
            origin_path=str(path),
            lang=lang,
            text_raw=raw,
            text_norm=norm,
            num_chars=len(norm),
            num_words=len(norm.split()),
        )


def canonicalize_text(text: str) -> str:
    text = fix_recoverable_encoding(text)
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    text = normalize_whitespace(text)
    return text

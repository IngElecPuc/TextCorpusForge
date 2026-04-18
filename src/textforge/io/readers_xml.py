from __future__ import annotations

from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree as ET

from textforge.io.readers_txt import canonicalize_text
from textforge.schemas.document import DocumentRecord
from textforge.utils.hashing import stable_hash


def iter_xml_documents(root: str | Path, source: str, domain: str, lang: str = "") -> Iterator[DocumentRecord]:
    root = Path(root)
    for path in root.rglob("*.xml"):
        try:
            tree = ET.parse(path)
            raw = " ".join(elem.text.strip() for elem in tree.iter() if elem.text and elem.text.strip())
        except ET.ParseError:
            continue

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

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from textforge.normalize.line_cleanup import canonicalize_segment


def iter_text_lines(path: str | Path) -> Iterator[tuple[int, str, str]]:
    path = Path(path)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for idx, raw in enumerate(handle, start=1):
            raw = raw.rstrip("\n")
            norm = canonicalize_segment(raw)
            yield idx, raw, norm


def load_text_lines(path: str | Path) -> list[tuple[int, str, str]]:
    return list(iter_text_lines(path))

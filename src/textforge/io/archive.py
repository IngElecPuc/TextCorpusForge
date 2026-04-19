from __future__ import annotations

import gzip
from pathlib import Path


def read_text_maybe_gzip(path: str | Path) -> str:
    path = Path(path)
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as handle:
            return handle.read()
    return path.read_text(encoding="utf-8", errors="replace")

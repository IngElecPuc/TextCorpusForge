from __future__ import annotations

from pathlib import Path
from typing import Iterator


def iter_ids_rows(path: str | Path) -> Iterator[dict]:
    path = Path(path)
    with path.open('r', encoding='utf-8', errors='replace') as handle:
        for row_idx, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            parts = line.split('	')
            if len(parts) < 4:
                continue
            src_doc, tgt_doc, src_keys_raw, tgt_keys_raw = parts[:4]
            yield {
                'row_index': row_idx,
                'src_doc': src_doc,
                'tgt_doc': tgt_doc,
                'src_keys': [tok for tok in src_keys_raw.split() if tok],
                'tgt_keys': [tok for tok in tgt_keys_raw.split() if tok],
            }

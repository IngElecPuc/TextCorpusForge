from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from textforge.io.readers_txt import canonicalize_text
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.utils.hashing import stable_hash


def iter_tsv_parallel(
    root: str | Path,
    source: str,
    domain: str,
    src_lang: str,
    tgt_lang: str,
    src_col: int = 0,
    tgt_col: int = 1,
    delimiter: str = "\t",
) -> Iterator[ParallelPairRecord]:
    root = Path(root)
    for path in root.rglob("*.tsv"):
        with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            for row_idx, row in enumerate(reader):
                if max(src_col, tgt_col) >= len(row):
                    continue
                src_raw = row[src_col]
                tgt_raw = row[tgt_col]
                src_norm = canonicalize_text(src_raw)
                tgt_norm = canonicalize_text(tgt_raw)
                ratio = _length_ratio(src_norm, tgt_norm)
                yield ParallelPairRecord(
                    pair_id=stable_hash(f"{source}:{path}:{row_idx}"),
                    source=source,
                    domain=domain,
                    origin_path=str(path),
                    src_lang=src_lang,
                    tgt_lang=tgt_lang,
                    src_text_raw=src_raw,
                    tgt_text_raw=tgt_raw,
                    src_text_norm=src_norm,
                    tgt_text_norm=tgt_norm,
                    src_words=len(src_norm.split()),
                    tgt_words=len(tgt_norm.split()),
                    length_ratio=ratio,
                )


def _length_ratio(src: str, tgt: str) -> float:
    src_len = max(1, len(src.split()))
    tgt_len = max(1, len(tgt.split()))
    return max(src_len, tgt_len) / min(src_len, tgt_len)

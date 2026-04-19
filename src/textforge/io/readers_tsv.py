from __future__ import annotations

import csv
from pathlib import Path

from textforge.normalize.line_cleanup import canonicalize_segment
from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord
from textforge.utils.hashing import stable_hash


def build_tsv_records(root: str | Path, dataset_name: str, domain: str, src_lang: str, tgt_lang: str, src_col: int = 0, tgt_col: int = 1) -> tuple[list[SegmentRecord], list[ParallelPairRecord], list[DocumentRecord]]:
    root = Path(root)
    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []
    documents: list[DocumentRecord] = []

    for path in root.rglob('*.tsv'):
        doc_group_id = stable_hash(f"{dataset_name}:{path}")
        pair_count = 0
        with path.open('r', encoding='utf-8', errors='replace', newline='') as handle:
            reader = csv.reader(handle, delimiter='	')
            for row_idx, row in enumerate(reader, start=1):
                if max(src_col, tgt_col) >= len(row):
                    continue
                src_raw = row[src_col]
                tgt_raw = row[tgt_col]
                src_norm = canonicalize_segment(src_raw)
                tgt_norm = canonicalize_segment(tgt_raw)
                src_key = f"row:{row_idx}:src"
                tgt_key = f"row:{row_idx}:tgt"
                segments.append(SegmentRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, segment_id=stable_hash(f"{path}:{src_key}"), lang=src_lang, text_raw=src_raw, text_norm=src_norm, sequence_index=row_idx, segment_key=src_key, num_chars=len(src_norm), num_words=len(src_norm.split())))
                segments.append(SegmentRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, segment_id=stable_hash(f"{path}:{tgt_key}"), lang=tgt_lang, text_raw=tgt_raw, text_norm=tgt_norm, sequence_index=row_idx, segment_key=tgt_key, num_chars=len(tgt_norm), num_words=len(tgt_norm.split())))
                pairs.append(ParallelPairRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, pair_id=stable_hash(f"{path}:pair:{row_idx}"), pair_index=row_idx, src_lang=src_lang, tgt_lang=tgt_lang, src_text_raw=src_raw, tgt_text_raw=tgt_raw, src_text_norm=src_norm, tgt_text_norm=tgt_norm, src_segment_keys=[src_key], tgt_segment_keys=[tgt_key], src_sequence_indices=[row_idx], tgt_sequence_indices=[row_idx], alignment_type='tsv_explicit', src_words=len(src_norm.split()), tgt_words=len(tgt_norm.split()), length_ratio=_length_ratio(src_norm, tgt_norm)))
                pair_count += 1

        documents.append(DocumentRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, document_id=doc_group_id, src_lang=src_lang, tgt_lang=tgt_lang, is_parallel=True, segment_count_src=pair_count, segment_count_tgt=pair_count, pair_count=pair_count, total_chars_src=sum(s.num_chars for s in segments if s.doc_group_id == doc_group_id and s.lang == src_lang), total_chars_tgt=sum(s.num_chars for s in segments if s.doc_group_id == doc_group_id and s.lang == tgt_lang), total_words_src=sum(s.num_words for s in segments if s.doc_group_id == doc_group_id and s.lang == src_lang), total_words_tgt=sum(s.num_words for s in segments if s.doc_group_id == doc_group_id and s.lang == tgt_lang)))

    return segments, pairs, documents


def _length_ratio(src: str, tgt: str) -> float:
    src_len = max(1, len(src.split()))
    tgt_len = max(1, len(tgt.split()))
    return max(src_len, tgt_len) / min(src_len, tgt_len)

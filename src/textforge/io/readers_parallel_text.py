from __future__ import annotations

from pathlib import Path

from textforge.io.readers_txt import load_text_lines
from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord
from textforge.utils.hashing import stable_hash


def build_unaligned_parallel_streams(
    root: str | Path,
    dataset_name: str,
    domain: str,
    src_lang: str,
    tgt_lang: str,
    src_path: str | Path,
    tgt_path: str | Path,
    group_name: str,
    is_dialogue: bool = False,
) -> tuple[list[SegmentRecord], list[ParallelPairRecord], list[DocumentRecord]]:
    src_path = Path(src_path)
    tgt_path = Path(tgt_path)
    doc_group_id = stable_hash(f"{dataset_name}:{group_name}:{src_path}:{tgt_path}")

    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []

    src_lines = load_text_lines(src_path)
    tgt_lines = load_text_lines(tgt_path)

    for seq_idx, (line_idx, raw, norm) in enumerate(src_lines, start=1):
        segments.append(
            SegmentRecord(
                dataset_name=dataset_name,
                domain=domain,
                origin_path=str(src_path),
                doc_group_id=doc_group_id,
                segment_id=stable_hash(f"{dataset_name}:src:{src_path}:{line_idx}"),
                lang=src_lang,
                text_raw=raw,
                text_norm=norm,
                sequence_index=seq_idx,
                segment_key=str(line_idx),
                segment_key_numeric=line_idx,
                is_dialogue=is_dialogue,
                can_concat_left=not is_dialogue,
                can_concat_right=not is_dialogue,
                casing_profile=_casing_profile(norm),
                num_chars=len(norm),
                num_words=len(norm.split()),
                quality_flags=["unaligned_stream"],
            )
        )

    for seq_idx, (line_idx, raw, norm) in enumerate(tgt_lines, start=1):
        segments.append(
            SegmentRecord(
                dataset_name=dataset_name,
                domain=domain,
                origin_path=str(tgt_path),
                doc_group_id=doc_group_id,
                segment_id=stable_hash(f"{dataset_name}:tgt:{tgt_path}:{line_idx}"),
                lang=tgt_lang,
                text_raw=raw,
                text_norm=norm,
                sequence_index=seq_idx,
                segment_key=str(line_idx),
                segment_key_numeric=line_idx,
                is_dialogue=is_dialogue,
                can_concat_left=not is_dialogue,
                can_concat_right=not is_dialogue,
                casing_profile=_casing_profile(norm),
                num_chars=len(norm),
                num_words=len(norm.split()),
                quality_flags=["unaligned_stream"],
            )
        )

    documents = [
        DocumentRecord(
            dataset_name=dataset_name,
            domain=domain,
            origin_path=f"{src_path}|{tgt_path}",
            doc_group_id=doc_group_id,
            document_id=doc_group_id,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            is_parallel=True,
            segment_count_src=len(src_lines),
            segment_count_tgt=len(tgt_lines),
            pair_count=0,
            total_chars_src=sum(len(norm) for _, _, norm in src_lines),
            total_chars_tgt=sum(len(norm) for _, _, norm in tgt_lines),
            total_words_src=sum(len(norm.split()) for _, _, norm in src_lines),
            total_words_tgt=sum(len(norm.split()) for _, _, norm in tgt_lines),
        )
    ]
    return segments, pairs, documents


def _casing_profile(text: str) -> str:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return "empty"
    if all(ch.isupper() for ch in letters):
        return "upper"
    if all(ch.islower() for ch in letters):
        return "lower"
    return "mixed"

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from textforge.align.monotonic import TextUnit, monotonic_align
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
    max_segments: int = 0,
) -> tuple[list[SegmentRecord], list[ParallelPairRecord], list[DocumentRecord]]:
    src_path = Path(src_path)
    tgt_path = Path(tgt_path)
    doc_group_id = stable_hash(f"{dataset_name}:{group_name}:{src_path}:{tgt_path}")

    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []

    src_lines = load_text_lines(src_path)
    tgt_lines = load_text_lines(tgt_path)
    if max_segments > 0:
        src_lines = src_lines[:max_segments]
        tgt_lines = tgt_lines[:max_segments]

    for seq_idx, (line_idx, raw, norm) in enumerate(src_lines, start=1):
        if not norm:
            continue
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
                metadata={"line_numbers": [line_idx], "block_index": 0},
            )
        )

    for seq_idx, (line_idx, raw, norm) in enumerate(tgt_lines, start=1):
        if not norm:
            continue
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
                metadata={"line_numbers": [line_idx], "block_index": 0},
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
            segment_count_src=sum(1 for _, _, norm in src_lines if norm),
            segment_count_tgt=sum(1 for _, _, norm in tgt_lines if norm),
            pair_count=0,
            total_chars_src=sum(len(norm) for _, _, norm in src_lines),
            total_chars_tgt=sum(len(norm) for _, _, norm in tgt_lines),
            total_words_src=sum(len(norm.split()) for _, _, norm in src_lines),
            total_words_tgt=sum(len(norm.split()) for _, _, norm in tgt_lines),
            metadata={"alignment_strategy": "none", "is_alignment_trusted": False},
        )
    ]
    return segments, pairs, documents


def build_monotonic_parallel_records(
    *,
    dataset_name: str,
    domain: str,
    src_lang: str,
    tgt_lang: str,
    src_path: str | Path,
    tgt_path: str | Path,
    group_name: str,
    strategy_name: str,
    is_dialogue: bool,
    allow_skip: bool,
    block_mode: str,
    trusted_alignment: bool,
    max_pairs: int = 0,
    max_tokens_approx: int = 0,
) -> tuple[list[SegmentRecord], list[ParallelPairRecord], list[DocumentRecord]]:
    src_path = Path(src_path)
    tgt_path = Path(tgt_path)
    src_rows = load_text_lines(src_path)
    tgt_rows = load_text_lines(tgt_path)

    src_blocks = _split_rows_into_blocks(src_rows, mode=block_mode)
    tgt_blocks = _split_rows_into_blocks(tgt_rows, mode=block_mode)
    block_count = max(len(src_blocks), len(tgt_blocks))

    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []
    documents: list[DocumentRecord] = []

    emitted_pairs = 0
    emitted_tokens = 0
    for block_index in range(block_count):
        src_block = src_blocks[block_index] if block_index < len(src_blocks) else []
        tgt_block = tgt_blocks[block_index] if block_index < len(tgt_blocks) else []
        if not src_block and not tgt_block:
            continue

        group_suffix = f"{group_name}:block:{block_index + 1}"
        doc_group_id = stable_hash(f"{dataset_name}:{group_suffix}:{src_path}:{tgt_path}")
        src_units = _rows_to_units(src_block)
        tgt_units = _rows_to_units(tgt_block)

        seen_segment_ids: set[str] = set()
        for unit in src_units:
            segment = _segment_from_unit(dataset_name, domain, str(src_path), doc_group_id, src_lang, unit, is_dialogue, block_index)
            if segment.segment_id not in seen_segment_ids:
                segments.append(segment)
                seen_segment_ids.add(segment.segment_id)
        for unit in tgt_units:
            segment = _segment_from_unit(dataset_name, domain, str(tgt_path), doc_group_id, tgt_lang, unit, is_dialogue, block_index)
            if segment.segment_id not in seen_segment_ids:
                segments.append(segment)
                seen_segment_ids.add(segment.segment_id)

        candidates = monotonic_align(
            src_units,
            tgt_units,
            max_merge_src=2,
            max_merge_tgt=2,
            skip_penalty=1.35 if allow_skip else 3.5,
            mismatch_penalty=4.0 if is_dialogue else 5.25,
            alignment_type=strategy_name,
        )

        block_pairs = _pairs_from_candidates(
            dataset_name=dataset_name,
            domain=domain,
            origin_path=str(src_path) + "|" + str(tgt_path),
            doc_group_id=doc_group_id,
            src_lang=src_lang,
            tgt_lang=tgt_lang,
            src_units=src_units,
            tgt_units=tgt_units,
            candidates=candidates,
            trusted_alignment=trusted_alignment,
        )
        if max_pairs > 0:
            remaining = max_pairs - emitted_pairs
            if remaining <= 0:
                break
            block_pairs = block_pairs[:remaining]
        if max_tokens_approx > 0:
            kept = []
            for pair in block_pairs:
                pair_tokens = max(1, int((len(pair.src_text_norm) + len(pair.tgt_text_norm)) / 4))
                if kept and emitted_tokens + pair_tokens > max_tokens_approx:
                    break
                kept.append(pair)
                emitted_tokens += pair_tokens
            block_pairs = kept
        pairs.extend(block_pairs)
        emitted_pairs += len(block_pairs)
        if block_pairs:
            documents.append(
            DocumentRecord(
                dataset_name=dataset_name,
                domain=domain,
                origin_path=f"{src_path}|{tgt_path}",
                doc_group_id=doc_group_id,
                document_id=doc_group_id,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                is_parallel=True,
                segment_count_src=len(src_units),
                segment_count_tgt=len(tgt_units),
                pair_count=len(block_pairs),
                total_chars_src=sum(len(unit.text_norm) for unit in src_units),
                total_chars_tgt=sum(len(unit.text_norm) for unit in tgt_units),
                total_words_src=sum(len(unit.text_norm.split()) for unit in src_units),
                total_words_tgt=sum(len(unit.text_norm.split()) for unit in tgt_units),
                metadata={
                    "alignment_strategy": strategy_name,
                    "block_index": block_index,
                    "is_alignment_trusted": trusted_alignment,
                    "allow_skip": allow_skip,
                },
            )
        )
        if (max_pairs > 0 and emitted_pairs >= max_pairs) or (max_tokens_approx > 0 and emitted_tokens >= max_tokens_approx):
            break

    allowed = {p.doc_group_id for p in pairs}
    segments = [s for s in segments if s.doc_group_id in allowed] if allowed else []
    documents = [d for d in documents if d.doc_group_id in allowed] if allowed else []
    return segments, pairs, documents


def _rows_to_units(rows: list[tuple[int, str, str]]) -> list[TextUnit]:
    units: list[TextUnit] = []
    for index, (line_number, raw, norm) in enumerate(rows):
        if not norm:
            continue
        units.append(
            TextUnit(
                index=index,
                text_raw=raw,
                text_norm=norm,
                sequence_index=index + 1,
                line_numbers=(line_number,),
            )
        )
    return units


def _split_rows_into_blocks(rows: list[tuple[int, str, str]], *, mode: str) -> list[list[tuple[int, str, str]]]:
    if mode == "single_stream":
        return [[row for row in rows if row[2]]]

    blocks: list[list[tuple[int, str, str]]] = []
    current: list[tuple[int, str, str]] = []
    for row in rows:
        if not row[2]:
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(row)
    if current:
        blocks.append(current)
    return blocks


def _pairs_from_candidates(
    *,
    dataset_name: str,
    domain: str,
    origin_path: str,
    doc_group_id: str,
    src_lang: str,
    tgt_lang: str,
    src_units: list[TextUnit],
    tgt_units: list[TextUnit],
    candidates,
    trusted_alignment: bool,
) -> list[ParallelPairRecord]:
    pairs: list[ParallelPairRecord] = []
    for pair_index, candidate in enumerate(candidates):
        src_slice = [src_units[i] for i in candidate.src_indices]
        tgt_slice = [tgt_units[i] for i in candidate.tgt_indices]
        src_text_raw = "\n".join(unit.text_raw for unit in src_slice)
        tgt_text_raw = "\n".join(unit.text_raw for unit in tgt_slice)
        src_text_norm = " ".join(unit.text_norm for unit in src_slice).strip()
        tgt_text_norm = " ".join(unit.text_norm for unit in tgt_slice).strip()
        if not src_text_norm and not tgt_text_norm:
            continue
        quality_flags = list(candidate.quality_flags)
        if not trusted_alignment:
            quality_flags.append("provisional_alignment")
        if not src_slice or not tgt_slice:
            quality_flags.append("drop_candidate")
        pairs.append(
            ParallelPairRecord(
                dataset_name=dataset_name,
                domain=domain,
                origin_path=origin_path,
                doc_group_id=doc_group_id,
                pair_id=stable_hash(f"{dataset_name}:{doc_group_id}:pair:{pair_index}"),
                pair_index=pair_index,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                src_text_raw=src_text_raw,
                tgt_text_raw=tgt_text_raw,
                src_text_norm=src_text_norm,
                tgt_text_norm=tgt_text_norm,
                src_segment_keys=["-".join(str(n) for n in unit.line_numbers) for unit in src_slice],
                tgt_segment_keys=["-".join(str(n) for n in unit.line_numbers) for unit in tgt_slice],
                src_sequence_indices=[unit.sequence_index for unit in src_slice],
                tgt_sequence_indices=[unit.sequence_index for unit in tgt_slice],
                alignment_type=candidate.alignment_type,
                src_words=len(src_text_norm.split()),
                tgt_words=len(tgt_text_norm.split()),
                length_ratio=_length_ratio(src_text_norm, tgt_text_norm),
                quality_flags=quality_flags,
                metadata={
                    "alignment_score": round(candidate.score, 4),
                    "is_alignment_trusted": trusted_alignment,
                    "src_line_numbers": [n for unit in src_slice for n in unit.line_numbers],
                    "tgt_line_numbers": [n for unit in tgt_slice for n in unit.line_numbers],
                },
            )
        )
    return [pair for pair in pairs if "drop_candidate" not in pair.quality_flags]


def _segment_from_unit(
    dataset_name: str,
    domain: str,
    origin_path: str,
    doc_group_id: str,
    lang: str,
    unit: TextUnit,
    is_dialogue: bool,
    block_index: int,
) -> SegmentRecord:
    return SegmentRecord(
        dataset_name=dataset_name,
        domain=domain,
        origin_path=origin_path,
        doc_group_id=doc_group_id,
        segment_id=stable_hash(f"{dataset_name}:{doc_group_id}:{lang}:{unit.line_numbers}"),
        lang=lang,
        text_raw=unit.text_raw,
        text_norm=unit.text_norm,
        sequence_index=unit.sequence_index,
        segment_key="-".join(str(n) for n in unit.line_numbers),
        segment_key_numeric=unit.line_numbers[0] if len(unit.line_numbers) == 1 else None,
        is_dialogue=is_dialogue,
        can_concat_left=not is_dialogue,
        can_concat_right=not is_dialogue,
        casing_profile=_casing_profile(unit.text_norm),
        num_chars=len(unit.text_norm),
        num_words=len(unit.text_norm.split()),
        quality_flags=[],
        metadata={"line_numbers": list(unit.line_numbers), "block_index": block_index},
    )


def _length_ratio(src_text: str, tgt_text: str) -> float:
    src_words = max(len(src_text.split()), 1)
    tgt_words = max(len(tgt_text.split()), 1)
    return round(max(src_words / tgt_words, tgt_words / src_words), 4)


def _casing_profile(text: str) -> str:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return "empty"
    if all(ch.isupper() for ch in letters):
        return "upper"
    if all(ch.islower() for ch in letters):
        return "lower"
    return "mixed"

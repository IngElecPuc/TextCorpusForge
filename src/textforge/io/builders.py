from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from textforge.io.readers_ids import iter_ids_rows
from textforge.io.readers_parallel_text import build_monotonic_parallel_records, build_unaligned_parallel_streams
from textforge.io.readers_tmx import build_tmx_records
from textforge.io.readers_tsv import build_tsv_records
from textforge.io.readers_txt import iter_text_lines
from textforge.io.readers_xml import iter_ces_alignment
from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord
from textforge.utils.hashing import stable_hash
from textforge.utils.paths import resolve_in_root




@dataclass
class BuildResult:
    segments: list[SegmentRecord]
    pairs: list[ParallelPairRecord]
    documents: list[DocumentRecord]
    stop_reason: str = "input_exhausted"
    first_limit_hit: str = "input_exhausted"


def _result(segments, pairs, documents, stop_reason="input_exhausted", first_limit_hit=None) -> BuildResult:
    first_limit_hit = first_limit_hit or stop_reason
    return BuildResult(segments=segments, pairs=pairs, documents=documents, stop_reason=stop_reason, first_limit_hit=first_limit_hit)

def build_dataset_records(dataset_cfg: dict, dataset_root: str | Path, limits: dict[str, Any] | None = None) -> BuildResult:
    dataset_root = Path(dataset_root)
    dataset = dataset_cfg['dataset']
    reader = dataset['reader']
    if reader == 'ces_alignment_xml':
        return _build_from_ces_alignment(dataset, dataset_root, limits)
    if reader == 'ids_sidecar':
        return _build_from_ids_sidecar(dataset, dataset_root, limits)
    if reader == 'parallel_sidecar_plain':
        return _build_from_plain_stream(dataset, dataset_root, limits)
    if reader == 'parallel_sidecar_monotonic':
        return _build_from_monotonic_plain(dataset, dataset_root, limits)
    if reader == 'tmx':
        segs, pairs, docs = build_tmx_records(dataset_root, dataset['name'], dataset['domain'], dataset['src_lang'], dataset['tgt_lang'])
        return _result(segs, pairs, docs)
    if reader == 'tsv_parallel':
        segs, pairs, docs = build_tsv_records(dataset_root, dataset['name'], dataset['domain'], dataset['src_lang'], dataset['tgt_lang'])
        return _result(segs, pairs, docs)
    raise ValueError(f"Reader no soportado: {reader}")


def _build_from_ces_alignment(dataset: dict, dataset_root: Path, limits: dict[str, Any] | None = None) -> BuildResult:
    src_path = _require(resolve_in_root(dataset_root, dataset['files']['src_text']))
    tgt_path = _require(resolve_in_root(dataset_root, dataset['files']['tgt_text']))
    alignment_path = _require(resolve_in_root(dataset_root, dataset['files']['alignment']))

    max_pairs = int((limits or {}).get('max_pairs', 0) or 0)
    max_tokens = int((limits or {}).get('max_tokens_approx', 0) or 0)
    src_iter = iter_text_lines(src_path)
    tgt_iter = iter_text_lines(tgt_path)
    src_cache: dict[str, tuple[int, str, str]] = {}
    tgt_cache: dict[str, tuple[int, str, str]] = {}
    selected_rows: list[dict[str, Any]] = []
    emitted_tokens = 0
    stop_reason = "input_exhausted"
    pair_count = 0
    stop_reason = "input_exhausted"

    for row in iter_ces_alignment(alignment_path):
        _ensure_keys_loaded(src_iter, src_cache, row['src_keys'])
        _ensure_keys_loaded(tgt_iter, tgt_cache, row['tgt_keys'])
        src_norm = ' '.join((_lookup_key(src_cache, k) or (None, '', ''))[2] for k in row['src_keys']).strip()
        tgt_norm = ' '.join((_lookup_key(tgt_cache, k) or (None, '', ''))[2] for k in row['tgt_keys']).strip()
        pair_tokens = _estimate_pair_tokens(src_norm, tgt_norm)
        if max_tokens > 0 and selected_rows and emitted_tokens + pair_tokens > max_tokens:
            stop_reason = "max_tokens_approx"
            break
        selected_rows.append(row)
        emitted_tokens += pair_tokens
        pair_count += 1
        if max_pairs > 0 and pair_count >= max_pairs:
            stop_reason = "max_pairs"
            break

    if not selected_rows:
        return _result([], [], [], stop_reason=stop_reason)

    group_buckets: dict[str, list[dict]] = defaultdict(list)
    for row in selected_rows:
        group_key = f"{row['from_doc']}|{row['to_doc']}" if dataset.get('structural', {}).get('group_from_alignment_docs', True) else 'global'
        group_buckets[group_key].append(row)

    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []
    documents: list[DocumentRecord] = []
    seen_segments: set[tuple[str, str, str]] = set()

    for group_name, group_rows in group_buckets.items():
        doc_group_id = stable_hash(f"{dataset['name']}:{group_name}")
        group_pair_count = 0
        for row in group_rows:
            src_texts, tgt_texts = [], []
            src_keys, tgt_keys = [], []
            src_seq_indices, tgt_seq_indices = [], []
            for key in row['src_keys']:
                lookup = _lookup_key(src_cache, key)
                seq, raw, norm = lookup or (None, '', '')
                src_texts.append(norm)
                src_keys.append(key)
                if seq is not None:
                    src_seq_indices.append(seq)
                    cache_key = (doc_group_id, dataset['src_lang'], key)
                    if cache_key not in seen_segments:
                        seen_segments.add(cache_key)
                        segments.append(_segment_from_line(dataset, str(src_path), doc_group_id, dataset['src_lang'], key, seq, raw, norm))
            for key in row['tgt_keys']:
                lookup = _lookup_key(tgt_cache, key)
                seq, raw, norm = lookup or (None, '', '')
                tgt_texts.append(norm)
                tgt_keys.append(key)
                if seq is not None:
                    tgt_seq_indices.append(seq)
                    cache_key = (doc_group_id, dataset['tgt_lang'], key)
                    if cache_key not in seen_segments:
                        seen_segments.add(cache_key)
                        segments.append(_segment_from_line(dataset, str(tgt_path), doc_group_id, dataset['tgt_lang'], key, seq, raw, norm))

            src_text_norm = ' '.join(t for t in src_texts if t).strip()
            tgt_text_norm = ' '.join(t for t in tgt_texts if t).strip()
            src_text_raw = ' '.join((_lookup_key(src_cache, k) or (None, '', ''))[1] for k in row['src_keys']).strip()
            tgt_text_raw = ' '.join((_lookup_key(tgt_cache, k) or (None, '', ''))[1] for k in row['tgt_keys']).strip()
            quality_flags = []
            if not src_text_norm or not tgt_text_norm:
                quality_flags.append('missing_sidecar_line')
            pairs.append(ParallelPairRecord(
                dataset_name=dataset['name'], domain=dataset['domain'], origin_path=str(alignment_path), doc_group_id=doc_group_id,
                pair_id=stable_hash(f"{dataset['name']}:{doc_group_id}:pair:{group_pair_count}"), pair_index=group_pair_count,
                src_lang=dataset['src_lang'], tgt_lang=dataset['tgt_lang'], src_text_raw=src_text_raw, tgt_text_raw=tgt_text_raw,
                src_text_norm=src_text_norm, tgt_text_norm=tgt_text_norm, src_segment_keys=src_keys, tgt_segment_keys=tgt_keys,
                src_sequence_indices=src_seq_indices, tgt_sequence_indices=tgt_seq_indices, alignment_type='ces_explicit',
                src_words=len(src_text_norm.split()), tgt_words=len(tgt_text_norm.split()), length_ratio=_length_ratio(src_text_norm, tgt_text_norm),
                quality_flags=quality_flags, metadata={'from_doc': row.get('from_doc', ''), 'to_doc': row.get('to_doc', '')},
            ))
            group_pair_count += 1
        documents.append(_document_summary(dataset, doc_group_id, f"{src_path}|{tgt_path}", segments, pairs))
    return _result(segments, pairs, documents, stop_reason=stop_reason)


def _build_from_ids_sidecar(dataset: dict, dataset_root: Path, limits: dict[str, Any] | None = None) -> BuildResult:
    src_path = _require(resolve_in_root(dataset_root, dataset['files']['src_text']))
    tgt_path = _require(resolve_in_root(dataset_root, dataset['files']['tgt_text']))
    ids_path = _require(resolve_in_root(dataset_root, dataset['files']['alignment_ids']))

    max_pairs = int((limits or {}).get('max_pairs', 0) or 0)
    max_tokens = int((limits or {}).get('max_tokens_approx', 0) or 0)
    src_iter = iter_text_lines(src_path)
    tgt_iter = iter_text_lines(tgt_path)
    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []
    documents: list[DocumentRecord] = []
    doc_cache: set[tuple[str, str, str]] = set()
    group_pairs: dict[str, int] = defaultdict(int)
    emitted_tokens = 0
    stop_reason = "input_exhausted"

    for idx_row in iter_ids_rows(ids_path):
        try:
            src_line_idx, src_raw, src_norm = next(src_iter)
            tgt_line_idx, tgt_raw, tgt_norm = next(tgt_iter)
        except StopIteration:
            break
        pair_tokens = _estimate_pair_tokens(src_norm, tgt_norm)
        if max_tokens > 0 and pairs and emitted_tokens + pair_tokens > max_tokens:
            stop_reason = "max_tokens_approx"
            break
        emitted_tokens += pair_tokens
        group_name = f"{idx_row['src_doc']}|{idx_row['tgt_doc']}" if dataset.get('structural', {}).get('group_from_alignment_docs', True) else 'global'
        doc_group_id = stable_hash(f"{dataset['name']}:{group_name}")
        src_key = ' '.join(idx_row['src_keys']) or str(src_line_idx)
        tgt_key = ' '.join(idx_row['tgt_keys']) or str(tgt_line_idx)
        cache_key_src = (doc_group_id, dataset['src_lang'], src_key)
        if cache_key_src not in doc_cache:
            doc_cache.add(cache_key_src)
            segments.append(_segment_from_line(dataset, str(src_path), doc_group_id, dataset['src_lang'], src_key, src_line_idx, src_raw, src_norm))
        cache_key_tgt = (doc_group_id, dataset['tgt_lang'], tgt_key)
        if cache_key_tgt not in doc_cache:
            doc_cache.add(cache_key_tgt)
            segments.append(_segment_from_line(dataset, str(tgt_path), doc_group_id, dataset['tgt_lang'], tgt_key, tgt_line_idx, tgt_raw, tgt_norm))
        pair_index = group_pairs[doc_group_id]
        group_pairs[doc_group_id] += 1
        pairs.append(ParallelPairRecord(
            dataset_name=dataset['name'], domain=dataset['domain'], origin_path=str(ids_path), doc_group_id=doc_group_id,
            pair_id=stable_hash(f"{dataset['name']}:{doc_group_id}:pair:{pair_index}"), pair_index=pair_index,
            src_lang=dataset['src_lang'], tgt_lang=dataset['tgt_lang'], src_text_raw=src_raw, tgt_text_raw=tgt_raw,
            src_text_norm=src_norm, tgt_text_norm=tgt_norm, src_segment_keys=idx_row['src_keys'] or [str(src_line_idx)],
            tgt_segment_keys=idx_row['tgt_keys'] or [str(tgt_line_idx)], src_sequence_indices=[src_line_idx], tgt_sequence_indices=[tgt_line_idx],
            alignment_type='ids_explicit', src_words=len(src_norm.split()), tgt_words=len(tgt_norm.split()), length_ratio=_length_ratio(src_norm, tgt_norm),
            metadata={'src_doc': idx_row['src_doc'], 'tgt_doc': idx_row['tgt_doc']},
        ))
        if max_pairs > 0 and len(pairs) >= max_pairs:
            stop_reason = "max_pairs"
            break
    for doc_group_id in sorted({p.doc_group_id for p in pairs}):
        documents.append(_document_summary(dataset, doc_group_id, f"{src_path}|{tgt_path}", segments, pairs))
    return _result(segments, pairs, documents, stop_reason=stop_reason)


def _build_from_monotonic_plain(dataset: dict, dataset_root: Path, limits: dict[str, Any] | None = None) -> BuildResult:
    src_path = _require(resolve_in_root(dataset_root, dataset['files']['src_text']))
    tgt_path = None
    candidates = dataset['files'].get('tgt_text_candidates')
    if candidates:
        for candidate in candidates:
            maybe = resolve_in_root(dataset_root, candidate)
            if maybe is not None:
                tgt_path = maybe
                break
    else:
        tgt_path = resolve_in_root(dataset_root, dataset['files'].get('tgt_text'))
    tgt_path = _require(tgt_path)
    structural = dataset.get('structural', {})
    segs, pairs, docs = build_monotonic_parallel_records(
        dataset_name=dataset['name'], domain=dataset['domain'], src_lang=dataset['src_lang'], tgt_lang=dataset['tgt_lang'],
        src_path=src_path, tgt_path=tgt_path, group_name=structural.get('group_name', dataset['name']),
        strategy_name=structural.get('alignment_strategy', 'monotonic_windowed'), is_dialogue=bool(structural.get('is_dialogue', False)),
        allow_skip=bool(structural.get('allow_skip', True)), block_mode=structural.get('block_mode', 'blankline_blocks'),
        trusted_alignment=bool(structural.get('is_alignment_trusted', False)), max_pairs=int((limits or {}).get('max_pairs', 0) or 0),
        max_tokens_approx=int((limits or {}).get('max_tokens_approx', 0) or 0),
    )
    return _result(segs, pairs, docs)


def _build_from_plain_stream(dataset: dict, dataset_root: Path, limits: dict[str, Any] | None = None) -> BuildResult:
    src_path = _require(resolve_in_root(dataset_root, dataset['files']['src_text']))
    tgt_path = None
    candidates = dataset['files'].get('tgt_text_candidates')
    if candidates:
        for candidate in candidates:
            maybe = resolve_in_root(dataset_root, candidate)
            if maybe is not None:
                tgt_path = maybe
                break
    else:
        tgt_path = resolve_in_root(dataset_root, dataset['files'].get('tgt_text'))
    tgt_path = _require(tgt_path)
    group_name = dataset.get('structural', {}).get('group_name', dataset['name'])
    is_dialogue = bool(dataset.get('structural', {}).get('is_dialogue', False))
    segs, pairs, docs = build_unaligned_parallel_streams(dataset_root, dataset['name'], dataset['domain'], dataset['src_lang'], dataset['tgt_lang'], src_path, tgt_path, group_name, is_dialogue=is_dialogue, max_segments=int((limits or {}).get('max_segments', 0) or 0))
    return _result(segs, pairs, docs)


def _ensure_keys_loaded(iterator, cache: dict[str, tuple[int, str, str]], keys: Iterable[str]) -> None:
    needed = max((_key_to_line_number(k) for k in keys if _is_numericish(k)), default=0)
    if needed <= 0:
        return
    current_max = max((_key_to_line_number(k) for k in cache.keys()), default=0)
    while current_max < needed:
        try:
            idx, raw, norm = next(iterator)
        except StopIteration:
            break
        cache[str(idx)] = (idx, raw, norm)
        current_max = idx


def _key_to_line_number(key: str) -> int:
    head = key.split(':')[0].split('.')[0].strip()
    try:
        return int(head)
    except ValueError:
        digits = ''.join(ch for ch in head if ch.isdigit())
        return int(digits) if digits else 0


def _lookup_key(index: dict[str, tuple[int, str, str]], key: str):
    if key in index:
        return index[key]
    short = key.split(':')[0]
    if short in index:
        return index[short]
    short = short.split('.')[0]
    return index.get(short)


def _is_numericish(key: str) -> bool:
    return any(ch.isdigit() for ch in key)


def _estimate_pair_tokens(src_text: str, tgt_text: str) -> int:
    return max(1, int((len(src_text) + len(tgt_text)) / 4))


def _segment_from_line(dataset: dict, origin_path: str, doc_group_id: str, lang: str, segment_key: str, sequence_index: int | None, raw: str, norm: str) -> SegmentRecord:
    flags = []
    if not norm:
        flags.append('empty_norm')
    return SegmentRecord(
        dataset_name=dataset['name'], domain=dataset['domain'], origin_path=origin_path, doc_group_id=doc_group_id,
        segment_id=stable_hash(f"{dataset['name']}:{doc_group_id}:{lang}:{segment_key}"), lang=lang, text_raw=raw, text_norm=norm,
        sequence_index=int(sequence_index or 0), segment_key=segment_key, segment_key_numeric=_maybe_int(segment_key),
        is_dialogue=bool(dataset.get('structural', {}).get('is_dialogue', False)),
        can_concat_left=not bool(dataset.get('structural', {}).get('is_dialogue', False)),
        can_concat_right=not bool(dataset.get('structural', {}).get('is_dialogue', False)),
        casing_profile=_casing_profile(norm), num_chars=len(norm), num_words=len(norm.split()), quality_flags=flags,
    )


def _document_summary(dataset: dict, doc_group_id: str, origin_path: str, segments: list[SegmentRecord], pairs: list[ParallelPairRecord]) -> DocumentRecord:
    src_lang = dataset['src_lang']
    tgt_lang = dataset['tgt_lang']
    doc_segments = [s for s in segments if s.doc_group_id == doc_group_id]
    doc_pairs = [p for p in pairs if p.doc_group_id == doc_group_id]
    return DocumentRecord(
        dataset_name=dataset['name'], domain=dataset['domain'], origin_path=origin_path, doc_group_id=doc_group_id, document_id=doc_group_id,
        src_lang=src_lang, tgt_lang=tgt_lang, is_parallel=True, segment_count_src=sum(1 for s in doc_segments if s.lang == src_lang),
        segment_count_tgt=sum(1 for s in doc_segments if s.lang == tgt_lang), pair_count=len(doc_pairs),
        total_chars_src=sum(s.num_chars for s in doc_segments if s.lang == src_lang), total_chars_tgt=sum(s.num_chars for s in doc_segments if s.lang == tgt_lang),
        total_words_src=sum(s.num_words for s in doc_segments if s.lang == src_lang), total_words_tgt=sum(s.num_words for s in doc_segments if s.lang == tgt_lang),
    )


def _length_ratio(src_text: str, tgt_text: str) -> float:
    src_words = max(1, len(src_text.split()))
    tgt_words = max(1, len(tgt_text.split()))
    return round(max(src_words / tgt_words, tgt_words / src_words), 6)


def _maybe_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    head = str(value).split(':')[0].split('.')[0]
    return int(head) if head.isdigit() else None


def _casing_profile(text: str) -> str:
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return 'mixed'
    if all(ch.isupper() for ch in letters):
        return 'upper'
    if text and text[:1].isupper() and sum(1 for ch in letters if ch.isupper()) <= max(1, len(letters) // 8):
        return 'sentence'
    if sum(1 for ch in letters if ch.isupper()) == 0:
        return 'lower'
    return 'mixed'


def _require(path: Path | None) -> Path:
    if path is None:
        raise FileNotFoundError('No se pudo resolver la ruta solicitada.')
    return path

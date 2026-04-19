from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord


def write_dataset_report(dataset_name: str, segments: list[SegmentRecord], pairs: list[ParallelPairRecord], documents: list[DocumentRecord], reports_dir: str | Path, sample_size: int = 8, runtime_limits: dict | None = None, generated_at_utc: str | None = None, config_relpath: str | None = None, stop_reason: str | None = None, first_limit_hit: str | None = None) -> tuple[Path, Path]:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    by_lang: dict[str, int] = {}
    for seg in segments:
        by_lang[seg.lang] = by_lang.get(seg.lang, 0) + 1
    estimated_tokens_src = sum(max(1, len(p.src_text_norm) // 4) for p in pairs)
    estimated_tokens_tgt = sum(max(1, len(p.tgt_text_norm) // 4) for p in pairs)
    estimated_tokens_total = estimated_tokens_src + estimated_tokens_tgt
    stop_reason = stop_reason or _infer_stop_reason(runtime_limits or {}, len(pairs), len(segments), len(documents), estimated_tokens_total)
    first_limit_hit = first_limit_hit or stop_reason

    report = {
        "dataset_name": dataset_name,
        "generated_at_utc": generated_at_utc,
        "config_path": config_relpath,
        "runtime_limits": runtime_limits or {},
        "stop_reason": stop_reason,
        "first_limit_hit": first_limit_hit,
        "documents": len(documents),
        "segments": len(segments),
        "pairs": len(pairs),
        "segments_by_lang": by_lang,
        "dialogue_segments": sum(1 for s in segments if s.is_dialogue),
        "empty_normalized_segments": sum(1 for s in segments if not s.text_norm),
        "pair_alignment_types": _count_values(p.alignment_type for p in pairs),
        "avg_segment_words": round(sum(s.num_words for s in segments) / max(1, len(segments)), 3),
        "avg_pair_length_ratio": round(sum(p.length_ratio for p in pairs) / max(1, len(pairs)), 3),
        "estimated_tokens_src": estimated_tokens_src,
        "estimated_tokens_tgt": estimated_tokens_tgt,
        "estimated_tokens_total": estimated_tokens_total,
    }

    report_path = reports_dir / f"{dataset_name}_report.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    sample_path = reports_dir / f"{dataset_name}_samples.md"
    with sample_path.open("w", encoding="utf-8") as handle:
        handle.write(f"# Muestras de {dataset_name}\n\n")
        handle.write("## Segmentos\n\n")
        for seg in segments[:sample_size]:
            handle.write(f"- `{seg.lang}` | grupo `{seg.doc_group_id}` | idx `{seg.sequence_index}` | `{seg.segment_key}`\n")
            handle.write(f"  - raw: {seg.text_raw[:220]}\n")
            handle.write(f"  - norm: {seg.text_norm[:220]}\n")
        handle.write("\n## Pares\n\n")
        for pair in pairs[:sample_size]:
            handle.write(f"- `{pair.alignment_type}` | grupo `{pair.doc_group_id}` | idx `{pair.pair_index}`\n")
            handle.write(f"  - src: {pair.src_text_norm[:220]}\n")
            handle.write(f"  - tgt: {pair.tgt_text_norm[:220]}\n")
    return report_path, sample_path


def _count_values(values: Iterable[str]) -> dict[str, int]:
    counter: dict[str, int] = {}
    for value in values:
        counter[value] = counter.get(value, 0) + 1
    return counter


def _infer_stop_reason(runtime_limits: dict, pair_count: int, segment_count: int, document_count: int, estimated_tokens_total: int) -> str:
    hits: list[str] = []
    max_pairs = int(runtime_limits.get('max_pairs', 0) or 0)
    max_segments = int(runtime_limits.get('max_segments', 0) or 0)
    max_documents = int(runtime_limits.get('max_documents', 0) or 0)
    max_tokens = int(runtime_limits.get('max_tokens_approx', 0) or 0)
    if max_pairs > 0 and pair_count >= max_pairs:
        hits.append('max_pairs')
    if max_segments > 0 and segment_count >= max_segments:
        hits.append('max_segments')
    if max_documents > 0 and document_count >= max_documents:
        hits.append('max_documents')
    if max_tokens > 0 and estimated_tokens_total >= max_tokens:
        hits.append('max_tokens_approx')
    if not hits:
        return 'input_exhausted'
    if len(hits) == 1:
        return hits[0]
    return 'multiple_limits'

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord


def write_dataset_report(dataset_name: str, segments: list[SegmentRecord], pairs: list[ParallelPairRecord], documents: list[DocumentRecord], reports_dir: str | Path, sample_size: int = 8) -> tuple[Path, Path]:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    by_lang: dict[str, int] = {}
    for seg in segments:
        by_lang[seg.lang] = by_lang.get(seg.lang, 0) + 1

    report = {
        "dataset_name": dataset_name,
        "documents": len(documents),
        "segments": len(segments),
        "pairs": len(pairs),
        "segments_by_lang": by_lang,
        "dialogue_segments": sum(1 for s in segments if s.is_dialogue),
        "empty_normalized_segments": sum(1 for s in segments if not s.text_norm),
        "pair_alignment_types": _count_values(p.alignment_type for p in pairs),
        "avg_segment_words": round(sum(s.num_words for s in segments) / max(1, len(segments)), 3),
        "avg_pair_length_ratio": round(sum(p.length_ratio for p in pairs) / max(1, len(pairs)), 3),
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

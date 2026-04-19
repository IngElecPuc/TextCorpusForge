from __future__ import annotations

import csv
import json
from pathlib import Path

from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord


def export_readable_samples(
    dataset_name: str,
    segments: list[SegmentRecord],
    pairs: list[ParallelPairRecord],
    documents: list[DocumentRecord],
    output_dir: str | Path,
    prefix: str | None = None,
) -> list[Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = prefix or dataset_name
    outputs: list[Path] = []

    pairs_jsonl = output_dir / f'{stem}_pairs.jsonl'
    with pairs_jsonl.open('w', encoding='utf-8') as handle:
        for pair in pairs:
            handle.write(json.dumps(pair.to_dict(), ensure_ascii=False) + '\n')
    outputs.append(pairs_jsonl)

    pairs_csv = output_dir / f'{stem}_pairs.csv'
    with pairs_csv.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['dataset_name', 'doc_group_id', 'pair_index', 'alignment_type', 'src_text_norm', 'tgt_text_norm', 'quality_flags'])
        writer.writeheader()
        for pair in pairs:
            writer.writerow({
                'dataset_name': pair.dataset_name,
                'doc_group_id': pair.doc_group_id,
                'pair_index': pair.pair_index,
                'alignment_type': pair.alignment_type,
                'src_text_norm': pair.src_text_norm,
                'tgt_text_norm': pair.tgt_text_norm,
                'quality_flags': '|'.join(pair.quality_flags),
            })
    outputs.append(pairs_csv)

    seg_jsonl = output_dir / f'{stem}_segments.jsonl'
    with seg_jsonl.open('w', encoding='utf-8') as handle:
        for seg in segments:
            handle.write(json.dumps(seg.to_dict(), ensure_ascii=False) + '\n')
    outputs.append(seg_jsonl)

    docs_json = output_dir / f'{stem}_documents.json'
    docs_json.write_text(json.dumps([doc.to_dict() for doc in documents], ensure_ascii=False, indent=2), encoding='utf-8')
    outputs.append(docs_json)

    return outputs

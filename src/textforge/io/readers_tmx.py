from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET

from textforge.normalize.line_cleanup import canonicalize_segment
from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord
from textforge.utils.hashing import stable_hash


def build_tmx_records(root: str | Path, dataset_name: str, domain: str, src_lang: str, tgt_lang: str) -> tuple[list[SegmentRecord], list[ParallelPairRecord], list[DocumentRecord]]:
    root = Path(root)
    segments: list[SegmentRecord] = []
    pairs: list[ParallelPairRecord] = []
    documents: list[DocumentRecord] = []

    for path in root.rglob('*.tmx'):
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            continue

        doc_group_id = stable_hash(f"{dataset_name}:{path}")
        src_count = 0
        tgt_count = 0

        for row_idx, tu in enumerate(tree.iterfind('.//tu'), start=1):
            segs: dict[str, str] = {}
            for tuv in tu.findall('.//tuv'):
                lang = tuv.attrib.get('{http://www.w3.org/XML/1998/namespace}lang') or tuv.attrib.get('lang') or ''
                seg = tuv.find('.//seg')
                if seg is not None and seg.text:
                    segs[lang.lower()] = seg.text

            src_raw = segs.get(src_lang.lower())
            tgt_raw = segs.get(tgt_lang.lower())
            if not src_raw or not tgt_raw:
                continue

            src_norm = canonicalize_segment(src_raw)
            tgt_norm = canonicalize_segment(tgt_raw)
            src_count += 1
            tgt_count += 1

            src_key = f"tu:{row_idx}:src"
            tgt_key = f"tu:{row_idx}:tgt"

            segments.append(SegmentRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, segment_id=stable_hash(f"{path}:{src_key}"), lang=src_lang, text_raw=src_raw, text_norm=src_norm, sequence_index=row_idx, segment_key=src_key, casing_profile='mixed', num_chars=len(src_norm), num_words=len(src_norm.split())))
            segments.append(SegmentRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, segment_id=stable_hash(f"{path}:{tgt_key}"), lang=tgt_lang, text_raw=tgt_raw, text_norm=tgt_norm, sequence_index=row_idx, segment_key=tgt_key, casing_profile='mixed', num_chars=len(tgt_norm), num_words=len(tgt_norm.split())))
            pairs.append(ParallelPairRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, pair_id=stable_hash(f"{path}:pair:{row_idx}"), pair_index=row_idx, src_lang=src_lang, tgt_lang=tgt_lang, src_text_raw=src_raw, tgt_text_raw=tgt_raw, src_text_norm=src_norm, tgt_text_norm=tgt_norm, src_segment_keys=[src_key], tgt_segment_keys=[tgt_key], src_sequence_indices=[row_idx], tgt_sequence_indices=[row_idx], alignment_type='tmx_explicit', src_words=len(src_norm.split()), tgt_words=len(tgt_norm.split()), length_ratio=_length_ratio(src_norm, tgt_norm)))

        documents.append(DocumentRecord(dataset_name=dataset_name, domain=domain, origin_path=str(path), doc_group_id=doc_group_id, document_id=doc_group_id, src_lang=src_lang, tgt_lang=tgt_lang, is_parallel=True, segment_count_src=src_count, segment_count_tgt=tgt_count, pair_count=len([p for p in pairs if p.doc_group_id == doc_group_id]), total_chars_src=sum(s.num_chars for s in segments if s.doc_group_id == doc_group_id and s.lang == src_lang), total_chars_tgt=sum(s.num_chars for s in segments if s.doc_group_id == doc_group_id and s.lang == tgt_lang), total_words_src=sum(s.num_words for s in segments if s.doc_group_id == doc_group_id and s.lang == src_lang), total_words_tgt=sum(s.num_words for s in segments if s.doc_group_id == doc_group_id and s.lang == tgt_lang)))

    return segments, pairs, documents


def _length_ratio(src: str, tgt: str) -> float:
    src_len = max(1, len(src.split()))
    tgt_len = max(1, len(tgt.split()))
    return max(src_len, tgt_len) / min(src_len, tgt_len)

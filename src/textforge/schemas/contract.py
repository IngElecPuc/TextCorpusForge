from __future__ import annotations

from dataclasses import fields
from typing import Type

from textforge.schemas.document import DocumentRecord
from textforge.schemas.parallel_pair import ParallelPairRecord
from textforge.schemas.segment import SegmentRecord

SCHEMA_CONTRACT_VERSION = 'stage1-v1'

SEGMENT_COLUMNS = [field.name for field in fields(SegmentRecord)]
PAIR_COLUMNS = [field.name for field in fields(ParallelPairRecord)]
DOCUMENT_COLUMNS = [field.name for field in fields(DocumentRecord)]


def contract_for(record_type: str) -> list[str]:
    mapping = {
        'segments': SEGMENT_COLUMNS,
        'pairs': PAIR_COLUMNS,
        'documents': DOCUMENT_COLUMNS,
    }
    if record_type not in mapping:
        raise KeyError(f'Unknown schema contract type: {record_type}')
    return list(mapping[record_type])


def describe_contract() -> dict[str, object]:
    return {
        'version': SCHEMA_CONTRACT_VERSION,
        'segments': SEGMENT_COLUMNS,
        'pairs': PAIR_COLUMNS,
        'documents': DOCUMENT_COLUMNS,
    }

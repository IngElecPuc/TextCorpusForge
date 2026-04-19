from __future__ import annotations

from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree as ET


def parse_ces_alignment(path: str | Path) -> list[dict]:
    return list(iter_ces_alignment(path))


def iter_ces_alignment(path: str | Path, max_pairs: int | None = None) -> Iterator[dict]:
    path = Path(path)
    pair_count = 0
    current_from = ''
    current_to = ''
    group_index = -1
    for event, elem in ET.iterparse(path, events=('start', 'end')):
        tag = elem.tag.split('}')[-1]
        if event == 'start' and tag == 'linkGrp':
            group_index += 1
            current_from = elem.attrib.get('fromDoc', '')
            current_to = elem.attrib.get('toDoc', '')
        elif event == 'end' and tag == 'link':
            xtargets = elem.attrib.get('xtargets', '')
            if ';' in xtargets:
                src_part, tgt_part = xtargets.split(';', maxsplit=1)
                yield {
                    'group_index': group_index,
                    'pair_index': pair_count,
                    'from_doc': current_from,
                    'to_doc': current_to,
                    'src_keys': [tok for tok in src_part.strip().split() if tok],
                    'tgt_keys': [tok for tok in tgt_part.strip().split() if tok],
                }
                pair_count += 1
                if max_pairs is not None and pair_count >= max_pairs:
                    break
            elem.clear()
        elif event == 'end' and tag == 'linkGrp':
            elem.clear()

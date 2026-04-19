from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


def parse_ces_alignment(path: str | Path) -> list[dict]:
    path = Path(path)
    tree = ET.parse(path)
    root = tree.getroot()
    alignments: list[dict] = []

    for group_idx, link_group in enumerate(root.findall('.//linkGrp')):
        from_doc = link_group.attrib.get('fromDoc', '')
        to_doc = link_group.attrib.get('toDoc', '')
        for pair_idx, link in enumerate(link_group.findall('./link')):
            xtargets = link.attrib.get('xtargets', '')
            if ';' not in xtargets:
                continue
            src_part, tgt_part = xtargets.split(';', maxsplit=1)
            src_keys = [tok for tok in src_part.strip().split() if tok]
            tgt_keys = [tok for tok in tgt_part.strip().split() if tok]
            alignments.append(
                {
                    'group_index': group_idx,
                    'pair_index': pair_idx,
                    'from_doc': from_doc,
                    'to_doc': to_doc,
                    'src_keys': src_keys,
                    'tgt_keys': tgt_keys,
                }
            )
    return alignments

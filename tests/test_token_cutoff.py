from pathlib import Path

from textforge.io.builders import build_dataset_records


def test_ces_alignment_stops_on_token_limit(tmp_path: Path):
    ds_root = tmp_path / 'dgt'
    ds_root.mkdir()
    (ds_root / 'DGT.en-es.en').write_text(('one two three four five six seven eight nine ten\n') * 50, encoding='utf-8')
    (ds_root / 'DGT.en-es.es').write_text(('uno dos tres cuatro cinco seis siete ocho nueve diez\n') * 50, encoding='utf-8')
    xml = '<cesAlign><linkGrp fromDoc="a" toDoc="b">' + ''.join(f'<link xtargets="{i};{i}" />' for i in range(1, 51)) + '</linkGrp></cesAlign>'
    (ds_root / 'DGT.en-es.xml').write_text(xml, encoding='utf-8')
    cfg = {'dataset': {'name': 'dgt', 'domain': 'legal', 'src_lang': 'en', 'tgt_lang': 'es', 'reader': 'ces_alignment_xml', 'files': {'src_text': 'DGT.en-es.en', 'tgt_text': 'DGT.en-es.es', 'alignment': 'DGT.en-es.xml'}, 'structural': {'group_from_alignment_docs': True}}}
    result = build_dataset_records(cfg, ds_root, limits={'max_pairs': 0, 'max_tokens_approx': 120})
    segs, pairs, docs = result.segments, result.pairs, result.documents
    assert 0 < len(pairs) < 50
    est = sum(max(1, int((len(p.src_text_norm) + len(p.tgt_text_norm)) / 4)) for p in pairs)
    assert est <= 120

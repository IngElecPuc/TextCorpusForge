from textforge.io.readers_xml import parse_ces_alignment


def test_parse_ces_alignment(tmp_path):
    xml_path = tmp_path / 'sample.xml'
    xml_path.write_text('<cesAlign><linkGrp fromDoc="a" toDoc="b"><link xtargets="1 2;3" /></linkGrp></cesAlign>', encoding='utf-8')
    rows = parse_ces_alignment(xml_path)
    assert rows[0]['src_keys'] == ['1', '2']
    assert rows[0]['tgt_keys'] == ['3']

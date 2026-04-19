import json
from pathlib import Path

from textforge.orchestration.pipeline import run_pipeline
import textforge.orchestration.stages as stages_mod
from textforge.settings import Settings


def build_minimal_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path
    (workspace / 'configs' / 'datasets').mkdir(parents=True)
    (workspace / 'configs' / 'pipelines').mkdir(parents=True)
    (workspace / 'configs' / 'base.yaml').write_text(
        """runtime:
  sample_size: 8
  max_pairs: 0
  max_segments: 0
  max_documents: 0
  max_tokens_approx: 0
  export_samples: true
  sample_export_size: 20
outputs:
  write_segments: true
  write_pairs: true
  write_documents: true
""",
        encoding='utf-8',
    )
    (workspace / 'configs' / 'paths.yaml').write_text('paths: {}\n', encoding='utf-8')
    ds_root = workspace / 'data_in' / 'DGT-2019.en-es'
    ds_root.mkdir(parents=True)
    (ds_root / 'DGT.en-es.en').write_text('Hello world\nAnother line\n', encoding='utf-8')
    (ds_root / 'DGT.en-es.es').write_text('Hola mundo\nOtra línea\n', encoding='utf-8')
    (ds_root / 'DGT.en-es.xml').write_text(
        '<cesAlign><linkGrp fromDoc="a" toDoc="b"><link xtargets="1;1" /><link xtargets="2;2" /></linkGrp></cesAlign>',
        encoding='utf-8',
    )
    (workspace / 'configs' / 'datasets' / 'dgt.yaml').write_text(
        f"""dataset:\n  name: dgt\n  domain: legal\n  src_lang: en\n  tgt_lang: es\n  reader: ces_alignment_xml\n  input_roots:\n    - {ds_root}\n  files:\n    src_text: DGT.en-es.en\n    tgt_text: DGT.en-es.es\n    alignment: DGT.en-es.xml\n  structural:\n    group_from_alignment_docs: true\n""",
        encoding='utf-8',
    )
    (workspace / 'configs' / 'pipelines' / 'canonicalize.yaml').write_text(
        """inputs:\n  dataset_configs:\n    - configs/datasets/dgt.yaml\nruntime:\n  max_pairs: 1\n  export_samples: true\n  sample_export_size: 5\noutputs:\n  write_segments: true\n  write_pairs: true\n  write_documents: true\n""",
        encoding='utf-8',
    )
    return workspace


def _fake_write_parquet(records, output_path, compression=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('stub', encoding='utf-8')
    return output_path


def test_stage1_writes_reproducible_reports(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(stages_mod, 'write_parquet', _fake_write_parquet)
    workspace = build_minimal_workspace(tmp_path)
    result = run_pipeline('canonicalize', workspace=workspace, config_path=workspace / 'configs' / 'pipelines' / 'canonicalize.yaml')
    assert result['total_pairs'] == 1

    reports_dir = workspace / 'data' / 'reports'
    report = json.loads((reports_dir / 'dgt_report.json').read_text(encoding='utf-8'))
    discard = json.loads((reports_dir / 'dgt_discard_report.json').read_text(encoding='utf-8'))
    manifest = json.loads((reports_dir / 'canonicalize_manifest.json').read_text(encoding='utf-8'))

    assert report['dataset_name'] == 'dgt'
    assert report['generated_at_utc']
    assert report['config_path'] == 'configs/datasets/dgt.yaml'
    assert report['runtime_limits']['max_pairs'] == 1
    assert report['stop_reason'] == 'max_pairs'
    assert report['estimated_tokens_total'] > 0
    assert discard['discarded_total'] == 0
    assert manifest['stats']['schema_contract_version'] == 'stage1-v1'
    assert 'segments' in manifest['stats']['schema_contract']
    assert manifest['config_snapshot']['runtime']['max_pairs'] == 1

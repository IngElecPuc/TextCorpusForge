import ast
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

from textforge.cli import main as cli_main
from textforge.orchestration.pipeline import run_pipeline
import textforge.orchestration.stages as stages_mod
from textforge.ui.app_state import AppState, DatasetSelection
from textforge.ui.config_builder import build_ui_pipeline_files


def build_workspace(tmp_path: Path) -> Path:
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
    (ds_root / 'DGT.en-es.en').write_text('Hello world\n', encoding='utf-8')
    (ds_root / 'DGT.en-es.es').write_text('Hola mundo\n', encoding='utf-8')
    (ds_root / 'DGT.en-es.xml').write_text('<cesAlign><linkGrp fromDoc="a" toDoc="b"><link xtargets="1;1" /></linkGrp></cesAlign>', encoding='utf-8')
    (workspace / 'configs' / 'datasets' / 'dgt.yaml').write_text(
        """dataset:
  name: dgt
  domain: legal
  src_lang: en
  tgt_lang: es
  reader: ces_alignment_xml
  input_roots: []
  files:
    src_text: DGT.en-es.en
    tgt_text: DGT.en-es.es
    alignment: DGT.en-es.xml
  structural:
    group_from_alignment_docs: true
""",
        encoding='utf-8',
    )
    (workspace / 'configs' / 'pipelines' / 'canonicalize.yaml').write_text(
        """inputs:
  dataset_configs: []
runtime:
  export_samples: false
outputs:
  write_segments: true
  write_pairs: true
  write_documents: true
""",
        encoding='utf-8',
    )
    return workspace


def _fake_write_parquet(records, output_path, compression=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('stub', encoding='utf-8')
    return output_path


def test_ui_generated_config_matches_cli_execution(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(stages_mod, 'write_parquet', _fake_write_parquet)
    workspace = build_workspace(tmp_path)
    state = AppState(
        dataset_selections=[DatasetSelection(name='dgt', domain='legal', input_root=str(workspace / 'data_in' / 'DGT-2019.en-es'), enabled=True, percentage=100.0)],
        max_pairs=1,
        export_samples=False,
    )
    pipeline_path, _ = build_ui_pipeline_files(workspace, state)
    direct_result = run_pipeline('canonicalize', workspace=workspace, config_path=pipeline_path)

    stdout = io.StringIO()
    monkeypatch.setattr(sys, 'argv', ['run_pipeline.py', 'canonicalize', '--workspace', str(workspace), '--config', str(pipeline_path)])
    with redirect_stdout(stdout):
        cli_main()
    cli_result = ast.literal_eval(stdout.getvalue().strip())
    assert cli_result['total_pairs'] == direct_result['total_pairs'] == 1
    assert cli_result['total_segments'] == direct_result['total_segments']
    assert cli_result['total_documents'] == direct_result['total_documents']

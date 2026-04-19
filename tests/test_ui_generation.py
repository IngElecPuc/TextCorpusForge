from pathlib import Path

from textforge.settings import Settings
from textforge.ui.app_state import AppState, DatasetSelection
from textforge.ui.config_builder import build_ui_pipeline_files


def test_build_ui_pipeline_files(tmp_path: Path):
    workspace = tmp_path
    (workspace / 'configs' / 'datasets').mkdir(parents=True)
    (workspace / 'configs' / 'pipelines').mkdir(parents=True)
    (workspace / 'configs' / 'datasets' / 'dgt.yaml').write_text(
        """dataset:
  name: dgt
  input_roots: []
  domain: legal
""",
        encoding='utf-8',
    )
    (workspace / 'configs' / 'pipelines' / 'canonicalize.yaml').write_text(
        """inputs:
  dataset_configs: []
user_request: {}
runtime: {}
""",
        encoding='utf-8',
    )

    state = AppState(
        dataset_selections=[DatasetSelection(name='dgt', domain='legal', input_root='/tmp/dgt', enabled=True, percentage=100.0)],
        max_pairs=100,
        max_tokens_approx=1000,
    )
    pipeline_path, dataset_paths = build_ui_pipeline_files(workspace, state)

    cfg = Settings.from_yaml(pipeline_path)
    assert cfg.get('runtime.max_pairs') == 100
    assert cfg.get('runtime.max_tokens_approx') == 1000
    assert len(dataset_paths) == 1
    assert cfg.get('paths.silver') == 'data/silver'
    assert cfg.get('outputs.parquet_compression') == 'zstd'

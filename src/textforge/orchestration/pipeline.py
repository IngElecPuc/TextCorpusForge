from __future__ import annotations

from pathlib import Path

from textforge.orchestration.stages import stage1_canonicalize
from textforge.settings import Settings


PIPELINES = {
    'canonicalize': stage1_canonicalize,
}


def run_pipeline(pipeline_name: str, workspace: str | Path = '.', config_path: str | Path | None = None) -> dict:
    workspace = Path(workspace)
    pipeline_cfg_path = Path(config_path) if config_path else workspace / 'configs' / 'pipelines' / f'{pipeline_name}.yaml'
    base_cfg = Settings.from_yaml(workspace / 'configs' / 'base.yaml')
    paths_cfg = Settings.from_yaml(workspace / 'configs' / 'paths.yaml')
    pipeline_cfg = Settings.from_yaml(pipeline_cfg_path)
    settings = base_cfg.merge(paths_cfg).merge(pipeline_cfg)
    return PIPELINES[pipeline_name](settings, workspace, pipeline_cfg_path)

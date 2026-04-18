from __future__ import annotations

from pathlib import Path
from pprint import pprint

from textforge.orchestration.registry import PIPELINE_REGISTRY
from textforge.settings import Settings


def run_pipeline(pipeline_name: str, config_path: Path, workspace: Path) -> dict:
    config = Settings.from_yaml(config_path)
    stage = PIPELINE_REGISTRY[pipeline_name]
    result = stage(config=config, workspace=workspace)
    pprint(result)
    return result

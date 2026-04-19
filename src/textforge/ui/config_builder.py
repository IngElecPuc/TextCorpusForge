from __future__ import annotations

from pathlib import Path
from typing import Any

from textforge.settings import Settings
from textforge.ui.app_state import AppState


def build_ui_pipeline_files(workspace: str | Path, state: AppState) -> tuple[Path, list[Path]]:
    workspace = Path(workspace)
    generated_dir = workspace / 'configs' / 'generated_ui'
    generated_dir.mkdir(parents=True, exist_ok=True)

    dataset_config_paths: list[Path] = []
    for selection in state.dataset_selections:
        if not selection.enabled:
            continue
        base_cfg_path = workspace / 'configs' / 'datasets' / f'{selection.name}.yaml'
        cfg = Settings.from_yaml(base_cfg_path)
        cfg.set('dataset.input_roots', [selection.input_root])
        cfg.set('dataset.domain', selection.domain)
        cfg.set('mix.percentage', float(selection.percentage))
        out_path = generated_dir / f'{selection.name}.yaml'
        cfg.to_yaml(out_path)
        dataset_config_paths.append(out_path)

    pipeline_cfg = Settings.from_yaml(workspace / 'configs' / 'pipelines' / 'canonicalize.yaml')
    pipeline_cfg.set('inputs.dataset_configs', [str(p.relative_to(workspace)) for p in dataset_config_paths])
    pipeline_cfg.set('user_request.approximate_token_budget', int(state.approximate_token_budget or 0))
    pipeline_cfg.set('user_request.target_task', state.task)
    pipeline_cfg.set('user_request.target_domain', state.target_domain)
    pipeline_cfg.set('runtime.max_pairs', int(state.max_pairs or 0))
    pipeline_cfg.set('runtime.max_segments', int(state.max_segments or 0))
    pipeline_cfg.set('runtime.max_documents', int(state.max_documents or 0))
    pipeline_cfg.set('runtime.max_tokens_approx', int(state.max_tokens_approx or 0))
    pipeline_cfg.set('runtime.stop_after_first_dataset', bool(state.stop_after_first_dataset))
    pipeline_cfg.set('runtime.export_samples', bool(state.export_samples))
    pipeline_cfg.set('runtime.sample_export_size', int(state.sample_export_size or 20))

    pipeline_out = generated_dir / 'canonicalize_from_ui.yaml'
    pipeline_cfg.to_yaml(pipeline_out)
    return pipeline_out, dataset_config_paths

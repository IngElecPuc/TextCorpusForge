from __future__ import annotations

import argparse
import json
from pathlib import Path

from textforge.orchestration.pipeline import run_pipeline
from textforge.settings import Settings

DATASETS = ['dgt', 'eubookshop', 'europarl', 'multiun', 'opensubtitles', 'unpc']


def build_smoke_config(workspace: Path, dataset_name: str, max_pairs: int, max_tokens: int, sample_size: int) -> Path:
    base = Settings.from_yaml(workspace / 'configs' / 'pipelines' / 'canonicalize.yaml')
    base.set('inputs.dataset_configs', [f'configs/datasets/{dataset_name}.yaml'])
    base.set('runtime.max_pairs', int(max_pairs))
    base.set('runtime.max_tokens_approx', int(max_tokens))
    base.set('runtime.stop_after_first_dataset', True)
    base.set('runtime.export_samples', True)
    base.set('runtime.sample_export_size', int(sample_size))
    out_dir = workspace / 'configs' / 'generated_smoke'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'smoke_{dataset_name}.yaml'
    base.to_yaml(out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description='Smoke test runner para Fase 1')
    parser.add_argument('--workspace', default='.')
    parser.add_argument('--datasets', nargs='*', default=DATASETS)
    parser.add_argument('--max-pairs', type=int, default=10)
    parser.add_argument('--max-tokens', type=int, default=0)
    parser.add_argument('--sample-size', type=int, default=10)
    args = parser.parse_args()

    workspace = Path(args.workspace)
    summary: dict[str, object] = {}
    for dataset in args.datasets:
        cfg = build_smoke_config(workspace, dataset, args.max_pairs, args.max_tokens, args.sample_size)
        result = run_pipeline('canonicalize', workspace=workspace, config_path=cfg)
        summary[dataset] = result
        print(f'[ok] {dataset}: {result}')
    out_path = workspace / 'data' / 'reports' / 'stage1_smoke_summary.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Resumen guardado en {out_path}')


if __name__ == '__main__':
    main()

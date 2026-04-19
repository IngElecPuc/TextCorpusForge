from __future__ import annotations

import json
from pathlib import Path

from textforge.io.builders import build_dataset_records
from textforge.reports.sample_exports import export_readable_samples
from textforge.settings import Settings
from textforge.ui.app_state import AppState


def run_preview(workspace: str | Path, state: AppState) -> dict:
    workspace = Path(workspace)
    active = [d for d in state.dataset_selections if d.enabled]
    if not active:
        raise ValueError('No hay datasets activos.')
    outputs = []
    summaries = []
    reports_dir = workspace / state.output_root / state.reports_subdir
    reports_dir.mkdir(parents=True, exist_ok=True)
    limits = {
        'max_pairs': max(1, int(state.sample_export_size or 20)),
        'max_segments': max(1, int(state.sample_export_size or 20)),
        'max_documents': max(1, min(int(state.sample_export_size or 20), 10)),
        'max_tokens_approx': int(state.max_tokens_approx or 0),
    }
    for selection in active:
        cfg = Settings.from_yaml(workspace / 'configs' / 'datasets' / f'{selection.name}.yaml').data
        cfg['dataset']['input_roots'] = [selection.input_root]
        root = selection.input_root
        result = build_dataset_records(cfg, root, limits=limits)
        segments, pairs, documents = result.segments, result.pairs, result.documents
        segments = segments[: limits['max_segments']]
        pairs = pairs[: limits['max_pairs']]
        documents = documents[: limits['max_documents']]
        prefix = f'preview_{selection.name}'
        exported = export_readable_samples(selection.name, segments, pairs, documents, reports_dir, prefix=prefix)
        outputs.extend(str(p) for p in exported)
        summaries.append({'dataset': selection.name, 'segments': len(segments), 'pairs': len(pairs), 'documents': len(documents)})
        if state.stop_after_first_dataset:
            break
    summary_path = reports_dir / 'preview_summary.json'
    summary_path.write_text(json.dumps({'summaries': summaries, 'outputs': outputs}, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'summary_path': str(summary_path), 'outputs': outputs, 'summaries': summaries}

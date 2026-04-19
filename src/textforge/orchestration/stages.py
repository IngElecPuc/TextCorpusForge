from __future__ import annotations

from pathlib import Path
from typing import Any

from textforge.io.builders import build_dataset_records
from textforge.io.manifest import RunManifest, write_manifest
from textforge.io.parquet_writer import write_parquet
from textforge.reports.corpus_report import write_dataset_report
from textforge.settings import Settings
from textforge.utils.logging import get_logger
from textforge.utils.paths import ensure_dir


logger = get_logger(__name__)


def stage1_canonicalize(config: Settings, workspace: Path, config_path: Path) -> dict[str, Any]:
    silver_dir = ensure_dir(workspace / 'data' / 'silver')
    reports_dir = ensure_dir(workspace / 'data' / 'reports')
    ensure_dir(silver_dir / 'segments')
    ensure_dir(silver_dir / 'pairs')
    ensure_dir(silver_dir / 'documents')

    manifest = RunManifest(pipeline_name='canonicalize', config_path=str(config_path))

    dataset_cfg_paths = config.get('inputs.dataset_configs', [])
    total_segments = 0
    total_pairs = 0
    total_documents = 0

    for dataset_cfg_rel in dataset_cfg_paths:
        dataset_cfg_path = workspace / dataset_cfg_rel
        dataset_cfg = Settings.from_yaml(dataset_cfg_path).data
        dataset_name = dataset_cfg['dataset']['name']
        roots = dataset_cfg['dataset'].get('input_roots', [])
        if not roots:
            relative_dir = dataset_cfg['dataset'].get('relative_dir')
            default_root = config.get('paths.datasets_root_default')
            if relative_dir and default_root:
                roots = [str(Path(default_root) / relative_dir)]

        manifest.inputs.append({'dataset': dataset_name, 'config_path': str(dataset_cfg_path), 'roots': roots})
        if not roots:
            logger.info('Saltando %s: no tiene input_roots configurado todavía.', dataset_name)
            continue

        all_segments = []
        all_pairs = []
        all_documents = []

        for root in roots:
            try:
                segments, pairs, documents = build_dataset_records(dataset_cfg, root)
            except FileNotFoundError as exc:
                logger.warning('Saltando %s en %s: %s', dataset_name, root, exc)
                continue
            all_segments.extend(segments)
            all_pairs.extend(pairs)
            all_documents.extend(documents)

        if not all_segments and not all_pairs and not all_documents:
            continue

        seg_path = silver_dir / 'segments' / f'{dataset_name}.parquet'
        pair_path = silver_dir / 'pairs' / f'{dataset_name}.parquet'
        doc_path = silver_dir / 'documents' / f'{dataset_name}.parquet'

        if config.get('outputs.write_segments', True):
            write_parquet((record.to_dict() for record in all_segments), seg_path)
            manifest.outputs.append(str(seg_path))
        if config.get('outputs.write_pairs', True):
            write_parquet((record.to_dict() for record in all_pairs), pair_path)
            manifest.outputs.append(str(pair_path))
        if config.get('outputs.write_documents', True):
            write_parquet((record.to_dict() for record in all_documents), doc_path)
            manifest.outputs.append(str(doc_path))

        report_json, report_md = write_dataset_report(dataset_name, all_segments, all_pairs, all_documents, reports_dir, sample_size=config.get('runtime.sample_size', 8))
        manifest.outputs.extend([str(report_json), str(report_md)])

        total_segments += len(all_segments)
        total_pairs += len(all_pairs)
        total_documents += len(all_documents)
        logger.info('Dataset %s -> segmentos=%s pares=%s documentos=%s', dataset_name, len(all_segments), len(all_pairs), len(all_documents))

    manifest.stats = {
        'total_segments': total_segments,
        'total_pairs': total_pairs,
        'total_documents': total_documents,
    }
    manifest_path = write_manifest(manifest, reports_dir / 'canonicalize_manifest.json')
    return {'manifest_path': str(manifest_path), **manifest.stats}

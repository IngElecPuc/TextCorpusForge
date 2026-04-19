from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from textforge.io.builders import build_dataset_records
from textforge.io.manifest import RunManifest, write_manifest
from textforge.io.parquet_writer import write_parquet
from textforge.reports.corpus_report import write_dataset_report
from textforge.reports.discard_report import write_discard_report
from textforge.reports.sample_exports import export_readable_samples
from textforge.schemas.contract import SCHEMA_CONTRACT_VERSION, describe_contract
from textforge.settings import Settings
from textforge.utils.logging import get_logger
from textforge.utils.paths import ensure_dir

logger = get_logger(__name__)
ProgressCallback = Callable[[dict[str, Any]], None]


def stage1_canonicalize(config: Settings, workspace: Path, config_path: Path, progress_callback: ProgressCallback | None = None, cancel_event: Any | None = None) -> dict[str, Any]:
    silver_dir = ensure_dir(workspace / str(config.get('paths.silver', 'data/silver')))
    reports_dir = ensure_dir(workspace / str(config.get('paths.reports', 'data/reports')))
    ensure_dir(silver_dir / 'segments')
    ensure_dir(silver_dir / 'pairs')
    ensure_dir(silver_dir / 'documents')
    ensure_dir(workspace / str(config.get('paths.tmp', 'data/tmp')))

    compression = str(config.get('outputs.parquet_compression', 'zstd'))
    manifest = RunManifest(pipeline_name='canonicalize', config_path=str(config_path), config_snapshot=config.data, stats={'schema_contract_version': SCHEMA_CONTRACT_VERSION})
    dataset_cfg_paths = config.get('inputs.dataset_configs', [])
    total_segments = total_pairs = total_documents = 0
    total_steps = max(len(dataset_cfg_paths), 1)
    emitted = {'pairs': 0, 'segments': 0, 'documents': 0}

    for index, dataset_cfg_rel in enumerate(dataset_cfg_paths, start=1):
        if cancel_event is not None and cancel_event.is_set():
            _emit(progress_callback, stage='cancelled', message='Ejecución cancelada por el usuario.', progress=index - 1, total=total_steps, **emitted)
            break
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
        _emit(progress_callback, stage='dataset_start', dataset=dataset_name, message=f'Leyendo {dataset_name}...', progress=index - 1, total=total_steps, **emitted)
        if not roots:
            continue
        all_segments = []
        all_pairs = []
        all_documents = []
        runtime_limits = {
            'schema_contract_version': SCHEMA_CONTRACT_VERSION,
            'max_pairs': int(config.get('runtime.max_pairs', 0) or 0),
            'max_segments': int(config.get('runtime.max_segments', 0) or 0),
            'max_documents': int(config.get('runtime.max_documents', 0) or 0),
            'max_tokens_approx': int(config.get('runtime.max_tokens_approx', 0) or 0),
        }
        for root in roots:
            if cancel_event is not None and cancel_event.is_set():
                break
            try:
                result = build_dataset_records(dataset_cfg, root, limits=runtime_limits)
                segments, pairs, documents = result.segments, result.pairs, result.documents
            except FileNotFoundError as exc:
                logger.warning('Saltando %s en %s: %s', dataset_name, root, exc)
                continue
            all_segments.extend(segments)
            all_pairs.extend(pairs)
            all_documents.extend(documents)
        if not all_segments and not all_pairs and not all_documents:
            _emit(progress_callback, stage='dataset_done', dataset=dataset_name, message=f'{dataset_name}: sin resultados.', progress=index, total=total_steps, **emitted)
            continue
        seg_path = silver_dir / 'segments' / f'{dataset_name}.parquet'
        pair_path = silver_dir / 'pairs' / f'{dataset_name}.parquet'
        doc_path = silver_dir / 'documents' / f'{dataset_name}.parquet'
        if config.get('outputs.write_segments', True):
            write_parquet((record.to_dict() for record in all_segments), seg_path, compression=compression)
            manifest.outputs.append(str(seg_path))
        if config.get('outputs.write_pairs', True):
            write_parquet((record.to_dict() for record in all_pairs), pair_path, compression=compression)
            manifest.outputs.append(str(pair_path))
        if config.get('outputs.write_documents', True):
            write_parquet((record.to_dict() for record in all_documents), doc_path, compression=compression)
            manifest.outputs.append(str(doc_path))
        report_json, report_md = write_dataset_report(dataset_name, all_segments, all_pairs, all_documents, reports_dir, sample_size=config.get('runtime.sample_size', 8), runtime_limits=runtime_limits, generated_at_utc=manifest.created_at_utc, config_relpath=str(dataset_cfg_rel), stop_reason=result.stop_reason, first_limit_hit=result.first_limit_hit)
        discard_report = write_discard_report(dataset_name, reports_dir)
        manifest.outputs.extend([str(report_json), str(report_md), str(discard_report)])
        if config.get('runtime.export_samples', True):
            sample_paths = export_readable_samples(dataset_name, all_segments[: config.get('runtime.sample_export_size', 20)], all_pairs[: config.get('runtime.sample_export_size', 20)], all_documents[: min(config.get('runtime.sample_export_size', 20), 10)], reports_dir)
            manifest.outputs.extend(str(p) for p in sample_paths)
        total_segments += len(all_segments)
        total_pairs += len(all_pairs)
        total_documents += len(all_documents)
        emitted.update({'pairs': total_pairs, 'segments': total_segments, 'documents': total_documents})
        _emit(progress_callback, stage='dataset_done', dataset=dataset_name, message=f'{dataset_name}: segmentos={len(all_segments)} pares={len(all_pairs)} documentos={len(all_documents)}', progress=index, total=total_steps, **emitted)
        if config.get('runtime.stop_after_first_dataset', False):
            break
    manifest.stats = {'schema_contract_version': SCHEMA_CONTRACT_VERSION, 'schema_contract': describe_contract(), 'total_segments': total_segments, 'total_pairs': total_pairs, 'total_documents': total_documents}
    manifest_path = write_manifest(manifest, reports_dir / 'canonicalize_manifest.json')
    _emit(progress_callback, stage='finished', message='Pipeline finalizado.', progress=total_steps, total=total_steps, manifest_path=str(manifest_path), **emitted)
    return {'manifest_path': str(manifest_path), **manifest.stats}


def _emit(callback: ProgressCallback | None, **payload: Any) -> None:
    if callback is not None:
        callback(payload)


def _apply_runtime_limits(config: Settings, segments, pairs, documents):
    max_pairs = int(config.get('runtime.max_pairs', 0) or 0)
    max_segments = int(config.get('runtime.max_segments', 0) or 0)
    max_documents = int(config.get('runtime.max_documents', 0) or 0)
    max_tokens_approx = int(config.get('runtime.max_tokens_approx', 0) or 0)
    stats = {}
    if max_pairs > 0:
        pairs = pairs[:max_pairs]
        stats['max_pairs'] = len(pairs)
    if max_segments > 0:
        segments = segments[:max_segments]
        stats['max_segments'] = len(segments)
    if max_documents > 0:
        documents = documents[:max_documents]
        stats['max_documents'] = len(documents)
    if max_tokens_approx > 0:
        running = 0
        limited_pairs = []
        for pair in pairs:
            pair_tokens = max(1, int((len(pair.src_text_norm) + len(pair.tgt_text_norm)) / 4))
            if limited_pairs and running + pair_tokens > max_tokens_approx:
                break
            limited_pairs.append(pair)
            running += pair_tokens
        pairs = limited_pairs
        stats['max_tokens_approx'] = running
        allowed_groups = {p.doc_group_id for p in pairs}
        if allowed_groups:
            segments = [s for s in segments if s.doc_group_id in allowed_groups]
            documents = [d for d in documents if d.doc_group_id in allowed_groups]
    return segments, pairs, documents, stats

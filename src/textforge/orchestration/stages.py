from __future__ import annotations

from pathlib import Path
from typing import Any

from textforge.io.manifest import RunManifest, write_manifest
from textforge.io.parquet_writer import write_parquet
from textforge.io.readers_tmx import iter_tmx_parallel
from textforge.io.readers_tsv import iter_tsv_parallel
from textforge.io.readers_txt import iter_txt_documents
from textforge.io.readers_xml import iter_xml_documents
from textforge.settings import Settings


def stage0_canonicalize(config: Settings, workspace: Path) -> dict[str, Any]:
    dataset_paths = [
        Path(p)
        for p in config.get("inputs.dataset_configs", [])
    ]

    bronze_out = workspace / "data" / "bronze"
    silver_out = workspace / "data" / "silver"
    reports_out = workspace / "data" / "reports"
    reports_out.mkdir(parents=True, exist_ok=True)

    manifest = RunManifest(
        pipeline_name="canonicalize",
        config_path=str(workspace / "configs" / "pipelines" / "canonicalize.yaml"),
    )

    total_docs = 0
    total_pairs = 0

    for dataset_cfg_path in dataset_paths:
        dataset_cfg = Settings.from_yaml(workspace / dataset_cfg_path)
        name = dataset_cfg.get("dataset.name", dataset_cfg_path.stem)
        roots = dataset_cfg.get("dataset.input_roots", [])
        domain = dataset_cfg.get("dataset.domain", "unknown")
        dtype = dataset_cfg.get("dataset.type", "document")
        langs = dataset_cfg.get("dataset.expected_languages", [])

        manifest.inputs.append({
            "dataset": name,
            "roots": roots,
            "domain": domain,
            "type": dtype,
            "expected_languages": langs,
        })

        if not roots:
            continue

        for root in roots:
            root_path = workspace / root if not Path(root).is_absolute() else Path(root)

            if dtype == "parallel":
                pair_records = list(iter_tmx_parallel(root_path, name, domain, langs[0], langs[1]))
                if not pair_records:
                    pair_records = list(iter_tsv_parallel(root_path, name, domain, langs[0], langs[1]))
                if pair_records:
                    out_path = silver_out / "pairs" / f"{name}.parquet"
                    write_parquet((r.to_dict() for r in pair_records), out_path)
                    manifest.outputs.append(str(out_path))
                    total_pairs += len(pair_records)
            else:
                doc_records = list(iter_txt_documents(root_path, name, domain, langs[0] if langs else ""))
                if not doc_records:
                    doc_records = list(iter_xml_documents(root_path, name, domain, langs[0] if langs else ""))
                if doc_records:
                    out_path = silver_out / "docs" / f"{name}.parquet"
                    write_parquet((r.to_dict() for r in doc_records), out_path)
                    manifest.outputs.append(str(out_path))
                    total_docs += len(doc_records)

    manifest.stats = {
        "total_documents": total_docs,
        "total_parallel_pairs": total_pairs,
    }
    manifest_path = reports_out / "canonicalize_manifest.json"
    write_manifest(manifest, manifest_path)
    return manifest.to_dict()

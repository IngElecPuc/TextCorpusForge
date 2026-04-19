from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable


DEFAULT_COMPRESSION = "zstd"


def write_parquet(records: Iterable[dict], output_path: str | Path) -> Path:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError(
            "write_parquet requiere pyarrow instalado. Añádelo al entorno antes de ejecutar la Fase 1."
        ) from exc

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [_normalize_for_parquet(row) for row in records]
    table = pa.Table.from_pylist(rows) if rows else pa.table({})
    pq.write_table(table, output_path, compression=DEFAULT_COMPRESSION)
    return output_path


def _normalize_for_parquet(value: Any) -> Any:
    if isinstance(value, dict):
        if not value:
            return None
        return {key: _normalize_for_parquet(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_for_parquet(item) for item in value]
    return value

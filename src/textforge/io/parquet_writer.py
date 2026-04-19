from __future__ import annotations

from pathlib import Path
from typing import Iterable


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

    rows = list(records)
    table = pa.Table.from_pylist(rows) if rows else pa.table({})
    pq.write_table(table, output_path, compression=DEFAULT_COMPRESSION)
    return output_path

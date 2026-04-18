from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet(records: Iterable[dict], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = list(records)
    if not rows:
        table = pa.table({})
    else:
        table = pa.Table.from_pylist(rows)

    pq.write_table(table, output_path)
    return output_path

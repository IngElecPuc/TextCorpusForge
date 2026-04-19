from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_discard_report(dataset_name: str, reports_dir: str | Path, discarded_by_rule: dict[str, int] | None = None, notes: list[str] | None = None) -> Path:
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        'dataset_name': dataset_name,
        'discarded_total': int(sum((discarded_by_rule or {}).values())),
        'discarded_by_rule': discarded_by_rule or {},
        'notes': notes or ['Fase 1 no aplica filtrado fuerte; reporte de descartes inicializado a cero.'],
    }
    out_path = reports_dir / f'{dataset_name}_discard_report.json'
    with out_path.open('w', encoding='utf-8') as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return out_path

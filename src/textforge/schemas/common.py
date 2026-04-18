from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class BaseRecord:
    source: str
    domain: str
    origin_path: str
    metadata: dict[str, Any] = field(default_factory=dict)

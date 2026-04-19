from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(slots=True)
class Settings:
    data: dict[str, Any]

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Settings":
        with Path(path).open("r", encoding="utf-8") as handle:
            return cls(data=yaml.safe_load(handle) or {})

    def get(self, dotted_key: str, default: Any = None) -> Any:
        current: Any = self.data
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def set(self, dotted_key: str, value: Any) -> None:
        parts = dotted_key.split(".")
        current = self.data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value

    def merge(self, other: "Settings") -> "Settings":
        return Settings(data=_deep_merge(dict(self.data), dict(other.data)))

    def to_yaml(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(self.data, handle, allow_unicode=True, sort_keys=False)
        return path


def _deep_merge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = dict(left)
    for key, value in right.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

from __future__ import annotations

from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_in_root(root: str | Path, relative: str | None) -> Path | None:
    if not relative:
        return None
    base = Path(root)
    candidate = base / relative
    return candidate if candidate.exists() else None

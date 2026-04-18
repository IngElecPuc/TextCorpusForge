from __future__ import annotations

import gzip
import shutil
import tarfile
import zipfile
from pathlib import Path


def extract_if_needed(input_path: str | Path, output_dir: str | Path) -> Path:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if input_path.suffix == ".zip":
        with zipfile.ZipFile(input_path, "r") as archive:
            archive.extractall(output_dir)
        return output_dir

    if input_path.suffix in {".tar", ".tgz", ".gz"} and tarfile.is_tarfile(input_path):
        with tarfile.open(input_path, "r:*") as archive:
            archive.extractall(output_dir)
        return output_dir

    if input_path.suffix == ".gz" and not tarfile.is_tarfile(input_path):
        target = output_dir / input_path.stem
        with gzip.open(input_path, "rb") as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return target

    return input_path

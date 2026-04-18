from __future__ import annotations

import argparse
from pathlib import Path

from textforge.orchestration.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TextForge CLI")
    parser.add_argument("--pipeline", required=True, help="Nombre del pipeline a ejecutar.")
    parser.add_argument("--config", required=True, help="Ruta al YAML del pipeline.")
    parser.add_argument("--workspace", default=".", help="Raíz del proyecto.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_pipeline(
        pipeline_name=args.pipeline,
        config_path=Path(args.config),
        workspace=Path(args.workspace),
    )


if __name__ == "__main__":
    main()

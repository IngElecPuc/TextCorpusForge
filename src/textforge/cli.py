from __future__ import annotations

import argparse
from pathlib import Path

from textforge.orchestration.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='TextForge CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    run_cmd = sub.add_parser('run', help='Ejecuta un pipeline por nombre')
    run_cmd.add_argument('pipeline', choices=['canonicalize'])
    run_cmd.add_argument('--workspace', default='.')
    run_cmd.add_argument('--config', default=None)

    canonicalize_cmd = sub.add_parser('canonicalize', help='Alias directo para la Fase 1')
    canonicalize_cmd.add_argument('--workspace', default='.')
    canonicalize_cmd.add_argument('--config', default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == 'run':
        result = run_pipeline(args.pipeline, workspace=Path(args.workspace), config_path=args.config)
    else:
        result = run_pipeline('canonicalize', workspace=Path(args.workspace), config_path=args.config)
    print(result)


if __name__ == '__main__':
    main()

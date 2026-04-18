# TextForge

Base de proyecto para limpieza, canonización y exportación de corpus de texto en Python.

## Objetivo

Construir un pipeline reproducible que permita:

- Ingerir corpus crudos desde carpetas seleccionadas por el usuario.
- Limpiar y canonizar texto y pares paralelos.
- Fijar un presupuesto aproximado de tokens final.
- Mezclar datasets por porcentaje y por dominio objetivo.
- Exportar datasets derivados para MT, BERT y GPT.
- Operar tanto por CLI como por una UI simple basada en Tkinter.

## Estado actual

Este scaffolding incluye:

- árbol de carpetas completo,
- plan del proyecto en `docs/PROJECT_PLAN.md`,
- base funcional de la etapa 0,
- estructura preparada para integrar etapas posteriores.

## Ejecución inicial

```bash
pip install -e .
python scripts/launch_ui.py
```

o por CLI:

```bash
python scripts/run_pipeline.py --pipeline canonicalize --config configs/pipelines/canonicalize.yaml
```

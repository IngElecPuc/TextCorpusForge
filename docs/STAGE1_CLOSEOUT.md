# Cierre formal de Fase 1

## Criterios cubiertos

### 1. Contrato de schema congelado

Se congela la versión `stage1-v1` para `segments`, `pairs` y `documents`.

Ver: `docs/SCHEMA_CONTRACT.md`

### 2. Smoke test por corpus real

Se deja `scripts/smoke_stage1.py` para correr una pasada corta por:

- DGT
- EUbookshop
- Europarl
- MultiUN
- OpenSubtitles
- UNPC

Ejemplo:

```bash
python scripts/smoke_stage1.py --workspace . --max-pairs 10
```

### 3. Reportes mínimos reproducibles

Cada corrida de `canonicalize` deja:

- `*_report.json`
- `*_samples.md`
- `*_discard_report.json`
- `canonicalize_manifest.json`
- muestras legibles cuando están activadas

### 4. Equivalencia UI y CLI

La UI genera un YAML ejecutable por la misma CLI. La prueba automática comprueba que una corrida con config generada desde la UI y una corrida disparada por CLI sobre ese mismo preset dan los mismos conteos base.

### 5. Alcance documentado

El alcance positivo y negativo de Fase 1 queda fijado en `docs/STAGE1_SCOPE.md`.

## Checklist operativa recomendada antes de abrir Fase 2

- correr `pytest`
- correr smoke corto por los 6 corpus
- validar 1 muestra manual por corpus
- confirmar que UI y CLI generan el mismo resultado para un preset pequeño
- confirmar que el contrato `stage1-v1` no cambia

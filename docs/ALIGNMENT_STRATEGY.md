# Estrategia de lectura y alineación por corpus

## Resumen

Esta entrega adapta la lógica fina de lectura al layout real de los seis corpus y separa dos familias:

- **alineamiento explícito y confiable**: DGT-2019, Europarl, UNPC
- **alineamiento lateral por IDs**: EUbookshop
- **alineamiento monotónico heurístico**: MultiUN, OpenSubtitles

## Corpus con alineamiento explícito

### DGT-2019, Europarl, UNPC

Se leen con:

- `*.en`
- `*.es`
- `*.xml`

El XML se interpreta como CES-like alignment y soporta:

- `1;1`
- `3 4;5`
- `1:1;1:1`

El `doc_group_id` se deriva de `fromDoc|toDoc` para preservar estructura documental.

## Corpus con sidecar de IDs

### EUbookshop

Se leen con:

- `*.en`
- `*.es`
- `*.ids`

Cada fila del `.ids` define:

- documento origen
- documento destino
- claves de segmentos source
- claves de segmentos target

En esta fase se mantienen tanto el texto como las claves externas en `metadata` y en los campos de segmento/par.

## Corpus sin sidecar explícito

### MultiUN

Se asume un corpus mayormente paralelo, pero no se fuerza una igualdad de líneas 1:1 ciega.

Estrategia:

1. separar en bloques por líneas en blanco
2. alinear cada bloque de forma monotónica
3. permitir movimientos `1-1`, `1-2`, `2-1`
4. penalizar fuertemente saltos `1-0` y `0-1`
5. marcar todo como `provisional_alignment`

La intención es producir pares utilizables para inspección y filtrado posterior, no declarar alineamiento oro.

### OpenSubtitles

Se trata como corpus dialogal desalineado.

Estrategia:

1. separar por bloques usando líneas en blanco
2. alinear monotónicamente dentro de cada bloque
3. permitir `1-1`, `1-2`, `2-1`, `1-0`, `0-1`
4. usar rasgos blandos:
   - longitud relativa
   - puntuación
   - dígitos
   - marcadores de diálogo (`-`, `—`)
   - comillas
5. marcar alineaciones no confiables y conservar score

Esto está pensado para minimizar deriva acumulada cuando faltan o sobran líneas.

## Silver producido

La salida sigue siendo:

- `segments/*.parquet`
- `pairs/*.parquet`
- `documents/*.parquet`

Con extras útiles:

- `metadata.line_numbers`
- `metadata.block_index`
- `metadata.alignment_score`
- `metadata.is_alignment_trusted`
- `quality_flags` como `merged_alignment`, `src_gap`, `tgt_gap`, `provisional_alignment`

## Notas

- Los pares de MultiUN y OpenSubtitles son **provisionales**.
- Los segmentos siempre conservan orden interno para reconstrucción de contexto.
- Los tokens especiales del modelo siguen fuera de silver.

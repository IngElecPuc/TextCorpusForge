# TextForge

TextForge es una aplicación en Python para construir corpus limpios, trazables y reproducibles para tareas de NLP.

Esta regeneración del scaffold ya viene adaptada al layout físico confirmado para los datasets iniciales, cuya raíz es:

```text
/home/felpipe/Datasets/Textos paralelos
```

## Layout confirmado

- `DGT-2019.en-es/` → `DGT.en-es.en`, `DGT.en-es.es`, `DGT.en-es.xml`
- `EUbookshop.en-es/` → `EUbookshop.en-es.en`, `EUbookshop.en-es.es`, `EUbookshop.en-es.ids`
- `Europarl.v8.en-es/` → `Europarl.v8.en-es.en`, `Europarl.v8.en-es.es`, `Europarl.v8.en-es.xml`
- `MultiUN.en-es/` → `MultiUN.en-es.en`, `MultiUN.en-es.es`
- `OpenSubtitles.en-es/` → `OpenSubtitles.en-es.en`, `OpenSubtitles.en-es.es`
- `UNPC.en-es/` → `UNPC.en-es.en`, `UNPC.en-es.es`, `UNPC.en-es.xml`

## Idea central de Fase 1

La capa silver **no** debe llevar tokens especiales del modelo. Debe almacenar texto limpio y metadatos estructurales:

- orden interno,
- grupo documental o conversacional,
- claves de segmento originales,
- trazabilidad de archivo fuente,
- tipo de alineamiento,
- bandera de confianza del alineamiento.

Esto permite después:

- concatenar contexto largo sin mezclar documentos indebidos,
- construir seq2seq, BERT o GPT con distintas longitudes,
- retokenizar sin rehacer limpieza,
- separar corpora con alineamiento explícito de corpora que requieren alineación posterior.

## Decisiones de reader por corpus

- DGT, Europarl y UNPC → `ces_alignment_xml`
- EUbookshop → `ids_sidecar`
- MultiUN → `parallel_sidecar_plain` como stream bilingüe sin alineamiento confiable
- OpenSubtitles → `parallel_sidecar_plain` como stream dialogal sin alineamiento confiable

## Salidas principales

- `data/silver/segments/<dataset>.parquet`
- `data/silver/pairs/<dataset>.parquet`
- `data/silver/documents/<dataset>.parquet`
- `data/reports/<dataset>_report.json`
- `data/reports/<dataset>_samples.md`
- `data/reports/canonicalize_manifest.json`

## Uso rápido

```bash
python scripts/run_pipeline.py canonicalize --workspace .
python scripts/launch_ui.py
```

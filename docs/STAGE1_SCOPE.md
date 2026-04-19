# Alcance de Fase 1

## Sí entra en Fase 1

- lectura de corpus reales
- canonización a schema silver
- alineación base por corpus
- normalización básica
- exportación a Parquet
- muestras legibles (`csv`, `jsonl`, `md`, `json`)
- trazabilidad mínima (`origin_path`, `doc_group_id`, `segment_key`, `metadata`)
- UI para configurar, previsualizar y ejecutar la canonización
- CLI para ejecutar la misma canonización con config YAML
- reportes mínimos reproducibles

## No entra todavía en Fase 1

- deduplicación exacta o difusa seria
- filtrado fuerte de calidad
- decontamination
- scoring por perplejidad
- curriculum ordering
- domain mixing final con muestreo probabilístico efectivo
- tokenización final para entrenamiento
- packing para GPT/BERT
- paralelización distribuida con PySpark

## Comentario sobre MultiUN y OpenSubtitles

En Fase 1 ambos corpus quedan soportados con alineación base monotónica y trazabilidad, pero **no** se consideran corpora con alineación cerrada de calidad final. La validación y el filtrado fuerte se reservan para la fase siguiente.

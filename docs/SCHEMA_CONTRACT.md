# Contrato de schema de Fase 1

Versión congelada: `stage1-v1`

Esta versión congela el schema canónico de salida silver para las tres tablas base:

- `segments`
- `pairs`
- `documents`

La regla para Fase 1 es simple: **no se agregan, renombran ni eliminan columnas** salvo que aparezca un problema real de lectura, persistencia o trazabilidad. Cualquier cambio posterior debe subir la versión del contrato.

## segments

Columnas, en orden:

- `dataset_name`
- `domain`
- `origin_path`
- `doc_group_id`
- `metadata`
- `segment_id`
- `lang`
- `text_raw`
- `text_norm`
- `sequence_index`
- `segment_key`
- `segment_key_numeric`
- `speaker`
- `is_dialogue`
- `can_concat_left`
- `can_concat_right`
- `casing_profile`
- `num_chars`
- `num_words`
- `quality_flags`

## pairs

Columnas, en orden:

- `dataset_name`
- `domain`
- `origin_path`
- `doc_group_id`
- `metadata`
- `pair_id`
- `pair_index`
- `src_lang`
- `tgt_lang`
- `src_text_raw`
- `tgt_text_raw`
- `src_text_norm`
- `tgt_text_norm`
- `src_segment_keys`
- `tgt_segment_keys`
- `src_sequence_indices`
- `tgt_sequence_indices`
- `alignment_type`
- `src_words`
- `tgt_words`
- `length_ratio`
- `quality_flags`

## documents

Columnas, en orden:

- `dataset_name`
- `domain`
- `origin_path`
- `doc_group_id`
- `metadata`
- `document_id`
- `src_lang`
- `tgt_lang`
- `split_hint`
- `is_parallel`
- `segment_count_src`
- `segment_count_tgt`
- `pair_count`
- `total_chars_src`
- `total_chars_tgt`
- `total_words_src`
- `total_words_tgt`

## Semántica mínima

- `text_raw`: texto leído del origen, sin normalización fuerte.
- `text_norm`: texto normalizado en Fase 1.
- `doc_group_id`: identificador estable del grupo lógico que permite reconstruir contexto y evitar concatenaciones incorrectas.
- `metadata`: metadatos auxiliares por fila; si no hay contenido se serializa como `null` para Parquet.
- `quality_flags`: banderas no destructivas; en Fase 1 no implican descarte fuerte.

## Compatibilidad esperada

Este contrato está pensado para:

- inspección humana en CSV/JSONL
- almacenamiento intermedio en Parquet
- exportación posterior a datasets tokenizados
- trazabilidad para depuración de alineación

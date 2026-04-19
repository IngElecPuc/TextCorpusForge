# TextForge · Plan actualizado de Fase 1

## 1. Punto de partida real observado en la muestra

La muestra ya permite fijar una decisión estructural importante:

- **DGT-2019**, **Europarl.v8** y **UNPC** traen archivos XML con enlaces tipo `xtargets`, es decir, alineamiento explícito por segmento.
- **EUbookshop** trae archivo `.ids`, que también aporta alineamiento explícito o semiexplícito por identificadores laterales.
- **MultiUN** y **OpenSubtitles** aparecen como textos bilingües laterales, pero en esta fase no hay garantía de alineamiento confiable por línea.
- En **OpenSubtitles** el orden es claramente conversacional, con guiones, intervenciones cortas y señales de posible deriva entre lados, por lo que no conviene forzar pares todavía.

### Conclusión operativa

La Fase 1 no debe asumir que todo corpus paralelo produce inmediatamente una tabla única de pares confiables.
Debe producir dos salidas canónicas distintas:

1. `segments.parquet`: unidades atómicas ordenadas y trazables.
2. `pairs.parquet`: solo donde existe alineamiento explícito o suficientemente confiable.

Además debe producir una tercera tabla resumida:

3. `documents.parquet`: grupos documentales o conversacionales con conteos y metadatos.

---

## 2. Objetivo formal de Fase 1

Tener un pipeline reproducible que:

- lea corpora desde carpeta,
- interprete formatos `txt`, `xml`, `tmx`, `tsv` e `ids`,
- escriba una capa silver canónica en Parquet,
- conserve el orden interno de los segmentos,
- conserve trazabilidad suficiente para reconstruir contexto,
- deje reportes de conteo y muestras,
- permita configuración por UI en Tkinter y por CLI.

---

## 3. Decisión importante: qué **no** hacer todavía

En esta fase, **silver no llevará tokens especiales del modelo**.

No se insertarán todavía:

- `<bos>`
- `<eos>`
- `<sep>`
- `<mask>`
- tokens de padding
- plantillas de prompts

### Motivo

Eso pertenece a la capa **tokenized** o al exportador por tarea, no al silver canónico.
Si se insertan demasiado temprano, se contamina el dataset con decisiones de entrenamiento que luego cuesta revertir.

Silver debe guardar texto limpio + estructura + trazabilidad.

---

## 4. Schema canónico de Fase 1

## 4.1 Tabla `segments`

Cada fila representa un segmento atómico reutilizable.

Campos clave:

- `dataset_name`
- `domain`
- `origin_path`
- `doc_group_id`
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
- `metadata`

### Función de esta tabla

Permite:

- rearmar documentos,
- concatenar contexto largo,
- construir BERT/GPT más adelante,
- revisar calidad línea a línea,
- preservar corpora aún no alineados.

## 4.2 Tabla `pairs`

Cada fila representa un par alineado de entrenamiento.

Campos clave:

- `pair_id`
- `pair_index`
- `doc_group_id`
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
- `metadata`

### Tipos de alineamiento iniciales

- `ces_explicit`
- `ids_explicit`
- `tmx_explicit`
- `tsv_explicit`

## 4.3 Tabla `documents`

Cada fila resume un grupo documental o conversacional.

Campos clave:

- `document_id`
- `doc_group_id`
- `src_lang`
- `tgt_lang`
- `is_parallel`
- `segment_count_src`
- `segment_count_tgt`
- `pair_count`
- `total_chars_src`
- `total_chars_tgt`
- `total_words_src`
- `total_words_tgt`

---

## 5. Criterio de agrupación para contexto largo

El proyecto necesita columnas que permitan concatenar texto después, pero sin mezclar material que no debería tocarse.

### Regla general

La concatenación futura debe ocurrir **solo dentro de un mismo `doc_group_id`**.

### Por dataset

- **DGT / Europarl / UNPC**: `doc_group_id` se deriva de los nombres `fromDoc` y `toDoc` del alineamiento XML.
- **EUbookshop**: `doc_group_id` se deriva de las rutas laterales del `.ids`.
- **MultiUN**: por ahora se conserva como stream bilingüe por archivo o por raíz, sin pares forzados.
- **OpenSubtitles**: se conserva como stream segmentado de diálogo; por defecto `can_concat_left/right = false` para evitar unir parlamentos de forma agresiva.

---

## 6. Decisiones de limpieza mínima en Fase 1

La normalización de esta etapa será deliberadamente conservadora.

### Sí se hace

- normalización Unicode (`NFC`)
- reparación de encoding recuperable (`ftfy`, si está disponible)
- normalización de espacios y `NBSP`
- eliminación de caracteres de control
- trimming externo

### No se hace todavía

- lowercasing global
- remoción agresiva de signos especiales
- eliminación de marcadores protocolarios tipo `<< >>`
- deduplicación
- filtrado por perplejidad
- detección de idioma
- alineación automática compleja

### Nota sobre mayúsculas

No se alterará el casing en silver.
En cambio, se guarda un `casing_profile` para permitir decisiones posteriores.

---

## 7. Tratamiento por corpus en Fase 1

## 7.1 DGT-2019.en-es

- reader: `ces_alignment_xml`
- entradas: `.en`, `.es`, `.xml`
- salida: segmentos + pares explícitos + resumen documental

## 7.2 Europarl.v8.en-es

- reader: `ces_alignment_xml`
- entradas: `.en`, `.es`, `.xml`
- el XML contiene 1:1 y también 1:n o n:1
- salida: segmentos + pares explícitos

## 7.3 UNPC.en-es

- reader: `ces_alignment_xml`
- el XML usa claves del tipo `1:1;1:1`
- esas claves se preservan en `segment_key`
- salida: segmentos + pares explícitos

## 7.4 EUbookshop.en-es

- reader: `ids_sidecar`
- entradas: `.en`, `.es`, `.ids`
- se preservan claves como `s4.1`, `s46.1 s46.2`, etc.
- salida: segmentos + pares explícitos

## 7.5 MultiUN.en-es

- reader: `parallel_sidecar_plain`
- en esta fase no se asume alineamiento confiable por línea
- salida: streams segmentados bilingües sin tabla de pares confiables

## 7.6 OpenSubtitles.en-es

- reader: `parallel_sidecar_plain`
- se marca como `is_dialogue = true`
- no se generan pares confiables en esta fase
- salida: streams segmentados con trazabilidad conversacional

---

## 8. Reportes de Fase 1

Cada dataset deja:

- `*_report.json`
- `*_samples.md`

Los reportes incluyen:

- cantidad de documentos
- cantidad de segmentos
- cantidad de pares
- segmentos por idioma
- segmentos vacíos tras normalización
- media de palabras por segmento
- media de ratio de longitud por par
- distribución por tipo de alineamiento

---

## 9. UI de Tkinter en esta fase

La UI queda enfocada a configuración y exportación de presets.

### Debe permitir

- elegir tarea destino (`seq2seq_mt`, `bert_pretrain`, `gpt_pretrain`)
- elegir dominio objetivo
- fijar presupuesto aproximado de tokens
- activar o desactivar datasets
- seleccionar carpeta por dataset
- fijar porcentaje de mezcla por dataset
- validar que la mezcla sume 100%
- exportar preset YAML
- exportar overrides de datasets

### No hace todavía

- no ejecuta alineación automática compleja
- no visualiza Parquet internamente
- no lanza entrenamiento

---

## 10. Entregables concretos de esta iteración

### Código no vacío para Fase 1

- readers base para `txt`, `xml`, `tmx`, `tsv`, `ids`
- builders por tipo de corpus
- schema canónico `segments / pairs / documents`
- normalización mínima
- manifest y reportes
- pipeline `canonicalize`
- UI Tkinter actualizada
- configs por corpus

### Artefacto esperado

Un ZIP con scaffold actualizado y listo para adaptar cuando llegue el `.txt` más detallado de estructura real.

---

## 11. Siguiente paso después de esta fase

Cuando llegue la descripción completa de la estructura real de carpetas y archivos, habrá que ajustar:

- resolución exacta de paths,
- segmentación documental por corpus,
- heurísticas de agrupación,
- si MultiUN admite alineación lineal usable o no,
- cómo detectar y tratar la deriva en OpenSubtitles,
- si conviene una tabla adicional `alignment_candidates` para la fase automática.

## Addendum: layout confirmado del input

La estructura física confirmada para la primera tanda de corpora es:

```text
/home/felpipe/Datasets/Textos paralelos/
├── DGT-2019.en-es/
├── EUbookshop.en-es/
├── Europarl.v8.en-es/
├── MultiUN.en-es/
├── OpenSubtitles.en-es/
└── UNPC.en-es/
```

Decisiones activas del scaffold regenerado:

- DGT, Europarl y UNPC se procesan con reader `ces_alignment_xml`.
- EUbookshop se procesa con reader `ids_sidecar`.
- MultiUN y OpenSubtitles se preservan en Fase 1 como streams bilingües ordenados, sin forzar pares en `pairs.parquet`.
- OpenSubtitles se marca como corpus dialogal para bloquear concatenación ciega entre turnos.
- Todas las configs de dataset ya incluyen `input_roots` apuntando al layout confirmado.

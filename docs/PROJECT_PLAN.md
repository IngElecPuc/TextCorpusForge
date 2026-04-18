# Plan de trabajo de TextForge

## 1. Propósito general

TextForge será una aplicación en Python para construir datasets limpios y trazables a partir de corpus textuales heterogéneos, con foco inmediato en:

- traducción automática con modelos encoder-decoder,
- preentrenamiento BERT,
- preentrenamiento GPT.

Además quedará preparada para tareas futuras como clasificación, NER, QA, resumen e instruction tuning.

El sistema debe permitir que el usuario defina:

- presupuesto aproximado de tokens final,
- mezcla porcentual entre datasets,
- dominio objetivo del problema,
- idioma o par de idiomas,
- tarea destino,
- reglas de filtrado y limpieza,
- rutas de entrada mediante selección de carpetas,
- modo de ejecución por CLI o por UI en Tkinter.

---

## 2. Requisito nuevo: presupuesto aproximado de tokens

El dataset objetivo no solo se definirá por corpus de entrada y filtros, sino también por un **tamaño aproximado en tokens** fijado por el usuario.

### 2.1 Implicancias

Se requiere una fase de planificación antes de exportar:

1. estimar el número de tokens por corpus o subcorpus,
2. aplicar pesos porcentuales solicitados,
3. proyectar cuántos documentos o pares deben extraerse por fuente,
4. construir una mezcla final lo más cercana posible al presupuesto objetivo,
5. informar desviación respecto del objetivo.

### 2.2 Estrategia recomendada

- mantener estadísticas por corpus: caracteres, palabras, documentos, pares y tokens estimados;
- permitir estimación rápida con:
  - conteo real usando tokenizer,
  - estimación preliminar por razón caracteres/tokens;
- seleccionar corpus por dominio y asignar cupos;
- permitir mezcla:
  - estricta por porcentaje,
  - flexible con rebalanceo si un corpus no alcanza volumen suficiente.

### 2.3 Ejemplo

Si el usuario pide:

- 120 millones de tokens,
- tarea `gpt_pretrain`,
- dominio objetivo `conversacional`,
- 60% OpenSubtitles,
- 20% Europarl,
- 20% MultiUN,

el sistema debe generar un plan de construcción aproximado, mostrar disponibilidad y advertir si alguna fuente no cubre su cuota.

---

## 3. Requisito nuevo: UI basada en Tkinter

La aplicación tendrá una interfaz local de escritorio en Tkinter para facilitar la configuración.

### 3.1 Funciones mínimas de la UI

- seleccionar carpetas fuente por dataset;
- elegir tarea objetivo:
  - seq2seq_mt,
  - bert_pretrain,
  - gpt_pretrain,
  - otras futuras;
- elegir dominio objetivo:
  - conversacional,
  - institucional,
  - parlamentario,
  - legal,
  - mixto,
  - personalizado;
- fijar presupuesto aproximado de tokens;
- fijar proporciones porcentuales entre datasets;
- cargar o guardar presets de configuración;
- previsualizar:
  - volumen detectado,
  - idiomas detectados,
  - resumen de filtros,
  - estimación de tokens;
- lanzar pipeline desde la UI;
- ver logs básicos y ruta de salida.

### 3.2 Alcance inicial de la UI

En la primera iteración, la UI no intentará reemplazar toda la CLI. Su objetivo será:

- capturar parámetros,
- validarlos,
- guardarlos como YAML o JSON,
- disparar pipelines predefinidos,
- mostrar resultados resumidos.

---

## 4. Decisiones de almacenamiento

La recomendación base se mantiene:

### 4.1 Formato principal
**Parquet particionado** como formato principal para capas bronze/silver/gold.

Razones:

- acceso secuencial eficiente en SSD,
- compresión y columnaridad,
- buena integración con DuckDB, PyArrow y Hugging Face Datasets,
- no depende de cargar todo en RAM.

### 4.2 Herramientas asociadas

- **DuckDB** para inspección, QA y consultas locales sobre Parquet;
- **PyArrow** para escritura/lectura robusta;
- **Hugging Face Datasets** para entrenamiento y cache Arrow;
- **memmap / bin-idx** solo en etapas finales donde convenga throughput extremo, especialmente GPT.

### 4.3 Descartes de momento

No usar PostgreSQL o MongoDB como backend principal de entrenamiento. Solo podrían servir más adelante para metadatos, dashboards o auditoría centralizada.

---

## 5. Capas de datos

## 5.1 Raw
Archivos originales sin alterar.

## 5.2 Bronze
Contenido extraído y estructurado mínimamente, todavía cercano al original.

## 5.3 Silver
Texto canonizado y filtrado con trazabilidad completa.

## 5.4 Gold
Datasets listos por tarea.

## 5.5 Tokenized
Representaciones finales para entrenamiento.

---

## 6. Etapas del pipeline

## Etapa 0. Ingesta, canonización mínima y planificación de mezcla

Esta etapa es la que se deja iniciada en este scaffolding.

### Objetivos

- leer corpus desde carpetas elegidas,
- descomprimir cuando haga falta,
- detectar estructura básica del dataset,
- convertir a un schema común,
- aplicar canonización mínima,
- escribir Parquet inicial,
- crear manifest,
- preparar insumos para estimación de tokens y mezcla.

### Incluye

- lectores básicos para TXT, XML, TMX y TSV;
- normalización Unicode;
- reparación básica de encoding recuperable;
- normalización de espacios y saltos;
- eliminación de caracteres de control;
- manifest JSON por corrida;
- escritura a Parquet;
- CLI mínima;
- UI mínima en Tkinter.

### Entregables

- `bronze/` y `silver/` iniciales,
- manifest con metadatos,
- reporte básico de conteos,
- configuración reproducible guardada.

---

## Etapa 1. Filtros baratos y trazables

- longitud mínima y máxima,
- ratio alfabético,
- proporción de mayúsculas,
- líneas sin puntuación final,
- patrones basura al inicio,
- pares idénticos,
- ratio de longitud source/target,
- confirmación de idioma.

---

## Etapa 2. Deduplicación

- deduplicación exacta,
- MinHash / LSH,
- deduplicación por n-gramas frecuentes,
- opciones semánticas en tareas seleccionadas.

---

## Etapa 3. Scoring de calidad

- perplejidad con modelo pequeño o KenLM,
- score semántico de alineación para MT,
- score de calidad agregado,
- descarte por umbrales configurables.

---

## Etapa 4. Decontamination

- hash exacto contra evaluation sets,
- overlap de n-gramas,
- similitud difusa contra benchmarks reservados.

---

## Etapa 5. Exportadores por tarea

- seq2seq_mt,
- bert_pretrain,
- gpt_pretrain,
- clasificación,
- NER,
- QA,
- summarization,
- instruction tuning.

---

## Etapa 6. Tokenización y packing

- entrenamiento de tokenizer,
- tokenización por lotes,
- packing GPT,
- collator dinámico para BERT,
- exportación Arrow,
- exportación memmap.

---

## 7. Reglas por tipo de tarea

## 7.1 MT
- detección de idioma en ambos lados,
- ratio de longitud,
- pares idénticos,
- score de alineación,
- eliminación de malos alineamientos.

## 7.2 BERT / GPT
- deduplicación agresiva,
- mezcla por dominio,
- filtro por perplejidad,
- manejo de documentos cortos según objetivo,
- control de diversidad por fuente.

## 7.3 Clasificación
- limpieza de etiquetas,
- stratified splitting,
- truncado consistente,
- balanceo o weighting.

## 7.4 NER
- validación BIO/BIOES,
- no cortar entidades al fragmentar,
- manejo explícito de solapamientos.

## 7.5 QA
- verificación de answer span,
- deduplicación de preguntas similares,
- normalización de respuestas.

## 7.6 Summarization
- ratio de compresión,
- cobertura extractiva,
- descarte de documentos truncados.

## 7.7 Instruction tuning
- verificación de formato,
- eliminación de respuestas evasivas,
- quality scoring con modelo juez en una etapa posterior.

---

## 8. Diseño de mezcla por dominios

El usuario podrá elegir un dominio objetivo. El sistema traducirá eso a una política de mezcla.

### Ejemplo de dominios

- `conversational`
  - prioriza OpenSubtitles;
- `institutional`
  - prioriza DGT, MultiUN, UNPC, EUbookshop;
- `parliamentary`
  - prioriza Europarl;
- `mixed`
  - mezcla configurable;
- `custom`
  - control total por porcentaje.

### Restricciones

- la suma de porcentajes debe ser 100%;
- si no hay suficiente volumen, el sistema debe:
  - advertir,
  - proponer rebalanceo,
  - o rellenar con fuentes compatibles.

---

## 9. Árbol base del proyecto

El árbol incluido en este scaffolding contempla:

- package principal `textforge`,
- UI Tkinter,
- configs por corpus y pipeline,
- módulos de normalización, filtros, dedup y exportación,
- scripts utilitarios,
- docs y tests.

---

## 10. Archivos no vacíos en esta entrega

Esta entrega incluye contenido en:

- `docs/PROJECT_PLAN.md`,
- archivos de la etapa 0,
- archivos mínimos de arranque del proyecto.

El resto queda como marcador estructural para desarrollos posteriores.

---

## 11. Prioridad de implementación real

Orden recomendado de trabajo a partir de este scaffolding:

1. adaptar lectores a la estructura real de DGT, EUbookshop, Europarl, MultiUN, OpenSubtitles y UNPC;
2. cerrar schema canónico de documentos y pares paralelos;
3. consolidar estimación de tokens y mezcla por porcentajes;
4. ampliar UI para validación y presets;
5. ejecutar primeras corridas pequeñas de ingesta;
6. recién después, endurecer filtros, dedup y scoring.

---

## 12. Criterios de éxito de la siguiente iteración

La siguiente iteración debería dejar resuelto:

- lectura real de tus datasets,
- escritura consistente de Parquet,
- manifest confiable,
- mezcla simple por porcentajes,
- estimación de tokens razonable,
- UI capaz de lanzar la etapa 0.

Con eso, el proyecto ya pasa de ser una idea a una base operable.

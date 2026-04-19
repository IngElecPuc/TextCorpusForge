# UI Controls

## Estado actual de ejecución

La aplicación corre el pipeline en un **worker thread** para no congelar la ventana.

- No usa PySpark.
- No usa multiprocessing pesado todavía.
- La estrategia actual es **serial incremental**, priorizando corte temprano real antes de paralelizar.

## Mejoras de esta iteración

- Layout en dos columnas.
- Botones siempre visibles.
- Barra de progreso por dataset.
- Botón de cancelación.
- Preview rápida.
- Lectura parcial real para `DGT`, `EUbookshop`, `Europarl`, `UNPC`, `MultiUN` y `OpenSubtitles` cuando se fijan límites pequeños.

## Controles

### Tarea destino
Etiqueta de intención del corpus: `seq2seq_mt`, `bert_pretrain`, `gpt_pretrain`.

### Dominio objetivo
Etiqueta del dominio principal: `mixed`, `conversational`, `institutional`, `parliamentary`, `legal`.

### Presupuesto total aprox. de tokens
Meta global declarativa del dataset final.

### Límite de pares
Corte temprano para pares paralelos. Es el control más útil para pruebas de traducción.

### Límite de segmentos
Corte temprano para segmentos monolingües.

### Límite de documentos
Corte temprano para grupos o documentos.

### Límite aprox. de tokens de salida
Corte por estimación barata de tokens. No es conteo real del tokenizer final.

### Tamaño de muestra exportada
Número de ejemplos exportados a JSONL/CSV/MD/JSON.

### Modo prueba / solo previsualización
No genera Parquet. Solo arma una muestra y exporta archivos inspeccionables.

### Detener tras el primer dataset activo
Útil para probar un solo corpus sin recorrer los demás.

### Exportar muestras legibles
Exporta JSONL/CSV/MD/JSON además del Parquet.

### Validar mezcla
Comprueba datasets activos y suma porcentual.

### Guardar preset YAML
Guarda la configuración visible de la UI.

### Previsualizar 20 ejemplos
Hace una lectura corta y exporta una muestra rápida.

### Generar silver Parquet
Ejecuta el pipeline `canonicalize` con la configuración actual.

### Cancelar ejecución
Solicita cancelación. El worker termina al siguiente punto seguro.

### Abrir carpeta de outputs
Muestra la carpeta `data/`.

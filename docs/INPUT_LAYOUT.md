# Input layout confirmado

Raíz esperada por defecto:

```text
/home/felpipe/Datasets/Textos paralelos
```

## Mapeo por corpus

### DGT-2019.en-es
- reader: `ces_alignment_xml`
- archivos:
  - `DGT.en-es.en`
  - `DGT.en-es.es`
  - `DGT.en-es.xml`

### EUbookshop.en-es
- reader: `ids_sidecar`
- archivos:
  - `EUbookshop.en-es.en`
  - `EUbookshop.en-es.es`
  - `EUbookshop.en-es.ids`

### Europarl.v8.en-es
- reader: `ces_alignment_xml`
- archivos:
  - `Europarl.v8.en-es.en`
  - `Europarl.v8.en-es.es`
  - `Europarl.v8.en-es.xml`

### MultiUN.en-es
- reader: `parallel_sidecar_plain`
- archivos:
  - `MultiUN.en-es.en`
  - `MultiUN.en-es.es`
- observación: en esta fase se conserva como stream bilingüe no alineado.

### OpenSubtitles.en-es
- reader: `parallel_sidecar_plain`
- archivos:
  - `OpenSubtitles.en-es.en`
  - `OpenSubtitles.en-es.es`
- observación: en esta fase se conserva como stream dialogal no alineado.

### UNPC.en-es
- reader: `ces_alignment_xml`
- archivos:
  - `UNPC.en-es.en`
  - `UNPC.en-es.es`
  - `UNPC.en-es.xml`

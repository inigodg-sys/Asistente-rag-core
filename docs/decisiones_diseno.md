## Overlap (chunking): 0 vs 120

**Fecha:** 2025-12-17  
**Objetivo:** Evaluar si el solape (overlap) entre chunks mejora la captura/recuperación de evidencias cuando una frase clave cae cerca del límite de chunk, y cuantificar el coste (número de chunks).

### Configuración
- Documento analizado: `data/raw/web/03_de_la_licitacion.md`  
- Evidencia buscada: **“El plazo del contrato será de ciento cuarenta y cuatro (144) meses …”**  
- Comparativa:
  - `overlap = 0` caracteres
  - `overlap = 120` caracteres (valor por defecto del pipeline)

### Método
Se generaron chunks para el mismo documento con ambos valores de overlap y se buscó la evidencia mediante patrón (regex) sobre el texto de los chunks, contabilizando:
- número total de chunks generados
- número de “hits” (chunks que contienen la evidencia)

Script utilizado:
- `tools/overlap_hit_144.py`

### Resultados
- `overlap = 0`:
  - chunks generados: **77**
  - hits (evidencia encontrada): **1**
- `overlap = 120`:
  - chunks generados: **113**
  - hits (evidencia encontrada): **1**

En ambos casos, la evidencia aparece completa dentro de un único chunk (misma sección `3`, id del tipo `03_de_la_licitacion:3:1`).

### Conclusión
Para esta evidencia concreta (“144 meses”) en `03_de_la_licitacion.md`, **no se observó mejora** en cobertura/recuperación al pasar de `overlap=0` a `overlap=120`, ya que la frase clave cabe completa en un chunk en ambos escenarios.  
El solape **sí incrementa** el número de chunks (y por tanto el coste de indexado/embeddings), por lo que su beneficio se justifica principalmente como **medida de robustez** ante evidencias cercanas a límites de chunk en otros documentos/secciones.

### Implicación para el pipeline
Se mantiene `overlap = 120` como valor por defecto por robustez, con la nota de que el valor óptimo puede depender del patrón de cortes del corpus y del método de chunking.

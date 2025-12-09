# Limpieza y Normalización de Documentos Markdown  
## Preparación del Corpus para el Asistente RAG – Licitación GF 001/2023  
### TFM – Big School (Iñaki Diez · 2025)

---

## 1. Introducción

Los documentos Markdown (`.md`) que forman el corpus principal del proyecto (capítulos y anexos de la licitación GF 001/2023) no proceden de una redacción manual perfecta, sino de procesos de conversión (PDF → MD, DOCX → MD, copias y pegados, etc.). Como consecuencia, presentan diversos problemas de formato y ruido textual.

Antes de aplicar el pipeline de ingesta, normalización y chunking, es necesario realizar una **limpieza y normalización previa** de estos Markdown para que:

- la estructura del pliego se reconozca correctamente,  
- los chunks se generen de forma coherente,  
- la trazabilidad normativa no se pierda,  
- y el rendimiento del RAG no se degrade.

Este documento describe el objetivo, los problemas típicos detectados y la estrategia de limpieza de los archivos Markdown.

---

## 2. Problemas típicos en los Markdown del corpus

Durante la inspección de los `.md` del proyecto, se observan los siguientes problemas frecuentes:

### 2.1 Numeraciones irregulares o rotas

- Aparición de patrones como `5.3.1.1 .` en lugar de `5.3.1.1`.  
- Números de artículo partidos en dos líneas (por ejemplo, `5.3.` en una línea y `1.1` en la siguiente).  
- Puntos, guiones o caracteres aislados tras la numeración.

Estos errores dificultan detectar las secciones normativas (por ejemplo, GF1, GF2, etc.) y afectan directamente al campo `section` de los chunks.

### 2.2 Saltos de línea no intencionados

- Frases partidas a la mitad debido al ancho de línea del PDF original.  
- Párrafos muy fragmentados, que no corresponden a la estructura lógica del texto.

Ejemplo de problema típico:

    La solución deberá cumplir con los requisitos técnicos
    establecidos en el Anexo A06, incluyendo las funcionalidades
    del sistema de gestión de flota...

Este tipo de corte perjudica el chunking y la generación de embeddings coherentes.

### 2.3 Encabezados mal formados

- Encabezados sin espacio tras los `#` (por ejemplo, `##5.3 Evaluación`).  
- Niveles de encabezado inconsistentes.  
- Secciones que deberían tener encabezado y no lo tienen.

Esto complica identificar correctamente capítulos, apartados y secciones.

### 2.4 Listas y viñetas corruptas

- Viñetas repetidas (`- - item`).  
- Líneas con guiones sueltos.  
- Listas transformadas en líneas independientes sin relación visual clara.

### 2.5 Caracteres extraños y artefactos de conversión

- Secuencias de espacios dobles o triples.  
- Caracteres no imprimibles.  
- Restos de marcas del PDF (encabezados/pies de página repetidos, numeración de páginas, etc.).

---

## 3. Impacto de la falta de limpieza en el RAG

Si no se limpia y normaliza el Markdown:

1. **Dificultades para detectar secciones**  
   La función de normalización que genera `SectionBlock` tendrá problemas para encontrar patrones como `5.3.1.1` o `A06.2.1`, lo que puede provocar que muchos chunks no tengan `section` asignado.

2. **Chunking poco coherente**  
   Los trozos de 600–900 caracteres pueden cortar frases en puntos arbitrarios, mezclando ideas distintas o dejando piezas sin sentido.

3. **Degradación de los embeddings**  
   El modelo de embeddings terminará representando texto con ruido, numeraciones rotas y artefactos, reduciendo la calidad de la recuperación.

4. **Pérdida de trazabilidad normativa**  
   Sin una correspondencia clara entre secciones del pliego y chunks, se dificulta justificar las respuestas del asistente con referencias exactas a capítulos y anexos.

En resumen, la limpieza de Markdown no es un lujo, sino un requisito técnico para el correcto funcionamiento del asistente RAG en un contexto regulatorio.

---

## 4. Objetivos de la limpieza y normalización de Markdown

El proceso de limpieza tiene los siguientes objetivos:

1. **Reconstruir la estructura lógica del pliego**  
   Hacer que capítulos, secciones y apartados sean detectables por patrones estables.

2. **Unificar y estabilizar numeraciones normativas**  
   Asegurar que expresiones como `5.3.1.1`, `A06.2.1` o similares aparezcan en una sola línea, sin caracteres basura.

3. **Eliminar ruido visual y artefactos de conversión**  
   Quitar caracteres sueltos, espacios innecesarios y residuos de formato.

4. **Mejorar la legibilidad semántica**  
   Conseguir que cada párrafo sea una unidad lógica coherente, facilitando chunking y embeddings.

5. **Preparar el texto para la función `normalize_markdown_sections`**  
   Simplificar la tarea de dividir el documento en `SectionBlock` fiables.

---

## 5. Estrategia general de limpieza

La limpieza se implementará mediante una función conceptual:

    clean_markdown(raw_md: str) -> str

que se ejecuta antes de `normalize_markdown_sections`.

La estrategia incluye al menos los siguientes pasos:

### 5.1 Normalización de espacios y saltos de línea

- Eliminar espacios repetidos en líneas (`"  "` → `" "`).  
- Unificar saltos de línea cuando una frase ha sido cortada por la conversión, respetando los párrafos lógicos.  
- Evitar líneas que contengan únicamente un número o un punto si claramente forman parte de un artículo numerado y deben fusionarse con la siguiente línea.

### 5.2 Corrección de numeraciones

- Detectar patrones de numeración normativa (`X.Y.Z`, `X.Y.Z.W`, `A06.2.1`, etc.) mediante expresiones regulares.  
- Unificar numeraciones partidas en varias líneas en una sola.  
- Eliminar puntos o guiones sobrantes tras la numeración.

Ejemplos de normalización:

- `5.3.1.1 .` → `5.3.1.1`  
- Línea `5.3.` seguida de línea `1.1 GF1` → `5.3.1.1 GF1`

### 5.3 Normalización de encabezados

- Asegurar que los encabezados tienen el formato correcto, por ejemplo:  
  `## 5.3 Evaluación y adjudicación`  
  `### 5.3.1 GF1`

- Insertar un espacio entre el símbolo de encabezado (`#`, `##`, `###`) y el texto cuando falte.  
- Uniformizar el uso de niveles de encabezado (`##`, `###`) según la estructura del documento.

### 5.4 Reparación de listas

- Arreglar viñetas dañadas (por ejemplo, `- - Item` pasa a `- Item`).  
- Unir líneas que claramente formen parte del mismo ítem de lista.  
- Eliminar líneas compuestas solo por guiones sin contenido real.

### 5.5 Eliminación de artefactos

- Eliminar caracteres no imprimibles.  
- Quitar restos de marcas del PDF: números de página, encabezados duplicados, pies de página.  
- Normalizar comillas, guiones largos y otros símbolos según convenga.

---

## 6. Integración en el pipeline de ingesta

La función `clean_markdown` se integrará en el pipeline de la siguiente forma:

1. `load_markdown(doc)` lee el contenido bruto del `.md`.  
2. `clean_markdown(raw_md)` normaliza el texto:  
   - corrige numeraciones,  
   - limpia saltos de línea y encabezados,  
   - elimina ruido de conversión.  
3. `normalize_markdown_sections(md_limpio, doc)` recibe ya un texto mucho más estructurado.  
4. `chunks_from_markdown_sections(sections, doc)` genera chunks coherentes y trazables.

Esta integración asegura que el chunking trabaje sobre un texto preparado y no sobre una conversión cruda.

---

## 7. Alineación con el diseño del TFM

La limpieza de Markdown:

- refuerza el diseño conceptual de modelo de documento y chunking,  
- mejora la calidad de los embeddings y de la recuperación RAG,  
- contribuye directamente a los KPIs definidos (Recall@k, Faithfulness),  
- y demuestra una aproximación profesional al tratamiento de datos normativos.

Desde un punto de vista académico, este proceso puede describirse en el capítulo de **Preparación del Corpus** o en el de **Metodología**, explicando:

- por qué es necesaria la limpieza,  
- qué problemas se encontraron,  
- y cómo se solucionaron de forma sistemática.

---

## 8. Próximos pasos

Tras documentar la necesidad y la estrategia de limpieza, los pasos siguientes serán:

1. Diseñar, a nivel técnico, la función `clean_markdown(raw_md: str) -> str` con reglas concretas y, si es necesario, expresiones regulares.  
2. Implementar dicha función en Python, integrándola en el módulo `ingest.py`.  
3. Probar la limpieza con varios `.md` representativos (por ejemplo, `05_evaluacion_adjudicacion.md` y anexos A06/A10).  
4. Revisar manualmente algunos ejemplos antes y después de la limpieza para validar su efectividad.

Con ello, el corpus Markdown quedará adecuadamente preparado para el pipeline de ingesta, normalización y chunking del asistente RAG.

---

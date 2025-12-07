# Pipeline de Ingesta, Normalización y Chunking  
## Flujo de Procesamiento del Corpus de la Licitación GF 001/2023  
### TFM – Big School (Iñaki Diez · 2025)

---

## 1. Introducción

El asistente RAG desarrollado en este proyecto debe operar sobre un corpus heterogéneo formado por capítulos normativos, anexos técnicos, tablas evaluativas y definiciones oficiales de la licitación GF 001/2023. Para que este corpus pueda ser utilizado de forma fiable por un modelo de lenguaje, es necesario transformarlo mediante un pipeline de ingesta cuidadosamente diseñado.

Este documento describe dicho pipeline: un conjunto de procesos destinados a descubrir, leer, normalizar y convertir los documentos brutos del proyecto en *chunks* semánticos estructurados, alineados con el modelo de documento del asistente y listos para el posterior cálculo de embeddings e indexación vectorial.

---

## 2. Rol del Pipeline de Ingesta en el Sistema RAG

El pipeline de ingesta constituye la primera etapa del sistema RAG. Sus responsabilidades principales son:

1. **Descubrir documentos** en el repositorio del proyecto.  
2. **Leerlos y parsearlos** según su formato (Markdown, CSV, JSON).  
3. **Normalizar semánticamente** su contenido.  
4. **Generar chunks** conformes al modelo definido en el diseño conceptual.

El resultado del pipeline es una colección de chunks homogéneos, trazables y estructurados, que servirán de insumo para las etapas posteriores:

- embeddings (vectorización),
- almacenamiento en FAISS,
- recuperación semántica (retriever),
- y generación de respuestas fundamentadas.

---

## 3. Estructura General del Pipeline

El pipeline se organiza en cuatro capas consecutivas:

1. **Descubrimiento de documentos**  
2. **Lectura y parseo**  
3. **Normalización semántica**  
4. **Generación de chunks**

Esta organización permite aislar responsabilidades, facilitar la depuración y asegurar una comprensión clara del flujo de datos.

---

## 4. Capa 1: Descubrimiento de Documentos

En esta fase se identifican todos los ficheros relevantes del corpus, almacenados en:

- `data/raw/web/` → capítulos y anexos (Markdown)  
- `data/raw/csv/` → tablas normalizadas (GF1, GF2, GF3, EIPU, ECPU, funcionalidades, plan de capacitación)  
- `data/raw/json/` → definiciones del pliego y otros datos estructurados  

Para cada documento se registran:

- Ruta del archivo (`source`)  
- Formato físico (`md`, `csv`, `json`)  
- Tipo lógico (`doc_type`): normativa, tabla, definición, formulario o tutorial  

Esta catalogación inicial garantiza que todos los documentos se procesen de manera coherente.

---

## 5. Capa 2: Lectura y Parseo

Aquí se obtiene el contenido bruto de cada documento, sin aplicar aún las reglas de chunking.

### 5.1 Markdown (Capítulos y Anexos)

- Se lee el texto completo del fichero.  
- Se preservan encabezados, numeraciones y listas.  
- Se mantiene la estructura jerárquica (crucial para artículos, apartados y secciones).

### 5.2 CSV (Tablas de Evaluación y Características)

- Se leen las cabeceras para identificar las columnas.  
- Cada fila se transforma en un registro estructurado.  
- Se conserva toda la información necesaria para construir frases semánticas.

### 5.3 JSON (Definiciones y Datos Estructurados)

- Se parsean los pares `termino`–`definicion` y sus identificadores (`id`).  
- Se valida la consistencia del contenido.

Esta capa produce representaciones internas coherentes para la normalización posterior.

---

## 6. Capa 3: Normalización Semántica

La normalización convierte el contenido de cada documento en texto comprensible por un modelo de lenguaje, respetando su estructura normativa y su función dentro del pliego.

### 6.1 Normalización de Markdown

- Limpieza de espacios redundantes y saltos innecesarios.  
- Separación del contenido en secciones según encabezados y numeraciones (por ejemplo, `5.3.1.1`).  
- Preparación de bloques listos para chunking con solape.

### 6.2 Normalización de CSV

Cada fila se convierte en una **frase semántica**:

Ejemplo (GF1):  
> “En GF1, un proyecto con 2000–3999 buses recibe 15 puntos según Art. 5.3.1.1.”

Beneficios:

- Los modelos de lenguaje comprenden mejor el contenido.  
- Se mantiene la trazabilidad hacia la tabla original mediante metadatos.

### 6.3 Normalización de JSON

- Cada definición se transforma en texto exacto.  
- Se asegura la preservación del lenguaje normativo oficial.  
- Se asocia cada término a su identificador (`section = id`).

---

## 7. Capa 4: Generación de Chunks

Aplicando el modelo de documento, se generan chunks homogéneos a partir de contenido normalizado.

### 7.1 Chunks de Normativa

- Chunk por sección/subsección.  
- 600–900 caracteres por chunk.  
- Overlap ≈ 120 caracteres.  
- Inclusión de:  
  - `doc_type = "normativa"`  
  - `section` = identificador normativo (ej. `5.3.1.1`)  
  - `source` = archivo Markdown  

### 7.2 Chunks de Tablas

- Cada frase semántica de fila → un chunk.  
- Se añaden metadatos de fila/columna.  
- `doc_type = "tabla"`.

### 7.3 Chunks de Definiciones

- Un chunk por término definido.  
- Representación exacta del texto normativo.  
- `doc_type = "definicion"`.

### 7.4 Documento “Rag (2)” (opcional)

- Se chunkifica como `doc_type = "tutorial"`.  
- Se excluye de las respuestas normativas.  
- Sirve de apoyo pedagógico para el TFM.

---

## 8. Resultado del Pipeline

El pipeline produce una colección final de chunks que:

- siguen el modelo formal del proyecto,  
- están alineados con la estructura de la licitación,  
- contienen texto semántico listo para vectorización,  
- incluyen trazabilidad normativa completa,  
- permiten evaluación rigurosa del sistema RAG.

Este conjunto puede almacenarse como un JSONL procesado o directamente entregarse a la capa de embeddings.

---

## 9. Alineación con los Objetivos del TFM

Este pipeline cumple varios objetivos clave del Trabajo Fin de Máster:

- **Rigor técnico:** tratamiento profesional de datos heterogéneos.  
- **Claridad conceptual:** separación de capas y roles del sistema.  
- **Reproducibilidad:** pipeline determinista y documentado.  
- **Trazabilidad normativa:** absolutamente necesaria para una licitación real.  
- **Aprendizaje profundo:** comprensión integral del funcionamiento de un sistema RAG.  
- **Excelencia académica:** documento defendible ante tribunal, claro y de alta calidad.

---

## 10. Conclusión

El pipeline de ingesta, normalización y chunking proporciona la base sobre la que se construye todo el asistente RAG. Gracias a este diseño, los documentos brutos de la licitación GF 001/2023 se transforman en representaciones semánticas consistentes y trazables, aptas para recuperación eficiente y generación de respuestas fundamentadas.

Este documento debe considerarse parte esencial del diseño conceptual del TFM.

---

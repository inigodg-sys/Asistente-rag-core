# Diseño Técnico del Pipeline de Ingesta (`ingest.py`)  
## Arquitectura de Implementación para el Asistente RAG – GF 001/2023  
### TFM – Big School (Iñaki Diez · 2025)

---

## 1. Introducción

Este documento describe el diseño técnico del módulo `ingest.py`, responsable de transformar el corpus de la licitación GF 001/2023 en una colección de *chunks* homogéneos y trazables.

El diseño está alineado con:

- El modelo de documento y chunking definido en el proyecto.  
- El pipeline conceptual de ingesta, normalización y chunking.  
- La estructura real del corpus: Markdown, CSV, JSON.  
- Los objetivos académicos y técnicos del TFM.

El propósito es proporcionar una arquitectura clara y defendible, antes de pasar al pseudocódigo y a la implementación.

---

## 2. Objetivo del módulo `ingest.py`

`ingest.py` debe:

1. Descubrir todos los documentos relevantes del corpus.  
2. Leer y parsear cada documento según su formato físico.  
3. Normalizar semánticamente su contenido.  
4. Generar chunks siguiendo el modelo unificado del TFM.  
5. Devolver una lista final de chunks, lista para embeddings y FAISS.

La arquitectura sigue un enfoque ETL:

- Extract → Descubrir y leer documentos.  
- Transform → Normalizar semánticamente.  
- Load → Construir chunks coherentes.

---

## 3. Estructura conceptual del módulo

El diseño se organiza en tres bloques:

1. Tipos y modelos internos.  
2. Funciones por capa del pipeline.  
3. Función orquestadora principal.

Cada bloque refleja una parte necesaria de la implementación final.

---

## 4. Modelos internos

Conceptualmente se definen los siguientes tipos:

### 4.1. `DocumentDescriptor`

Representa metadatos sobre un archivo detectado en el repositorio.

Campos sugeridos:

- `path` → ruta del archivo.  
- `doc_type` → tipo lógico del documento (`"normativa"`, `"tabla"`, `"definicion"`, `"tutorial"`, `"formulario"`).  
- `format` → tipo físico (`"md"`, `"csv"`, `"json"`).

### 4.2. `SectionBlock`

Representa una sección o subsección de contenido normativo antes del chunking.

Campos sugeridos:

- `section_id` → identificador de sección, por ejemplo `5.3.1.1`, `A06.2.1`.  
- `text` → texto completo de la sección.

### 4.3. `CsvRow`

Representa una fila de un CSV ya leída y estructurada (por ejemplo, una fila de GF1 o de funcionalidades A10).

Puede almacenar:

- valores por columna (`rango_buses`, `puntos`, etc.),  
- el índice de fila,  
- y metadatos adicionales.

### 4.4. `DefinitionEntry`

Representa una definición limpia del pliego extraída del JSON de definiciones.

Campos sugeridos:

- `id` → identificador normativo (por ejemplo, `"2.8"`).  
- `termino` → término definido (por ejemplo, `"COF"`).  
- `definicion` → texto completo de la definición.

### 4.5. `Chunk`

Modelo final que cumple el documento oficial del TFM:

- `text` → contenido limpio y normalizado.  
- `source` → ruta del archivo de origen.  
- `doc_type` → tipo lógico (`"normativa"`, `"tabla"`, `"definicion"`, `"formulario"`, `"tutorial"`).  
- `section` → identificador normativo o de sección, si aplica.  
- `id` → identificador interno del chunk (opcional).  
- `tags` → lista de etiquetas temáticas.  
- `metadatos` → diccionario con información adicional (fila, columna, término, valor, etc.).

---

## 5. Funciones del pipeline

Las funciones se agrupan por capa del pipeline: descubrimiento, lectura y parseo, normalización y generación de chunks.

---

### 5.1 Capa 1 — Descubrimiento de documentos

Función principal:

- `discover_documents(config) -> list[DocumentDescriptor]`

Responsabilidades:

- Recorrer las rutas `data/raw/web`, `data/raw/csv` y `data/raw/json`.  
- Crear un `DocumentDescriptor` para cada archivo detectado.  
- Asignar `doc_type` y `format` según la ubicación y extensión:
  - Archivos en `web/*.md` → normalmente `doc_type = "normativa"` o `"formulario"`.  
  - Archivos en `csv/*.csv` → `doc_type = "tabla"`.  
  - Archivos en `json/*.json` (por ejemplo `definiciones.json`) → `doc_type = "definicion"`.

Esta capa prepara la lista de documentos a procesar en las etapas posteriores.

---

### 5.2 Capa 2 — Lectura y parseo

Aquí se extrae el contenido bruto de cada documento, sin aplicar aún el chunking.

Funciones típicas:

- `load_markdown(doc: DocumentDescriptor) -> str`  
  - Lee el texto completo de un archivo `.md`.  
  - Preserva saltos de línea y estructura básica.

- `load_csv(doc: DocumentDescriptor) -> list[dict]`  
  - Carga un archivo CSV y devuelve una lista de filas como diccionarios.  

- `load_json_definitions(doc: DocumentDescriptor) -> list[dict]`  
  - Lee `definiciones.json` y devuelve una lista de objetos con `id`, `termino` y `definicion`.

En esta capa, el sistema conoce el contenido pero aún no lo ha normalizado semánticamente.

---

### 5.3 Capa 3 — Normalización semántica

Esta capa convierte el contenido leído en unidades semánticas coherentes con el pliego.

#### 5.3.1 Normalización de Markdown

Función:

- `normalize_markdown_sections(raw_md: str, doc: DocumentDescriptor) -> list[SectionBlock]`

Responsabilidades:

- Dividir el Markdown en secciones y subsecciones basadas en:
  - encabezados (`#`, `##`, `###`),  
  - numeraciones de artículos / apartados (por ejemplo, `5.3.1.1`, `A06.2.1`),  
  - bloques de texto lógicos.

- Asignar a cada `SectionBlock`:
  - un `section_id` (cuando exista numeración),  
  - y el texto asociado.

#### 5.3.2 Normalización de CSV

Función:

- `normalize_csv_rows(rows: list[dict], doc: DocumentDescriptor) -> list[str]`

Responsabilidades:

- Convertir cada fila de la tabla en una frase semántica en lenguaje natural, por ejemplo:

  - “En GF1, un proyecto con 2000–3999 buses recibe 15 puntos según Art. 5.3.1.1.”

- Incluir, cuando sea posible, referencias a la sección normativa (por ejemplo, al artículo del Capítulo 5 al que pertenece la tabla).

El resultado es una lista de frases que representan la información de las tablas de manera legible y útil para un modelo de lenguaje.

#### 5.3.3 Normalización de definiciones (JSON)

Función:

- `normalize_definitions(entries: list[dict], doc: DocumentDescriptor) -> list[DefinitionEntry]`

Responsabilidades:

- Asegurar que cada entrada del JSON dispone de:
  - `id` normativo,  
  - `termino`,  
  - `definicion` limpia.

- Construir objetos `DefinitionEntry` listos para convertirse en chunks exactos.

---

### 5.4 Capa 4 — Generación de chunks

Una vez que el contenido está normalizado, se generan los chunks finales siguiendo el modelo unificado.

#### 5.4.1 Chunks de normativa / formularios

Función:

- `chunks_from_markdown_sections(sections: list[SectionBlock], doc: DocumentDescriptor) -> list[Chunk]`

Responsabilidades:

- Aplicar chunking con:
  - longitud objetivo de aproximadamente 600–900 caracteres,  
  - solape de unos 120 caracteres entre chunks consecutivos.

- Para cada chunk:
  - asignar `doc_type = "normativa"` o `"formulario"`,  
  - establecer `section` con el `section_id` del bloque si existe,  
  - completar `source`, `tags` y `metadatos` relevantes.

#### 5.4.2 Chunks de tablas (CSV)

Función:

- `chunks_from_csv_sentences(sentences: list[str], doc: DocumentDescriptor) -> list[Chunk]`

Responsabilidades:

- Convertir cada frase semántica generada en la normalización en un `Chunk`.  
- Asignar:
  - `doc_type = "tabla"`,  
  - `source` = fichero CSV correspondiente,  
  - `section` = referencia al apartado del pliego donde se define la tabla, si se conoce,  
  - `metadatos` = fila, columnas, valores, etc.

#### 5.4.3 Chunks de definiciones (JSON)

Función:

- `chunks_from_definitions(defs: list[DefinitionEntry], doc: DocumentDescriptor) -> list[Chunk]`

Responsabilidades:

- Crear un `Chunk` por cada `DefinitionEntry`.  
- Asignar:
  - `doc_type = "definicion"`,  
  - `section` = `id` de la definición (por ejemplo, `"2.8"`),  
  - `text` = definición exacta,  
  - `tags` = lista con `"definicion"` y el término definido.

#### 5.4.4 Documento “Rag (2)” como tutorial (opcional)

En caso de incluirlo:

- Se trataría como `doc_type = "tutorial"`.  
- Se excluiría del contexto normativo al responder preguntas sobre la licitación.  
- Su uso sería meramente pedagógico.

---

## 6. Función orquestadora

La función principal del módulo conectará todas las capas:

- `ingest_all_docs(config) -> list[Chunk]`

Responsabilidades:

1. Llamar a `discover_documents` para obtener todos los `DocumentDescriptor`.  
2. Para cada documento:
   - seleccionar la función de lectura adecuada (`load_markdown`, `load_csv`, `load_json_definitions`),  
   - aplicar la normalización correspondiente (`normalize_markdown_sections`, `normalize_csv_rows`, `normalize_definitions`),  
   - generar los chunks apropiados (`chunks_from_markdown_sections`, `chunks_from_csv_sentences`, `chunks_from_definitions`).  
3. Unificar todos los chunks en una única lista y devolverla.

Esta función será el punto de entrada para:

- scripts de línea de comandos,  
- notebooks de experimentación,  
- o módulos posteriores que generen embeddings e índices FAISS.

---

## 7. Alineación con el TFM y la visión industrial

Este diseño:

- Es modular: cada función tiene una responsabilidad clara.  
- Es transparente: facilita la explicación y defensa del diseño en el TFM.  
- Es escalable: permite añadir nuevos formatos o tipos de documentos sin reescribir todo el módulo.  
- Es generalizable: el mismo enfoque puede adaptarse a otras licitaciones y cuerpos normativos distintos.  
- Está alineado con el modelo de documento y chunking, garantizando coherencia total del proyecto.

---

## 8. Conclusión

El diseño técnico de `ingest.py` transforma el modelo conceptual del pipeline de ingesta en una arquitectura lista para implementar. Esta estructura:

- mantiene la trazabilidad normativa,  
- homogeniza documentos heterogéneos,  
- permite indexar información de forma fiable,  
- y proporciona una base sólida para la calidad del sistema RAG.

Con este diseño, estamos preparados para el siguiente paso: derivar el pseudocódigo completo y, posteriormente, la implementación real del módulo `ingest.py`.

---

# ASISTENTE-RAG-CORE

**TFM – Big-School** Asistente RAG (core) aplicado a la licitación **GF 001/2023** (Gestión de Flota + SIPU).

---

## Objetivo

Construir un **asistente RAG multiformato** que:

* Lea documentos en PDF/DOCX/HTML/MD/TXT/CSV/JSON.
* Recupere pasajes por similitud.
* Responda **solo con ese contexto**.
* Incluya **citas a las fuentes** (trazabilidad).

Aplicado al corpus de la licitación pública para la **provisión de servicios tecnológicos de Gestión de Flota (SGF) e Información a Personas Usuarias (SIPU)** del Sistema de Transporte Público Metropolitano.

---

## Principios

* **Veracidad > elocuencia:** Si no hay evidencia suficiente → *"no tengo suficiente información para afirmar esto"*.
* **Trazabilidad:** Cada respuesta debe poder enlazarse a uno o varios documentos/orígenes concretos.
* **Reproducibilidad:** Mismo input → misma consulta → mismos resultados (controlados).
* **Simplicidad → mejora:** Empezar con una arquitectura clara y después iterar.

---

## Diagrama (Big Picture)

```text
Ingesta (PDF/DOCX/HTML/MD/TXT/CSV/JSON)
  └─ Limpieza/normalización → { text, source, section_path, page, tags }
      └─ Chunking con solape (size≈800, overlap≈120)
          └─ Embeddings (Sentence-Transformers)
              └─ Índice vectorial (FAISS, persistente)
                  └─ Recuperación top-k (k≈5–8)
                      └─ (Mejora) Re-ranking con Cross-Encoder
                          └─ Prompt seguro + LLM → Respuesta con citas
```

---

## Corpus actual (pliego GF + anexos)

El corpus principal del proyecto está formado por:

### Capítulos normativos del pliego (`data/raw/web/`)

* `01_antecedentes_generales.md`
* `02_definiciones.md`
* `03_de_la_licitacion.md`
* `04_de_las_ofertas.md`
* `05_evaluacion_adjudicacion.md`
* `06_al_09_obligaciones_confidencialidad_jurisdiccion_interpretacion.md`

### Anexos (formularios y especificaciones técnicas)

* `A02_A05_antecedentes_generales.md` – Identificación oferente, consorcio, declaraciones.
* `A06_formulario_de_la_solucion.md` – Arquitectura SGF/SIPU, hardware mínimo, comunicaciones.
* `A07_formulario_experiencia_GF.md` – Experiencia GF1/GF2/GF3.
* `A08_formulario_experiencia_EIPU.md` – Experiencia en información a personas usuarias.
* `A09_formulario_experiencia_ECPU.md` – Experiencia en contadores de personas usuarias.
* `A10_Descripciones_tecnicas_de_las_funcionalidades.md` – Funcionalidades 3.1.x y 3.2.x.
* `A11_formulario_plan_de_capacitacion.md`
* `A12_formulario_de_oferta_economica.md`
* `A13_valores_de_reposicion.md`

### Tablas normalizadas en CSV (`data/raw/csv/`)

Este conjunto de `.md` + `.csv` constituye el corpus de entrada para el sistema RAG del TFM.

#### Criterios de evaluación (Cap. 5):
* `cronograma_licitacion.csv`
* `experiencia_gf1.csv`
* `experiencia_gf2.csv`
* `experiencia_eipu.csv`
* `experiencia_ecpu.csv`
* `plan_capacitacion_pc.csv`

#### Arquitectura técnica (A06):
* `a06_computador_embarcado.csv`
* `a06_consola_conductor.csv`
* `a06_contador_personas.csv`
* `a06_modem_bus.csv`
* `a06_componentes_hardware.csv`

#### Funcionalidades (A10):
* `a10_funcionalidades_mandatorias.csv`
* `a10_funcionalidades_adicionales.csv`

#### Plan de capacitación (A11):
* `a11_personas_capacitar.csv`

### Datos estructurados en JSON (`data/raw/json/`)

Además del corpus en Markdown y de las tablas normalizadas en CSV, el proyecto incluye datos estructurados en formato JSON utilizados para mejorar la precisión y trazabilidad del sistema RAG.

#### Definiciones del pliego (Capítulo 2)
* **Archivo:** `definiciones.json`
* **Contenido:** Todas las definiciones formales del Capítulo 2 del pliego, en formato estructurado:

```json
{
  "id": "2.8",
  "termino": "Centros de Operacion de Flota (COF)",
  "definicion": "Unidad del OST mediante la cual controlan y supervisan el desempeño de la prestación de sus servicios."
}
```

**Estos datos permiten:**
* Consultas precisas sobre términos normativos.
* Chunking semántico altamente estructurado.
* Menos alucinaciones en respuestas que requieren definiciones exactas.
* Mayor trazabilidad y consistencia normativa.

---

## Modelo de Documento RAG (Chunk Model)

El sistema RAG utiliza un modelo unificado para representar todos los fragmentos de información procesados por el asistente.

Cada chunk, independientemente de su origen (MD, CSV o JSON), se normaliza en la siguiente estructura:

```json
{
  "text": "Contenido del fragmento utilizado para embeddings",
  "source": "ruta/archivo_de_origen.md",
  "type": "md | csv | json",
  "section": "capítulo/anexo/sección",
  "id": "identificador interno (si existe, ej: definición 2.8)",
  "tags": ["evaluacion", "GF1", "funcionalidades", "PC", ...],
  "metadatos": {
    "fila": 12, 
    "columna": "puntaje",
    "termino": "COF",
    "definicion": "Unidad del OST…"
  }
}
```

### Tipos de chunk

| Tipo | Origen | Ejemplo | Uso en RAG |
| :--- | :--- | :--- | :--- |
| **MD** | Capítulos y Anexos | `05_evaluacion_adjudicacion.md` | Normativa, fórmulas, reglas |
| **CSV** | Tablas normalizadas | `experiencia_gf1.csv` | Criterios cuantitativos |
| **JSON** | Datos semánticos | `definiciones.json` | Definiciones exactas |

### Cómo se usarán en el asistente
* **MD:** Chunking textual clásico (800 tokens con solape).
* **CSV:** Cada fila se convierte en frase semántica enriquecida.
  * *Ejemplo:* “Rango 2000–3999 buses corresponde a 15 puntos en GF1 según Tabla 5.3.1.1”
* **JSON:** Definición normativa limpia.
  * *Ejemplo:* “COF: Unidad del OST que supervisa el desempeño...”

### Ventajas del modelo unificado
* Permite recuperar información heterogénea en una sola llamada FAISS.
* **Facilita explicaciones completas y trazables:** “Según definición 2.8…” + “Según GF1 tabla…” + “Según Artículo 5.3…”
* Optimiza la precisión del RAG y reduce alucinaciones.

---

## Estructura del repositorio

```text
asistente-rag-core/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ raw/
│  │  ├─ web/        # capítulos y anexos del pliego en Markdown
│  │  ├─ csv/        # tablas normalizadas (GF, EIPU, ECPU, A06, A10, A11, etc.)
│  │  ├─ json/       # definiciones, metadatos adicionales
│  │  └─ imagenes/   # imágenes auxiliares (tablas, esquemas)
│  └─ index/         # índice FAISS u otros índices persistentes (NO versionar)
├─ notebooks/        # experimentos, análisis, prototipos RAG
└─ src/
   └─ rag_core/      # ingest, index, retriever, qa (a completar)
```

---

## Criterios de éxito (KPIs internos)

* **Recall@5 ≥ 0.80** en un gold set de 20–30 preguntas relevantes sobre la licitación GF.
* **Faithfulness ≥ 85%** (Respuestas soportadas por las citas, sin alucinaciones no justificadas).
* **Latencia ≤ 3 s** por consulta típica (índice en memoria, k≈5–8).
* **README narrativo** con diagrama y ejemplos reproducibles.
* **Trazabilidad completa** de cada respuesta a secciones (capítulos/anexos) del pliego.

---

## Cómo arrancar (local)

### 1. Crear entorno virtual

```bash
python -m venv .venv
```

### 2. Activar entorno

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\activate
```

**Linux/Mac (Bash):**
```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -U pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz con el siguiente contenido:

```ini
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
DOCS_DIR=./data/raw
INDEX_DIR=./data/index/faiss_index
# OPENAI_API_KEY=   # si se usa OpenAI u otro proveedor
```

---

## Roadmap

### MVP
* Ingesta de Markdown + CSV del pliego GF.
* Limpieza y normalización → chunks con metadatos `{ text, source, section, tipo, tags }`.
* Embeddings + FAISS.
* RetrievalQA con citas a fuentes.

### Mejoras
* Re-ranking (Cross-Encoder).
* Integración BM25 + denso.
* Chunking por secciones normativas (capítulo, artículo, anexo, tabla).

---

## Evaluación

* Recall@k, MRR.
* Faithfulness.
* Casos cualitativos (explicación y trazabilidad por chunk).

---

## Riesgos y mitigación

* **PDFs escaneados:** Se evita en el MVP (se trabaja con DOCX/MD). OCR se puede añadir después.
* **Recall bajo:** Ajustar tamaño de chunk, valor de k en top-k y activar re-ranking.
* **Alucinaciones:** Prompt “solo contexto” + decisión de abstenerse si no hay contexto suficiente o si la similitud es baja.
* **Inconsistencias de corpus:** Uso de CSV normalizados + enlaces explícitos entre `.md` y `data/raw/csv`.

---

## Guía de entorno

* `docs/SETUP_VSCODE_JUPYTER.md` – Guía para trabajar con VS Code + Jupyter en este repo.
# TFM – Asistente RAG (core) aplicado a licitación GF 001/2023 (SGF + SIPU)

Asistente RAG multiformato para consultar el corpus de la licitación pública GF 001/2023 (Gestión de Flota + SIPU) y responder solo con evidencia del corpus, con trazabilidad y reproducibilidad.

---

## Objetivo

Construir un sistema RAG que:

- Lea documentos en PDF/DOCX/MD/TXT/CSV/JSON (MVP: MD/CSV/JSON; PDF/DOCX por fases).
- Normalice y “chunkee” el contenido.
- Indexe y recupere pasajes relevantes por similitud.
- Genere respuestas ancladas al contexto recuperado.
- Incluya citas / referencias a fuentes (documento, sección, id).

---

## Principios

- Veracidad > elocuencia: si no hay evidencia suficiente → “no tengo suficiente información para afirmar esto”.
- Trazabilidad: cada respuesta debe enlazarse a uno o varios fragmentos (source/section/id).
- Reproducibilidad: mismo input → mismo chunking → misma búsqueda → mismos resultados (con parámetros controlados).
- Iteración profesional: cambios importantes se prueban en ramas feature/* y se integran por PR/merge.

---

## Estado actual del proyecto (2025-12-17)

### Hecho
- Diseño conceptual completo (modelo de documento, chunking, pipeline).
- Implementación de limpieza Markdown:
  - src/rag_core/clean_markdown.py (v1 estable, basada en pseudocódigo).
  - src/rag_core/clean_markdown_v2.py (v2 opcional) con normalización de bullets “• → -”.
  - src/rag_core/cleaning.py (wrapper/compatibilidad; evitar duplicación de lógica).
- Sanity checks:
  - notebooks/clean_markdown_sanity.ipynb (pruebas de v1 y comparación v1 vs v2).
- Herramientas:
  - tools/compare_cleaners.py (diff automático entre módulos).
- Repositorio migrado y funcionando en el nuevo equipo (repo + venv + dependencias mínimas + datos).

### En progreso / siguiente hito
- Implementar src/rag_core/ingest.py (ingesta end-to-end: descubrir → leer → limpiar → chunking → chunks.jsonl).
- Añadir tests reproducibles (pytest) para clean_markdown (v1/v2) en rama feature/clean-markdown-tests.
- Primera ejecución completa: ingesta → chunks → baseline retrieval.

---

## Big picture del sistema

Ingesta → Limpieza/Normalización → Chunking → Embeddings → Vector store → Retrieval → (Re-ranking opcional) → Prompt seguro → LLM → Respuesta con citas

---

## Estructura del repositorio

    asistente-rag-core/
    ├─ README.md
    ├─ requirements.txt
    ├─ .env.example
    ├─ .gitignore
    ├─ data/
    │  ├─ raw/
    │  │  ├─ web/      # MD/TXT normalizados (entrada)
    │  │  ├─ csv/      # tablas (entrada)
    │  │  └─ json/     # definiciones / estructuras (entrada)
    │  └─ index/       # índices vectoriales (NO versionar)
    ├─ docs/           # diseño y especificaciones (pipeline, chunking, etc.)
    ├─ notebooks/
    │  └─ clean_markdown_sanity.ipynb
    ├─ src/
    │  └─ rag_core/
    │     ├─ __init__.py
    │     ├─ clean_markdown.py
    │     ├─ clean_markdown_v2.py
    │     ├─ cleaning.py
    │     ├─ ingest.py          # (a implementar)
    │     ├─ index.py           # (a implementar)
    │     ├─ retriever.py       # (a implementar)
    │     └─ qa.py              # (a implementar)
    └─ tools/
       └─ compare_cleaners.py

Nota: carpetas como tmp_outputs/ son artefactos locales y no deben versionarse.

---

## Instalación rápida

### 1) Crear y activar entorno virtual

Windows (PowerShell)

    python -m venv .venv
    .\.venv\Scripts\Activate

macOS/Linux

    python3 -m venv .venv
    source .venv/bin/activate

### 2) Instalar dependencias

    pip install -U pip
    pip install -r requirements.txt

### 3) Variables de entorno

Crea .env desde .env.example (no se versiona).

---

## Sanity check de clean_markdown

Notebook:
- notebooks/clean_markdown_sanity.ipynb

Qué valida:
- unión conservadora de líneas partidas (casos típicos PDF/DOCX → texto)
- corrección de numeración fragmentada (5.3.1. + título)
- normalización de headings Markdown (##Titulo → ## Titulo)
- corrección de listas básicas (- - item → - item)
- eliminación de artefactos (v1)

Limitaciones conocidas:
- v1 no normaliza “•” a “-” (por diseño MVP).
- v2 sí normaliza bullets “• → -” (mejora estructural).
- Corrección de “ruido OCR” (p.ej. operaci6n) se deja fuera del MVP por riesgo/ambigüedad; se considera mejora futura.

---

## Ingesta (MVP end-to-end)

Objetivo del MVP:
1) Descubrir archivos en data/raw/{web,csv,json}
2) Leer/parsear por formato
3) Aplicar clean_markdown (v1)
4) Chunking normativa (aprox. 600–900 chars, overlap ~120)
5) Guardar salida chunks.jsonl con trazabilidad (source/section/id)

Comando objetivo (cuando ingest.py esté listo):

    python -c "from rag_core.ingest import IngestConfig, ingest_corpus; print(len(ingest_corpus(IngestConfig(repo_root='.'))))"

---

## Modelo de chunk (salida mínima)

Cada chunk debe permitir trazabilidad:

    {
      "text": "...",
      "source": "data/raw/web/archivo.md",
      "doc_type": "normativa",
      "section": "5.3.1",
      "id": "archivo:5.3.1:0",
      "tags": [],
      "metadatos": {"chunk_index": 0}
    }

---

## Evaluación (MVP)

Retrieval
- Recall@k
- MRR / nDCG (si aplica)
- Smoke tests cualitativos (preguntas realistas + verificación de evidencias)

Generación
- Faithfulness (respuestas soportadas por citas)
- Abstención correcta (si no hay evidencia)

---

## Flujo Git recomendado

- main: estable.
- ramas feature/*:
  - feature/ingest-mvp
  - feature/clean-markdown-tests
- PR corto → merge a main.

---

## Roadmap

1) ingest.py + chunks.jsonl (MVP)
2) Vector store + embeddings
3) Retriever baseline (top-k)
4) Evaluación mínima (gold set 20–30 preguntas)
5) Mejora técnica: re-ranking / chunking adaptativo / híbrbrido BM25+denso (opcional)
6) CLI / mini UI (opcional)

## Como generar evidencia
- conda run -n rag --no-capture-output python .\cli\answer.py "forma de pago" ...
Asistente-rag-core

TFM Big-school

Asistente RAG (core)

Objetivo. Construir un asistente RAG multiformato que lea PDF/DOCX/HTML/MD/TXT/CSV/JSON, recupere pasajes por similitud y responda solo con ese contexto, incluyendo citas a las fuentes.
Principios. Veracidad > elocuencia (si no hay evidencia → “no tengo suficiente información…”), trazabilidad, reproducibilidad, simplicidad→mejora.

Diagrama (big picture)
Ingesta (PDF/DOCX/HTML/MD/TXT/CSV/JSON)
  └─ Limpieza/normalización → {text, source, section_path, page, tags}
      └─ Chunking con solape (size≈800, overlap≈120)
          └─ Embeddings (Sentence-Transformers)
              └─ Índice vectorial (FAISS, persistente)
                  └─ Recuperación top-k (k≈5–8)
                      └─ (Mejora) Re-ranking con Cross-Encoder
                          └─ Prompt seguro + LLM → Respuesta con **citas**

Criterios de éxito (KPIs internos)

Recall@5 ≥ 0.80 en un gold set de 20–30 preguntas.

Faithfulness ≥ 85 % (respuestas soportadas por las citas).

Latencia ≤ 3 s por consulta típica (índice en memoria, k≈5–8).

README narrativo con diagrama y ejemplos reproducibles.

Estructura del repo
asistente-rag-core/
├─ README.md
├─ requirements.txt
├─ .gitignore
├─ data/
│  ├─ raw/        # documentos (NO versionar)
│  └─ index/      # índice FAISS (NO versionar)
├─ notebooks/
└─ src/
   └─ rag_core/   # (se irá completando: ingest, index, retriever, qa)

Cómo arrancar (local)
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt

# Variables locales (crear .env)
# EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# DOCS_DIR=./data/raw
# INDEX_DIR=./data/index/faiss_index
# OPENAI_API_KEY=     # si usas OpenAI


Coloca documentos en data/raw/ (al menos 5 formatos).

(Próx. capítulos) Construye índice FAISS y lanza la CLI para preguntar.

Roadmap

MVP: ingesta 5 formatos → chunking → embeddings + FAISS → RetrievalQA + citas.

Mejora: re-ranking (y opcional BM25+denso / chunking por secciones).

Evaluación: Recall@k, MRR, faithfulness, ejemplos cualitativos.

Riesgos y mitigación

PDFs escaneados → saltar en MVP (OCR después).

Recall bajo → ajustar chunking/k, activar re-ranking.

Alucinación → prompt “solo contexto” + abstenerse si score bajo.


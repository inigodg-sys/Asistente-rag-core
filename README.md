# Asistente-rag-core
TFM Big-school
# Asistente RAG (core)

Proyecto TFM: asistente RAG multiformato (texto, PDF, etc.)
- **Objetivo:** construir un pipeline RAG reproducible y evaluable (calidad de recuperación y generación).
- **Stack:** Python, Hugging Face, LangChain, FAISS, FastAPI (serving), Docker (más adelante).

## Estructura
- `src/`: librería del core (ingesta, chunking, embeddings, indexado, retrieval, generación).
- `notebooks/`: prototipos y experimentos.
- `docs/`: documentación funcional/técnica.
- `data/`: datos locales (no versionados).

## Cómo arrancar (local)
```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt  # lo crearemos en breve


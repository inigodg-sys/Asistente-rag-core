# Roadmap del proyecto (RAG multiformato)

## MVP (Fase I)
- Ingesta de 5 formatos (PDF, DOCX, HTML/MD/TXT, CSV, JSON).
- Limpieza y normalización → esquema `{text, source, section_path, page, tags}`.
- Chunking con solape (≈800/120).
- Embeddings (Sentence-Transformers) + índice FAISS persistente.
- RetrievalQA con prompt seguro y **citas**.

## Mejora (Fase II)
- **Mejora principal: Re-ranking con Cross-Encoder** (reordena top-k; objetivo: ↑ precisión y ↑ faithfulness).
- (Opcional) Recuperación **híbrida** BM25 + denso.
- (Opcional) **Chunking adaptativo** por secciones/títulos.

## Evaluación (Fase III)
- Gold set (20–30 preguntas) por formato.
- Métricas: Recall@k, MRR/nDCG y *faithfulness*/tasa de abstención.
- Informe “baseline vs. +re-ranking” con tablas y ejemplos cualitativos.

## Entrega (Fase IV)
- README narrativo con diagrama, pasos de ejecución y respuestas a las preguntas del enunciado.
- Capturas/visualizaciones y demo mínima (CLI/mini-UI).

# Riesgos (MVP RAG)

1) **Alucinación del LLM**  
   *Mitigación:* prompt “solo contexto”, umbral de similitud, respuesta de abstención (“no tengo suficiente información”), citas obligatorias.

2) **Recall bajo en recuperación**  
   *Mitigación:* ajustar chunking (tamaño/solape), aumentar k, enriquecer corpus, activar re-ranking, opción híbrida BM25+denso.

3) **Heterogeneidad/ruido de formatos**  
   *Mitigación:* limpieza/normalización por formato, mapeo CSV/JSON a “fichas”, filtrado de HTML (whitelist de etiquetas).

4) **PDFs escaneados (sin texto)**  
   *Mitigación:* excluir en el MVP y planificar OCR (fase posterior) con validación de calidad.

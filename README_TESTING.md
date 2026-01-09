# README_TESTING.md — Testing & Evidencia reproducible (TFM)

Este repositorio implementa un asistente **RAG** (Retrieval-Augmented Generation) aplicado al corpus de la licitación **GF 001/2023**.  
El objetivo de este README es doble:

1) **Ejecutar tests por capas** (CAPA A/B/C) de forma simple y reproducible.  
2) **Generar evidencia auditable** (artefactos + manifest) para defensa del TFM.

---

## Contexto para el tribunal (lectura rápida)

Un sistema RAG es una cadena de etapas. Antes de evaluar “qué tan bien responde”, debemos demostrar que el sistema es **reproducible** y que su **plumbing** funciona:

- **CAPA A (Ingesta):** documentos multiformato → lista de `Chunk` con `id`, `doc_type`, `source`, `section`, `text` (y metadatos).  
- **CAPA B (Indexación):** `Chunk[]` → embeddings → índice (FAISS) + metadata persistente.  
- **CAPA C (Retrieval):** query → top-k → mapping a metadata → resultados con trazabilidad.

En esta fase, cerramos formalmente **testing** con:
- tests por capas (markers),
- y evidencia reproducible generada por script (manifest + stats + salida JSONL).

---

## Filosofía de testing (por qué está diseñado así)

- **Veracidad > elocuencia:** si el sistema no puede recuperar y citar, no debe inventar.  
- **Reproducibilidad:** mismos inputs → mismo pipeline → resultados consistentes.  
- **Tests estables:** preferimos invariantes (patrones/contratos) a asserts frágiles (valores exactos que cambian por detalles menores).  
- **Capas independientes:** CAPA C puede depender de librerías nativas (p. ej. FAISS). Si faltan, esos tests deben **saltarse** (SKIP) y no romper CAPA A.

---

## 0) Preparación del entorno

> Recomendación: ejecutar siempre desde la **raíz del repo**.

### Confirmar raíz del repo
```bash
git rev-parse --show-toplevel
```

### Windows (PowerShell)
```powershell
# Activar venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar toda la suite
python -m pytest -q
```

### macOS / Linux
```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

### Ver markers disponibles
```bash
python -m pytest --markers
```

---

## 1) Ejecutar tests por capas (markers)

Los markers se definen en `pytest.ini`.  
Ejecuta subconjuntos con `-m`:

### CAPA A — Ingesta (Unit)
```bash
python -m pytest -q -m ingest_unit
```

### CAPA A — Ingesta (Integration)
```bash
python -m pytest -q -m ingest_integration
```

### CAPA A — Ingesta (E2E smoke)
```bash
python -m pytest -q -m ingest_e2e
```

### CAPA A completa (Unit + Integration + E2E)
```bash
python -m pytest -q -m "ingest_unit or ingest_integration or ingest_e2e"
```

### CAPA C — Retrieval (plumbing)
```bash
python -m pytest -q -m retrieval
```

> Nota sobre FAISS: el test de retrieval usa `pytest.importorskip("faiss")`.  
> Si FAISS no está instalado, el test se marcará como **SKIPPED** (esto es correcto; no es un fallo).

### Todo excepto tests lentos
```bash
python -m pytest -q -m "not slow"
```

### Ver qué se ejecutaría (sin correr nada)
```bash
python -m pytest -q -m ingest_e2e --collect-only
```

---

## 2) Evidencia reproducible (para el TFM)

Además de los tests, generamos artefactos reproducibles mediante un script dedicado.

### A) Evidencia “universal” (smoke) — recomendada para cualquier máquina
Este modo crea un mini-corpus sintético en un directorio temporal y ejecuta la ingesta ahí (no depende del corpus real).

```bash
python tools/generate_ingest_evidence.py --mode smoke
```

Artefactos generados (por defecto en `reports/ingest_smoke/`):
- `run_manifest.json`  
  Contiene: `mode`, `python`, `platform`, `cwd`, `git_head`, parámetros relevantes de configuración (chunking) y un resumen de salida.
- `chunk_stats.json`  
  Resumen legible: nº de chunks, distribución por `doc_type`, longitudes y muestras de IDs.
- `chunks.jsonl`  
  Salida completa (auditable) de los chunks generados.

### B) Evidencia sobre el corpus real (full) — útil, pero potencialmente pesada
```bash
python tools/generate_ingest_evidence.py --mode full --write-jsonl 0
```

- `--write-jsonl 0` evita generar un JSONL grande si el corpus real es pesado.
- Produce al menos `run_manifest.json` y `chunk_stats.json` en `reports/ingest_full/`.

---

## 3) Capturar evidencia de ejecución de pytest (recomendado)

Para archivar una ejecución reproducible, guarda:

### Output del test run
```bash
python -m pytest -q > reports/pytest_output.txt
```

### Snapshot del entorno (dependencias)
```bash
pip freeze > reports/env_freeze.txt
```

### Ruta del intérprete Python (útil para auditoría)
```bash
python -c "import sys; print(sys.executable)" > reports/python_path.txt
```

---

## 4) Qué cubren estos tests (y qué NO)

### Cubre (en esta fase)
- **CAPA A (ingesta):**
  - que el pipeline procesa formatos mínimos (MD/CSV/JSON) de forma end-to-end (smoke),
  - que produce chunks con tipos (`doc_type`) e IDs trazables,
  - que la salida se puede materializar en JSONL (evidencia).
- **CAPA C (retrieval plumbing):**
  - que el mecanismo de retrieval funciona (query → embedding → FAISS → hits + metadata),
  - con un embedder determinista (sin depender de modelos reales ni red),
  - y sin romper la suite si falta FAISS (SKIP correcto).

### NO cubre todavía (normal y esperado)
- Calidad semántica real de embeddings (requiere modelo real).
- Evaluación cuantitativa con gold set (Recall@k / Hit@k).
- Pipeline completo CAPA B (embeddings + FAISS persistido + metadatos completos) con corpus real.
- “Answer generation” con citas en formato final (eso pertenece a la fase de RAG end-to-end).

---

## 5) Troubleshooting rápido

### “No encuentro `pytest.ini`”
Asegúrate de estar en la raíz del repo:
```bash
git rev-parse --show-toplevel
```

### “Se seleccionan 0 tests con un marker”
Verifica que el marker existe y está aplicado:
```bash
python -m pytest --markers
python -m pytest -m ingest_e2e --collect-only
```

### “Retrieval aparece SKIPPED”
Es correcto si no tienes FAISS instalado. Si quieres ejecutarlo:
- instala FAISS según tu sistema/entorno (dependencia nativa),
- y repite:
```bash
python -m pytest -q -m retrieval
```

---

## 6) Próxima fase del proyecto (después del cierre de testing)

- **Indexación real (CAPA B):** embeddings + FAISS persistido + metadata/manifest trazable.  
- **Retrieval real (CAPA C):** recuperación top-k estable y trazable.  
- **Evaluación mínima:** gold set + métricas Recall@k/Hit@k + ejemplos con citas para defensa del TFM.

---

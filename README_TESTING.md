# Testing & Evidencia (TFM)

Este repositorio se testea por **capas** para validar que todo lo producido funciona **antes** de pasar a la siguiente fase del proyecto.

## Filosofía

- **CAPA A (Ingesta)**: documentos -> `Chunk[]` (IDs, source, section, doc_type, metadatos).
- **CAPA B (Indexación)**: `Chunk[]` -> embeddings -> índice (FAISS u otro) + metadata.
- **CAPA C (Retrieval)**: query -> top-k -> mapping a meta -> hits.

## 0) Preparación del entorno

1) Activar el virtualenv (PowerShell):

```powershell
cd <root-del-repo>
./.venv/Scripts/Activate.ps1
```

2) Instalar dependencias (si aplica):

```powershell
python -m pip install -r requirements.txt
```

3) Ejecutar toda la suite:

```powershell
python -m pytest -q
```

> Nota: el test de retrieval usa `pytest.importorskip("faiss")`. Si FAISS no está instalado, ese test aparecerá como **SKIPPED** (esto es intencional: no debe romper la suite cuando estás trabajando en ingesta).

## 1) Ejecutar por capas (markers)

Los markers están definidos en `pytest.ini`. Ejemplos:

### Solo CAPA A (ingesta)

```powershell
python -m pytest -q -m "ingest_unit or ingest_e2e"
```

### Solo CAPA C (retrieval)

```powershell
python -m pytest -q -m retrieval
```

### Todo menos lo lento

```powershell
python -m pytest -q -m "not slow"
```

## 2) Evidencia reproducible (para el TFM)

### A) Evidencia de ingesta (smoke)

Genera artefactos en `reports/ingest_smoke/`:

```powershell
python tools/generate_ingest_evidence.py --mode smoke
```

Archivos generados:
- `reports/ingest_smoke/run_manifest.json`
- `reports/ingest_smoke/chunk_stats.json`
- `reports/ingest_smoke/chunks.jsonl` (si `--write-jsonl 1`, por defecto)

### B) Evidencia de ingesta sobre corpus real

Esto procesa `data/raw/...` del repo actual (puede tardar más):

```powershell
python tools/generate_ingest_evidence.py --mode full --write-jsonl 0
```

## 3) Capturar logs de pytest (recomendado)

```powershell
mkdir reports -Force
python -m pytest -q | Tee-Object -FilePath reports/pytest_output.txt
python -m pip freeze > reports/env_freeze.txt
python -c "import sys; print(sys.executable)" > reports/python_path.txt
```

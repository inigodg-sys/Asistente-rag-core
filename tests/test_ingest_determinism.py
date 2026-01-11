"""
CAPA A — Test de determinismo básico (ingesta).

Objetivo pedagógico:
- Ejecutar ingest_corpus(cfg) DOS veces con el mismo input y la misma config.
- Verificar que la salida es estable:
  - mismo conjunto de ids
  - para cada id: mismo texto (hash), doc_type, source y section

Nota:
- No exigimos mismo ORDEN global de chunks (discover_documents usa rglob y el orden puede variar).
  Exigimos determinismo de contenido por id, que es lo crítico para indexación/citas.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json

import pytest

from rag_core.ingest import IngestConfig, ingest_corpus

pytestmark = pytest.mark.ingest_integration


def _write_mini_repo(repo_root: Path) -> None:
    """Crea estructura data/raw/... y escribe 3 documentos mínimos."""
    (repo_root / "data/raw/web").mkdir(parents=True, exist_ok=True)
    (repo_root / "data/raw/csv").mkdir(parents=True, exist_ok=True)
    (repo_root / "data/raw/json").mkdir(parents=True, exist_ok=True)

    (repo_root / "data/raw/web/demo.md").write_text(
        "Intro.\n\n## 1 Alcance\nTexto del alcance.\n\n## 2 Requisitos\nR1: algo.\nR2: algo más.\n",
        encoding="utf-8",
    )

    (repo_root / "data/raw/csv/demo.csv").write_text(
        "col1,col2\na,1\nb,2\n",
        encoding="utf-8",
    )

    (repo_root / "data/raw/json/definiciones_demo.json").write_text(
        json.dumps(
            [
                {"id": "D1", "termino": "SLA", "definicion": "Acuerdo de nivel de servicio"},
                {"id": "D2", "termino": "KPI", "definicion": "Indicador clave"},
            ],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _fingerprint_chunk(c) -> tuple:
    """
    Crea una huella estable por chunk (por id):
    - hash del texto (para comparar contenido sin comparar strings largos)
    - doc_type, source, section (tienen que ser estables para trazabilidad)
    """
    text_bytes = (c.text or "").encode("utf-8")
    text_hash = hashlib.sha256(text_bytes).hexdigest()
    return (text_hash, c.doc_type, c.source, c.section)


def test_ingest_is_deterministic_for_same_input_and_cfg(tmp_path: Path) -> None:
    repo_root = tmp_path
    _write_mini_repo(repo_root)

    cfg = IngestConfig(repo_root=repo_root)

    chunks_a = ingest_corpus(cfg)
    chunks_b = ingest_corpus(cfg)

    assert chunks_a and chunks_b, "Ambas ejecuciones deben producir chunks"

    # Construimos dicts por id para ignorar el orden global de salida
    map_a = {c.id: _fingerprint_chunk(c) for c in chunks_a}
    map_b = {c.id: _fingerprint_chunk(c) for c in chunks_b}

    # 1) mismo conjunto de ids
    assert set(map_a.keys()) == set(map_b.keys()), "La ingesta debe producir el mismo conjunto de ids"

    # 2) por cada id: misma huella (texto/doc_type/source/section)
    assert map_a == map_b, "Para cada id, el contenido y metadatos deben ser idénticos entre ejecuciones"

"""
CAPA A — Test de contrato mínimo de Chunk (ingesta).

Objetivo pedagógico:
- Ejecutar ingest_corpus(cfg) sobre un mini-corpus sintético y controlado.
- Verificar que CADA chunk cumple el contrato mínimo necesario para:
  (1) indexación posterior (CAPA B),
  (2) retrieval trazable (CAPA C),
  (3) citas/auditoría (TFM).

Este test no mide "calidad semántica". Mide contrato y trazabilidad mínima.
"""

from __future__ import annotations

from pathlib import Path
import json

import pytest

from rag_core.ingest import IngestConfig, ingest_corpus

pytestmark = pytest.mark.ingest_integration


def _write_mini_repo(repo_root: Path) -> None:
    """Crea estructura data/raw/... y escribe 3 documentos mínimos."""
    (repo_root / "data/raw/web").mkdir(parents=True, exist_ok=True)
    (repo_root / "data/raw/csv").mkdir(parents=True, exist_ok=True)
    (repo_root / "data/raw/json").mkdir(parents=True, exist_ok=True)

    # Markdown con headings numerados (para split + section ids)
    (repo_root / "data/raw/web/demo.md").write_text(
        "Intro.\n\n## 1 Alcance\nTexto del alcance.\n\n## 2 Requisitos\nR1: algo.\nR2: algo más.\n",
        encoding="utf-8",
    )

    # CSV mínimo
    (repo_root / "data/raw/csv/demo.csv").write_text(
        "col1,col2\na,1\nb,2\n",
        encoding="utf-8",
    )

    # JSON mínimo (definiciones)
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


def test_chunks_respect_minimal_contract(tmp_path: Path) -> None:
    """
    Contrato mínimo que exigimos a la salida de CAPA A:
    - id: no vacío y único
    - text: no vacío
    - source: no vacío y apunta a un fichero existente
    - doc_type: pertenece al conjunto permitido
    - section: coherente con el tipo (tabla -> None; normativa/definicion -> no vacía)
    - tags/metadatos: tipos correctos (list/dict)
    """
    repo_root = tmp_path
    _write_mini_repo(repo_root)

    cfg = IngestConfig(repo_root=repo_root)
    chunks = ingest_corpus(cfg)

    assert chunks, "ingest_corpus() debería producir chunks para el mini-corpus"

    allowed_doc_types = {"normativa", "tabla", "definicion", "tutorial", "formulario"}

    # 1) IDs no vacíos + únicos (base de trazabilidad)
    ids = [c.id for c in chunks]
    assert all(i is not None and str(i).strip() for i in ids), "Todos los chunks deben tener id"
    assert len(ids) == len(set(ids)), "Los ids de chunk deben ser únicos"

    # 2) Contrato campo a campo
    for c in chunks:
        assert isinstance(c.text, str) and c.text.strip(), "Chunk.text debe ser str no vacío"
        assert isinstance(c.source, str) and c.source.strip(), "Chunk.source debe ser str no vacío"
        assert Path(c.source).exists(), f"Chunk.source debe apuntar a un fichero existente: {c.source}"
        assert c.doc_type in allowed_doc_types, f"doc_type inválido: {c.doc_type}"

        # tags/metadatos: tipos correctos (aunque puedan estar vacíos)
        assert isinstance(c.tags, list), "Chunk.tags debe ser list"
        assert isinstance(c.metadatos, dict), "Chunk.metadatos debe ser dict"

        # section coherente por doc_type (contrato mínimo actual de nuestro pipeline)
        if c.doc_type == "tabla":
            assert c.section is None, "En CSV/tabla, section debe ser None"
            assert Path(c.source).suffix.lower() == ".csv"
        elif c.doc_type == "definicion":
            assert c.section is not None and str(c.section).strip(), "En definicion, section debe existir"
            assert Path(c.source).suffix.lower() == ".json"
        elif c.doc_type == "normativa":
            assert c.section is not None and str(c.section).strip(), "En normativa, section debe existir"
            assert Path(c.source).suffix.lower() == ".md"

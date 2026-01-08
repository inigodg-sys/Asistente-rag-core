"""CAPA A — Smoke test end-to-end de ingesta.

Idea pedagógica:
- Creamos un "mini repo" temporal con tmp_path (NO tocamos tu disco)
- Colocamos 1 MD + 1 CSV + 1 JSON en data/raw/...
- Ejecutamos ingest_corpus(cfg)
- Verificamos invariantes: cantidad, doc_types, patrones de IDs
- Guardamos un artefacto jsonl (evidencia) dentro del tmp_path

Este test NO mide calidad semántica, solo valida que el pipeline de ingesta está cableado.
"""

from __future__ import annotations

from pathlib import Path
import json

import pytest

from rag_core.ingest import IngestConfig, ingest_corpus, save_chunks_jsonl


pytestmark = pytest.mark.ingest_e2e


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
        ),
        encoding="utf-8",
    )


def test_ingest_end2end_smoke(tmp_path: Path):
    repo_root = tmp_path
    _write_mini_repo(repo_root)

    cfg = IngestConfig(repo_root=repo_root)

    chunks = ingest_corpus(cfg)

    # 1) Debe producir algo
    assert len(chunks) > 0

    # 2) Debe contener los 3 tipos esperados
    doc_types = {c.doc_type for c in chunks}
    assert "normativa" in doc_types  # MD
    assert "tabla" in doc_types      # CSV
    assert "definicion" in doc_types # JSON

    # 3) IDs: patrones básicos
    ids = [c.id for c in chunks if c.id]
    assert any(i.startswith("demo:") for i in ids)       # demo.md / demo.csv
    assert any(":row:" in i for i in ids)               # CSV
    assert any(i.startswith("def:D") for i in ids)      # JSON

    # 4) Guardado JSONL (artefacto de evidencia)
    out_path = repo_root / "reports/ingest_smoke/chunks_smoke.jsonl"
    save_chunks_jsonl(chunks, out_path)
    assert out_path.exists()
    assert out_path.stat().st_size > 0

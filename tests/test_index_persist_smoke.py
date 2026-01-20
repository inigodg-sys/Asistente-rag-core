"""
CAPA B — Test de persistencia (build -> save -> load) y consistencia básica.

Qué valida:
- Que el builder crea los 3 artefactos canónicos: faiss.index, meta.jsonl, manifest.json
- Que el índice y la meta están alineados: index.ntotal == len(meta)

No usa modelos reales: parchea get_embedder() para usar DummyEmbedder determinista.
"""

from __future__ import annotations

from pathlib import Path
import json
import hashlib
import re

import pytest
import numpy as np

faiss = pytest.importorskip("faiss")  # type: ignore

from rag_core.retriever import Retriever

pytestmark = pytest.mark.index


class DummyEmbedder:
    """Embedder determinista y rápido (hashing trick)."""

    def __init__(self, dim: int = 64):
        self.dim = dim
        self.device = "cpu"

    def encode(self, texts, batch_size=32, normalize=True, show_progress_bar=False):
        vecs = []
        for t in texts:
            v = np.zeros(self.dim, dtype=np.float32)
            tokens = re.findall(r"\w+", str(t).lower(), flags=re.UNICODE)
            for tok in tokens:
                h = hashlib.md5(tok.encode("utf-8")).digest()
                idx = int.from_bytes(h[:4], "little") % self.dim
                v[idx] += 1.0
            if normalize:
                n = np.linalg.norm(v) + 1e-12
                v = v / n
            vecs.append(v)
        return np.stack(vecs, axis=0).astype(np.float32)


def _write_chunks_jsonl(path: Path) -> None:
    """Mini-corpus controlado para indexación."""
    rows = [
        {
            "id": "c1",
            "source": str(path.parent / "docA.md"),
            "section": "1",
            "text": "Requisitos de arquitectura del sistema de gestión de flota.",
        },
        {
            "id": "c2",
            "source": str(path.parent / "docB.md"),
            "section": "2",
            "text": "Plazos de entrega y criterios de aceptación del servicio.",
        },
        {
            "id": "c3",
            "source": str(path.parent / "docC.md"),
            "section": "3",
            "text": "Definiciones: SLA y KPI para el contrato.",
        },
    ]

    # Creamos ficheros dummy solo para que source exista (si tu pipeline lo exige)
    (path.parent / "docA.md").write_text("# A\n", encoding="utf-8")
    (path.parent / "docB.md").write_text("# B\n", encoding="utf-8")
    (path.parent / "docC.md").write_text("# C\n", encoding="utf-8")

    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _load_meta(meta_path: Path) -> list[dict]:
    meta: list[dict] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                meta.append(json.loads(line))
    return meta


def _run_index_builder(chunks_path: Path, out_dir: Path, monkeypatch) -> None:
    """
    Ejecuta el builder de index_faiss dentro del mismo proceso para que monkeypatch funcione.
    Soporta dos estilos comunes:
    - función build_index(...)
    - main() con argparse (simulando sys.argv)
    """
    import sys
    import rag_core.index_faiss as mod

    # Parcheamos get_embedder dentro del módulo index_faiss
    monkeypatch.setattr(mod, "get_embedder", lambda model_name, device=None: DummyEmbedder(dim=64))

    out_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(mod, "build_index"):
        mod.build_index(
            chunks_path=chunks_path,
            out_dir=out_dir,
            model_name="dummy",
            device="cpu",
            batch_size=16,
            show_progress=False,
        )
        return

    if hasattr(mod, "main"):
        argv_backup = sys.argv[:]
        try:
            sys.argv = [
                "index_faiss",
                "--chunks",
                str(chunks_path),
                "--out_dir",
                str(out_dir),
                "--model",
                "dummy",
                "--device",
                "cpu",
                "--batch_size",
                "16",
            ]
            mod.main()
        finally:
            sys.argv = argv_backup
        return

    raise RuntimeError("index_faiss.py no expone build_index() ni main().")


def test_index_build_save_load_and_consistency(tmp_path: Path, monkeypatch) -> None:
    chunks_path = tmp_path / "chunks.jsonl"
    out_dir = tmp_path / "index_out"
    _write_chunks_jsonl(chunks_path)

    _run_index_builder(chunks_path, out_dir, monkeypatch)

    index_path = out_dir / "faiss.index"
    meta_path = out_dir / "meta.jsonl"
    manifest_path = out_dir / "manifest.json"

    # 1) Artefactos existen y no están vacíos
    assert index_path.exists() and index_path.stat().st_size > 0
    assert meta_path.exists() and meta_path.stat().st_size > 0
    assert manifest_path.exists() and manifest_path.stat().st_size > 0

    # 2) Cargar y verificar consistencia del mapping
    index = faiss.read_index(str(index_path))
    meta = _load_meta(meta_path)

    assert index.ntotal == len(meta), "Contrato CAPA B: index.ntotal debe igualar len(meta)"

    # 3) Smoke de retrieval local con DummyEmbedder (sin modelo real)
    emb = DummyEmbedder(dim=64)
    r = Retriever(index=index, meta=meta, embedder_model="dummy", embedder=emb)
    hits = r.retrieve("gestión de flota arquitectura", k=2)
    assert len(hits) == 2

"""
CAPA B — Test de mapping correcto índice <-> meta.

Qué valida:
- Que una query controlada recupera el chunk esperado (por id)
- Que el text devuelto pertenece al chunk correcto (no hay desalineación)

Este test detecta el fallo más peligroso: "recupera bien, pero cita mal".
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


def _load_meta(meta_path: Path) -> list[dict]:
    meta: list[dict] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                meta.append(json.loads(line))
    return meta


def _write_chunks_jsonl(path: Path) -> None:
    rows = [
        {
            "id": "c1",
            "source": "docA.md",
            "section": "1",
            "text": "Arquitectura del sistema de gestión de flota y componentes principales.",
        },
        {
            "id": "c2",
            "source": "docB.md",
            "section": "2",
            "text": "Condiciones económicas, pagos y facturación del contrato.",
        },
        {
            "id": "c3",
            "source": "docC.md",
            "section": "3",
            "text": "Requisitos de ciberseguridad: ISO 27001, control de accesos y auditoría.",
        },
    ]
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _run_index_builder(chunks_path: Path, out_dir: Path, monkeypatch) -> None:
    import sys
    import rag_core.index_faiss as mod

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


def test_index_mapping_returns_expected_chunk(tmp_path: Path, monkeypatch) -> None:
    chunks_path = tmp_path / "chunks.jsonl"
    out_dir = tmp_path / "index_out"
    _write_chunks_jsonl(chunks_path)

    _run_index_builder(chunks_path, out_dir, monkeypatch)

    index_path = out_dir / "faiss.index"
    meta_path = out_dir / "meta.jsonl"

    index = faiss.read_index(str(index_path))
    meta = _load_meta(meta_path)

    assert index.ntotal == len(meta)

    emb = DummyEmbedder(dim=64)
    r = Retriever(index=index, meta=meta, embedder_model="dummy", embedder=emb)

    hits = r.retrieve("arquitectura gestión flota", k=1)
    assert len(hits) == 1

    top = hits[0]
    assert top["id"] == "c1", "El mapping índice->meta debe devolver el id correcto"
    assert "gestión de flota" in top["text"].lower(), "El texto devuelto debe corresponder al chunk esperado"

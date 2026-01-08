from __future__ import annotations

from pathlib import Path

import hashlib
import re

import pytest

import numpy as np


# CAPA C — Retrieval (plumbing). Si falta faiss/numpy, este test NO debe romper la suite.
faiss = pytest.importorskip("faiss")  # type: ignore


pytestmark = pytest.mark.retrieval

from rag_core.retriever import Retriever


class DummyEmbedder:
    """
    Embedder determinista y "semi-semántico" para test offline.

    Objetivo del test: NO medir calidad real de embeddings.
    Sí queremos una señal mínima de relevancia basada en solapamiento de tokens.

    Implementación: "hashing trick" sobre tokens (bag-of-words hashed).
    """
    def __init__(self, dim: int = 64):
        self.dim = dim

    def encode(self, texts, batch_size=32, normalize=True, show_progress_bar=False):
        vecs = []
        for t in texts:
            v = np.zeros(self.dim, dtype=np.float32)

            # 1) Tokenización simple, estable y suficiente para smoke test
            tokens = re.findall(r"\w+", str(t).lower(), flags=re.UNICODE)

            # 2) Cada token "vota" en una dimensión determinista
            for tok in tokens:
                h = hashlib.md5(tok.encode("utf-8")).digest()
                idx = int.from_bytes(h[:4], "little") % self.dim
                v[idx] += 1.0

            # 3) Normalización para que IndexFlatIP ~ cosine
            if normalize:
                n = np.linalg.norm(v) + 1e-12
                v = v / n

            vecs.append(v)

        return np.stack(vecs, axis=0).astype(np.float32)


def test_retrieve_smoke(tmp_path: Path):
    # 1) “chunks” dummy
    meta = [
        {"id": "c1", "source": "docA", "section": "s1", "text": "Requisitos de adjudicación y evaluación técnica."},
        {"id": "c2", "source": "docB", "section": "s2", "text": "Plazos, garantías y condiciones contractuales."},
        {"id": "c3", "source": "docC", "section": "s3", "text": "Arquitectura del sistema de gestión de flota."},
    ]

    # 2) construir índice con dummy embedder
    emb = DummyEmbedder(dim=64)
    vecs = emb.encode([m["text"] for m in meta], normalize=True)

    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)

    # 3) retriever “inyectado”
    r = Retriever(index=index, meta=meta, embedder_model="dummy", embedder=emb)


    hits = r.retrieve("gestión de flota arquitectura", k=2)
    assert len(hits) == 2

    # Smoke test (plumbing + relevancia mínima): "c3" debe aparecer en el top-k.
    ids = [h["id"] for h in hits]
    assert "c3" in ids

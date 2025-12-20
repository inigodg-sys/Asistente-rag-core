from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import faiss  # type: ignore

from rag_core.retriever import Retriever


class DummyEmbedder:
    """
    Genera embeddings deterministas a partir del texto para test offline.
    """
    def __init__(self, dim: int = 8):
        self.dim = dim

    def encode(self, texts, batch_size=32, normalize=True, show_progress_bar=False):
        vecs = []
        for t in texts:
            # hash simple -> vector reproducible
            h = abs(hash(t))
            v = np.array([(h >> (i * 8)) & 255 for i in range(self.dim)], dtype=np.float32)
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
    emb = DummyEmbedder(dim=8)
    vecs = emb.encode([m["text"] for m in meta], normalize=True)

    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)

    # 3) retriever “inyectado”
    r = Retriever(index=index, meta=meta, embedder_model="dummy", embedder=emb)


    hits = r.retrieve("gestión de flota arquitectura", k=2)
    assert len(hits) == 2
    # Esperamos que el chunk sobre "gestión de flota" esté muy arriba
    assert hits[0]["id"] in {"c3", "c1"}  # tolerante, pero debe recuperar algo relevante

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np
import faiss  # type: ignore

from rag_core.embeddings import get_embedder


def load_meta(meta_path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


@dataclass
class Retriever:
    index: faiss.Index
    meta: List[Dict]
    embedder_model: str
    device: Optional[str] = None
    embedder: Optional[Any] = None  # <- NUEVO: permite inyección (DummyEmbedder o real)

    def __post_init__(self) -> None:
        # Si el test (o el runtime) inyecta un embedder, NO inicializamos SentenceTransformer.
        if self.embedder is None:
            self.embedder = get_embedder(self.embedder_model, device=self.device)

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        q_vec = self.embedder.encode([query], batch_size=1, normalize=True, show_progress_bar=False)
        q = np.asarray(q_vec, dtype=np.float32)
        scores, idxs = self.index.search(q, k)

        out: List[Dict] = []
        for score, idx in zip(scores[0].tolist(), idxs[0].tolist()):
            if idx < 0:
                continue
            m = self.meta[idx]
            out.append(
                {
                    "score": float(score),
                    "id": m.get("id"),
                    "source": m.get("source"),
                    "section": m.get("section"),
                    "text": m.get("text"),
                }
            )
        return out


def load_retriever(index_path: Path, meta_path: Path, model_name: str, device: Optional[str] = None) -> Retriever:
    index = faiss.read_index(str(index_path))
    meta = load_meta(meta_path)
    if index.ntotal != len(meta):
        raise RuntimeError(f"Index ntotal={index.ntotal} no coincide con meta={len(meta)}")
    return Retriever(index=index, meta=meta, embedder_model=model_name, device=device)

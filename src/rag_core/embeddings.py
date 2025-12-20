from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

try:
    import torch
except Exception:  # pragma: no cover
    torch = None

from sentence_transformers import SentenceTransformer


def pick_device(prefer: Optional[str] = None) -> str:
    """
    Decide device de forma reproducible:
    - Si 'prefer' se pasa, úsalo.
    - Si hay CUDA disponible, usa 'cuda'.
    - Si no, 'cpu'.
    """
    if prefer:
        return prefer
    if torch is not None and torch.cuda.is_available():
        return "cuda"
    return "cpu"


@dataclass
class Embedder:
    model_name: str
    device: str

    def __post_init__(self) -> None:
        self.model = SentenceTransformer(self.model_name, device=self.device)

    def encode(
        self,
        texts: List[str],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """
        Devuelve np.ndarray float32 con shape (N, D).
        Si normalize=True, devuelve vectores L2-normalizados (para cosine con IP).
        """
        vecs = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
            normalize_embeddings=normalize,
        )
        # SentenceTransformers puede devolver float64 a veces; forzamos float32 para FAISS.
        return np.asarray(vecs, dtype=np.float32)


def get_embedder(model_name: str, device: Optional[str] = None) -> Embedder:
    device = pick_device(device)
    return Embedder(model_name=model_name, device=device)

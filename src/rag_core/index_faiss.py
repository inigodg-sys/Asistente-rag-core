from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np

import faiss  # type: ignore

from rag_core.embeddings import get_embedder


def read_jsonl(path: Path) -> Iterable[Dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_chunk_id(rec: Dict, idx: int) -> str:
    """
    Garantiza ID estable aunque falte rec["id"].
    Usa source+section+idx como fallback (suficiente para reproducibilidad local).
    """
    if rec.get("id"):
        return str(rec["id"])
    base = f"{rec.get('source','')}|{rec.get('section','')}|{idx}"
    return hashlib.sha1(base.encode("utf-8")).hexdigest()


def build_index(
    chunks_path: Path,
    out_dir: Path,
    model_name: str,
    batch_size: int = 32,
    device: str | None = None,
    show_progress: bool = True,
) -> Tuple[Path, Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    index_path = out_dir / "faiss.index"
    meta_path = out_dir / "meta.jsonl"
    manifest_path = out_dir / "manifest.json"

    # 1) cargar chunks
    records: List[Dict] = []
    texts: List[str] = []
    for i, rec in enumerate(read_jsonl(chunks_path)):
        text = rec.get("text")
        if not text or not str(text).strip():
            continue
        cid = stable_chunk_id(rec, i)
        meta = {
            "id": cid,
            "source": rec.get("source"),
            "section": rec.get("section"),
            # guardamos text aquí para retrieval simple (sin re-leer chunks.jsonl)
            "text": str(text),
        }
        records.append(meta)
        texts.append(str(text))

    if not records:
        raise RuntimeError(f"No hay chunks válidos en {chunks_path}")

    # 2) embeddings (GPU si hay)
    embedder = get_embedder(model_name=model_name, device=device)
    vecs = embedder.encode(
        texts,
        batch_size=batch_size,
        normalize=True,           # L2 -> cosine via inner product
        show_progress_bar=show_progress,
    )

    if vecs.ndim != 2:
        raise RuntimeError("Embeddings con shape inválido")

    n, d = vecs.shape

    # 3) FAISS exacto baseline (IP con vectores normalizados = cosine)
    index = faiss.IndexFlatIP(d)
    index.add(vecs)

    # 4) persistir
    faiss.write_index(index, str(index_path))

    with meta_path.open("w", encoding="utf-8") as f:
        for m in records:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "chunks_path": str(chunks_path),
        "chunks_sha256": sha256_file(chunks_path),
        "model_name": model_name,
        "device": embedder.device,
        "num_vectors": int(n),
        "dim": int(d),
        "index_type": "IndexFlatIP (cosine via L2-normalized embeddings)",
        "artifacts": {
            "faiss_index": str(index_path),
            "meta_jsonl": str(meta_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return index_path, meta_path, manifest_path


def main() -> None:
    p = argparse.ArgumentParser(description="Build FAISS index from chunks.jsonl")
    p.add_argument("--chunks", type=str, required=True, help="Path a data/index/chunks.jsonl")
    p.add_argument("--out_dir", type=str, default="data/index", help="Directorio de salida (artefactos locales)")
    p.add_argument("--model", type=str, default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    p.add_argument("--batch_size", type=int, default=32)
    p.add_argument("--device", type=str, default=None, help="cuda/cpu (opcional)")
    args = p.parse_args()

    index_path, meta_path, manifest_path = build_index(
        chunks_path=Path(args.chunks),
        out_dir=Path(args.out_dir),
        model_name=args.model,
        batch_size=args.batch_size,
        device=args.device,
        show_progress=True,
    )
    print(f"[OK] Index:    {index_path}")
    print(f"[OK] Meta:     {meta_path}")
    print(f"[OK] Manifest: {manifest_path}")


if __name__ == "__main__":
    main()

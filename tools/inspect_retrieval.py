from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import faiss  # type: ignore

from rag_core.embeddings import get_embedder
from rag_core.retriever import Retriever


def load_meta(meta_path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def find_by_id(meta: List[Dict], chunk_id: str) -> Optional[Dict]:
    for m in meta:
        if m.get("id") == chunk_id:
            return m
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--q", help="Pregunta para inspeccionar retrieval")
    ap.add_argument("--id", help="Lookup directo de un chunk id (muestra texto/source/section)")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--index", default="data/index/faiss.index")
    ap.add_argument("--meta", default="data/index/meta.jsonl")
    ap.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    ap.add_argument("--device", default=None)
    ap.add_argument("--snippet", type=int, default=260)
    args = ap.parse_args()

    index_path = Path(args.index)
    meta_path = Path(args.meta)

    meta = load_meta(meta_path)

    if args.id:
        m = find_by_id(meta, args.id)
        if not m:
            print("NOT FOUND:", args.id)
            return 1
        print("ID:", m.get("id"))
        print("SOURCE:", m.get("source"))
        print("SECTION:", m.get("section"))
        print("TEXT:\n", m.get("text"))
        return 0

    if not args.q:
        print("ERROR: use --q or --id")
        return 2

    index = faiss.read_index(str(index_path))
    if index.ntotal != len(meta):
        raise RuntimeError(f"Mapping inconsistente: index.ntotal={index.ntotal} vs len(meta)={len(meta)}")

    emb = get_embedder(model_name=args.model, device=args.device)
    r = Retriever(index=index, meta=meta, embedder_model=args.model, device=args.device, embedder=emb)

    hits = r.retrieve(args.q, k=args.k)

    print("\nQUESTION:", args.q)
    print("-" * 80)
    for i, h in enumerate(hits, 1):
        txt = (h.get("text") or "").replace("\n", " ")
        txt = (txt[: args.snippet] + "…") if len(txt) > args.snippet else txt
        print(f"{i:02d}  score={h['score']:.4f}  id={h.get('id')}")
        print(f"     source={h.get('source')}  section={h.get('section')}")
        print(f"     text={txt}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

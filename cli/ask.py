from __future__ import annotations

import argparse
from pathlib import Path

from rag_core.retriever import load_retriever


def main() -> None:
    p = argparse.ArgumentParser(description="Ask (retrieval baseline): query -> top-k chunks trazables")
    p.add_argument("query", type=str)
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--index", type=str, default="data/index/faiss.index")
    p.add_argument("--meta", type=str, default="data/index/meta.jsonl")
    p.add_argument("--model", type=str, default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    p.add_argument("--device", type=str, default=None, help="cuda/cpu (opcional)")
    args = p.parse_args()

    r = load_retriever(
        index_path=Path(args.index),
        meta_path=Path(args.meta),
        model_name=args.model,
        device=args.device,
    )
    hits = r.retrieve(args.query, k=args.k)

    print("\n=== TOP-K CHUNKS (trazables) ===")
    for i, h in enumerate(hits, 1):
        print(f"\n[{i}] score={h['score']:.4f}")
        print(f"    source : {h.get('source')}")
        print(f"    section: {h.get('section')}")
        print(f"    id     : {h.get('id')}")
        txt = (h.get("text") or "").strip()
        print(f"    text   : {txt[:400]}{'...' if len(txt) > 400 else ''}")

    print("\n=== BORRADOR (solo evidencia concatenada) ===")
    draft = "\n\n".join([f"- ({h.get('source')} | {h.get('section')} | {h.get('id')})\n{h.get('text')}" for h in hits])
    print(draft[:2000] + ("...\n" if len(draft) > 2000 else ""))


if __name__ == "__main__":
    main()

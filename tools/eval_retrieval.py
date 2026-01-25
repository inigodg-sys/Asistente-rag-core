from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np

# Dependencias del proyecto
import faiss  # type: ignore
from rag_core.embeddings import get_embedder
from rag_core.retriever import Retriever


def load_meta(meta_path: Path) -> List[Dict]:
    meta: List[Dict] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                meta.append(json.loads(line))
    return meta


def load_gold_csv(gold_path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with gold_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            qid = (r.get("qid") or "").strip()
            q = (r.get("question") or "").strip()
            expected = (r.get("expected_ids") or "").strip()
            expected_ids = [x.strip() for x in expected.split(";") if x.strip()]
            if not qid or not q:
                continue
            rows.append({"qid": qid, "question": q, "expected_ids": expected_ids})
    return rows


def hit_and_recall_at_k(expected_ids: List[str], got_ids: List[str]) -> Tuple[int, float]:
    if not expected_ids:
        # Si no hay gold definido, no lo contamos (lo marcaremos como "missing gold")
        return -1, float("nan")
    got = set(got_ids)
    exp = set(expected_ids)
    inter = exp.intersection(got)
    hit = 1 if len(inter) > 0 else 0
    recall = len(inter) / max(1, len(exp))
    return hit, recall


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gold", required=True, help="CSV con qid,question,expected_ids (separados por ;) ")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--index", default="data/index/faiss.index")
    p.add_argument("--meta", default="data/index/meta.jsonl")
    p.add_argument("--model", default=None, help="Nombre del modelo SentenceTransformers (si el Retriever lo requiere)")
    p.add_argument("--device", default=None, help="cpu|cuda (si aplica)")
    p.add_argument("--out", default="reports/eval/retrieval_eval_v0.json")
    args = p.parse_args()

    gold_path = Path(args.gold)
    index_path = Path(args.index)
    meta_path = Path(args.meta)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Cargar artefactos CAPA B
    index = faiss.read_index(str(index_path))
    meta = load_meta(meta_path)

    if index.ntotal != len(meta):
        raise RuntimeError(f"Mapping inconsistente: index.ntotal={index.ntotal} vs len(meta)={len(meta)}")

    # Embedder real (igual que en tu CLI)
    # Si args.model es None, get_embedder usará el default que tengáis por defecto en el módulo/llamadas.
    # Si en vuestro proyecto el modelo debe especificarse, pásalo por --model.
    model_name = args.model if args.model else "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    emb = get_embedder(model_name=model_name, device=args.device)

    r = Retriever(index=index, meta=meta, embedder_model=model_name, embedder=emb)

    gold = load_gold_csv(gold_path)

    results = []
    hits = []
    recalls = []
    missing = 0

    for row in gold:
        qid = row["qid"]
        q = row["question"]
        expected_ids = row["expected_ids"]

        retrieved = r.retrieve(q, k=args.k)
        got_ids = [h.get("id") for h in retrieved if h.get("id")]

        hit, recall = hit_and_recall_at_k(expected_ids, got_ids)

        if hit == -1:
            missing += 1

        if hit in (0, 1):
            hits.append(hit)
        if not np.isnan(recall):
            recalls.append(recall)

        results.append({
            "qid": qid,
            "question": q,
            "k": args.k,
            "expected_ids": expected_ids,
            "got_ids": got_ids,
            "hit_at_k": hit,
            "recall_at_k": recall,
            "top1": retrieved[0] if retrieved else None,
        })

    summary = {
        "gold_file": str(gold_path),
        "index": str(index_path),
        "meta": str(meta_path),
        "model": model_name,
        "device": args.device or "auto",
        "k": args.k,
        "n_questions": len(gold),
        "n_missing_gold": missing,
        "hit_at_k_mean": float(np.mean(hits)) if hits else None,
        "recall_at_k_mean": float(np.mean(recalls)) if recalls else None,
    }

    payload = {"summary": summary, "results": results}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK: evaluación guardada en", out_path)
    print("SUMMARY:", json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

import faiss  # type: ignore

from rag_core.retriever import Retriever


def parse_expected_ids(s: str) -> List[str]:
    return [x.strip() for x in (s or "").split(";") if x.strip()]


def load_gold(path: Path) -> List[Dict]:
    rows: List[Dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "qid": r["qid"],
                    "question": r["question"],
                    "expected_ids": parse_expected_ids(r["expected_ids"]),
                }
            )
    return rows


def load_meta_jsonl(meta_path: Path) -> List[Dict]:
    meta: List[Dict] = []
    with meta_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            meta.append(json.loads(line))
    return meta


def eval_threshold(
    gold_rows: List[Dict],
    retriever: Retriever,
    k: int,
    min_score: float,
) -> Tuple[Dict, List[Dict]]:
    results: List[Dict] = []
    hit_sum = 0.0
    rec_sum = 0.0

    for row in gold_rows:
        qid = row["qid"]
        q = row["question"]
        expected = row["expected_ids"]

        hits = retriever.retrieve(q, k=k)  # List[Dict] con score/id/source/section/text

        filtered = [h for h in hits if float(h.get("score", -1e9)) >= min_score]
        got_ids = [h.get("id") for h in filtered if h.get("id")]

        exp_set = set(expected)
        got_set = set(got_ids)

        hit_at_k = 1.0 if (exp_set & got_set) else 0.0
        recall_at_k = (len(exp_set & got_set) / len(exp_set)) if exp_set else 0.0

        hit_sum += hit_at_k
        rec_sum += recall_at_k

        results.append(
            {
                "qid": qid,
                "question": q,
                "k": k,
                "min_score": min_score,
                "expected_ids": expected,
                "got_ids": got_ids,
                "hit_at_k": hit_at_k,
                "recall_at_k": recall_at_k,
                "top1": filtered[0] if filtered else None,
            }
        )

    n = len(gold_rows)
    summary = {
        "gold_file": None,
        "k": k,
        "min_score": min_score,
        "n_questions": n,
        "hit_at_k_mean": hit_sum / n if n else 0.0,
        "recall_at_k_mean": rec_sum / n if n else 0.0,
    }
    return summary, results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--min_score", type=float, default=0.35)
    ap.add_argument("--index", required=True)
    ap.add_argument("--meta", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    gold_path = Path(args.gold)
    index_path = Path(args.index)
    meta_path = Path(args.meta)
    out_path = Path(args.out)

    gold_rows = load_gold(gold_path)

    index = faiss.read_index(str(index_path))
    meta = load_meta_jsonl(meta_path)

    retriever = Retriever(index, meta, args.model, args.device)

    summary, results = eval_threshold(gold_rows, retriever, k=args.k, min_score=args.min_score)
    summary["gold_file"] = str(gold_path)

    payload = {"summary": summary, "results": results}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK: saved", out_path)
    print("SUMMARY:", json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

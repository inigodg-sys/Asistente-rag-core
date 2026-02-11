from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, List

REFUSAL_PATTERNS = [
    r"\bno (hay|existe) (evidencia|informaci[oó]n)\b",
    r"\binsuficiente (evidencia|informaci[oó]n)\b",
    r"\bno (puedo|es posible) (concluir|determinar)\b",
    r"\bno (se (encuentra|indica|menciona)|aparece) en (los|las) (documentos|bases|anexos)\b",
    r"\bno dispongo de (evidencia|informaci[oó]n)\b",
    r"\bno (est[áa]|se encuentra) (disponible|especificado)\b",
    r"\bno (puedo|podemos) responder\b",
    r"\bla evidencia proporcionada no contiene\b",
    r"\bno contiene informaci[oó]n\b",

    # Variantes frecuentes (observadas en tus raws)
    r"\bno especifica\b",
    r"\bno se especifica\b",
    r"\bno incluye\b",
    r"\bno se incluye\b",
    r"\bno indica\b",
    r"\bno se indica\b",
    r"\bno menciona\b",
    r"\bno se menciona\b",
    r"\bno detalla\b",
    r"\bno se detalla\b",
    r"\bno define\b",
    r"\bno se define\b",
    r"\bno establece\b",
    r"\bno se establece\b",
    r"\bno proporciona\b",
    r"\bno se proporciona\b",
    r"\bno consta\b",
    r"\bno figura\b",
    r"\bno es posible afirmar\b",
]

CITATION_PATTERNS = [
    r"\bCitas\s*:",
    r"\bSources?\b",
    r"\bFuentes?\b",
    r"\[\s*[^|\]]+\s*\|\s*[^|\]]+\s*\|\s*[^\]]+\s*\]",  # "- [id | ... | path]"
    r"\bid\s*=",
    r"\bsource\s*=",
]

def read_gold(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def detect_refusal(text: str) -> bool:
    t = (text or "")
    return any(re.search(p, t, flags=re.IGNORECASE) for p in REFUSAL_PATTERNS)

def detect_citations(text: str) -> bool:
    t = (text or "")
    return any(re.search(p, t, flags=re.IGNORECASE) for p in CITATION_PATTERNS)

def run_answer(repo_root: Path, question: str, k: int, min_score: float, backend: str, llm_model: str, device: str) -> str:
    cmd = [
        "python3", "cli/answer.py", question,
        "-k", str(k),
        "--min_score", str(min_score),
       	"--backend", backend,
        "--llm_model", llm_model,
        "--device", device,
    ]
    p = subprocess.run(
        cmd,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return ((p.stdout or "") + "\n" + (p.stderr or "")).strip()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--min_score", type=float, default=0.35)
    ap.add_argument("--backend", default="openai")
    ap.add_argument("--llm_model", default="gpt-4.1-mini")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", default="reports/eval_negative_v1.json")
    ap.add_argument("--save_raw_dir", default="reports/negative_raw")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    gold_path = Path(args.gold)
    out_path = Path(args.out)
    raw_dir = Path(args.save_raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    rows = read_gold(gold_path)

    results: List[Dict] = []
    n_tol = 0
    n_str = 0

    for i, r in enumerate(rows, 1):
        qid = (r.get("qid") or "").strip()
        q = (r.get("question") or "").strip()
        expected = (r.get("expected") or "").strip()

        if not qid or not q:
            continue

        print(f"[NEG] {i}/{len(rows)} {qid}", flush=True)

        raw = run_answer(
            repo_root=repo_root,
            question=q,
            k=args.k,
            min_score=args.min_score,
            backend=args.backend,
            llm_model=args.llm_model,
            device=args.device,
        )

        raw_path = raw_dir / f"{qid}.txt"
        raw_path.write_text(raw, encoding="utf-8")

        has_ref = detect_refusal(raw)
        has_cit = detect_citations(raw)

        correct_tol = (expected == "NO_ANSWER") and has_ref
        correct_str = (expected == "NO_ANSWER") and has_ref and (not has_cit)

        if correct_tol:
            n_tol += 1
        if correct_str:
            n_str += 1

        results.append({
            "qid": qid,
            "question": q,
            "expected": expected,
            "k": args.k,
            "min_score": args.min_score,
            "backend": args.backend,
            "llm_model": args.llm_model,
            "has_refusal": has_ref,
            "has_citations": has_cit,
            "correct_no_answer_tolerant": correct_tol,
            "correct_no_answer_strict": correct_str,
            "raw_path": str(raw_path),
        })

    n = len(results)
    summary = {
        "gold_file": str(gold_path),
        "n_questions": n,
        "k": args.k,
        "min_score": args.min_score,
        "backend": args.backend,
        "llm_model": args.llm_model,
        "no_answer_correct_tolerant": n_tol,
        "no_answer_accuracy_tolerant": (n_tol / n) if n else 0.0,
        "no_answer_correct_strict": n_str,
        "no_answer_accuracy_strict": (n_str / n) if n else 0.0,
        "raw_dir": str(raw_dir),
    }

    payload = {"summary": summary, "results": results}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK:", out_path)
    print("SUMMARY:", json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

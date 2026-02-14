from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional


_CITATION_LINE_RE = re.compile(r"^\s*-\s*\[(?P<id>[^\]|]+)\s*\|", re.UNICODE)
_CITAS_HEADER_RE = re.compile(r"^\s*Citas:\s*$", re.IGNORECASE)


@dataclass
class ItemResult:
    qid: str
    question: str
    expected_ids: List[str]
    used_hit_ids: List[str]
    cited_ids: List[str]
    has_citas_block: bool
    citas_count: int
    citation_coverage: float
    citation_only_from_used: bool
    contains_refusal: bool
    raw_path: str


def _parse_expected_ids(s: str) -> List[str]:
    s = (s or "").strip()
    if not s:
        return []
    # expected ids separated by ';'
    parts = [p.strip() for p in s.split(";")]
    return [p for p in parts if p]


def _extract_cited_ids(answer_text: str) -> Tuple[bool, List[str]]:
    lines = answer_text.splitlines()
    in_citas = False
    cited: List[str] = []
    has_block = False

    for line in lines:
        if _CITAS_HEADER_RE.match(line):
            in_citas = True
            has_block = True
            continue
        if in_citas:
            m = _CITATION_LINE_RE.match(line)
            if m:
                cited.append(m.group("id").strip())
            # stop condition: blank line after citas block (optional)
            # keep reading anyway; citations are bullet lines.
    return has_block, cited


def _extract_used_hit_ids(answer_text: str) -> List[str]:
    """
    Our LLM generator returns JSON-like dict in code? No.
    In this project, answer.py prints human answer + optional 'Citas:' block.
    We therefore approximate "used_hit_ids" = cited_ids (since citations map to used sources).
    """
    _, cited = _extract_cited_ids(answer_text)
    return cited


def _looks_like_refusal(answer_text: str) -> bool:
    t = (answer_text or "").lower()
    # Heuristics similar to negative benchmark, but looser.
    patterns = [
        "no tengo evidencia",
        "no hay evidencia",
        "no está especificado",
        "no se especifica",
        "no indica",
        "no se indica",
        "no menciona",
        "no se menciona",
        "no es posible determinar",
        "suggested",  # just in case
    ]
    return any(p in t for p in patterns)


def _run_answer_py(repo_root: Path, question: str, k: int, min_score: Optional[float],
                   backend: str, llm_model: str, device: str, max_sources: int) -> str:
    cmd = [
        "python3",
        str(repo_root / "cli" / "answer.py"),
        question,
        "-k",
        str(k),
        "--backend",
        backend,
        "--llm_model",
        llm_model,
        "--device",
        device,
        "--max_sources",
        str(max_sources),
    ]
    if min_score is not None:
        cmd += ["--min_score", str(min_score)]

    # We want stdout only; if error, capture for debugging.
    p = subprocess.run(cmd, cwd=str(repo_root), text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"answer.py failed (rc={p.returncode}). stderr:\n{p.stderr}\nstdout:\n{p.stdout}")
    return p.stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True, help="CSV con gold generativo (qid,question,expected_ids,notes)")
    ap.add_argument("--k", type=int, default=20)
    ap.add_argument("--min_score", type=float, default=None)
    ap.add_argument("--max_sources", type=int, default=10)
    ap.add_argument("--backend", type=str, default="openai")
    ap.add_argument("--llm_model", type=str, default="gpt-4.1-mini")
    ap.add_argument("--device", type=str, default="cpu")
    ap.add_argument("--out", required=True)
    ap.add_argument("--save_raw_dir", required=True)
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    gold_path = Path(args.gold)
    out_path = Path(args.out)
    raw_dir = Path(args.save_raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(open(gold_path, "r", encoding="utf-8", newline="")))

    results: List[Dict] = []
    for i, r in enumerate(rows, 1):
        qid = (r.get("qid") or "").strip()
        q = (r.get("question") or "").strip()
        exp_ids = _parse_expected_ids(r.get("expected_ids") or "")

        print(f"[GEN] {i}/{len(rows)} {qid}")

        txt = _run_answer_py(
            repo_root=repo_root,
            question=q,
            k=args.k,
            min_score=args.min_score,
            backend=args.backend,
            llm_model=args.llm_model,
            device=args.device,
            max_sources=args.max_sources,
        )

        raw_path = raw_dir / f"{qid}.txt"
        raw_path.write_text(txt, encoding="utf-8")

        has_citas, cited_ids = _extract_cited_ids(txt)

        # In our system, citations correspond to evidence used. Use that as proxy.
        used_hit_ids = _extract_used_hit_ids(txt)

        # Citation coverage: how many expected ids are present in citations.
        exp_set = set(exp_ids)
        cited_set = set(cited_ids)
        coverage = (len(exp_set & cited_set) / len(exp_set)) if exp_set else 0.0

        # Strict: cited ids should be subset of "used" (here same), keep field anyway.
        citation_only_from_used = set(cited_ids).issubset(set(used_hit_ids))

        contains_refusal = _looks_like_refusal(txt)

        item = ItemResult(
            qid=qid,
            question=q,
            expected_ids=exp_ids,
            used_hit_ids=used_hit_ids,
            cited_ids=cited_ids,
            has_citas_block=has_citas,
            citas_count=len(cited_ids),
            citation_coverage=coverage,
            citation_only_from_used=citation_only_from_used,
            contains_refusal=contains_refusal,
            raw_path=str(raw_path),
        )
        results.append(item.__dict__)

    # Aggregate metrics
    n = len(results)
    n_with_citas = sum(1 for it in results if it["has_citas_block"])
    mean_cov = sum(it["citation_coverage"] for it in results) / n if n else 0.0
    strict_ok = sum(1 for it in results if it["citation_only_from_used"])
    refusals = sum(1 for it in results if it["contains_refusal"])

    summary = {
        "gold_file": str(gold_path),
        "n_questions": n,
        "k": args.k,
        "min_score": args.min_score,
        "max_sources": args.max_sources,
        "backend": args.backend,
        "llm_model": args.llm_model,
        "device": args.device,
        "has_citas_rate": n_with_citas / n if n else 0.0,
        "mean_citation_coverage": mean_cov,
        "citation_only_from_used_rate": strict_ok / n if n else 0.0,
        "refusal_rate": refusals / n if n else 0.0,
        "raw_dir": str(raw_dir),
    }

    out = {"summary": summary, "results": results}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK:", out_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

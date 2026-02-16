from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

"""Genera evidencia reproducible de la CAPA A (ingesta).

Uso:
  python tools/generate_ingest_evidence.py --mode smoke
  python tools/generate_ingest_evidence.py --mode full --write-jsonl 0

- mode=smoke: crea un mini-corpus dentro de un tmp dir y ejecuta ingest_corpus
- mode=full: ejecuta ingest_corpus sobre el repo actual (data/raw/...)

Artefactos (por defecto):
  reports/ingest_<mode>/
    - run_manifest.json
    - chunk_stats.json
    - chunks.jsonl (si write_jsonl=1)

Este script es ideal para anexar en el TFM como evidencia de reproducibilidad.
"""

import argparse
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List

from rag_core.ingest import IngestConfig, ingest_corpus, save_chunks_jsonl


def _git_head(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root))
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def _write_mini_repo(repo_root: Path) -> None:
    (repo_root / "data/raw/web").mkdir(parents=True, exist_ok=True)
    (repo_root / "data/raw/csv").mkdir(parents=True, exist_ok=True)
    (repo_root / "data/raw/json").mkdir(parents=True, exist_ok=True)

    (repo_root / "data/raw/web/demo.md").write_text(
        "Intro.\n\n## 1 Alcance\nTexto del alcance.\n\n## 2 Requisitos\nR1: algo.\nR2: algo más.\n",
        encoding="utf-8",
    )

    (repo_root / "data/raw/web/demo.txt").write_text(
        "Documento TXT.\n\nSección 1\n- Punto A\n- Punto B\n\nFin.\n",
        encoding="utf-8",
    )

    (repo_root / "data/raw/web/demo.html").write_text(
        "<html><body><h1>Doc HTML</h1><p>Texto en <b>HTML</b>.</p><ul><li>Item 1</li><li>Item 2</li></ul></body></html>",
        encoding="utf-8",
    )

    (repo_root / "data/raw/csv/demo.csv").write_text(
        "col1,col2\na,1\nb,2\n",
        encoding="utf-8",
    )
    (repo_root / "data/raw/json/definiciones_demo.json").write_text(
        json.dumps(
            [
                {"id": "D1", "termino": "SLA", "definicion": "Acuerdo de nivel de servicio"},
                {"id": "D2", "termino": "KPI", "definicion": "Indicador clave"},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _chunk_stats(chunks) -> Dict[str, Any]:
    lengths: List[int] = [len(c.text) for c in chunks]
    by_type: Dict[str, int] = {}
    for c in chunks:
        by_type[c.doc_type] = by_type.get(c.doc_type, 0) + 1

    def _safe_mean(xs: List[int]) -> float:
        return (sum(xs) / len(xs)) if xs else 0.0
    by_ext: Dict[str, int] = {}
    for c in chunks:
        ext = Path(c.source).suffix.lower()
        by_ext[ext] = by_ext.get(ext, 0) + 1

    return {
        "n_chunks": len(chunks),
        "by_doc_type": by_type,
        "by_source_ext": by_ext,
        "length_chars": {
            "min": min(lengths) if lengths else 0,
            "mean": round(_safe_mean(lengths), 2),
            "max": max(lengths) if lengths else 0,
        },
        "sample_ids": [c.id for c in chunks[:10]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--write-jsonl", type=int, choices=[0, 1], default=1)
    args = ap.parse_args()

    repo_root = Path.cwd()

    if args.mode == "smoke":
        with tempfile.TemporaryDirectory() as td:
            tmp_root = Path(td)
            _write_mini_repo(tmp_root)
            cfg = IngestConfig(repo_root=tmp_root)
            chunks = ingest_corpus(cfg)

            out_dir = repo_root / "reports" / "ingest_smoke"
            out_dir.mkdir(parents=True, exist_ok=True)

            if args.write_jsonl:
                save_chunks_jsonl(chunks, out_dir / "chunks.jsonl")

            stats = _chunk_stats(chunks)
            manifest = {
                "mode": "smoke",
                "python": sys.version,
                "platform": platform.platform(),
                "cwd": str(repo_root),
                "git_head": _git_head(repo_root),
                "cfg": {
                    "normative_target_chars": cfg.normative_target_chars,
                    "normative_max_chars": cfg.normative_max_chars,
                    "normative_overlap_chars": cfg.normative_overlap_chars,
                },
                "stats": stats,
            }

            (out_dir / "chunk_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
            (out_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

            print(f"OK: evidencia generada en {out_dir}")
            return 0

    # mode == full
    cfg = IngestConfig(repo_root=repo_root)
    chunks = ingest_corpus(cfg)

    out_dir = repo_root / "reports" / "ingest_full"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.write_jsonl:
        save_chunks_jsonl(chunks, out_dir / "chunks.jsonl")

    stats = _chunk_stats(chunks)
    manifest = {
        "mode": "full",
        "python": sys.version,
        "platform": platform.platform(),
        "cwd": str(repo_root),
        "git_head": _git_head(repo_root),
        "cfg": {
            "normative_target_chars": cfg.normative_target_chars,
            "normative_max_chars": cfg.normative_max_chars,
            "normative_overlap_chars": cfg.normative_overlap_chars,
        },
        "stats": stats,
    }

    (out_dir / "chunk_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: evidencia generada en {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

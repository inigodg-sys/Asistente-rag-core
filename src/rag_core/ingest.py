from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

from rag_core.clean_markdown import clean_markdown

# --- OCR noise fix (Spanish): ci6n/ci6nes ---
_GAP = r"[ \t\u00A0\u200b\u200c\u200d\ufeff]*"

_RE_CI6NES = re.compile(fr"c{_GAP}i{_GAP}6{_GAP}n{_GAP}e{_GAP}s", re.IGNORECASE)
_RE_CI6N   = re.compile(fr"c{_GAP}i{_GAP}6{_GAP}n", re.IGNORECASE)

def _only_letters(s: str) -> str:
    return re.sub(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ]", "", s)

def _rep_ci6nes(m: re.Match) -> str:
    letters = _only_letters(m.group(0))
    return "CIONES" if letters.isupper() else "ciones"

def _rep_ci6n(m: re.Match) -> str:
    letters = _only_letters(m.group(0))
    return "CIÓN" if letters.isupper() else "ción"

def fix_spanish_ocr_noise(text: str) -> str:
    # 1) plural (sin tilde): acciones, publicaciones, etc.
    text = _RE_CI6NES.sub(_rep_ci6nes, text)
    # 2) singular (con tilde): acción, publicación, etc.
    text = _RE_CI6N.sub(_rep_ci6n, text)
    return text



DocType = Literal["normativa", "tabla", "definicion", "tutorial", "formulario"]
FmtType = Literal["md", "csv", "json"]


# =========================
# Modelos
# =========================

@dataclass(frozen=True)
class DocumentDescriptor:
    path: Path
    doc_type: DocType
    format: FmtType


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    doc_type: DocType
    section: Optional[str] = None
    id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadatos: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IngestConfig:
    repo_root: Path = Path(".")
    raw_web: Path = Path("data/raw/web")
    raw_csv: Path = Path("data/raw/csv")
    raw_json: Path = Path("data/raw/json")

    # Chunking normativa (MVP): ~600–900 chars con overlap
    normative_target_chars: int = 800
    normative_max_chars: int = 900
    normative_overlap_chars: int = 120

    include_exts: Tuple[str, ...] = (".md", ".csv", ".json")
    exclude_names_contains: Tuple[str, ...] = (".gitkeep",)

    tutorial_name_hints: Tuple[str, ...] = ("rag", "tutorial", "guia", "guide")
    formulario_name_hints: Tuple[str, ...] = ("a06", "formulario")


# =========================
# Discover
# =========================

def discover_documents(cfg: IngestConfig) -> List[DocumentDescriptor]:
    roots = [
        cfg.repo_root / cfg.raw_web,
        cfg.repo_root / cfg.raw_csv,
        cfg.repo_root / cfg.raw_json,
    ]

    out: List[DocumentDescriptor] = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if any(x in p.name for x in cfg.exclude_names_contains):
                continue
            if p.suffix.lower() not in cfg.include_exts:
                continue

            fmt = _ext_to_format(p.suffix.lower())
            if fmt is None:
                continue

            doc_type = _infer_doc_type(p, fmt, cfg)
            out.append(DocumentDescriptor(path=p, doc_type=doc_type, format=fmt))

    return sorted(out, key=lambda d: str(d.path))


def _ext_to_format(ext: str) -> Optional[FmtType]:
    return {"md": "md", "csv": "csv", "json": "json"}.get(ext.lstrip("."))


def _infer_doc_type(path: Path, fmt: FmtType, cfg: IngestConfig) -> DocType:
    name = path.name.lower()
    if any(h in name for h in cfg.formulario_name_hints):
        return "formulario"
    if any(h in name for h in cfg.tutorial_name_hints):
        return "tutorial"
    if fmt == "csv":
        return "tabla"
    if fmt == "json":
        return "definicion"
    return "normativa"


# =========================
# Read/parse
# =========================

def read_and_parse(desc: DocumentDescriptor) -> Any:
    if desc.format == "md":
       text = desc.path.read_text(encoding="utf-8", errors="replace")
       text = fix_spanish_ocr_noise(text)
       return text

    if desc.format == "csv":
        return _read_csv(desc.path)
    if desc.format == "json":
        return json.loads(desc.path.read_text(encoding="utf-8", errors="replace"))
    raise ValueError(f"Formato no soportado: {desc.format}")


def _read_csv(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: fix_spanish_ocr_noise(v or "") for k, v in row.items()})

    return rows


# =========================
# Normalize + chunk
# =========================

_HEADING_SECTION_RE = re.compile(r"^\s*#{1,6}\s+(?P<section>[A-Za-z]?\d+(?:\.\d+)*\.?)\b")


def ingest_corpus(cfg: IngestConfig) -> List[Chunk]:
    """
    Orquestador del MVP de ingesta:
    - descubre documentos
    - lee y parsea
    - limpia (clean_markdown v1)
    - chunking a un modelo común (Chunk)
    """
    chunks: List[Chunk] = []
    for desc in discover_documents(cfg):
        parsed = read_and_parse(desc)

        if desc.format == "md":
            chunks.extend(_ingest_md(desc, parsed, cfg))
        elif desc.format == "csv":
            chunks.extend(_ingest_csv(desc, parsed))
        elif desc.format == "json":
            chunks.extend(_ingest_json(desc, parsed))

    return chunks


def _ingest_md(desc: DocumentDescriptor, md_text: str, cfg: IngestConfig) -> List[Chunk]:
    cleaned = clean_markdown(md_text)
    blocks = _split_md_into_section_blocks(cleaned)

    out: List[Chunk] = []
    for section_id, text in blocks:
        pieces = chunk_text(
            text,
            target=cfg.normative_target_chars,
            max_chars=cfg.normative_max_chars,
            overlap=cfg.normative_overlap_chars,
        )
        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if not piece:
                continue
            out.append(
                Chunk(
                    text=piece,
                    source=str(desc.path),
                    doc_type=desc.doc_type,
                    section=section_id,
                    id=f"{desc.path.stem}:{section_id}:{i}",
                    metadatos={"chunk_index": i},
                )
            )
    return out


def _split_md_into_section_blocks(text: str) -> List[Tuple[str, str]]:
    lines = text.split("\n")
    blocks: List[Tuple[str, str]] = []

    current_section: Optional[str] = None
    buf: List[str] = []

    def flush():
        nonlocal current_section, buf
        if current_section is None:
            return
        body = "\n".join(buf).strip()
        if body:
            blocks.append((current_section, body))
        buf = []

    for line in lines:
        m = _HEADING_SECTION_RE.match(line)
        if m:
            flush()
            sec = m.group("section").strip().rstrip(".")
            current_section = sec if sec else "unknown"
            buf.append(line)
        else:
            if current_section is None:
                current_section = "preamble"
            buf.append(line)

    flush()
    return blocks


def _ingest_csv(desc: DocumentDescriptor, rows: List[Dict[str, str]]) -> List[Chunk]:
    out: List[Chunk] = []
    for i, row in enumerate(rows):
        parts = [f"{k}: {v.strip()}" for k, v in row.items() if (v or "").strip()]
        txt = " | ".join(parts).strip()
        if not txt:
            continue
        out.append(
            Chunk(
                text=txt,
                source=str(desc.path),
                doc_type="tabla",
                section=None,
                id=f"{desc.path.stem}:row:{i}",
                metadatos={"row_index": i, "columns": list(row.keys())},
            )
        )
    return out


def _ingest_json(desc: DocumentDescriptor, obj: Any) -> List[Chunk]:
    """
    MVP: extrae definiciones si el JSON tiene campos tipo:
      {id, termino/término, definicion/definición}
    """
    entries: List[Tuple[str, str, str]] = []

    def add_one(d: Dict[str, Any]):
        id_ = str(d.get("id", "")).strip()
        termino = str(d.get("termino", d.get("término", ""))).strip()
        definicion = str(d.get("definicion", d.get("definición", ""))).strip()
        
        termino = fix_spanish_ocr_noise(termino)
        definicion = fix_spanish_ocr_noise(definicion)
        if id_ and termino and definicion:
            entries.append((id_, termino, definicion))

    if isinstance(obj, list):
        for it in obj:
            if isinstance(it, dict):
                add_one(it)
    elif isinstance(obj, dict):
        for key in ("definitions", "definiciones"):
            if key in obj and isinstance(obj[key], list):
                for it in obj[key]:
                    if isinstance(it, dict):
                        add_one(it)
                break
        else:
            for k, v in obj.items():
                if isinstance(v, dict):
                    d = dict(v)
                    d.setdefault("id", k)
                    add_one(d)

    out: List[Chunk] = []
    for (id_, termino, definicion) in entries:
        out.append(
            Chunk(
                text=f"{termino}: {definicion}",
                source=str(desc.path),
                doc_type="definicion",
                section=id_,
                id=f"def:{id_}",
                metadatos={"termino": termino},
            )
        )
    return out


def chunk_text(text: str, target: int, max_chars: int, overlap: int) -> List[str]:
    text = text.strip()
    if not text:
        return []

    n = len(text)
    chunks: List[str] = []
    start = 0

    while start < n:
        prev_start = start
        end = min(start + max_chars, n)

        # Si el texto restante cabe, cerramos
        if n - start <= max_chars:
            chunks.append(text[start:n])
            break

        preferred = min(start + target, end)
        cut = _find_cut(text, start, end, preferred)
        if cut <= start:
            cut = end

        # Guardamos chunk
        chunks.append(text[start:cut])

        # Proponemos siguiente start con solape
        next_start = max(0, cut - overlap)

        # ✅ Regla anti-bucle: si no avanzamos, avanzamos sin overlap
        if next_start <= prev_start:
            next_start = cut

        # ✅ Segunda red de seguridad: si aún no avanza, salimos
        if next_start <= prev_start:
            break

        start = next_start

    return chunks



def _find_cut(text: str, start: int, end: int, preferred: int) -> int:
    window = text[start:end]
    rel = preferred - start
    rel = max(0, min(rel, len(window)))

    for sep in ("\n\n", "\n", " "):
        pos = window.rfind(sep, 0, rel)
        if pos != -1 and (start + pos) > start + 50:
            return start + pos

    for sep in ("\n\n", "\n", " "):
        pos = window.find(sep, rel)
        if pos != -1 and (start + pos) < end - 20:
            return start + pos

    return end


def save_chunks_jsonl(chunks: Sequence[Chunk], out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c.__dict__, ensure_ascii=False) + "\n")

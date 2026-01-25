from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional


def _one_line(text: str, max_len: int = 240) -> str:
    """Convierte un bloque en una frase corta y estable (determinista)."""
    t = " ".join((text or "").strip().split())
    if len(t) <= max_len:
        return t
    return t[: max_len - 1].rstrip() + "…"


def _format_citation(hit: Dict[str, Any]) -> str:
    """Formato de cita estable y fácil de auditar."""
    src = hit.get("source", "")
    sec = hit.get("section", "")
    cid = hit.get("id", "")
    return f"[{cid} | {sec} | {src}]"


@dataclass(frozen=True)
class GeneratorConfig:
    max_sources: int = 3               # cuántos chunks usamos para responder
    min_score: Optional[float] = None  # si se define, ignora hits por debajo
    max_quote_len: int = 240           # cuánto texto mostramos por evidencia


class Generator:
    """
    Generador determinista (baseline) para CAPA D.
    No usa LLM. No inventa: solo reescribe/condensa evidencia recuperada.
    """

    def __init__(self, cfg: Optional[GeneratorConfig] = None):
        self.cfg = cfg or GeneratorConfig()

    def generate(self, question: str, hits: List[Dict[str, Any]]) -> Dict[str, Any]:
        q = (question or "").strip()
        hits = hits or []

        # 1) Si no hay evidencia, no inventamos
        if not hits:
            return {
                "answer": "No tengo evidencia suficiente en los documentos recuperados para responder a esa pregunta.",
                "citations": [],
                "used_hit_ids": [],
            }

        # 2) Filtrado opcional por score
        filtered: List[Dict[str, Any]] = []
        for h in hits:
            if self.cfg.min_score is None:
                filtered.append(h)
            else:
                try:
                    if float(h.get("score", 0.0)) >= float(self.cfg.min_score):
                        filtered.append(h)
                except Exception:
                    filtered.append(h)

        if not filtered:
            return {
                "answer": "No tengo evidencia suficiente (los fragmentos recuperados no alcanzan el umbral mínimo de relevancia).",
                "citations": [],
                "used_hit_ids": [],
            }

        # 3) Tomamos top-N (ya vienen ordenados por score desde Retriever)
        top = filtered[: self.cfg.max_sources]

        # 4) Construimos respuesta: resumen + evidencias en bullets + citas
        bullets = []
        citations = []
        used_ids = []

        for h in top:
            cid = str(h.get("id", "")).strip()
            if cid:
                used_ids.append(cid)
            citations.append({
                "id": h.get("id"),
                "source": h.get("source"),
                "section": h.get("section"),
                "score": h.get("score"),
            })

            snippet = _one_line(str(h.get("text", "")), max_len=self.cfg.max_quote_len)
            bullets.append(f"- {snippet} {_format_citation(h)}")

        header = "Según los fragmentos recuperados, la evidencia relevante es:"
        if q:
            header = f"Pregunta: {q}\n\n{header}"

        answer = header + "\n" + "\n".join(bullets)

        return {
            "answer": answer,
            "citations": citations,
            "used_hit_ids": used_ids,
        }

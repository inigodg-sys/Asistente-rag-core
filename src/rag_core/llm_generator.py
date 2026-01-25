from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional

from rag_core.generator import GeneratorConfig, _format_citation, _one_line
from rag_core.llm_backend import LLMClient


@dataclass(frozen=True)
class LLMGeneratorConfig(GeneratorConfig):
    # hereda max_sources, min_score, max_quote_len
    system_style: str = "Responde de forma clara y concisa."
    require_citations: bool = True


class LLMGenerator:
    """
    Generador con LLM: usa hits como contexto y produce respuesta + citas.
    Mantiene regla no-alucinación.
    """

    def __init__(self, llm: LLMClient, cfg: Optional[LLMGeneratorConfig] = None):
        self.llm = llm
        self.cfg = cfg or LLMGeneratorConfig()

    def generate(self, question: str, hits: List[Dict[str, Any]]) -> Dict[str, Any]:
        q = (question or "").strip()
        hits = hits or []

        if not hits:
            return {
                "answer": "No tengo evidencia suficiente en los documentos recuperados para responder a esa pregunta.",
                "citations": [],
                "used_hit_ids": [],
            }

        # Filtrado por score (si aplica)
        filtered = []
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

        top = filtered[: self.cfg.max_sources]

        # Construimos prompt con evidencia + citas
        context_lines = []
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
            context_lines.append(f"- {snippet} {_format_citation(h)}")

        prompt = (
            f"Instrucciones: {self.cfg.system_style}\n"
            f"Pregunta: {q}\n\n"
            "Evidencia (solo puedes usar lo siguiente):\n"
            + "\n".join(context_lines)
            + "\n\n"
            "Redacta una respuesta basada SOLO en la evidencia. "
            "Si la evidencia no basta, dilo explícitamente."
        )

        answer_text = self.llm.complete(prompt).strip()

        # Regla de contrato: si require_citations, añadimos un bloque final con citas usadas
        if self.cfg.require_citations and citations:
            cite_lines = [f"- {_format_citation(h)}" for h in top]
            answer_text = answer_text + "\n\nCitas:\n" + "\n".join(cite_lines)

        return {
            "answer": answer_text,
            "citations": citations,
            "used_hit_ids": used_ids,
        }

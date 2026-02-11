from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import re
from rag_core.generator import GeneratorConfig, _format_citation, _one_line
from rag_core.llm_backend import LLMClient

_NO_ANSWER_PATTERNS = [
    r"\bno (hay|existe) (evidencia|informaci[oó]n)\b",
    r"\binsuficiente (evidencia|informaci[oó]n)\b",
    r"\bno (puedo|es posible) (concluir|determinar)\b",
    r"\bla evidencia proporcionada no contiene\b",
    r"\bno contiene informaci[oó]n\b",
    r"\bno especifica\b",
    r"\bno se especifica\b",
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
    r"\bno incluye\b",
    r"\bno se incluye\b",
]

def _looks_like_no_answer(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    # (Opcional) futuro: si algún día usas sentinel "NO_ANSWER ..."
    if t.upper().startswith("NO_ANSWER"):
        return True
    return any(re.search(p, t, flags=re.IGNORECASE) for p in _NO_ANSWER_PATTERNS)

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
        # Política de higiene: si la respuesta parece NO_ANSWER (rechazo), NO adjuntamos citas
        # para evitar dar falsa sensación de respaldo documental.
        if self.cfg.require_citations and citations and (not _looks_like_no_answer(answer_text)):
         cite_lines = [f"- {_format_citation(h)}" for h in top]
         answer_text = answer_text + "\n\nCitas:\n" + "\n".join(cite_lines)

        return {
            "answer": answer_text,
            "citations": citations,
            "used_hit_ids": used_ids,
        }

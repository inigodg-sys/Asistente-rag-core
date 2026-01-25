from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, List, Dict, Any


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


@dataclass
class MockLLM:
    """LLM determinista: devuelve siempre una respuesta basada en el prompt (sin red)."""
    def complete(self, prompt: str) -> str:
        # Respuesta simple y estable: primera línea + marcador
        lines = [ln.strip() for ln in prompt.splitlines() if ln.strip()]
        head = lines[0] if lines else "Respuesta"
        return f"{head}\n\n(Respuesta generada por MockLLM)"

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI

from rag_core.llm_backend import LLMClient


@dataclass
class OpenAILLMConfig:
    model: str = "gpt-4.1-mini"
    temperature: float = 0.2
    max_output_tokens: int = 350


class OpenAILLM(LLMClient):
    """
    Backend LLM real (OpenAI) que cumple el contrato LLMClient:
      - complete(prompt: str) -> str
    """
    def __init__(self, api_key: Optional[str] = None, config: Optional[OpenAILLMConfig] = None):
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError(
                "OPENAI_API_KEY no está configurada. "
                "En PowerShell: $env:OPENAI_API_KEY='...'"
            )
        self.client = OpenAI(api_key=key)
        self.cfg = config or OpenAILLMConfig()

    def complete(self, prompt: str) -> str:
        resp = self.client.responses.create(
            model=self.cfg.model,
            input=prompt,
            temperature=self.cfg.temperature,
            max_output_tokens=self.cfg.max_output_tokens,
        )
        return resp.output_text.strip()

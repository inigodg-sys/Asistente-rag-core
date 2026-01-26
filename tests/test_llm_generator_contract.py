from __future__ import annotations

import pytest

from rag_core.llm_backend import MockLLM
from rag_core.llm_generator import LLMGenerator, LLMGeneratorConfig

pytestmark = pytest.mark.generate


def test_llm_generator_no_evidence_no_hallucination():
    g = LLMGenerator(MockLLM())
    out = g.generate("como se paga", hits=[])

    assert "No tengo evidencia suficiente" in out["answer"]
    assert out["citations"] == []
    assert out["used_hit_ids"] == []


def test_llm_generator_includes_only_valid_citations_and_appends_citation_block():
    hits = [
        {
            "score": 0.9,
            "id": "docX:1:1",
            "source": "C:/x/docX.md",
            "section": "1",
            "text": "El pago se realiza mediante cuotas mensuales.",
        },
        {
            "score": 0.8,
            "id": "docY:2:3",
            "source": "C:/x/docY.md",
            "section": "2",
            "text": "El valor del pago se expresa en UF.",
        },
    ]

    g = LLMGenerator(MockLLM(), LLMGeneratorConfig(max_sources=2, min_score=None))
    out = g.generate("como se paga", hits=hits)

    # Debe mantener solo ids presentes
    assert {c["id"] for c in out["citations"]} == {"docX:1:1", "docY:2:3"}
    assert out["used_hit_ids"] == ["docX:1:1", "docY:2:3"]

    # Debe añadir bloque final de citas (formato estable)
    assert "Citas:" in out["answer"]
    assert "[docX:1:1 | 1 | C:/x/docX.md]" in out["answer"]
    assert "[docY:2:3 | 2 | C:/x/docY.md]" in out["answer"]


def test_llm_generator_is_deterministic_with_mockllm():
    hits = [
        {
            "score": 0.9,
            "id": "docX:1:1",
            "source": "C:/x/docX.md",
            "section": "1",
            "text": "El pago se realiza mediante cuotas mensuales.",
        }
    ]

    g = LLMGenerator(MockLLM())
    out1 = g.generate("como se paga", hits=hits)
    out2 = g.generate("como se paga", hits=hits)

    assert out1 == out2

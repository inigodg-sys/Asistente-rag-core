from __future__ import annotations

import pytest

from rag_core.generator import Generator, GeneratorConfig

pytestmark = pytest.mark.generate


def test_generator_no_evidence_no_hallucination():
    g = Generator()
    out = g.generate("como se paga", hits=[])
    assert "No tengo evidencia suficiente" in out["answer"]
    assert out["citations"] == []
    assert out["used_hit_ids"] == []


def test_generator_includes_only_valid_citations():
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
    g = Generator(GeneratorConfig(max_sources=2))
    out = g.generate("como se paga", hits=hits)

    # Debe citar solo ids presentes
    assert "docX:1:1" in out["answer"]
    assert "docY:2:3" in out["answer"]
    assert all(c["id"] in {"docX:1:1", "docY:2:3"} for c in out["citations"])


def test_generator_is_deterministic():
    hits = [
        {
            "score": 0.9,
            "id": "docX:1:1",
            "source": "C:/x/docX.md",
            "section": "1",
            "text": "El pago se realiza mediante cuotas mensuales.",
        }
    ]
    g = Generator()
    out1 = g.generate("como se paga", hits=hits)
    out2 = g.generate("como se paga", hits=hits)
    assert out1 == out2

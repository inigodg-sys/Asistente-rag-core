import pytest

from rag_core.clean_markdown import clean_markdown
from rag_core.clean_markdown_v2 import clean_markdown_v2


# CAPA A — Unit tests (limpieza)
pytestmark = pytest.mark.ingest_unit


def test_returns_str():
    out = clean_markdown("hola")
    assert isinstance(out, str)


def test_normalizes_crlf_to_lf():
    raw = "a.\r\nb.\r\nc.\r"
    out = clean_markdown(raw)
    assert "\r" not in out
    assert "a.\nb.\nc." in out


def test_fix_headings_adds_space_after_hashes():
    raw = "##Titulo\n###Subtitulo\n#Main"
    out = clean_markdown(raw)
    assert "## Titulo" in out
    assert "### Subtitulo" in out
    assert "# Main" in out


def test_fix_numbering_joins_fragment_with_next_line():
    raw = "5.3.1.\nEvaluación técnica\n\nTexto"
    out = clean_markdown(raw)
    # Esperamos que quede en la misma línea (fragmento + título)
    assert ("5.3.1. Evaluación técnica" in out) or ("5.3.1 Evaluación técnica" in out)


def test_fix_lists_double_dash():
    raw = "- - item uno\n- - item dos"
    out = clean_markdown(raw)
    assert "- item uno" in out
    assert "- item dos" in out
    assert "- - item uno" not in out


def test_remove_artifacts_page_numbers_and_separators():
    raw = "23\n-----\nContenido útil\n2023\n___\n"
    out = clean_markdown(raw)
    # 23 debe desaparecer (página suelta <= 3 dígitos)
    assert "\n23\n" not in f"\n{out}\n"
    # Separadores deben desaparecer
    assert "-----" not in out
    assert "___" not in out
    # 2023 debe quedarse (4 dígitos, puede ser un año)
    assert "2023" in out
    # Contenido útil se queda
    assert "Contenido útil" in out


def test_v2_normalizes_bullet_symbol_to_dash():
    raw = "• paneles de información;\n• servicio de Predictor;"
    out_v1 = clean_markdown(raw)
    out_v2 = clean_markdown_v2(raw)

    # v1 no cambia '•' (MVP)
    assert "•" in out_v1

    # v2 sí normaliza a '- '
    assert "- paneles de información;" in out_v2
    assert "- servicio de Predictor;" in out_v2
    assert "•" not in out_v2


def test_does_not_crash_on_long_text():
    raw = ("Linea sin punto\n" * 5000) + "FIN."
    out = clean_markdown(raw)
    assert isinstance(out, str)
    assert len(out) > 0

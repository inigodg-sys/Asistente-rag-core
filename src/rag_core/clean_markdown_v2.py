from __future__ import annotations

import re
from typing import Iterable, List

# Importamos la v1 como “base estable”
from rag_core.clean_markdown import clean_markdown as clean_markdown_v1
from rag_core.clean_markdown import remove_artifacts as remove_artifacts_v1


def clean_markdown_v2(raw_md: str) -> str:
    """
    Versión 2 del limpiador:
    - Mantiene intacta la v1 (pseudocódigo original).
    - Añade normalización de bullets y artefactos extendidos.

    Orden:
      1) v1 (pipeline base)
      2) normalize_bullets (mejora estructural)
      3) remove_artifacts_extended (mejora estructural)
    """
    text = clean_markdown_v1(raw_md)
    text = normalize_bullets(text)
    text = remove_artifacts_extended(text)
    return text


def normalize_bullets(text: str) -> str:
    """
    Normaliza viñetas comunes a formato Markdown "- ".

    Convierte, SOLO al inicio de línea:
      • Texto   -> - Texto
      · Texto   -> - Texto
      – Texto   -> - Texto
      * Texto   -> - Texto

    No toca:
      - listas que ya están con "- "
      - guiones en medio de frases
    """
    lines = text.split("\n")
    out: List[str] = []

    bullet_re = re.compile(r"^(\s*)([•·–*])\s*(.+)$")

    for line in lines:
        m = bullet_re.match(line)
        if m:
            indent, _bullet, content = m.groups()
            out.append(f"{indent}- {content.strip()}")
        else:
            out.append(line)

    return "\n".join(out)


def remove_artifacts_extended(
    text: str,
    extra_prefixes: Iterable[str] = (
        "TOMADO DE RAZÓN",
        "TOMADO DE RAZON",
        "CONTRALORA GENERAL",
        "DOROTHY AURORA",  # ejemplo; ajustable
    ),
) -> str:
    """
    Extiende la eliminación de artefactos.

    Estrategia segura:
      - Primero aplica remove_artifacts_v1 (lo que ya teníamos).
      - Luego elimina líneas cuyo prefijo coincida con 'extra_prefixes'
        (comparación en mayúsculas).
    """
    text = remove_artifacts_v1(text)

    lines = text.split("\n")
    out: List[str] = []

    prefixes_upper = tuple(p.upper() for p in extra_prefixes)

    for line in lines:
        stripped = line.strip()
        upper = stripped.upper()

        if any(upper.startswith(p) for p in prefixes_upper):
            continue

        out.append(line)

    return "\n".join(out)

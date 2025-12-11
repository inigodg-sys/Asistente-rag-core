from __future__ import annotations

import re
from typing import List


def clean_markdown(raw_md: str) -> str:
    """
    Limpia y normaliza un texto Markdown procedente de conversiones PDF/DOCX.

    Etapas (en orden):
      1. Normalizar saltos de línea y espacios.
      2. Corregir numeraciones normativas sencillas.
      3. Normalizar encabezados Markdown (#, ##, ###).
      4. Reparar listas y viñetas básicas.
      5. Eliminar artefactos típicos (números de página, líneas basura).

    Parámetros
    ----------
    raw_md : str
        Texto Markdown bruto.

    Returns
    -------
    str
        Texto Markdown limpio y normalizado.
    """
    text = raw_md

    text = normalize_newlines_and_spaces(text)
    text = fix_numbering(text)
    text = fix_headings(text)
    text = fix_lists(text)
    text = remove_artifacts(text)

    return text


# ============================================================
# 1) Saltos de línea y espacios
# ============================================================

def normalize_newlines_and_spaces(text: str) -> str:
    """
    Normaliza saltos de línea y espacios, y une líneas que parecen
    continuación de una misma frase (heurística muy conservadora).

    Pasos:
      - Convertir CRLF/CR a LF.
      - strip() de cada línea (quita espacios al principio y final).
      - Reducir espacios múltiples internos a un solo espacio.
      - Unir líneas que parecen continuación (usando _looks_like_continuation).
    """
    # Normalizar saltos de línea de Windows/Mac a \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = text.split("\n")
    clean_lines: List[str] = []

    # 1ª pasada: limpiar espacios extremos y reducir espacios múltiples
    for line in lines:
        # Quita espacios al principio y al final
        line = line.strip()
        # Reducir secuencias de espacios múltiples (no tocamos tabs)
        line = re.sub(r"[ ]{2,}", " ", line)
        clean_lines.append(line)

    # 2ª pasada: unir líneas que parecen ser continuación de la anterior
    joined_lines: List[str] = []
    i = 0
    while i < len(clean_lines):
        current = clean_lines[i]
        if i + 1 < len(clean_lines):
            nxt = clean_lines[i + 1]
        else:
            nxt = None

        if nxt is not None and _looks_like_continuation(current, nxt):
            # Unimos current + nxt en una sola línea
            merged = current + " " + nxt
            joined_lines.append(merged)
            i += 2
        else:
            joined_lines.append(current)
            i += 1

    return "\n".join(joined_lines)


def _looks_like_continuation(current: str, nxt: str) -> bool:
    """
    Heurística muy conservadora para decidir si 'nxt' continúa
    la frase de 'current'.

    Reglas principales:
      - current no termina en ., ;, :, ?, ! (puntuación fuerte).
      - current no es un encabezado Markdown ni una viñeta.
      - nxt no empieza con '#', '-' ni con una numeración de sección.
      - nxt no está vacía.

    Esto intenta unir solamente líneas que se han cortado “a mitad de frase”
    por culpa del PDF/DOCX → texto.
    """
    if not current:
        return False

    # Si la línea actual parece encabezado o viñeta, no unimos
    stripped_current = current.lstrip()
    if stripped_current.startswith("#") or stripped_current.startswith("-"):
        return False

    # Si la línea actual termina en puntuación fuerte, asumimos fin de frase
    if current.endswith((".", ";", ":", "?", "!")):
        return False

    if nxt is None:
        return False

    stripped_next = nxt.lstrip()

    # Si la siguiente es encabezado, viñeta o numeración al inicio, no es continuación
    if stripped_next.startswith("#") or stripped_next.startswith("-"):
        return False

    if _starts_with_section_number(stripped_next):
        return False

    # Si la siguiente está vacía, no unimos
    if stripped_next == "":
        return False

    return True


def _starts_with_section_number(line: str) -> bool:
    """
    Detecta si la línea empieza con algo tipo:
      5.3.
      5.3.1
      5.3.1.1
      A06.2.1

    Patrón: opcional letra+digitos, luego grupos de .digitos
    Ej: "5.3.1", "A06.2.1"
    """
    return bool(re.match(r"^[A-Za-z]?\d+(\.\d+)+", line.strip()))


# ============================================================
# 2) Corrección de numeraciones
# ============================================================

def fix_numbering(text: str) -> str:
    """
    Corrige numeraciones normativas sencillas y une fragmentos partidos.

    Casos:
      - "5.3.1.1 ." → "5.3.1.1"
      - Líneas que son solo "5.3.", "5.3.1." etc. se unen con la siguiente.
    """
    lines = text.split("\n")
    result: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else None

        # Quitar " .", ". " u otros residuos después de una numeración completa
        # Ej: "5.3.1.1 ." -> "5.3.1.1"
        line = re.sub(r"^(\d+(\.\d+)+)\s*\.\s*$", r"\1", line)

        # Unir líneas que son trozos de numeración con la siguiente línea
        if _is_number_fragment(line) and nxt is not None:
            merged = line.strip() + " " + nxt.lstrip()
            result.append(merged)
            i += 2
            continue

        result.append(line)
        i += 1

    return "\n".join(result)


def _is_number_fragment(line: str) -> bool:
    """
    Devuelve True si la línea parece un trozo de numeración sola, tipo:
      '5.3.'
      '5.3.1.'
      '5.3.1.1'
      'A06.2.1.'

    para luego unirla con la línea siguiente.
    """
    stripped = line.strip()
    if not stripped:
        return False

    # Aceptar cosas como '5.3.', '5.3.1.', 'A06.2.1.'
    # Permitimos un punto final opcional.
    return bool(re.match(r"^[A-Za-z]?\d+(\.\d+)+\.?$", stripped))


# ============================================================
# 3) Normalizar encabezados Markdown
# ============================================================

def fix_headings(text: str) -> str:
    """
    Normaliza encabezados Markdown simples.

    Caso típico:
      "##5.3 Evaluación"  →  "## 5.3 Evaluación"

    Regla:
      - Si una línea empieza con uno o más '#'
        y no hay espacio tras los '#', se inserta un espacio.
    """
    lines = text.split("\n")
    result: List[str] = []

    for line in lines:
        stripped = line.lstrip()

        # Si empieza por uno o varios # seguidos de algo sin espacio, añadimos espacio.
        # Ej: "##5.3 Evaluación" -> "## 5.3 Evaluación"
        if stripped.startswith("#"):
            match = re.match(r"^(#+)(\S.*)$", stripped)
            if match:
                hashes, rest = match.groups()
                stripped = f"{hashes} {rest}"
                # Volvemos a respetar la indentación original
                line = " " * (len(line) - len(line.lstrip())) + stripped

        result.append(line)

    return "\n".join(result)


# ============================================================
# 4) Reparar listas y viñetas básicas
# ============================================================

def fix_lists(text: str) -> str:
    """
    Repara algunos artefactos típicos de listas.

    Caso implementado (MVP):
      - Doble viñeta: "- - texto" → "- texto"

    Se pueden añadir más reglas en el futuro si el corpus lo requiere.
    """
    lines = text.split("\n")
    result: List[str] = []

    for line in lines:
        stripped = line.lstrip()

        # Corregir doble viñeta: "- - texto" -> "- texto"
        if stripped.startswith("- - "):
            stripped = stripped.replace("- - ", "- ", 1)
            line = " " * (len(line) - len(line.lstrip())) + stripped

        result.append(line)

    return "\n".join(result)


# ============================================================
# 5) Eliminar artefactos típicos
# ============================================================

def remove_artifacts(text: str) -> str:
    """
    Elimina algunas líneas que casi seguro son ruido:

      1) Números de página aislados: "23", "7" (1–3 dígitos).
      2) Líneas con solo guiones o separadores largos: "---", "____", "====".
      3) Cabeceras/pies muy genéricos repetidos:
         - 'LICITACIÓN PUBLICA...'
         - 'LICITACION PUBLICA...'

    Estas reglas se pueden ajustar según veamos el comportamiento en el corpus real.
    """
    lines = text.split("\n")
    result: List[str] = []

    for line in lines:
        stripped = line.strip()

        # 1) Números de página aislados: "23", "7"
        if stripped.isdigit() and len(stripped) <= 3:
            continue

        # 2) Líneas con solo guiones o separadores largos
        if re.match(r"^[-_=]{3,}$", stripped):
            continue

        # 3) Cabeceras/pies muy genéricos repetidos
        upper = stripped.upper()
        if upper.startswith("LICITACIÓN PUBLICA") or upper.startswith("LICITACION PUBLICA"):
            continue

        result.append(line)

    return "\n".join(result)

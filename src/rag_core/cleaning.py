import re
from typing import List


def clean_markdown(raw_md: str) -> str:
    """
    Limpia y normaliza un texto Markdown procedente de conversiones PDF/DOCX.

    Etapas:
      1. Normalizar saltos de línea y espacios.
      2. Corregir numeraciones normativas sencillas.
      3. Normalizar encabezados Markdown (#, ##, ###).
      4. Reparar listas y viñetas básicas.
      5. Eliminar artefactos típicos (números de página, líneas basura).
    """
    text = raw_md

    text = normalize_newlines_and_spaces(text)
    text = fix_numbering(text)
    text = fix_headings(text)
    text = fix_lists(text)
    text = remove_artifacts(text)

    return text


# ---------------------------
# 1) Saltos de línea y espacios
# ---------------------------

def normalize_newlines_and_spaces(text: str) -> str:
    # Normalizar saltos de línea de Windows a \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = text.split("\n")
    clean_lines: List[str] = []

    # 1ª pasada: limpiar espacios extremos y reducir espacios múltiples
    for line in lines:
        line = line.strip()
        # Reducir secuencias de espacios múltiples (pero no tocamos tabs)
        line = re.sub(r"[ ]{2,}", " ", line)
        clean_lines.append(line)

    # 2ª pasada (muy conservadora): unir líneas que parecen continuación
    joined_lines: List[str] = []
    i = 0
    while i < len(clean_lines):
        current = clean_lines[i]
        if i + 1 < len(clean_lines):
            nxt = clean_lines[i + 1]
        else:
            nxt = None

        if nxt is not None and _looks_like_continuation(current, nxt):
            merged = current + " " + nxt
            joined_lines.append(merged)
            i += 2
        else:
            joined_lines.append(current)
            i += 1

    return "\n".join(joined_lines)


def _looks_like_continuation(current: str, nxt: str) -> bool:
    """
    Heurística muy conservadora para decidir si nxt continúa la frase de current.

    Regla básica:
      - current no termina en ., ;, :, ?, ! ni en encabezado Markdown.
      - nxt no empieza con '#', '-', ni con un patrón claro de numeración de sección.
    """
    if not current:
        return False

    # Si la línea actual parece encabezado o viñeta, no unimos
    if current.lstrip().startswith("#") or current.lstrip().startswith("-"):
        return False

    # Si la línea actual termina en puntuación fuerte, no unimos
    if current.endswith((".", ";", ":", "?", "!")):
        return False

    if nxt is None:
        return False

    stripped = nxt.lstrip()

    # Si la siguiente es encabezado, viñeta o numeración al inicio, no es continuación
    if stripped.startswith("#") or stripped.startswith("-"):
        return False

    if _starts_with_section_number(stripped):
        return False

    # Si la siguiente está vacía, no unimos
    if stripped == "":
        return False

    return True


def _starts_with_section_number(line: str) -> bool:
    """
    Detecta si la línea empieza con algo tipo:
      5.3.
      5.3.1
      5.3.1.1
      A06.2.1
    """
    # Patrón: opcional letra+digitos, luego grupos de .digitos
    # Ej: "5.3.1", "A06.2.1"
    return bool(re.match(r"^[A-Za-z]?\d+(\.\d+)+", line.strip()))


# ---------------------------
# 2) Corrección de numeraciones
# ---------------------------

def fix_numbering(text: str) -> str:
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
            merged = line + " " + nxt.lstrip()
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


# ---------------------------
# 3) Normalizar encabezados
# ---------------------------

def fix_headings(text: str) -> str:
    lines = text.split("\n")
    result: List[str] = []

    for line in lines:
        stripped = line.lstrip()

        # Si empieza por uno o varios # seguidos de algo sin espacio, añadimos espacio.
        # Ej: "##5.3 Evaluación" -> "## 5.3 Evaluación"
        if stripped.startswith("#"):
            # Detectar patrón "#texto" sin espacio tras la ristra de #
            match = re.match(r"^(#+)(\S.*)$", stripped)
            if match:
                hashes, rest = match.groups()
                stripped = f"{hashes} {rest}"
                # Volvemos a respetar la indentación original
                line = " " * (len(line) - len(line.lstrip())) + stripped

        result.append(line)

    return "\n".join(result)


# ---------------------------
# 4) Reparar listas
# ---------------------------

def fix_lists(text: str) -> str:
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


# ---------------------------
# 5) Eliminar artefactos
# ---------------------------

def remove_artifacts(text: str) -> str:
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

        # 3) Cabeceras/pies muy genéricos repetidos (ajustar según corpus real)
        if stripped.upper().startswith("LICITACIÓN PUBLICA") or stripped.upper().startswith("LICITACION PUBLICA"):
            continue

        result.append(line)

    return "\n".join(result)

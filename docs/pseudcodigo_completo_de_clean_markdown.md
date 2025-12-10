# Pseudocódigo Completo de `clean_markdown(raw_md: str)`  
## TFM – Asistente RAG · Licitación GF 001/2023  
### Versión consolidada en un único bloque (lista para copiar y pegar)

---

## 1. Descripción general

La función `clean_markdown(raw_md: str) -> str` aplica una serie de transformaciones al texto crudo de un archivo Markdown convertido desde PDF/DOCX.  
Su objetivo es:

- limpiar ruido de conversión,  
- reconstruir la estructura lógica del documento,  
- estabilizar numeraciones normativas,  
- reparar encabezados,  
- reconstruir listas,  
- eliminar artefactos.

El siguiente pseudocódigo agrupa **toda la lógica técnica en un único bloque**, siguiendo las decisiones de diseño documentadas en el proyecto.

---

## 2. Pseudocódigo completo

```python
###############################################################
# clean_markdown(raw_md: str) -> str
# Pseudocódigo general de la función de limpieza de Markdown
###############################################################

function clean_markdown(raw_md: str) -> str:
    """
    Aplica varias etapas de limpieza sobre un texto Markdown:
    1. Normalización de saltos de línea y espacios
    2. Corrección de numeraciones normativas
    3. Normalización de encabezados Markdown
    4. Reparación de listas y viñetas corruptas
    5. Eliminación de artefactos de conversión PDF → MD
    """
    text = raw_md

    # 1. Normalizar saltos de línea y espacios
    text = normalize_newlines_and_spaces(text)

    # 2. Corregir numeraciones del pliego (5.3.1.1, A06.2.1, etc.)
    text = fix_numbering(text)

    # 3. Normalizar encabezados (## 5.3 Evaluación, ### 5.3.1 GF1, etc.)
    text = fix_headings(text)

    # 4. Reparar listas y viñetas (p. ej., "- - Item" → "- Item")
    text = fix_lists(text)

    # 5. Eliminar artefactos de conversión (números de página, líneas basura)
    text = remove_artifacts(text)

    return text



###############################################################
# 1. normalize_newlines_and_spaces(text)
###############################################################

function normalize_newlines_and_spaces(text: str) -> str:
    # Reemplazar \r\n por \n
    text = text.replace("\r\n", "\n")

    # Separar líneas
    lines = text.split("\n")
    clean_lines = []

    # Primera pasada: limpieza básica de espacios
    for line in lines:
        line = trim_espacios_extremos(line)       # quitar espacios al principio y final
        line = reducir_espacios_multiples(line)   # "  " → " "
        clean_lines.append(line)

    # Segunda pasada (opcional): unir líneas que parecen continuar la misma frase
    joined_lines = []
    i = 0
    while i < len(clean_lines):
        current = clean_lines[i]
        next_line = clean_lines[i+1] if (i+1 < len(clean_lines)) else None

        if next_line is not None and es_continuacion_de_frase(current, next_line):
            merged = current + " " + next_line
            joined_lines.append(merged)
            i = i + 2
        else:
            joined_lines.append(current)
            i = i + 1

    return unir_con_nl(joined_lines)



###############################################################
# 2. fix_numbering(text)
###############################################################

function fix_numbering(text: str) -> str:
    lines = text.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        next_line = lines[i+1] if i+1 < len(lines) else None

        # Quitar puntos o espacios sueltos tras numeraciones: "5.3.1.1 ." → "5.3.1.1"
        line = reemplazar_patron(r"^(\d+(\.\d+)+)\s*\.$", r"\1", line)

        # Si la línea parece una numeración incompleta ("5.3.", "4.2.")
        # y la siguiente empieza con otra numeración o texto, unirlas.
        if es_trozo_numeracion(line) and next_line is not None:
            merged = unir_lineas_numeracion(line, next_line)
            result_lines.append(merged)
            i = i + 2
            continue

        result_lines.append(line)
        i = i + 1

    return unir_con_nl(result_lines)



###############################################################
# 3. fix_headings(text)
###############################################################

function fix_headings(text: str) -> str:
    lines = text.split("\n")
    result = []

    for line in lines:
        # Caso típico: "##5.3 Evaluación" → "## 5.3 Evaluación"
        if linea_empieza_con_hash_sin_espacio(line):
            line = insertar_espacio_despues_hash(line)

        # También se puede reforzar consistencia de niveles si se desea
        # Ej.: convertir "# 5. ..." en "## 5. ..."
        # (opcional, según el estilo del corpus)

        result.append(line)

    return unir_con_nl(result)



###############################################################
# 4. fix_lists(text)
###############################################################

function fix_lists(text: str) -> str:
    lines = text.split("\n")
    result = []

    for i in range(0, len(lines)):
        line = lines[i]

        # Arreglar viñetas corruptas: "- - item" → "- item"
        if linea_es_doble_viñeta(line):
            line = corregir_doble_viñeta(line)

        # Opcional: unir líneas de la misma viñeta si no terminan en ".", ";", etc.
        # y la línea siguiente no empieza por "-", "#", ni numeración de sección.

        result.append(line)

    return unir_con_nl(result)



###############################################################
# 5. remove_artifacts(text)
###############################################################

function remove_artifacts(text: str) -> str:
    lines = text.split("\n")
    result = []

    for line in lines:
        # Detectar y eliminar números de página aislados
        if es_numero_de_pagina(line):
            continue

        # Detectar encabezados o pies repetidos del PDF
        if es_encabezado_repetido_pdf(line):
            continue

        # Eliminar líneas compuestas solo por guiones u otros símbolos residuales
        if es_linea_solo_guiones_basura(line):
            continue

        result.append(line)

    return unir_con_nl(result)

# CH06 — Benchmark Negativo v2 (No-Answer Correctness)

## 0) Objetivo y relación con CH04/CH05

En **CH04** se construyó y calibró `gold_retrieval_v2` (50 preguntas) para medir el rendimiento del retrieval cuando **sí existe evidencia** en el corpus.
En **CH05** se realizaron ablations (`k` y `min_score`) para justificar decisiones de parámetros y entender el trade-off cobertura vs coste/ruido.

Este capítulo (CH06) completa la evaluación desde la perspectiva de **seguridad y robustez**: medir el comportamiento del sistema cuando **NO existe evidencia suficiente** en el corpus.

**Idea clave:** un sistema RAG industrial no solo debe responder bien cuando hay evidencia, sino también **abstenerse correctamente** cuando no la hay, evitando alucinaciones y evitando citas engañosas.

---

## 1) Dataset negativo: `gold_negative_v1`

### 1.1 Qué contiene

Archivo:
- `eval/gold_negative_v1.csv`

Formato:
- `qid`
- `question`
- `expected` (en este benchmark, siempre `NO_ANSWER`)
- `notes`

Cada fila representa una pregunta **plausible** en contexto de licitación, pero diseñada para que el corpus actual **no contenga información suficiente** para responder con evidencia verificable.

---

## 2) Definición de la tarea: “no-answer correctness”

Para cada pregunta negativa, el comportamiento deseado es:

1. **Rechazo correcto (refusal / abstención)**
   El sistema debe indicar explícitamente que no puede responder con la evidencia disponible (p.ej. “no hay evidencia”, “no está especificado”, “no se puede determinar con los documentos disponibles”).

2. **No alucinación**
   No debe inventar datos (números, fechas, requisitos) que no están soportados por el corpus.

3. **Higiene de citas**
   Si el sistema se abstiene, no debe adjuntar citas que puedan inducir a pensar que existe respaldo documental para la respuesta.

Dado que diferentes implementaciones pueden tener distintas políticas de citación, se definen dos métricas:

- **No-Answer Accuracy (Tolerant):** correcto si hay rechazo explícito, independientemente de si hay citas.
- **No-Answer Accuracy (Strict):** correcto si hay rechazo explícito **y además** no hay citas.

Estas dos métricas separan:
- **Seguridad semántica** (no responder cuando no hay evidencia) → tolerant
- **Calidad/higiene de citación** en rechazos → strict

---

## 3) Metodología de evaluación (runner reproducible)

### 3.1 Ejecución

Se utiliza un runner automático que:
- lee `eval/gold_negative_v1.csv`,
- para cada pregunta ejecuta `cli/answer.py` con parámetros fijos (`k=10`, `min_score=0.35`),
- guarda la salida cruda por `qid` en un directorio de auditoría,
- aplica heurísticos para detectar:
  - **rechazo** (patrones de lenguaje),
  - **presencia de citas**,
- computa métricas “tolerant” y “strict”.

Artefactos:
- reporte JSON: `reports/eval_negative_v1_v4.json`
- auditoría por pregunta: `reports/negative_raw_v1_v4/<qid>.txt`

---

## 4) Resultados finales (v4) — k=10, min_score=0.35

Configuración:
- `k = 10`
- `min_score = 0.35`
- `backend = openai`
- `llm_model = gpt-4o-mini`
- `n_questions = 20`

### 4.1 Métricas agregadas

Resultado final:

- **No-Answer Accuracy (Tolerant): 20/20 = 1.00**
- **No-Answer Accuracy (Strict): 20/20 = 1.00**

Resumen (del reporte):

```json
{
  "gold_file": "eval/gold_negative_v1.csv",
  "n_questions": 20,
  "k": 10,
  "min_score": 0.35,
  "backend": "openai",
  "llm_model": "gpt-4o-mini",
  "no_answer_correct_tolerant": 20,
  "no_answer_accuracy_tolerant": 1.0,
  "no_answer_correct_strict": 20,
  "no_answer_accuracy_strict": 1.0,
  "raw_dir": "reports/negative_raw_v1_v4"
}
```

### 4.2 Interpretación

- **Tolerant = 1.00** indica que el sistema se abstiene correctamente en todas las preguntas negativas: el modelo expresa explícitamente que la evidencia no permite responder con precisión (no se inventan requisitos, cifras o fechas).
- **Strict = 1.00** confirma que, además, cuando el sistema se abstiene, no adjunta citas (evitando confusión y reforzando la seguridad interpretativa de la salida).

Este resultado es especialmente relevante en escenarios de licitación, donde una respuesta inventada o una cita irrelevante puede inducir errores graves.

---

## 5) Cambios y calibración que llevaron al resultado final

Este benchmark pasó por varias iteraciones. La versión final (v4) se alcanzó con dos mejoras principales:

### 5.1 Mejora 1: Higiene de citación en NO_ANSWER

**Problema observado (inicialmente):**
El sistema tendía a imprimir un bloque de `Citas:` incluso cuando el contenido principal era un rechazo (`NO_ANSWER`). Esto producía `strict ≈ 0.0` aunque el rechazo fuera correcto.

**Solución implementada (política de salida):**
Se cambió `src/rag_core/llm_generator.py` para aplicar la política:
> Si la respuesta parece NO_ANSWER (rechazo), NO adjuntar el bloque “Citas:”

Esto se implementó añadiendo un detector `_looks_like_no_answer(answer_text)` y condicionando la concatenación de citas:

```python
if self.cfg.require_citations and citations and (not _looks_like_no_answer(answer_text)):
    cite_lines = [f"- {_format_citation(h)}" for h in top]
    answer_text = answer_text + "\n\nCitas:\n" + "\n".join(cite_lines)
```

**Impacto esperado:**
- Mejora la higiene de citación en abstención.
- Evita dar falsa sensación de respaldo documental.
- Permite que strict refleje realmente el comportamiento “sin citas”.

### 5.2 Mejora 2: Robustez del detector de rechazo (evaluador)

**Problema observado durante auditoría:**
Varias “fallas” resultaron ser falsos negativos del evaluador: el modelo rechazaba correctamente usando formulaciones como:
- “La evidencia proporcionada no especifica…”
- “La evidencia proporcionada no incluye…”
- “No es posible afirmar…”
pero el evaluador no detectaba esas expresiones y marcaba `has_refusal=False`.

**Solución implementada:**
Se robusteció `tools/eval_negative.py` ampliando `REFUSAL_PATTERNS` con variantes observadas en los outputs reales (no especifica, no incluye, no indica, no menciona, etc.).

Además, se corrigieron incidencias operativas:
- archivos desincronizados entre Windows/WSL,
- errores de sintaxis por inserciones/pegados incorrectos,
- y se consolidó una versión limpia y compilable del evaluator.

**Impacto esperado:**
- La métrica tolerant deja de penalizar respuestas correctas.
- La evaluación se alinea con el comportamiento real del sistema.
- Se garantiza reproducibilidad.

---

## 6) Auditoría y reproducibilidad

### 6.1 Ejecución (comando principal)

```bash
python3 tools/eval_negative.py \
  --gold eval/gold_negative_v1.csv \
  --k 10 --min_score 0.35 \
  --backend openai --llm_model gpt-4o-mini --device cpu \
  --out reports/eval_negative_v1_v4.json \
  --save_raw_dir reports/negative_raw_v1_v4
```

### 6.2 Verificación del resumen

```bash
python3 -c "import json; print(json.load(open('reports/eval_negative_v1_v4.json','r',encoding='utf-8'))['summary'])"
```

### 6.3 Inspección manual (auditoría por pregunta)

```bash
sed -n '1,120p' reports/negative_raw_v1_v4/<qid>.txt
```

Esto permite verificar manualmente:
- que el rechazo es explícito,
- que no hay afirmaciones inventadas,
- que no hay bloque “Citas:” en NO_ANSWER (strict).

### 6.4 Sanity check: conteo de fallos

```bash
python3 - <<'PY'
import json
d=json.load(open("reports/eval_negative_v1_v4.json","r",encoding="utf-8"))
bad=[it for it in d["results"] if not it.get("correct_no_answer_tolerant", False)]
print("fail_tolerant:", len(bad))
PY
```

---

## 7) Limitaciones y future work

1.  **Dependencia de heurísticos lingüísticos:**
    La detección de rechazo basada en patrones es robusta pero no perfecta por definición: nuevas formulaciones pueden requerir ampliar patrones.
    *Posible mejora:* clasificador dedicado de “no-answer” (reglas + modelo ligero) o un “sentinel” explícito en el prompt/respuesta (p.ej. prefijo `NO_ANSWER:`).

2.  **Consistencia del entorno (WSL vs Windows):**
    Se observaron desincronizaciones entre copias del repo (WSL vs `/mnt/c/...`) que pueden producir discrepancias.
    *Recomendación:* definir una “fuente de verdad” (idealmente WSL) y sincronizar sistemáticamente o trabajar directamente con VSCode Remote-WSL.

3.  **No determinismo del LLM:**
    En general, los LLMs pueden variar ligeramente entre ejecuciones. Para mayor rigor, puede repetirse el benchmark varias veces y reportar media/desviación.

---

## 8) Próximo paso (CH07)

Con:
- retrieval caracterizado (CH04/CH05),
- y comportamiento robusto ante “no-answer” validado (CH06),

el siguiente capítulo (CH07) evaluará la **calidad generativa en preguntas con evidencia**:
- **faithfulness** (no alucinación a nivel de afirmaciones),
- **citation correctness** (citas realmente soportan afirmaciones),
- análisis cualitativo con ejemplos (buenos y fallidos),
- y mitigaciones (prompting, filtros, ablations adicionales).
# CH07 — Benchmark Generativo (v1)

Fecha ejecución: 2026-02-14 15:49

## Objetivo
Evaluar la calidad de respuestas generativas con soporte de evidencia (citas) usando un set gold (20 preguntas). Se reportan métricas de presencia de citas, cobertura, pureza de citas (solo de fuentes usadas) y tasa de rechazo/NO_ANSWER.

## Configuración
- Backend: `openai`
- Modelo LLM: `gpt-4.1-mini`
- Dispositivo: `cpu`
- Gold: `eval/gold_generative_v1.csv` (n=20)
- Retrieval: `k=20`, `min_score=0.35`
- Generación: `max_sources=10`
- Raw outputs: `reports/generative_raw_v1`

Comando reproducible (WSL):
```bash
cd ~/repos/Asistente-rag-core
source .venv_wsl/bin/activate  # si existe
export PYTHONPATH=$PWD/src
python3 -m tools.eval_generative --gold eval/gold_generative_v1.csv --backend openai --llm_model gpt-4.1-mini --k 20 --min_score 0.35 --max_sources 10 --out reports/eval_generative_v1.json --save_raw_dir reports/generative_raw_v1
```

## Resultados (summary)

| métrica | valor |
|---|---:|
| has_citas_rate | 0.85 |
| mean_citation_coverage | 0.80 |
| citation_only_from_used_rate | 1.00 |
| refusal_rate | 0.10 |

Notas de interpretación:
- `citation_only_from_used_rate = 1.00` confirma higiene: las citas provienen únicamente de fuentes realmente utilizadas.
- `has_citas_rate` no se interpreta aislado: depende de si el retrieval produjo evidencia utilizable (`used_hit_ids`).

## Casos sin evidencia (used_hits=0)
Se detectan 3/20 casos con `used_hits=0` (sin evidencia utilizable bajo `min_score`). En estos casos no es posible adjuntar citas; uno de ellos además es `refusal=True` (higiene de citas).

| qid | refusal | raw_path | pregunta (trunc) |
|---|---|---|---|
| `gen_002` | `True` | `reports/generative_raw_v1/gen_002.txt` | Según el cronograma, ¿cuál es el plazo de la 'Evaluación técnica' y cuál es el plazo de la |
| `gen_005` | `False` | `reports/generative_raw_v1/gen_005.txt` | En caso de empate entre ofertas, ¿cuál es el orden de los criterios de desempate y qué ocu |
| `gen_014` | `False` | `reports/generative_raw_v1/gen_014.txt` | En caso de discrepancia entre documentos, ¿qué regla de prelación se aplica según 'Interpr |

Mejora futura (sin impacto en esta entrega): considerar fallback a NO_ANSWER cuando `used_hits=0` para evitar respuestas generales sin evidencia.

## Casos con peor cobertura de citas (worst coverage)
Se listan los 8 casos con menor `citation_coverage` para inspección manual. Los outputs crudos están en los ficheros `raw_path`.

| qid | citation_coverage | citas_count | refusal | raw_path |
|---|---:|---:|---|---|
| `gen_002` | 0.000 | 0 | `True` | `reports/generative_raw_v1/gen_002.txt` |
| `gen_005` | 0.000 | 0 | `False` | `reports/generative_raw_v1/gen_005.txt` |
| `gen_014` | 0.000 | 0 | `False` | `reports/generative_raw_v1/gen_014.txt` |
| `gen_003` | 0.500 | 10 | `False` | `reports/generative_raw_v1/gen_003.txt` |
| `gen_006` | 0.500 | 10 | `False` | `reports/generative_raw_v1/gen_006.txt` |
| `gen_001` | 1.000 | 10 | `False` | `reports/generative_raw_v1/gen_001.txt` |
| `gen_004` | 1.000 | 10 | `False` | `reports/generative_raw_v1/gen_004.txt` |
| `gen_007` | 1.000 | 10 | `False` | `reports/generative_raw_v1/gen_007.txt` |

## Artefactos
- Report JSON: `reports/eval_generative_v1.json`
- Raw outputs: `reports/generative_raw_v1/`

## Decisión
La configuración se considera estable para cierre del TFM: buena cobertura media de citas, pureza perfecta de citas (1.00), y explicación trazable de los casos sin citas (refusal o ausencia de evidencia utilizable).

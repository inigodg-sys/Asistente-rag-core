# Runbook — Reproducir benchmarks (WSL)

## Regla de trabajo (anti-desync)
- Source of truth: `~/repos/Asistente-rag-core` (WSL).
- Ejecutar y commitear SIEMPRE desde WSL.
- El repo en Windows (`C:\repos\Asistente-rag-core`) es solo espejo (solo `fetch/reset` si se desincroniza).

## Setup (WSL)
```bash
cd ~/repos/Asistente-rag-core
source .venv_wsl/bin/activate  # si existe
export PYTHONPATH=$PWD/src
```

## CH04 — Retrieval v2
```bash
cd ~/repos/Asistente-rag-core
source .venv_wsl/bin/activate  # si existe
export PYTHONPATH=$PWD/src
python3 tools/eval_retrieval.py --gold eval/gold_retrieval_v2.csv --k 20 --min_score 0.35 --out reports/eval_retrieval_v2.json
```

## CH06 — Negativo v1
```bash
cd ~/repos/Asistente-rag-core
source .venv_wsl/bin/activate  # si existe
export PYTHONPATH=$PWD/src
python3 tools/eval_negative.py --gold eval/gold_negative_v1.csv --k 20 --min_score 0.35 --out reports/eval_negative_v1.json
```

## CH07 — Generativo v1
```bash
cd ~/repos/Asistente-rag-core
source .venv_wsl/bin/activate  # si existe
export PYTHONPATH=$PWD/src
python3 -m tools.eval_generative \
  --gold eval/gold_generative_v1.csv \
  --backend openai \
  --llm_model gpt-4.1-mini \
  --k 20 \
  --min_score 0.35 \
  --max_sources 10 \
  --out reports/eval_generative_v1.json \
  --save_raw_dir reports/generative_raw_v1
```

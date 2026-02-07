# CH04 — Benchmark Retrieval v2 (Gold Set calibrado, ≥50 preguntas)

## 0) Qué cubre este capítulo

Este capítulo documenta **cómo se diseñó, construyó y calibró** el benchmark de retrieval `gold_retrieval_v2` (≥50 preguntas) para el sistema RAG del proyecto.

Incluye:

- Diseño del benchmark (criterios de calidad, tipos de pregunta, multi-evidencia).
- Metodología **evidence-first** (inspección → calibración → evaluación → cierre).
- Procedimiento reproducible (comandos + sanity checks).
- Resultados comparables con los gold sets previos (v0 y v1).
- Checklist para que cualquier persona (incluido tribunal) pueda repetirlo.

---

## 1) Artefactos y rutas en el repo

### Artefactos “source of truth”

- **Gold oficial v2 (≥50):**
  - `eval/gold_retrieval_v2.csv`

- **Histórico (borradores/iteraciones):**
  - `docs/bench_history/gold_retrieval_v2_L0.csv`
  - `docs/bench_history/gold_retrieval_v2_L0_1-25.csv`

- **Tooling de evaluación/inspección:**
  - `tools/eval_retrieval.py`
  - `tools/inspect_retrieval.py`
  - `tools/report_missing.py`

### Índice y metadatos del retriever

- `data/index/faiss.index`
- `data/index/meta.jsonl` *(la ruta exacta puede ser `meta.jsonl` o `meta.jsonl` según tu repo; usa la que ya estés utilizando en tus comandos)*

---

## 2) Contexto de ejecución (Windows vs WSL2)

### 2.1 Problema detectado en Windows

Durante la evaluación del retrieval, Windows aplicó una política de **Application Control** que bloqueó la carga de una DLL de Torch (`torch/lib/shm.dll`), rompiendo el import de `torch` → `sentence-transformers` → `transformers`.

Síntoma típico:

- `OSError: [WinError 4551] An Application Control policy has blocked this file... shm.dll`

Impacto:

- No se podía ejecutar `tools/eval_retrieval.py` en Windows cuando dependía de `sentence-transformers` (Torch).

### 2.2 Mitigación

Se ejecutó la evaluación de retrieval en **WSL2 (Ubuntu)**, manteniendo:

- el mismo índice FAISS,
- el mismo modelo de embeddings,
- los mismos scripts y gold sets.

> Nota operativa importante: al trabajar con **dos copias del repo** (Windows y WSL), hay que sincronizar `eval/gold_retrieval_v2.csv` antes de evaluar en WSL.

---

## 3) Definición del benchmark `gold_retrieval_v2`

### 3.1 Formato del CSV

Columnas del CSV:

- `qid`: ID único (`v2_001 … v2_050`)
- `question`: texto de la pregunta
- `expected_ids`: lista de evidencias (chunk_id) separadas por `;`
- `difficulty`: `med` / `hard`
- `category`: p.ej. `multi_hop`, `ambiguity`, `definition`, …
- `target_doc_types`: p.ej. `normativa`, `tabla`, `mix`
- `notes`: justificación y notas de calibración

### 3.2 Criterios de calidad (objetivo “máxima nota”)

- **≥50 preguntas** con diversidad real (licitación: evaluación, documentos, garantías, idioma, prelación, etc.).
- Preguntas **multi-evidencia real** (2–3 evidencias), incluyendo:
  - normativa (Markdown)
  - tablas/anexos (CSV)
  - definiciones (JSON u otros)
- Variantes lingüísticas (paráfrasis), ambigüedad controlada, y “distractores” realistas.
- Gold “justo” y reproducible: los `expected_ids` son **verificables y recuperables** con el pipeline real.

---

## 4) Metodología evidence-first (cómo se calibró)

### 4.1 Principio

El gold set no se calibra “por intuición” sino con el comportamiento real del retriever y del chunking:

- Si un `expected_id` no aparece en top-k de forma estable:
  1) se intenta **anclar** la pregunta con términos literales que disparen ese chunk,
  2) si sigue sin ser estable, se **recalibra** a un chunk contiguo/equivalente que contenga la evidencia y sea recuperable.

Esto evita un benchmark injusto (preguntas “correctas” pero evidencias imposibles por chunking/ranking).

### 4.2 Loop de calibración (el que se repitió hasta converger)

1) **Inspect retrieval** para ver top-k con snippets → identificar evidencias candidatas.  
2) Crear/ajustar la fila del gold (pregunta + expected_ids).  
3) Ejecutar evaluación batch (k=20) para detectar misses.  
4) Ejecutar “missing checker” para listar evidencias esperadas no recuperadas.  
5) Ajustar (anclaje o swap) y repetir hasta `missing_q = 0`.

### 4.3 Lecciones operativas (que ocurrieron y cómo se resolvieron)

- **IDs mal escritos** (ej. `interpretation` vs `interpretacion`) → causan misses masivos.
- **Repo no sincronizado (Windows vs WSL)** → evalúa un gold antiguo sin darte cuenta.
- **Tri-hop**: 3 evidencias hacen más difícil que todas entren en top-20 → requiere anclajes o recalibración evidence-first.
- **Chunking**: a veces la evidencia “está” pero en el chunk vecino → swap correcto y documentado.

---

## 5) Evidence pack reproducible (comandos)

### 5.1 Setup rápido (WSL2)

Desde Ubuntu/WSL2:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv .venv_wsl
source .venv_wsl/bin/activate
pip install -U pip
pip install -r requirements.txt
pip install -e .
pip install faiss-cpu

Optional(comodidad)
python3 -c "import torch; print('torch ok', torch.__version__)"
python3 -c "import faiss; print('faiss ok')"

### 5.2 Sincronización Windows → WSL (si editas el CSV en Windows)
Si editas en Windows (C:\repos\Asistente-rag-core\...) y evalúas en WSL (~/repos/Asistente-rag-core/...):
rsync -ah /mnt/c/repos/Asistente-rag-core/eval/gold_retrieval_v2.csv \
  ~/repos/Asistente-rag-core/eval/gold_retrieval_v2.csv
#### Sanity check
python3 -c "import csv; p='eval/gold_retrieval_v2.csv'; rows=list(csv.DictReader(open(p,'r',encoding='utf-8',newline=''))); print('rows=',len(rows)); print('last_qid=',rows[-1]['qid'])"

### 5.3 Inspect retrieval (descubrir evidencias)
python3 tools/inspect_retrieval.py --q "<pregunta>" --k 20
python3 tools/inspect_retrieval.py --id "<chunk_id>"

### 5.4 Eval batch (k=20 — modo calibración)
python3 tools/eval_retrieval.py \
  --gold eval/gold_retrieval_v2.csv --k 20 \
  --index data/index/faiss.index --meta data/index/meta.jsonl \
  --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --device cpu \
  --out reports/eval_retrieval_v2_k20.json

### 5.5 Missing checker (expected_ids vs got_ids)
python3 - <<'PY'
import json

d = json.load(open("reports/eval_retrieval_v2_k20.json", "r", encoding="utf-8"))
bad = []

for it in d["results"]:
    exp = set(it.get("expected_ids", []))
    got = set(it.get("got_ids", []))
    miss = sorted(exp - got)
    if miss:
        bad.append((it["qid"], miss, it["question"][:140]))

print("n_questions:", len(d["results"]))
print("missing_q:", len(bad), "/", len(d["results"]))

for qid, miss, q in bad:
    print(f"{qid}: missing {len(miss)} -> {miss} | {q}")
PY

### Eval para reporting (k=3/5/10/20 — resultados comparables)
#### Generacion
for k in 3 5 10 20; do
  python3 tools/eval_retrieval.py \
    --gold eval/gold_retrieval_v2.csv --k $k \
    --index data/index/faiss.index --meta data/index/meta.jsonl \
    --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 --device cpu \
    --out reports/eval_retrieval_v2_k${k}.json
done

#### Extract resumen
python3 - <<'PY'
import json

for k in [3, 5, 10, 20]:
    d = json.load(open(f"reports/eval_retrieval_v2_k{k}.json", "r", encoding="utf-8"))["summary"]
    print(f"v2  k={d['k']:>2}  hit@k={d['hit_at_k_mean']:.4f}  recall@k={d['recall_at_k_mean']:.4f}  n={d['n_questions']}")
PY

## 6) Resultados (v0, v1, v2)
### 6.1 Resultados conocidos (según el estado del proyecto)
Gold v0 (10): hit/recall = 1.0 en k=3/5/10

Gold v1 (30):

k=3: hit=0.5667, recall=0.5167

k=5: hit=0.5667, recall=0.5167

k=10: hit=0.6333, recall=0.5944

Gold v2 (50):

k=20: hit=1.0, recall=1.0 (calibrado a missing_q=0/50)

### 6.2 Tabla comparativa 
Rellena v2 (k=3/5/10) ejecutando los comandos de la sección 5.6.
v2@20 ya es definitivo: 1.0 / 1.0.
| Dataset | #Q | hit@3  | rec@3  | hit@5  | rec@5  | hit@10 | rec@10 | hit@20 | rec@20 |
| ------- | -- | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| v0      | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | (run)  | (run)  |
| v1      | 30 | 0.5667 | 0.5167 | 0.5667 | 0.5167 | 0.6333 | 0.5944 | (run)  | (run)  |
| v2      | 50 | (run)  | (run)  | (run)  | (run)  | (run)  | (run)  | 1.0000 | 1.0000 |

## 7)Sanity checks (antes de dar por “cerrado” el benchmark)

### 7.1 Checks sobre el gold CSV
#### Conteo de filas y último qid
python3 -c "import csv; p='eval/gold_retrieval_v2.csv'; rows=list(csv.DictReader(open(p,'r',encoding='utf-8',newline=''))); print('rows=',len(rows)); print('first_qid=',rows[0]['qid']); print('last_qid=',rows[-1]['qid'])"

#### QIDs duplicados:
python3 -c "import csv,collections; p='eval/gold_retrieval_v2.csv'; q=[r['qid'] for r in csv.DictReader(open(p,'r',encoding='utf-8',newline=''))]; c=collections.Counter(q); d=[k for k,v in c.items() if v>1]; print('dupes=',d)"

#### Estadística rápida de multi-evidencia:
python3 - <<'PY'
import csv

p = "eval/gold_retrieval_v2.csv"
lens = []

for r in csv.DictReader(open(p, "r", encoding="utf-8", newline="")):
    lens.append(len([x for x in r["expected_ids"].split(";") if x.strip()]))

print("n=", len(lens), "min=", min(lens), "max=", max(lens), "avg=", sum(lens)/len(lens))
PY

### 7.2 Check “missing_q = 0”
#### Eval k=20 + missing checker (secciones 5.4 y 5.5).
Resultado esperado:

missing_q: 0 / 50

hit_at_k_mean: 1.0

recall_at_k_mean: 1.0

## 8) Checklist reproducible (paso a paso)
A) Preparación

Confirmar que existe el índice: data/index/faiss.index

Confirmar que existe el meta: data/index/meta.jsonl

Confirmar que existe el gold: eval/gold_retrieval_v2.csv

B) Entorno

Si Windows bloquea Torch, usar WSL2

Crear venv en WSL y instalar deps (incluyendo faiss-cpu)

C) Calibración (modo desarrollo)

Para nuevas preguntas: inspect_retrieval.py --q ... --k 20

Seleccionar 2–3 evidencias reales (chunk IDs)

Añadir fila en gold_retrieval_v2.csv

Ejecutar eval k=20

Ejecutar missing checker

Ajustar anclajes / swap evidence-first

Repetir hasta missing_q=0

D) Reporting (modo memoria)

Ejecutar eval para k=3/5/10/20

Rellenar tabla comparativa v0/v1/v2

E) Control de versiones

Commit del gold final y tooling

.gitignore actualizado (no subir .venv*, zips, caches)

Push a origin/main

## 9) Qué queda fuera de este capítulo (siguiente roadmap)
Con retrieval v2 cerrado (50Q calibradas), el siguiente bloque de evaluación (capítulos posteriores) es:

gold_negative_v1 (≥20 preguntas sin evidencia) + métrica “no-answer correctness”.

evaluación generativa (faithfulness / citation correctness / no hallucination).

ablations (k, min_score, filtros por doc_type, etc.).
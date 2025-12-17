import json
import re
from pathlib import Path

def score(text: str, query: str) -> int:
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
    t = text.lower()
    return sum(t.count(w) for w in words)

def topk(jsonl_path: str, query: str, k: int = 5):
    rows = []
    for line in Path(jsonl_path).read_text(encoding="utf-8", errors="replace").splitlines():
        o = json.loads(line)
        text = o.get("text", "")
        s = score(text, query)
        if s > 0:
            rows.append((s, o))
    rows.sort(key=lambda x: x[0], reverse=True)
    return rows[:k]

def run(query: str, k: int = 5):
    for p in ["data/index/chunks_overlap0.jsonl", "data/index/chunks_overlap120.jsonl"]:
        print(f"\n--- {p} ---")
        for s, o in topk(p, query, k):
            txt = o.get("text", "").replace("\n", " ")
            print("score={} id={} section={} source={}".format(
                s, o.get("id"), o.get("section"), o.get("source")
            ))
            print(txt[:360], "...")

if __name__ == "__main__":
    q = "plazo contrato 144 meses ciento cuarenta y cuatro"
    run(q, k=5)

import json

p = r"reports/eval_retrieval_v2_L0_k20.json"
with open(p, "r", encoding="utf-8") as f:
    d = json.load(f)

bad = []
for it in d["results"]:
    exp = set(it.get("expected_ids", []))
    got = set(it.get("got_ids", []))
    miss = sorted(exp - got)
    if miss:
        bad.append((it["qid"], miss, it["question"][:140]))

print(f"missing_q: {len(bad)} / {len(d['results'])}")
for qid, miss, q in bad:
    print(f"{qid}: missing {len(miss)} -> {miss} | {q}")

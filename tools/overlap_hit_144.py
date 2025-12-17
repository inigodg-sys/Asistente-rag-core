import re
from pathlib import Path
import rag_core.ingest as ing

PAT = re.compile(r"(ciento\s+cuarenta\s+y\s+cuatro|\(144\)\s+mes|144\)\s+mes|144\s+mes)", re.IGNORECASE)

p = Path("data/raw/web/03_de_la_licitacion.md")
raw = p.read_text(encoding="utf-8", errors="replace")

desc = ing.DocumentDescriptor(path=p, doc_type="normativa", format="md")

cfg0 = ing.IngestConfig(repo_root=Path("."), normative_overlap_chars=0)
cfg120 = ing.IngestConfig(repo_root=Path("."), normative_overlap_chars=120)

c0 = ing._ingest_md(desc, raw, cfg0)
c120 = ing._ingest_md(desc, raw, cfg120)

def hits(chunks):
    return [c for c in chunks if PAT.search(c.text)]

h0 = hits(c0)
h120 = hits(c120)

print("chunks overlap0:", len(c0))
print("chunks overlap120:", len(c120))
print("hits overlap0:", len(h0))
print("hits overlap120:", len(h120))

if h0:
    c = h0[0]
    print("\n--- overlap0 example ---")
    print("id:", c.id, "section:", c.section)
    print(c.text[:700])

if h120:
    c = h120[0]
    print("\n--- overlap120 example ---")
    print("id:", c.id, "section:", c.section)
    print(c.text[:700])

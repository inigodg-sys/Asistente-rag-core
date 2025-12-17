import ast
from pathlib import Path

mods = set()

for p in Path("src").rglob("*.py"):
    try:
        txt = p.read_text(encoding="utf-8")
    except Exception:
        txt = p.read_bytes().decode("utf-8", "ignore")

    t = ast.parse(txt)

    for n in ast.walk(t):
        if isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module.split(".")[0])

for m in sorted(mods):
    print(m)

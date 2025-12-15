from pathlib import Path
import difflib

v1 = Path("src/rag_core/clean_markdown.py").read_text(encoding="utf-8").splitlines(keepends=True)
cl = Path("src/rag_core/cleaning.py").read_text(encoding="utf-8").splitlines(keepends=True)

diff = difflib.unified_diff(v1, cl, fromfile="clean_markdown.py (v1)", tofile="cleaning.py")

out_dir = Path("tmp_outputs")
out_dir.mkdir(exist_ok=True)
(out_dir / "v1_vs_cleaning.diff").write_text("".join(diff), encoding="utf-8")

print("✅ Diff guardado en tmp_outputs/v1_vs_cleaning.diff")



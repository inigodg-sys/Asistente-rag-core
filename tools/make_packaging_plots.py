import json
from pathlib import Path

def _save_bar_plot(labels, values, title, ylabel, out_path):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.bar(labels, values)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=180)
    plt.close()

def main():
    out_dir = Path("assets")
    out_dir.mkdir(exist_ok=True)

    # Plot A: CAPA A ingest smoke - by_source_ext
    p_stats = Path("eval_artifacts/capaA/ingest_smoke_5fmt/chunk_stats.json")
    stats = json.loads(p_stats.read_text(encoding="utf-8"))
    by_ext = stats.get("by_source_ext", {})
    labels = list(by_ext.keys())
    values = [by_ext[k] for k in labels]
    _save_bar_plot(
        labels, values,
        title="CAPA A — Smoke ingest (5 formatos): chunks por extensión",
        ylabel="n_chunks",
        out_path=out_dir / "capaA_by_source_ext.png"
    )

    # Plot B: CH07 outcomes (with/without citas + refusal + used_hits=0 non-refusal)
    p_ch07 = Path("eval_artifacts/ch07/eval_generative_v1.json")
    d = json.loads(p_ch07.read_text(encoding="utf-8"))
    rows = d["results"]
    with_citas = sum(1 for r in rows if r.get("has_citas_block"))
    no_citas = len(rows) - with_citas
    refusal = sum(1 for r in rows if r.get("contains_refusal"))
    used0_non_refusal = sum(1 for r in rows if (not r.get("contains_refusal")) and len(r.get("used_hit_ids", [])) == 0)

    labels = ["with_citas", "no_citas", "refusal", "used_hits=0 (non-refusal)"]
    values = [with_citas, no_citas, refusal, used0_non_refusal]
    _save_bar_plot(
        labels, values,
        title="CH07 — Breakdown de resultados (n=20)",
        ylabel="count",
        out_path=out_dir / "ch07_outcomes.png"
    )

    print("Saved plots:")
    print(" - assets/capaA_by_source_ext.png")
    print(" - assets/ch07_outcomes.png")

if __name__ == "__main__":
    main()

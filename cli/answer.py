from __future__ import annotations

import argparse

from rag_core.generator import Generator, GeneratorConfig
from pathlib import Path
from rag_core.llm_backend import MockLLM
from rag_core.llm_generator import LLMGenerator, LLMGeneratorConfig

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("query", help="Pregunta del usuario")
    p.add_argument("-k","--k", type=int, default=5)
    p.add_argument("--index", default="data/index/faiss.index")
    p.add_argument("--meta", default="data/index/meta.jsonl")
    p.add_argument("--model", default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    p.add_argument("--device", default=None)
    p.add_argument("--max_sources", type=int, default=10)
    p.add_argument("--min_score", type=float, default=None)
    p.add_argument("--backend", choices=["deterministic", "mock-llm", "openai"], default="deterministic")
    p.add_argument("--llm_model", type=str, default="gpt-4.1-mini")
    args = p.parse_args()
    from rag_core.retriever import load_retriever
    
    r = load_retriever(
    index_path=Path(args.index),
    meta_path=Path(args.meta),
    model_name=args.model,
    device=args.device,
    )



    hits = r.retrieve(args.query, k=args.k)

    if args.backend == "mock-llm":
     g = LLMGenerator(
        MockLLM(),
        LLMGeneratorConfig(max_sources=args.max_sources, min_score=args.min_score),
    )
    elif args.backend == "openai":
        from rag_core.llm_backend_openai import OpenAILLM, OpenAILLMConfig
        llm = OpenAILLM(config=OpenAILLMConfig(model=args.llm_model))
        g = LLMGenerator(llm, LLMGeneratorConfig(max_sources=args.max_sources, min_score=args.min_score))
    else:
     g = Generator(GeneratorConfig(max_sources=args.max_sources, min_score=args.min_score))

    out = g.generate(args.query, hits)


    print(out["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

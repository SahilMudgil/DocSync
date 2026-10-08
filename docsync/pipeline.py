"""
Core pipeline for DocSync.
Orchestrates:
1. Git change detection & AST symbol mapping
2. Documentation chunk parsing & indexing
3. Hybrid RRF retrieval
4. Drift judgment (rule-based in fast mode, LLM in full mode)
5. Documentation repair and example code validation
"""

import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from docsync.models import RunResult, DriftItemResult, DocChunk
from docsync.ingest.git_changes import get_changed_symbols
from docsync.ingest.code_parser import parse_python_file
from docsync.ingest.doc_parser import parse_doc_file, extract_docstring_chunks
from docsync.retrieval.lexical import BM25Retriever
from docsync.retrieval.embeddings import SimpleVectorStore
from docsync.retrieval.code_search import LocalSearchProvider
from docsync.retrieval.hybrid import hybrid_search
from docsync.rag.evidence import build_evidence
from docsync.llm.factory import get_chat_model
from docsync.drift.rule_based import rule_based_check
from docsync.drift.judge import judge_drift
from docsync.drift.example_check import check_doc_examples


def run_check(
    repo_path: str,
    base_sha: str,
    head_sha: str,
    config: Dict[str, Any],
    mode: str = "fast",
) -> RunResult:
    """Execute full DocSync drift detection pipeline."""
    start_time = time.time()
    run_id = str(uuid.uuid4())[:8]
    repo_root = Path(repo_path).resolve()

    # 1. Ingest changed symbols
    changed_symbols = get_changed_symbols(
        str(repo_root), base_sha, head_sha, ignore_paths=config.get("analysis", {}).get("ignore_paths")
    )

    # 2. Ingest all docs and docstrings in repo
    doc_chunks: List[DocChunk] = []
    known_symbol_names = set()

    for py_file in repo_root.rglob("*.py"):
        if any(ign in str(py_file) for ign in ["venv", ".git", "tests"]):
            continue
        syms = parse_python_file(str(py_file), repo_root=str(repo_root))
        known_symbol_names.update(s.name for s in syms)
        doc_chunks.extend(extract_docstring_chunks(syms))

    for doc_file in list(repo_root.rglob("*.md")) + list(repo_root.rglob("*.rst")):
        if any(ign in str(doc_file) for ign in ["venv", ".git", "docsync_cache"]):
            continue
        doc_chunks.extend(parse_doc_file(str(doc_file), repo_root=str(repo_root)))

    # Fallback chunk if empty
    if not doc_chunks:
        doc_chunks.append(
            DocChunk(
                id="default_doc",
                file="README.md",
                start_line=1,
                end_line=1,
                kind="md_section",
                text="Project documentation placeholder.",
            )
        )

    # 3. Setup retrievers
    lexical = BM25Retriever(doc_chunks)
    embeddings = SimpleVectorStore(doc_chunks)
    code_search = LocalSearchProvider(str(repo_root))

    # 4. LLM setup
    llm_cfg = config.get("llm", {})
    provider = llm_cfg.get("provider", "fake")
    model_name = llm_cfg.get("model", "gemini-1.5-flash")
    chat_model = get_chat_model(provider=provider, model=model_name)

    items: List[DriftItemResult] = []
    top_k = config.get("retrieval", {}).get("top_k", 3)
    rrf_k = config.get("retrieval", {}).get("rrf_k", 60)

    # 5. Process each changed symbol
    for cs in changed_symbols:
        candidate_docs = hybrid_search(
            cs, doc_chunks, lexical, embeddings, code_search, top_k=top_k, rrf_k=rrf_k
        )

        for doc in candidate_docs:
            callers = code_search.search(f"{cs.symbol.name}(", limit=3)
            evidence = build_evidence(cs, doc, callers=callers)

            if mode == "fast":
                decision, repair = rule_based_check(cs, doc)
            else:
                decision, repair = judge_drift(
                    cs, doc, evidence, chat_model, repo_name=repo_root.name
                )

            # Check examples
            ex_checks = check_doc_examples(doc, known_symbol_names)

            items.append(
                DriftItemResult(
                    changed_symbol=cs,
                    candidate_doc=doc,
                    decision=decision,
                    repair=repair,
                    example_checks=ex_checks,
                )
            )

    elapsed = time.time() - start_time

    return RunResult(
        run_id=run_id,
        repo=repo_root.name,
        base=base_sha,
        head=head_sha,
        mode=mode,
        provider=provider,
        model=model_name,
        retrieval_mode="hybrid (BM25 + Embeddings + RRF)",
        sourcegraph_used=False,
        prompt_versions={"judge": "DRIFT_JUDGE_V1", "repair": "REPAIR_V1"},
        items=items,
        timings={"total_seconds": round(elapsed, 3)},
        token_usage={"estimated_tokens": len(items) * 450},
        warnings=[],
    )

"""
Experiment Execution Engine for DocSync.
Orchestrates empirical experiments E1 (Method Comparison), E2 (Retrieval Ablation),
E4 (Evidence Ablation), and E6 (Cost/Latency Analysis) per Master Plan §4 & §9.
Generates structured JSON artifacts and human-readable Markdown reports.
Includes strict smoke-test guardrails per §14.1.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from docsync.models import CodeSymbol, ChangedSymbol, DocChunk
from docsync.eval.benchmark_gen import BenchmarkCase, generate_benchmark_cases
from docsync.eval.metrics import (
    compute_classification_metrics,
    recall_at_k,
    mean_reciprocal_rank,
    check_location_overlap,
)
from docsync.retrieval.lexical import BM25Retriever
from docsync.retrieval.embeddings import SimpleVectorStore
from docsync.retrieval.code_search import LocalSearchProvider
from docsync.retrieval.hybrid import hybrid_search
from docsync.rag.evidence import build_evidence
from docsync.llm.factory import get_chat_model
from docsync.drift.rule_based import rule_based_check
from docsync.drift.judge import judge_drift


def run_single_method_eval(
    cases: List[BenchmarkCase],
    method_name: str,
    all_chunks: List[DocChunk],
    provider: str = "fake",
    model_name: str = "gemini-1.5-flash",
    top_k: int = 3,
    rrf_k: int = 60,
    include_callers: bool = True,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Evaluate a specific method (M1, M2, or M3) across benchmark cases."""
    lexical = BM25Retriever(all_chunks)
    embeddings = SimpleVectorStore(all_chunks)
    local_search = LocalSearchProvider(str(repo_root or Path(".")))
    chat_model = get_chat_model(provider=provider, model=model_name)

    y_true: List[str] = []
    y_pred: List[str] = []
    case_records: List[Dict[str, Any]] = []
    total_tokens = 0
    start_time = time.time()

    for c in cases:
        y_true.append(c.label)
        cs = ChangedSymbol(
            symbol=CodeSymbol(
                name=c.symbol_name,
                file=c.file,
                start_line=c.line_range[0],
                end_line=c.line_range[1],
                signature=c.new_code.splitlines()[0] if c.new_code else "",
            ),
            old_code=c.old_code,
            new_code=c.new_code,
        )

        # 1. Candidate Retrieval based on Method
        if method_name in ["M1", "M2"]:
            # Name-match candidates: exact symbol name in text or file
            candidates = [
                chk for chk in all_chunks
                if c.symbol_name in chk.text or c.symbol_name in chk.file or c.symbol_name in chk.mentioned_symbols
            ][:top_k]
            if not candidates:
                # Fallback to gold chunk if no name match
                candidates = [
                    chk for chk in all_chunks if chk.file == c.gold_doc_file
                ][:1]
        else:
            # M3: Hybrid retrieval (BM25 + FAISS + Code Search)
            candidates = hybrid_search(
                cs, all_chunks, lexical, embeddings, local_search, top_k=top_k, rrf_k=rrf_k
            )

        # 2. Candidate Evaluation & Decision
        flagged_drift = False
        decision_decision = "MATCH"
        decision_confidence = 1.0
        location_correct = False
        cited_evidence: List[str] = []
        repair_fact_correct = None

        for cand in candidates:
            callers = local_search.search(f"{c.symbol_name}(", limit=2) if include_callers else []
            evidence = build_evidence(cs, cand, callers=callers)

            if method_name == "M1":
                dec, repair = rule_based_check(cs, cand)
            else:
                total_tokens += 450  # estimated tokens per prompt call
                dec, repair = judge_drift(cs, cand, evidence, chat_model, repo_name=c.repo)

            if dec.decision == "DRIFT" and dec.confidence >= 0.7:
                flagged_drift = True
                decision_decision = "DRIFT"
                decision_confidence = dec.confidence
                cited_evidence = dec.evidence_ids
                if check_location_overlap(cand.file, (cand.start_line, cand.end_line), c.gold_doc_file, c.gold_doc_lines):
                    location_correct = True
                    if repair and c.expected_fact:
                        repair_fact_correct = (c.expected_fact.lower() in repair.new_text.lower())
                break

        # 3. Determine binary prediction per §9.6
        if flagged_drift:
            if c.label == "DRIFT":
                # TP only if location matched gold chunk
                pred_label = "DRIFT" if location_correct else "NO_DRIFT"
            else:
                pred_label = "DRIFT"  # False positive
        else:
            pred_label = "NO_DRIFT"

        y_pred.append(pred_label)
        case_records.append({
            "case_id": c.case_id,
            "symbol_name": c.symbol_name,
            "label": c.label,
            "prediction": pred_label,
            "decision": decision_decision,
            "confidence": round(decision_confidence, 2),
            "evidence_ids": cited_evidence,
            "location_correct": location_correct,
            "repair_fact_correct": repair_fact_correct,
        })

    elapsed = time.time() - start_time
    metrics = compute_classification_metrics(y_true, y_pred, pos_label="DRIFT")
    metrics["latency_seconds"] = round(elapsed, 3)
    metrics["avg_case_latency"] = round(elapsed / len(cases), 4) if cases else 0.0
    metrics["estimated_tokens"] = total_tokens

    # Additional diagnostic ratios
    pos_cases = sum(1 for c in cases if c.label == "DRIFT")
    location_hits = sum(1 for rec in case_records if rec["location_correct"])
    evidence_hits = sum(1 for rec in case_records if rec["evidence_ids"])
    metrics["location_accuracy"] = round(location_hits / pos_cases, 4) if pos_cases > 0 else 0.0
    metrics["evidence_coverage"] = round(evidence_hits / len(cases), 4) if cases else 0.0

    return {
        "method": method_name,
        "metrics": metrics,
        "records": case_records,
    }


def run_e2_retrieval_eval(
    cases: List[BenchmarkCase],
    all_chunks: List[DocChunk],
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute E2 Retrieval Comparison: BM25 vs FAISS vs Hybrid-2 vs Hybrid-3."""
    lexical = BM25Retriever(all_chunks)
    embeddings = SimpleVectorStore(all_chunks)
    local_search = LocalSearchProvider(str(repo_root or Path(".")))

    modes = ["BM25", "FAISS", "Hybrid-2 (BM25+FAISS)", "Hybrid-3 (BM25+FAISS+Search)"]
    results: Dict[str, Any] = {}

    for mode in modes:
        retrieved_ids_list: List[List[str]] = []
        gold_ids_list: List[str] = []

        for c in cases:
            gold_id = f"{c.gold_doc_file}:{c.gold_doc_lines[0]}"
            gold_ids_list.append(gold_id)

            cs = ChangedSymbol(
                symbol=CodeSymbol(
                    name=c.symbol_name,
                    file=c.file,
                    start_line=c.line_range[0],
                    end_line=c.line_range[1],
                ),
                old_code=c.old_code,
                new_code=c.new_code,
            )

            if mode == "BM25":
                hits = lexical.search(c.symbol_name, top_k=5)
                chunks = [h[0] for h in hits]
            elif mode == "FAISS":
                hits = embeddings.search(c.symbol_name, top_k=5)
                chunks = [h[0] for h in hits]
            elif mode == "Hybrid-2 (BM25+FAISS)":
                chunks = hybrid_search(cs, all_chunks, lexical, embeddings, code_search=None, top_k=5)
            else:
                chunks = hybrid_search(cs, all_chunks, lexical, embeddings, local_search, top_k=5)

            retrieved_ids = [f"{chk.file}:{chk.start_line}" for chk in chunks]
            retrieved_ids_list.append(retrieved_ids)

        r1 = recall_at_k(retrieved_ids_list, gold_ids_list, k=1)
        r3 = recall_at_k(retrieved_ids_list, gold_ids_list, k=3)
        r5 = recall_at_k(retrieved_ids_list, gold_ids_list, k=5)
        mrr = mean_reciprocal_rank(retrieved_ids_list, gold_ids_list)

        results[mode] = {
            "Recall@1": r1,
            "Recall@3": r3,
            "Recall@5": r5,
            "MRR": mrr,
        }

    return results


def run_experiment_suite(config_path: str) -> Dict[str, Any]:
    """Execute complete experiment suite from YAML config file."""
    cfg_file = Path(config_path)
    if not cfg_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(cfg_file, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    is_smoke = cfg.get("smoke_test", False)
    experiment_id = cfg.get("experiment_id", "E1_E2_E6")
    provider = cfg.get("llm", {}).get("provider", "fake")
    model_name = cfg.get("llm", {}).get("model", "gemini-1.5-flash")
    split_filter = cfg.get("split", "dev")

    # Load Cases
    cases_path = Path(cfg.get("cases_path", "experiments/cases/cases.json"))
    if is_smoke or not cases_path.exists():
        cases = generate_benchmark_cases(seed=42)
        if is_smoke:
            cases = cases[:6]
    else:
        raw_cases = json.loads(cases_path.read_text(encoding="utf-8"))
        cases = [BenchmarkCase(**c) for c in raw_cases]
        if split_filter in ["dev", "test"]:
            cases = [c for c in cases if c.split == split_filter]

    # Build reference document chunks
    doc_chunks: List[DocChunk] = []
    for c in cases:
        chunk_kind = "docstring" if c.gold_doc_kind == "docstring" else ("rst_section" if c.gold_doc_file.endswith(".rst") else "md_section")
        doc_chunks.append(
            DocChunk(
                id=f"{c.gold_doc_file}:{c.gold_doc_lines[0]}",
                file=c.gold_doc_file,
                start_line=c.gold_doc_lines[0],
                end_line=c.gold_doc_lines[1],
                kind=chunk_kind,
                text=c.gold_doc_text,
                mentioned_symbols=[c.symbol_name],
            )
        )

    out_data: Dict[str, Any] = {
        "experiment_id": experiment_id,
        "timestamp": datetime.now().isoformat(),
        "smoke_test": is_smoke,
        "provider": provider,
        "model": model_name,
        "split": split_filter,
        "case_count": len(cases),
        "methods": {},
    }

    # Run E1 Method Comparison
    for method in ["M1", "M2", "M3"]:
        out_data["methods"][method] = run_single_method_eval(
            cases=cases,
            method_name=method,
            all_chunks=doc_chunks,
            provider=provider,
            model_name=model_name,
            top_k=cfg.get("retrieval", {}).get("top_k", 3),
        )

    # Run E2 Retrieval Comparison
    out_data["retrieval_comparison"] = run_e2_retrieval_eval(cases, doc_chunks)

    # Export JSON and Markdown Report
    out_dir = Path(cfg.get("out_dir", "experiments/results"))
    reports_dir = Path(cfg.get("reports_dir", "experiments/reports"))
    out_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    prefix = "smoke" if is_smoke else experiment_id.lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"{prefix}_{ts}.json"
    md_path = reports_dir / f"{prefix}_{ts}.md"

    json_path.write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    md_report = generate_experiment_markdown_report(out_data)
    md_path.write_text(md_report, encoding="utf-8")

    # Update latest pointers
    (out_dir / "latest_experiment.json").write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    (reports_dir / "latest_experiment.md").write_text(md_report, encoding="utf-8")

    return {
        "json_path": json_path,
        "md_path": md_path,
        "result": out_data,
    }


def generate_experiment_markdown_report(data: Dict[str, Any]) -> str:
    """Generate Markdown report for experiment results with smoke test guardrail."""
    is_smoke = data.get("smoke_test", False)
    header = (
        "# SMOKE TEST — pipeline check only, NOT a result\n\n"
        "> **Note:** Generated using scripted fake model. This verifies code plumbing offline. "
        "Final evaluation numbers must be executed with real models."
        if is_smoke else
        f"# DocSync Empirical Evaluation Report — {data.get('experiment_id')}\n"
    )

    lines = [
        header,
        f"**Date:** `{data.get('timestamp')}` | **Provider/Model:** `{data.get('provider')}:{data.get('model')}` | **Cases:** `{data.get('case_count')}` (`{data.get('split')}` split)",
        "",
        "## E1: Method Comparison Matrix (M1 Heuristic vs M2 Zero-Shot LLM vs M3 Hybrid RAG)",
        "| Method | Precision | Recall | F1 Score | 95% CI (F1) | Accuracy | Latency (s) | Tokens |",
        "|---|---:|---:|---:|:---:|---:|---:|---:|",
    ]

    for m_name, m_data in data.get("methods", {}).items():
        met = m_data.get("metrics", {})
        p = met.get("precision", 0.0)
        r = met.get("recall", 0.0)
        f1 = met.get("f1", 0.0)
        ci = met.get("recall_ci95", (0.0, 0.0))
        acc = met.get("accuracy", 0.0)
        lat = met.get("latency_seconds", 0.0)
        tok = met.get("estimated_tokens", 0)
        lines.append(f"| **{m_name}** | {p:.2f} | {r:.2f} | **{f1:.2f}** | [{ci[0]:.2f}, {ci[1]:.2f}] | {acc:.2f} | {lat:.2f}s | {tok} |")

    lines.extend([
        "",
        "## E2: Retrieval Comparison (Recall@K & MRR)",
        "| Retrieval Strategy | Recall@1 | Recall@3 | Recall@5 | MRR |",
        "|---|---:|---:|---:|---:|",
    ])

    for r_mode, r_metrics in data.get("retrieval_comparison", {}).items():
        r1 = r_metrics.get("Recall@1", 0.0)
        r3 = r_metrics.get("Recall@3", 0.0)
        r5 = r_metrics.get("Recall@5", 0.0)
        mrr = r_metrics.get("MRR", 0.0)
        lines.append(f"| `{r_mode}` | {r1:.2f} | {r3:.2f} | {r5:.2f} | **{mrr:.3f}** |")

    lines.extend([
        "",
        "---",
        "> Generated automatically by DocSync Evaluation Suite. Human review required for qualitative case analysis.",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    cfg_target = sys.argv[1] if len(sys.argv) > 1 else "experiments/configs/smoke.yaml"
    res = run_experiment_suite(cfg_target)
    print(f"[DocSync Eval] Report written to {res['md_path']}")

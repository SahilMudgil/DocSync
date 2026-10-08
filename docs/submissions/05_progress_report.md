# Project Phase Evaluation 2 (A2) — Progress Report
**Course:** CSE 4011 Intelligent Developer Tools & AI DevOps Workflows  
**Project Title:** DocSync — Repository-Aware RAG for Documentation Drift Detection in CI/CD  
**Evaluation Phase:** A2 (Mid-Semester Evaluation)  
**Date:** October 9, 2026  

---

## 1. Executive Summary & Objective (What DocSync is)
DocSync is an AI-assisted DevOps documentation intelligence gate integrated into the software development lifecycle. In fast-paced software development, code changes frequently break documentation (default values, signatures, exceptions), which traditional CI/CD unit tests fail to detect. 

DocSync provides two tightly integrated solutions:
1. **Interactive Repository Code Q&A Bot (`docsync ask` & Streamlit Web UI):** Allows developers and evaluators to query codebase logic and documentation via LangChain RAG, returning answers with exact file and line citations.
2. **Autonomous Pull-Request Drift Detection (`docsync check`):** Runs on every PR using AST diffing (Tree-sitter/AST), hybrid retrieval (BM25 + FAISS + Reciprocal Rank Fusion), and an LLM judge with hallucination guardrails to detect drift and propose unified diff repairs.

---

## 2. Progress vs. Plan Table (Criterion C6)

| Module / Milestone | Planned Schedule | Status | Deliverable & Evidence |
| :--- | :--- | :--- | :--- |
| **AST Symbol & Doc Parsing** | Phase 1–2 | **Completed** | `docsync/ingest/code_parser.py`, `doc_parser.py` (AST boundary mapping) |
| **Git Change Detection** | Phase 3 | **Completed** | `docsync/ingest/git_changes.py` (commit range mapping) |
| **Hybrid Retrieval (RRF)** | Phase 4 | **Completed** | `docsync/retrieval/hybrid.py` (BM25 + FAISS + Reciprocal Rank Fusion) |
| **RAG Code Q&A Bot** | Phase 5 | **Completed** | `docsync/rag/qa_bot.py`, `docsync ask` CLI command |
| **Drift Judge & Repair** | Phase 5–6 | **Completed** | `docsync/drift/judge.py` (citation guardrails), `repair.py` (unified diffs) |
| **Deterministic Demo** | Phase 7 | **Completed** | `scripts/run_demo.py` (C0 $\to$ C1 MATCH, C1 $\to$ C2 DRIFT) |
| **CI/CD Automation** | Phase 8 | **Completed** | `.github/workflows/docsync-pr.yml`, `.github/workflows/test.yml` |
| **Containers & Orchestration** | DevOps Spec | **Completed** | `Dockerfile` (multi-stage), `docker-compose.yml` |
| **Web Dashboard** | Phase 13 | **Completed (50% Scope)**| `dashboard/streamlit_app.py` (Interactive Q&A + PR Viewer) |
| **AWS Cloud Instance** | DevOps Spec | **In Progress** | AWS EC2 Ubuntu instance deployment for Ollama & open models |
| **Benchmark E1–E6** | Phase 11 | Planned for A3 | Synthetic AST mutation benchmark on Pallets/Flask |

---

## 3. Working Prototype & Demo Evidence (Criterion C7 & C9)
- **Deterministic Offline Demo:** Verified via `python scripts/run_demo.py`. Successfully detects a parameter default change (`timeout=30` $\to$ `60`), generating a unified diff repair without false alarms on harmless refactors.
- **Repository Q&A Bot:** Tested via `python -m docsync.cli ask "How does fetch_data handle timeout?" --repo examples/demo_project`. Returns grounded answer with exact citations (`docs/usage.md:3-13`, `client.py:5-12`).
- **Containerization & CI:** Fully dockerized via `docker-compose.yml` with health checks on port 8501.

---

## 4. Problem Solving & Technical Insights (Criterion C8)
- **Challenge:** LLMs often hallucinate file references or declare drift on cosmetic wording changes.
- **Solution:** Enforced strict post-processing logic in `docsync/drift/judge.py`. If the LLM claims drift without citing valid extracted evidence tokens (`E1`, `E2`, `D1`), the decision is automatically downgraded to `UNCERTAIN`.
- **Challenge:** Windows console character encoding limitations with emojis.
- **Solution:** Configured UTF-8 stdout encoding and robust text badges to guarantee cross-platform compatibility across Windows, Linux, and Docker.

---

## 5. Next Steps for End-Term (A3)
1. Run empirical evaluation experiments (E1 Method Comparison, E2 Retrieval Ablation, E3 Model Comparison on Gemini vs DeepSeek-Coder).
2. Complete Sweep.dev autonomous pull-request remediation loop.
3. Conduct AI-assisted testing coverage analysis using CodiumAI / Qodo.

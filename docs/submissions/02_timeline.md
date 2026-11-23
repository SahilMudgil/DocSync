# Project Timeline & Milestone Tracking (Criterion C6)

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows  
**Deliverable:** A1 Submission & Progress vs. Plan Tracking  

---

## 1. Master Schedule & Milestone Progression

| Phase / Milestone | Planned Dates | Actual Completion | Deliverables & Verification Status | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0: Environment & Verification** | Day 0 (Oct 4) | Oct 4 | Virtualenv, dependencies, `docsync --help`, tool checks | **Completed** |
| **Phase 1: Config & Data Models** | Oct 4–5 | Oct 5 | Pydantic schemas (`models.py`), YAML config loader, unit tests | **Completed** |
| **Phase 2: Code & Doc Parsing** | Oct 6 | Oct 6 | Tree-sitter & AST parser, docstring chunking (`ingest/`) | **Completed** |
| **Phase 3: Git Change Detection** | Oct 6 | Oct 6 | Git diff changed-line to symbol mapper (`git_changes.py`) | **Completed** |
| **Phase 4: Hybrid Retrieval (RRF)** | Oct 7 | Oct 7 | BM25 + FAISS + Reciprocal Rank Fusion (`hybrid.py`) | **Completed** |
| **Phase 5: Evidence & LLM Judge** | Oct 7 | Oct 7 | Prompt templates, evidence formatting, citation guardrails | **Completed** |
| **Phase 6: Repair & Example Checks** | Oct 7–8 | Oct 8 | Unified diff generator (`repair.py`), AST syntax validation | **Completed** |
| **Phase 7: Core Pipeline & A2 Demo** | Oct 8 | Oct 8 | `pipeline.py`, CLI commands (`check`, `ask`), `scripts/run_demo.py` | **Completed** |
| **Phase 8: GitHub Actions & Sweep** | Oct 8–9 | Oct 9 | `.github/workflows/docsync-pr.yml`, `sweep.yaml`, patch flow | **Completed** |
| **Phase 9: Test Suite & AI Testing** | Oct 9 | Oct 9 | 50+ unit/integration tests passing offline, `ai_testing.md` | **Completed** |
| **Phase 10: Sourcegraph Adapter** | Oct 10 | Oct 19 | GraphQL API adapter with local fallback, 6 unit tests | **Completed** |
| **Phase 11: Benchmark & Metrics** | Oct 12–14 | Oct 19 | 32-case AST mutation dataset on Flask, E1/E2/E6 runner | **Completed** |
| **Phase 12: Prompt Lab** | Oct 15–16 | Oct 19 | `eval/prompt_lab.py`, V1 vs V2 prompt comparisons, model matrix | **Completed** |
| **Phase 13: Web Dashboard** | Oct 17 | Oct 19 | 5-tab Streamlit dashboard with Ground-Truth Case Explorer | **Completed** |
| **Phase 14: Hardening & Final Docs** | Oct 18–19 | Oct 19 | Ethics doc, AI disclosure, evaluation report, clean Docker setup | **Completed** |

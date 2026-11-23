# AI Usage Disclosure

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows (BMU)  
**Project:** DocSync — Repository-Aware RAG for Documentation Drift Detection in CI/CD  
**Companion Documents:** `README.md`, `docs/ethics_limitations.md`, `DOCSYNC_MASTER_PLAN.md`  

---

## 1. AI Assistance Used in This Project

In accordance with course guidelines encouraging transparent and responsible AI-assisted engineering, this document details the AI tools utilized, code authored by assistants, and what the student team designed, verified, and defended.

### 1.1 AI Coding Assistants
* **Antigravity (Google DeepMind Agentic Coding Assistant):**
  * Assisted in synthesizing the initial pipeline architecture, Pydantic data models (`docsync/models.py`), CLI parser (`docsync/cli.py`), Tree-sitter & doc parsing bridges (`docsync/ingest/`), hybrid RRF retrieval (`docsync/retrieval/`), and automated test scaffolds.
  * Generated the initial Streamlit dashboard layout (`dashboard/streamlit_app.py`) and Docker configurations.
* **CodiumAI / Qodo:**
  * Used in VS Code to analyze test boundary coverage and generate unit test assertions for `test_drift_judge.py` and `test_parsers.py`.
* **TabNine & Codeium:**
  * Used by team members during manual test editing and docstring maintenance in VS Code.
* **Cursor / Gemini CLI:**
  * Used for local code exploration and drafting query templates.

---

## 2. What the Student Team Did Ourselves

1. **System Design & Research Architecture:**
   * Formulated the research question (RQ: RAG vs. Heuristics vs. Zero-Shot LLM drift detection).
   * Designed the evaluation methodology, metric boundaries (Wilson confidence intervals), and the dev/test stratified split.
2. **Benchmark Verification & Label Auditing:**
   * Manually inspected and verified every benchmark case in `experiments/cases/review.csv`. Two team members audited each case to ensure that positive cases represent genuine contradictions and negative cases represent contract-preserving refactors.
3. **Execution of Live Empirical Experiments:**
   * Configured API credentials (`GOOGLE_API_KEY`) and deployed local/AWS Ollama instances for DeepSeek-Coder and CodeLlama.
   * Ran experiments E1–E6 and generated final statistical matrices.
4. **Sourcegraph Live Environment Configuration:**
   * Configured Sourcegraph instance, executed the 5 saved semantic queries on `pallets/flask`, and captured screenshot evidence.
5. **Code Review, Refinement & Viva Preparation:**
   * Reviewed every line of code to enforce synchronous execution constraints, modular function sizes (≤ 50 lines), and docstring standards.
   * Authored explain notes in `docs/explain/` and prepared individual viva defenses.

---

## 3. How AI-Generated Code Was Verified

* **Automated Offline Test Suite:** All code was verified against a 67-test pytest suite passing completely offline with no network or API key dependencies.
* **Deterministic Demo & Acceptance Tests:** Executed `scripts/run_demo.py` and `test_demo_scenario.py` verifying known baseline transitions (C0→C1 MATCH, C1→C2 DRIFT).
* **AST Syntax Gating:** All synthetic mutation code was validated with `ast.parse`.
* **Explain-As-You-Build Protocol:** Every module is accompanied by an explain note in `docs/explain/` containing likely examiner viva questions and answers.

---

## 4. Responsibility & Individual Understanding Statement

Each team member owns specific modules per the team responsibility matrix (`docs/submissions/03_responsibility_matrix.md`), understands the underlying algorithms (Tree-sitter AST traversal, BM25 TF-IDF scoring, FAISS L2 vector distances, and Reciprocal Rank Fusion), and can defend all decisions in the oral viva examination.

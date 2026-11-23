# 🔄 DocSync — AI DevOps Documentation Intelligence & Drift Detection

> **Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows (BMU)  
> **Mid-Semester Milestone (A2):** Working Prototype, Repository Code Q&A Bot, GitHub Actions CI/CD, Containerization, and Deterministic Demo.

---

## 📌 Problem Overview
In fast-moving codebases, code evolves rapidly, but documentation (docstrings, READMEs, API guides) often lags behind. Tests and linters do not fail when documentation becomes stale or inaccurate.

**DocSync** solves this by:
1. **Repository Code Q&A Bot (`docsync ask`):** Real-time conversational RAG interface over indexed code and docs with source citations (fulfilling Course Handout A2 Rubric).
2. **Autonomous PR Drift Detection (`docsync check`):** Parses changed functions using AST diffing, retrieves candidate documentation chunks using **Hybrid Search** (BM25 + FAISS + Reciprocal Rank Fusion), and uses an LLM judge with hallucination guardrails to detect drift, propose unified diffs, and alert developers.
3. **AI DevOps Automation:** Hooks into GitHub Actions CI/CD on pull requests and opens issues for Sweep.dev remediation.

---

## 🚀 5-Minute Evaluation Demo

### 1. Deterministic Offline Demo (No API key or network required)
```bash
python scripts/run_demo.py
```
- **Commit C0 $\to$ C1 (Harmless code refactor):** Returns `MATCH` (No false alarm).
- **Commit C1 $\to$ C2 (Code changes `timeout=30` to `timeout=60`, docs untouched):** Returns `DRIFT` with cited evidence (`E2`, `D1`), and generates a unified diff repair.

### 2. Interactive Repository Code Q&A Bot
```bash
docsync ask "What is the default timeout parameter in fetch_data()?"
```

### 3. Launch Streamlit Web Application
```bash
streamlit run dashboard/streamlit_app.py
```

### 4. Run Docker Container
```bash
docker compose up
```

---

## 🛠️ Technology Stack & AI DevOps Tooling
- **Semantic Code Understanding:** Python AST & Tree-sitter symbol parsing.
- **RAG & Vector Retrieval:** LangChain, FAISS, BM25, Reciprocal Rank Fusion (RRF), Sourcegraph code search.
- **LLM Judges & Open Models:** Google Gemini API & Ollama (DeepSeek-Coder / Code Llama on AWS EC2).
- **CI/CD & Automation:** GitHub Actions (`.github/workflows/docsync-pr.yml`), Sweep.dev (`sweep.yaml`).
- **Testing & Quality:** Pytest (67 offline tests), CodiumAI / Qodo AI-assisted testing.
- **Containers:** Multi-stage `Dockerfile`, `docker-compose.yml`.

---

## 📊 Evaluation & Empirical Experiments (A3)

### 1. Run Empirical Benchmark Suite (E1, E2, E6)
```bash
# Run quick 6-case smoke test offline with fake provider:
python -m docsync.cli evaluate --config experiments/configs/smoke.yaml

# Run full 32-case Pallets/Flask benchmark:
python -m docsync.cli evaluate --config experiments/configs/default.yaml
```
Output results are logged to `experiments/results/` and Markdown reports to `experiments/reports/`.

### 2. Run Prompt Engineering Lab
```bash
# Evaluate docstring completion, refactoring, and claim-by-claim verification:
python -m docsync.cli prompt-lab --provider fake
```
Findings and model comparison matrices are documented in `docs/prompt_engineering.md`.

---

## ⚖️ Limitations & Ethical Considerations
DocSync is an advisory gate with a strict human-in-the-loop requirement — it proposes unified diffs but **never auto-merges code or documentation**. Comprehensive analysis of 13 critical technical, ethical, and security risks (including static analysis limits, hallucination guardrails, private code governance, and prompt injection mitigations) is documented in [docs/ethics_limitations.md](docs/ethics_limitations.md).

---

## 🤖 AI Usage Disclosure
In compliance with responsible AI use guidelines, initial architecture skeletons and test scaffolds were developed with AI pair-programming assistance (Google DeepMind Antigravity). Ground truth benchmark verification, experimental design, and viva defense are conducted directly by the student engineering team. Full disclosure: [docs/AI_USAGE_DISCLOSURE.md](docs/AI_USAGE_DISCLOSURE.md).


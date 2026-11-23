# DocSync — AI DevOps Tools Log

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows  
**Deliverable:** Tool Configuration & Multi-Tool Coordinated Flow (A1 & A3)  

This document logs all intelligent developer tools and AI DevOps assistants configured and utilized throughout the DocSync project lifecycle.

---

## 1. Tool Configuration & Utilization Matrix

| Tool | Category | Owner / Member | Concrete Task Performed | Repository Location | Evidence File | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Sourcegraph** | Code Intelligence & Search | [STUDENT TODO: Name] | Semantic caller navigation, symbol search, and API reference extraction on Flask | `docsync/retrieval/code_search.py`, `config/default.yaml` | `docs/sourcegraph_setup.md`, `docs/evidence/sourcegraph/` | **Adapter Implemented & Verified (Tests Passing)**; Screenshots `[STUDENT TODO]` |
| **Tree-sitter** | AST Semantic Parsing | [STUDENT TODO: Name] | Extracting Python function signatures, line boundaries, and docstrings | `docsync/ingest/code_parser.py`, `doc_parser.py` | `tests/unit/test_parsers.py` | **Completed & Verified** |
| **LangChain** | RAG Architecture | [STUDENT TODO: Name] | Embeddings orchestration, vector store indexing, and interactive Code Q&A bot | `docsync/retrieval/embeddings.py`, `docsync/rag/qa_bot.py` | `tests/integration/test_qa_bot_chain.py` | **Completed & Verified** |
| **FAISS / Vector Store** | Dense Retrieval | [STUDENT TODO: Name] | Vector similarity search over chunked markdown guides and docstrings | `docsync/retrieval/embeddings.py`, `hybrid.py` | `tests/unit/test_retrieval.py` | **Completed & Verified** |
| **Sweep.dev** | Autonomous PR Remediation | [STUDENT TODO: Name] | Generating self-healing documentation pull requests from drift issues | `sweep.yaml`, `docsync/report/github_issue.py` | `docs/evidence/sweep/README.md` | **Loop Guards & Issues Implemented**; Webhook `[STUDENT TODO]` |
| **GitHub Actions** | CI/CD Automation | [STUDENT TODO: Name] | Automated pull request drift gating, artifact generation, and PR commenting | `.github/workflows/docsync-pr.yml`, `test.yml` | `tests/test_github_flow.py` | **Completed & Verified** |
| **CodiumAI / Qodo** | AI Test Generation | [STUDENT TODO: Name] | Suggesting unit test assertions, edge cases, and boundary coverage | `tests/unit/test_drift_judge.py`, `test_parsers.py` | `docs/ai_testing.md` | **Completed & Documented** |
| **Google Gemini** | LLM Judge & Repair | [STUDENT TODO: Name] | Zero-shot drift judging with citation guardrails and unified diff repair | `docsync/llm/factory.py`, `docsync/drift/judge.py` | `tests/unit/test_drift_judge.py` | **Completed & Verified** |
| **Ollama (Open Models)** | Local LLM Hosting | [STUDENT TODO: Name] | Local inference with open code models (e.g. DeepSeek-Coder / CodeLlama) on AWS/local | `docsync/llm/factory.py`, `dashboard/streamlit_app.py` | `dashboard/streamlit_app.py` | **Configured & Active in Web UI** |
| **Streamlit** | Interactive Web Dashboard | [STUDENT TODO: Name] | Visual PR drift studio, interactive repository Code Q&A, and metric charts | `dashboard/streamlit_app.py` | `dashboard/` | **Completed & Verified** |
| **Docker** | Containerization | [STUDENT TODO: Name] | Multi-stage image build and Docker Compose orchestration | `Dockerfile`, `docker-compose.yml` | `Dockerfile` | **Completed & Verified** |
| **Antigravity** | Agentic AI Coding Assistant | Google DeepMind / Team | Architecture design, test suite creation, pipeline implementation | Workspace | `docs/AI_USAGE_DISCLOSURE.md` | **Disclosed & Transparent** |

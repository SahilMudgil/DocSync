# Team Responsibility Matrix (Criterion C5 & C10)

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows  
**Deliverable:** A1 Submission & Work Allocation Matrix  

---

## 1. Work Allocation Across 5 Engineering Roles

Every team member is responsible for specific architectural modules, their unit tests, and viva defense, while maintaining comprehensive understanding of the full pipeline.

| Role | Responsibility Area | Target Modules & Files | Auxiliary Responsibilities | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **R1** | **Code Intelligence & Parsing** | `docsync/ingest/` (`code_parser.py`, `doc_parser.py`, `git_changes.py`), Sourcegraph adapter (`code_search.py`) | Sourcegraph Docker setup, 5 saved query screenshots, explain notes for ingestion | `[STUDENT TODO: Member 1 Name]` |
| **R2** | **Retrieval Architecture & RAG** | `docsync/retrieval/` (`lexical.py`, `embeddings.py`, `hybrid.py`), `rag/evidence.py`, `rag/qa_bot.py` | FAISS vector store indexing, Reciprocal Rank Fusion tuning, E2 Retrieval Ablation analysis | `[STUDENT TODO: Member 2 Name]` |
| **R3** | **LLM Reasoning & Prompts** | `docsync/llm/` (`factory.py`, `prompts.py`), `drift/judge.py`, `repair.py`, `eval/prompt_lab.py` | Google Gemini API configuration, Ollama local hosting, Prompt Lab V1 vs V2 analysis | `[STUDENT TODO: Member 3 Name]` |
| **R4** | **CI/CD, Automation & Testing** | `.github/workflows/` (`docsync-pr.yml`, `test.yml`), `sweep.yaml`, `drift/example_check.py`, `Dockerfile` | Sweep.dev webhook integration, CodiumAI test generation evidence (`ai_testing.md`), Docker compose health checks | `[STUDENT TODO: Member 4 Name]` |
| **R5** | **Evaluation & Dashboard** | `docsync/eval/` (`benchmark_gen.py`, `mutations.py`, `run_experiment.py`, `metrics.py`), `dashboard/` | Ground-truth benchmark human verification (`review.csv`), Streamlit Case Explorer, ethics & limitations report | `[STUDENT TODO: Member 5 Name]` |

---

## 2. Shared Team Responsibilities
* Complete participation in end-to-end oral defense and viva.
* Peer code review across all Git pull requests.
* Verification of benchmark ground truth labels.

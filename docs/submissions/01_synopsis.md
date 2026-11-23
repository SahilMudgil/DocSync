# Project Charter / Synopsis (A1 Submission)

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows (BMU)  
**Project Title:** DocSync — Repository-Aware RAG for Documentation Drift Detection in CI/CD  
**Faculty Mentor:** Dr. Kiran Khatter  
**Team Members:** `[STUDENT TODO: Member Names & Roll Numbers]`  

---

## 1. Problem Definition (Criterion C1)
In continuous software development, source code evolves rapidly (functions renamed, default arguments changed, return types altered), but associated documentation (README guides, API reference docs, docstrings, tutorial code snippets) is frequently left untouched. Standard automated unit tests and CI/CD pipelines fail to detect this discrepancy because tests only check code behavior, not documentation truthfulness. Consequently, stale documentation misleads developers, breaks client integrations, and accumulates technical debt.

## 2. Objectives & Measurable Outcomes (Criterion C2)
1. **Semantic Code Understanding:** Parse Python function ASTs using Tree-sitter to detect signature changes, modified literals, and docstring boundaries across Git commit ranges.
2. **Hybrid RAG Retrieval:** Locate candidate documentation sections using Reciprocal Rank Fusion (RRF) over BM25 keyword matching, FAISS dense embeddings (MiniLM-L6-v2), and local/Sourcegraph caller reference search.
3. **Guardrailed LLM Drift Judge:** Evaluate documentation consistency with strict anti-hallucination guardrails, outputting `MATCH`, `DRIFT`, or `UNCERTAIN` supported by cited evidence tokens (`E1`, `E2`, `D1`).
4. **Automated Documentation Repair:** Propose minimal unified diff patches for detected drift without ever auto-merging into production source code.
5. **Interactive Repository Code Q&A Bot:** Provide a natural language query interface (`docsync ask` and Streamlit tab) citing exact line ranges to satisfy the A2 rubric.
6. **CI/CD & Sweep Integration:** Run automated checks on every pull request via GitHub Actions (`docsync-pr.yml`) and open remediating draft PRs via Sweep.dev.
7. **Empirical Benchmarking:** Evaluate precision, recall, latency, and token cost against heuristic rule-based (M1) and zero-shot LLM (M2) baselines across a 32-case verified benchmark on Pallets/Flask.

## 3. Methodology (Criterion C3)
* **Code Intelligence:** Tree-sitter & Python `ast` for symbol contracts.
* **Retrieval & RAG:** LangChain, HuggingFace Sentence-Transformers, FAISS vector stores, BM25, and Sourcegraph GraphQL search.
* **LLMs & Prompts:** Google Gemini 1.5 Flash (hosted) and DeepSeek-Coder / CodeLlama (via local/AWS Ollama).
* **DevOps Automation:** GitHub Actions, Sweep.dev webhooks, multi-stage Docker containerization.
* **Evaluation & Testing:** Pytest suite (AI-assisted with CodiumAI/Qodo), synthetic AST mutation benchmark with 50/50 stratified split, Wilson 95% confidence intervals.

## 4. Feasibility & Resource Planning (Criterion C4)
* **Software Tools:** All frameworks (LangChain, FAISS, Streamlit, Tree-sitter) are open source.
* **Hardware:** Modest compute budget; open code models run on local laptops or cloud EC2 (`m7i-flex.large`), with zero-cost offline fallback.
* **Work Division:** 5 clearly partitioned engineering roles with individual viva accountability.

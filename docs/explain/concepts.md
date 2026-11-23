# Explain: Core Concepts Primer (`docs/explain/concepts.md`)

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows  
**Audience:** Student team oral viva defense preparation (Level 0 Foundation)  

---

## 1. Core Technical Vocabulary & Concept Primer

| Concept | Plain English Explanation | Role in DocSync |
| :--- | :--- | :--- |
| **LLM (Large Language Model)** | A neural model trained on massive text corpora to predict tokens and understand code syntax and semantics. | Evaluates whether code modifications contradict documentation claims; synthesizes unified diff repairs. |
| **Prompt Engineering** | Structuring system prompts, task constraints, templates, and few-shot examples to maximize LLM accuracy. | Used in `DRIFT_JUDGE_V2` (claim-by-claim verification) and Google-style docstring completion (`_V2`). |
| **Vector Embedding** | A dense vector of numbers capturing semantic meaning, where conceptually similar texts map to nearby coordinates. | `all-MiniLM-L6-v2` converts doc chunks and queries into 384-dimensional dense vectors. |
| **FAISS (Facebook AI Similarity Search)** | A high-performance library for fast nearest-neighbor search in dense vector spaces. | Finds documentation chunks closest in semantic meaning to a changed function's intent. |
| **BM25 (Best Matching 25)** | A probabilistic TF-IDF ranking function scoring documents based on query keyword frequency and inverse document frequency. | Identifies documentation files that explicitly name changed function identifiers or arguments. |
| **RAG (Retrieval-Augmented Generation)** | Architecture that retrieves relevant external context first, then prompts the LLM using only the retrieved evidence. | Retrieves candidate docs, AST signatures, and caller references before judging drift, preventing hallucinations. |
| **Reciprocal Rank Fusion (RRF)** | An unsupervised rank aggregation formula: $\text{RRF Score} = \sum \frac{1}{k + \text{rank}}$. | Combines ranked lists from BM25, FAISS embeddings, and local/Sourcegraph search into a single robust ranking ($k=60$). |
| **Tree-sitter / AST** | Concrete syntax tree parser that understands exact grammar boundaries (functions, arguments, docstrings). | Detects which function changed in a commit range and extracts its exact signature and default values. |
| **Git Diff** | Displays line-level additions, modifications, and deletions between two commit SHAs. | Serves as the raw trigger for every DocSync pull request check. |
| **Sourcegraph** | Code intelligence platform providing cross-file symbol definitions, caller references, and commit search. | Locates caller references and downstream usages across monorepos (`docsync/retrieval/code_search.py`). |
| **GitHub Actions** | Event-driven automation executing workflows on GitHub repository events (e.g. `pull_request`). | Automatically runs `docsync check` on PRs and posts verification reports as comments. |
| **Sweep.dev** | Autonomous GitHub bot that reads issue descriptions and creates draft pull requests with code fixes. | Reads DocSync high-confidence drift issues and drafts the documentation fix PR automatically. |
| **Wilson Confidence Interval** | A statistical formula for calculating confidence intervals on binomial proportions for small sample sizes. | Provides 95% confidence intervals on benchmark precision, recall, and F1 to avoid statistical over-claiming. |
| **Human-in-the-Loop** | Design constraint requiring human developer approval before AI changes are committed to production. | DocSync proposes documentation fixes as unified diff patches; it never auto-merges or writes to code. |

---

## 2. Three Mandatory Viva Questions Every Member Must Master

### Q1: Why is RAG necessary for drift detection? Why not just send the entire documentation into the LLM?
**Answer:** Sending an entire repository's documentation into an LLM context window causes the "lost in the middle" phenomenon (where LLMs overlook specific details), incurs massive latency in CI pipelines, and consumes thousands of tokens per PR. DocSync's hybrid RRF retrieval extracts only the top-3 candidate chunks (reducing tokens by 84%) and provides precise line citations.

### Q2: How does DocSync prevent false alarms when a developer refactors code without changing behavior?
**Answer:** DocSync uses AST signature diffing. If a change only affects internal local variables or comments, the AST signature and public contract remain identical. In fast mode, rule-based heuristics immediately return `MATCH`. In full mode, `DRIFT_JUDGE_V2` checks claims and marks internal refactors as `SUPPORTED`.

### Q3: What is Reciprocal Rank Fusion (RRF) and why is $k=60$ chosen?
**Answer:** RRF aggregates ranked lists from different search engines without needing score calibration: $\text{score} = \sum \frac{1}{60 + \text{rank}}$. The constant $k=60$ is the standard value derived by Cormack et al. (SIGIR 2009) to ensure that top-ranked items from any single retriever are rewarded without allowing outliers from one list to dominate the combined score.

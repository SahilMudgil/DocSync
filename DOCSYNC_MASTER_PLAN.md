# DocSync — Master Build Plan

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows (BMU)
**Project:** DocSync — Repository-Aware RAG for Documentation Drift Detection in CI/CD
**Audience of this file:** the implementation agent (Antigravity) and the 3–5 students who must understand and defend everything it builds.
**Companion file:** `DOCSYNC_COURSE_PACK.md` (course paperwork, templates, concept primer, viva prep). Read both.

---

## 0. READ THIS FIRST — rules for the implementation agent

### 0.1 The one rule that beats all others
**The students must be able to explain every line.** If a choice is between "clever" and "clear", pick clear. If a feature cannot be explained in two minutes by a 7th-semester CS student, simplify it or drop it.

**IMPLEMENTATION REQUIREMENT.** This document is an implementation specification, not a documentation task. The agent must create the working repository described here (code, tests, workflows, dashboard, Docker, templates). It must not stop at READMEs, diagrams, skeletons, placeholders or TODO lists. Every row of the traceability table in §16 must be implemented and verified offline, unless its owner is marked STUDENT (real-world evidence that only the team can produce, see §15).

### 0.2 Code-style rules (hard limits)
- Python 3.11+. **Synchronous code only** (no `async`, no FastAPI, no threads).
- Plain functions and small classes. Pydantic models for data. One `Protocol` (code search provider) is the only "design pattern" allowed.
- Functions ≤ ~50 lines. Files ≤ ~300 lines. Whole `docsync/` package target **≤ 2,500 lines**.
- Type hints on public functions. Short comments that explain **why**, not what. No marketing language in comments or docs.
- Every module starts with a 3–6 line docstring: *what it does, input, output, how it works*.
- Use argparse (standard library) for the CLI.
- No database. Results are JSON files; the dashboard reads those files.
- No agent swarms. The "pipeline" is ordinary Python functions called in order.

### 0.3 Explain-as-you-build (mandatory)
After finishing **each phase**, create/update `docs/explain/<module>.md` containing:
1. What this module does (3 lines)
2. Input → output example (real data from the repo)
3. How it works (5–8 lines, plain English)
4. 3 likely viva questions with short answers

This is how the students learn the code. Do not skip it.

### 0.4 Honesty rules (non-negotiable)
- **Never invent** metrics, benchmark results, token counts, Sourcegraph results, Sweep PRs, or screenshots. If an experiment has not been run, write `TBD — run <command>`.
- **Never claim a tool was used unless it was actually used.** Tools that only the students can run (Sourcegraph UI, Sweep GitHub app, CodiumAI/Codeium, TabNine, Cursor, Gemini CLI, V0.dev) are listed in §15 as **STUDENT TASKS**. Create the file/template and put `[STUDENT TODO]` markers; do not fill them with fake evidence.
- If an external service is unavailable, implement the adapter + a local fallback, and make the run report say which one was really used.
- Never convert an error into a "MATCH". Errors are reported as errors.
- **Keep two claims apart (details in §14.1):** "the software passes automated tests offline" is **not** the same as "the AI approach was evaluated with real models". Outputs of the scripted fake model are never put in a results table. Final E1–E6 results must be produced by the **students**, on their machines, with real models; the agent may only run smoke tests.
- Do not fabricate student contributions: contribution and responsibility matrices are filled by the team from Git history, not generated.
- Include `docs/AI_USAGE_DISCLOSURE.md` (template in the course pack). The README must have an "AI assistance" section saying this project was built with AI coding assistance and what the students did themselves.

### 0.5 Working method
1. Work phase by phase (§12). Do not start the dashboard before the pipeline works.
2. After each phase: run `pytest`, run `ruff check`, commit with a plain message (`add git change detection`, `fix retrieval metadata`).
3. Pin dependency versions in `requirements.txt` after confirming they install together (reuse versions from the students' earlier CodeBase_RAG project when possible: `tree-sitter==0.24.0`, `tree-sitter-python==0.23.6`, `langchain==0.3.x` family, `faiss-cpu`, `sentence-transformers`).
4. Verify current model names and tool instructions from official docs before using them (names change). **Never hard-code model names**; read them from config/env.
5. At the end, write `docs/IMPLEMENTATION_STATUS.md`: what is done, what is partial, what needs students.

### 0.6 Optional reuse
If the folder `reference/CodeBase_RAG-main/` is present, you may reuse and adapt: `tree_sitter_parser.py`, `vector_store.py`, `rate_limiter.py`, `ci.yml`, `sweep.yaml`, and test fixtures such as the fake embeddings/fake chat model. State in the README what was reused. The students already know that codebase, which makes DocSync easier to defend.

---

## 1. What we are building (plain English)

**The problem.** Developers change code, but the README and docs keep describing the old behaviour. Example: code changes `timeout=30` to `timeout=60`; the docs still say "defaults to 30 seconds". Tests pass, CI is green, and the documentation is silently wrong.

**DocSync** provides two complementary AI-assisted capabilities built on a shared repository intelligence index:

1. **Interactive Repository Code Q&A Bot (`docsync ask` & Streamlit tab):** Developers and examiners can query the repository in natural language (e.g., *"How is error handling implemented in client.py?"*, *"What parameters does fetch_data accept?"*). LangChain retrieves relevant code symbols and documentation chunks from FAISS (or ChromaDB) and generates an answer citing exact file names and line ranges. This directly and verbatim fulfills the handout's A2 requirement: *"RAG-based code Q&A bot using LangChain or LlamaIndex with real project repositories"*.
2. **Autonomous Pull-Request Drift Detection (CI/CD):** An automated pipeline that runs on every PR:
   - Find **which functions changed** (git diff + Tree-sitter AST parsing).
   - Find **which documentation might describe them** (hybrid search: BM25 keyword + FAISS embeddings + caller graph).
   - Ask an LLM: *"Does this documentation still match the new code?"* using only retrieved evidence → `MATCH`, `DRIFT`, or `UNCERTAIN` with evidence IDs.
   - If `DRIFT`: propose a documentation fix and render a unified diff.
   - Check code examples in the docs (syntax parsing + identifier validation).
   - Post a readable report on the pull request. **A human decides** — DocSync never merges automatically.
   - Optionally open an issue labelled `sweep` so Sweep.dev drafts the documentation PR; DocSync then re-checks that PR.

**The research part.** We measure whether the RAG approach beats simpler baselines (rule-based M1, LLM-only M2) on a verified benchmark, measuring precision, recall, latency, and tokens.

**Why it fits the course:** It integrates Tree-sitter (semantic code understanding), embeddings/FAISS/ChromaDB (repository intelligence & Code Q&A), LangChain RAG, open/hosted LLMs, prompt engineering, Sourcegraph, GitHub Actions CI/CD, Sweep.dev automation, AI test generation (CodiumAI/Codeium), evaluation benchmarks, and Streamlit (working web application) — fulfilling all course outcomes CO1–CO3.

---

## 2. Course handout compliance map

Every graded item in the handout must map to a concrete deliverable and an evidence file.

### 2.1 Assessment items → deliverables

| Handout item (marks) | DocSync deliverable | Evidence location |
|---|---|---|
| **A1** Synopsis/problem definition (5) | One-page synopsis, timeline, responsibility matrix | `docs/submissions/01_synopsis.md`, `02_timeline.md`, `03_responsibility_matrix.md` |
| **A1** Prompt engineering for completion & refactoring (5) | Prompt Lab: docstring-completion + refactor prompts, V1 vs V2, across models | `docsync/eval/prompt_lab.py` (CLI `prompt-lab`), `experiments/results/prompt_lab_*.json`, `docs/prompt_engineering.md` |
| **A1** Sourcegraph setup & semantic navigation (10) | Sourcegraph instance + 5 saved queries + adapter in DocSync | `docs/sourcegraph_setup.md`, `docs/evidence/sourcegraph/` |
| **A1** Tool configuration & code exploration (5) | TabNine/Codeium in VS Code, Ollama with open code models, Cursor, Gemini CLI, V0.dev | `docs/tools_log.md`, `docs/evidence/tools/` |
| **A1** Documentation (5) | README, explain notes, methodology | `README.md`, `docs/` |
| **A2** RAG Q&A with LangChain/LlamaIndex (10) | **Dual RAG capabilities:** (1) Interactive Repository Code Q&A Bot (`docsync ask` CLI & Streamlit Q&A tab) with cited code/doc snippets; (2) RAG evidence retrieval + drift judge built with **LangChain** (embeddings, FAISS/Chroma store, prompt templates, chat models, output parsing) | `docsync/rag/qa_bot.py`, `docsync/retrieval/`, `docsync/llm/` |
| **A2** GitHub Actions CI/CD with Sweep.dev (10) | `test.yml`, `docsync-pr.yml`, `sweep.yaml`, issue-to-PR loop | `.github/workflows/`, `docs/evidence/sweep/` |
| **A2** Test generation with CodiumAI/Codeium (5) | Tests generated/extended with the tool, reviewed and fixed by students | `docs/ai_testing.md`, `docs/evidence/codium/` |
| **A2** Integration quality & documentation (5) | End-to-end demo, progress report | `docs/submissions/04_demo_script.md`, `05_progress_report.md` |
| **A3** Integration of retrieval & automation (15) | RAG runs inside the PR pipeline and feeds Sweep | `docsync-pr.yml`, `docsync/pipeline.py` |
| **A3** Multiple tools, coordinated flow (10) | One architecture diagram + tools log | §5, `docs/tools_log.md` |
| **A3** Custom prompts, code search, evaluation (5) | Versioned prompts, hybrid search, benchmark & metrics | §8, §9, `experiments/` |
| **A3** Functional completeness & innovation (5) | Full pipeline + Streamlit dashboard + benchmark | whole repo |
| **A3** Presentation, teamwork, usability (5) | PPT, demo script, contribution matrix | `docs/submissions/` |

### 2.2 Course outcomes

- **CO1** (foundations/tools, ethics, code models): model comparison (Gemini vs ≥1 open code model through Ollama), concept primer, `docs/ethics_limitations.md`.
- **CO2** (apply tools for search, testing, automation): Sourcegraph, CodiumAI/Codeium tests, GitHub Actions, Sweep.dev.
- **CO3** (create AI-augmented workflows): RAG pipeline integrated into DevOps toolchain; final integrated project.

### 2.3 Handout topics to touch (and where)

| Topic | Where |
|---|---|
| Code models (Code Llama, StarCoder2, DeepSeek Coder via Ollama/HF) | Experiment E3, Prompt Lab |
| RAG accuracy implications for code retrieval | Experiments E2, E4 (Recall@K, MRR, ablations) |
| Repository Code Q&A Bot with LangChain / FAISS / ChromaDB | `docsync/rag/qa_bot.py` (`docsync ask` and Streamlit Q&A tab) |
| Semantic code understanding & repository intelligence | Tree-sitter AST parsing (`ingest/code_parser.py`) + Sourcegraph query formulation |
| Working web application demonstrated (Handout Criterion 90) | Streamlit Web Dashboard (`dashboard/streamlit_app.py`) + Docker Compose |
| Code understanding across repositories | Benchmark on Flask (+ optional Requests) |
| AI testing tools | `docs/ai_testing.md` + doc-example checker |
| GitHub Actions + AI-enhanced CI | `docsync-pr.yml` |
| Sweep.dev end-to-end automation | issue → draft PR → DocSync re-check |
| Ethics, limitations, interpretability | `docs/ethics_limitations.md`, evidence-required decisions |
| Gemini CLI, V0.dev, Cursor, Sourcegraph | `docs/tools_log.md` (each used for a defined small task) |

### 2.4 Project criteria C1–C15 → where evidence lives
C1–C5 (A1): synopsis, objectives, methodology, feasibility/timeline, individual understanding (viva notes). C6–C10 (A2): progress vs plan, technical understanding (explain notes), problem solving (failure analysis), documentation, individual contribution (contribution matrix). C11–C15 (A3): final product, technical depth, innovation, presentation, individual contribution. The course pack has a table mapping each of these to files.

---

## 3. Scope and deliberate simplifications

DocSync is intentionally **smaller** than a research-grade system so that every student can explain it.

| Included | Not included (and why) |
|---|---|
| Python repositories only | Other languages (keeps parsing simple) |
| Markdown, reStructuredText, Python docstrings | HTML/Notebook docs |
| Tree-sitter for Python symbols | Full static analysis / type inference |
| FAISS + LangChain + MiniLM embeddings | Training our own models |
| 3 methods compared (rule-based, LLM-only, RAG+LLM) | 5+ baselines |
| Controlled benchmark on Flask (labelled, human-verified) | Large historical-commit study (optional stretch only) |
| JSON result files | Database server |
| Advisory report + proposed diff | Auto-merge, auto-edit, auto-deploy |
| Local Ollama + Gemini | Fine-tuning |

**Stretch goals (only after everything else is done):** second repository (Requests), a handful of real historical doc-fix commits as extra test cases.

---

## 4. Research question and experiments

> **RQ:** Does repository-aware RAG + an LLM detect documentation drift caused by code changes more accurately than a rule-based checker and an LLM-only approach, and what does it cost in CI time and tokens?

Sub-questions: (a) Does semantic/hybrid retrieval find the right doc better than keyword search? (b) How do top-K and evidence type affect results? (c) How do an open code model and a hosted model compare? (d) Does a better prompt (V2) help?

| ID | Experiment | Compares | Metrics |
|---|---|---|---|
| E1 | Method comparison | M1 rule-based vs M2 LLM-only vs M3 RAG+LLM (same model, same cases) | Precision, Recall, F1, FPR, FNR, uncertain-rate, confusion matrix, **correct-location rate, evidence-cited rate, repair fact-correct rate** (all computed from results) |
| E2 | Retrieval comparison | BM25 vs embedding (FAISS) vs hybrid-2 (BM25+embedding, RRF) vs hybrid-3 (adds the code-search list) | Recall@1/3/5, MRR (also split by gold-doc kind, §9.8) |
| E3 | Model comparison | Gemini vs ≥1 Ollama code model (e.g., Code Llama / DeepSeek-Coder; StarCoder2 optional) on M3 | same as E1 + invalid-JSON rate + latency |
| E4 | Ablation | top-K ∈ {1,3,5}; with/without caller evidence; with/without old code | F1, latency, tokens |
| E5 | Prompt versions | DRIFT_JUDGE V1 vs V2; docstring-completion V1 vs V2 | F1 / completeness score |
| E6 | Cost & latency | per-case time, LLM calls, tokens per method | table from logs |

Use a **dev/test split** (50/50, fixed seed 42): tune prompts/top-K only on dev; report final numbers on test. Report **counts** (TP/FP/TN/FN), not only percentages — the sample is small, so do not over-claim. The RQ is a question, not a promise: if rule-based wins on some case types, report that honestly. Methodological safeguards are in §9.8.

---

## 5. Architecture

### 5.1 Pipeline (what runs on a PR)

```text
 Pull request (base SHA → head SHA)
        │
        ▼
 [1] git_changes.py        git diff → changed .py files + changed line ranges
        │
        ▼
 [2] code_parser.py        Tree-sitter → symbols (functions/classes/methods) with line ranges
        │                  → ChangedSymbol list (old code from base SHA, new code from head SHA)
        ▼
 [3] doc_parser.py         .md / .rst / docstrings → DocChunk list (path, lines, text, mentioned symbols)
        │
        ▼
 [4] retrieval/            For each ChangedSymbol, rank DocChunks:
        │                    • BM25 (keywords)
        │                    • embeddings + FAISS (meaning)
        │                    • code search results (Sourcegraph or local): who mentions/calls the symbol
        │                    → fused with Reciprocal Rank Fusion → top-K candidates
        ▼
 [5] evidence.py           Build numbered evidence: E1 old code, E2 new code, E3.. callers, D1.. candidate doc
        │
        ▼
 [6] drift/judge.py        LangChain prompt → LLM → JSON {decision, confidence, reason, evidence_ids}
        │                  + deterministic post-checks (evidence must exist, else UNCERTAIN)
        ▼
 [7] drift/repair.py       Only if DRIFT: LLM proposes corrected doc text; unified diff made with difflib
        │  drift/example_check.py   code blocks in doc: syntax check + do the names still exist?
        ▼
 [8] report/               Markdown report + JSON result → PR comment + artifact
        │
        ▼
 Human review ──► (optional) issue labelled "sweep" → Sweep.dev drafts docs PR → DocSync checks that PR too
```

### 5.2 System context (tools and where each is used)

```text
Interactive Developer Query ──► docsync ask ──────┐
                                                  ▼
Developer / PR ─► GitHub Actions ─► DocSync CLI ─┬─► Tree-sitter, git            (code understanding)
                                                 ├─► LangChain + MiniLM + FAISS/Chroma (RAG & Q&A)
                                                 ├─► Sourcegraph (local/demo) / local search (CI)
                                                 ├─► Gemini API or Ollama (Code Llama / DeepSeek)
                                                 └─► report.md + result.json
                                        │
                                        ├─► PR comment + artifact
                                        └─► Issue "Sweep: ..." ─► Sweep.dev ─► draft docs PR ─► DocSync re-check

Dashboard (Streamlit Web App) ◄─┬── reads result JSON files (Run viewer & Experiments)
                                └── provides Interactive Code Q&A Bot web UI tab
Tests: pytest (+ CodiumAI/Codeium assisted)
```

### 5.3 Two operating modes
- **fast** — rule-based check + hybrid retrieval, **no LLM**. Free, safe for every PR.
- **full** — RAG + LLM judge + repair. Used when an API key is configured (CI) or when Ollama is running (local).
The report always prints which mode, provider, model, retrieval mode, and whether Sourcegraph was used.

### 5.4 Where Sourcegraph can and cannot run
Sourcegraph (local Docker or other instance) indexes the repo on the machine where it runs. GitHub Actions cannot reach a student's `localhost`. Therefore: **CI uses the local search provider; local runs, demo and experiments can use Sourcegraph.** The report states which was used. This is an honest design limit, not a bug.

---

## 6. Data models (Pydantic, in `docsync/models.py`)

```text
CodeSymbol     name, kind(function|method|class), file, start_line, end_line, signature, code
ChangedSymbol  symbol(CodeSymbol, new) + old_code(str|None) + change_type(added|modified|deleted)
DocChunk       id, file, start_line, end_line, kind(docstring|md_section|rst_section), text,
               mentioned_symbols(list[str]), code_blocks(list[str])
SearchHit      file, line, snippet, source(local|sourcegraph), score
EvidenceItem   id("E1","D1",...), kind(old_code|new_code|caller|doc), file, start_line, end_line, text
DriftDecision  decision(MATCH|DRIFT|UNCERTAIN|MODEL_ERROR), confidence(0-1), reason,
               evidence_ids(list[str]), repair_needed(bool)
RepairSuggestion  doc_id, new_text, unified_diff, evidence_ids, notes
ExampleCheck   doc_id, block_index, syntax_ok, unknown_names(list[str]), status(PASS|WARN|FAIL|SKIPPED)
RunResult      run_id, repo, base, head, mode, provider, model, retrieval_mode, sourcegraph_used,
               prompt_versions, items(list of per-symbol/doc results), timings, token_usage, warnings
BenchmarkCase  id, repo, commit, file, symbol, mutation_type, label(DRIFT|NO_DRIFT), split(dev|test),
               old_code, new_code, gold_doc{file,start_line,end_line}, expected_fact, verified_by(list)
```

---

## 7. Component specifications

### 7.1 `ingest/git_changes.py`
- Input: repo path, base SHA, head SHA. Use `subprocess` + `git diff --unified=0 --name-status base head` (or GitPython).
- Output: for each changed `.py` file: list of changed line ranges in the **new** file, and old/new file text (`git show sha:path`).
- Handle: added, modified, deleted, renamed files (renamed = treat as modified under the new path; deleted = all its symbols are "deleted").
- Ignore: tests directory by default (configurable), vendored folders, non-.py files.

### 7.2 `ingest/code_parser.py` (Tree-sitter)
- Parse a Python file → list of `CodeSymbol` (top-level functions, classes, methods with `Class.method` naming), with signature, line range, docstring location.
- A symbol is "changed" if its line range overlaps a changed line range. Get `old_code` by locating the same-named symbol in the base version of the file (match by qualified name; if absent → `added`).
- Keep it simple: no cross-file resolution, no type inference.

### 7.3 `ingest/doc_parser.py`
- **Markdown**: split by headings (`#`…); **reStructuredText**: split by underlined titles; keep line ranges. Cap chunk size (~1500 chars, overlap 150) so embeddings stay meaningful.
- **Docstrings**: each function/class docstring is its own `DocChunk` (kind=docstring) — this is where most drift lives.
- **Mentioned symbols**: tokens in backticks, `:func:`/`:class:`/`:meth:` roles, and identifiers that match a known symbol name.
- **Code blocks**: extract ```python fenced blocks, `.. code-block:: python`, and `>>>` examples into `code_blocks`.

### 7.4 `retrieval/`
- `lexical.py`: BM25 via `rank_bm25` over doc chunk text (tokenize identifiers: split on `_` and camelCase).
- `embeddings.py`: **LangChain** `HuggingFaceEmbeddings` (default `sentence-transformers/all-MiniLM-L6-v2`, configurable) + **LangChain vector store** (FAISS by default, with ChromaDB selectable via `vector_store: faiss | chroma`). Cache the model and persist the index per (repo, commit) in `.docsync_cache/`.
- `code_search.py`: `CodeSearchProvider` Protocol → `search(query, limit) -> list[SearchHit]`.
  - `LocalSearchProvider`: regex/`grep`-style search over repo files + the symbol table (finds callers `name(` and doc mentions).
  - `SourcegraphProvider`: see §10.2. Same output type.
- `hybrid.py`: **Reciprocal Rank Fusion** of up to three ranked lists — BM25, embeddings, code-search hits mapped to doc chunks. Formula: `score(d) = Σ 1/(60 + rank_i(d))`. Add a small bonus if the chunk's `mentioned_symbols` contains the changed symbol's exact name. Return top-K with per-method ranks for explainability.
- Query construction for a changed symbol: `"<qualified name> <signature> <first docstring line> <changed parameter names>"`.

### 7.5 `rag/evidence.py`
Build a numbered evidence list for one (ChangedSymbol, candidate DocChunk):
`E1` old code, `E2` new code (and a short diff), `E3–E5` up to 3 caller snippets (from code search), `D1` the candidate documentation text. IDs are what the LLM must cite. Truncate long code to a configured character cap (state truncation in the evidence).

### 7.5b `rag/qa_bot.py` (Repository Code Q&A Bot — Handout A2 Rubric)
- Conversational / question-answering chain over the indexed codebase and documentation chunks built with LangChain.
- **Input:** natural language query (e.g., *"How does the timeout default work?"*, *"Where is error handling defined?"*), repository path, top-K.
- **Retrieval:** queries the LangChain vector store (FAISS/ChromaDB) for relevant doc chunks and symbol docstrings.
- **Prompt:** `CODE_QA_V1` instructs the chat model to formulate a direct, technical answer based on retrieved snippets, citing exact file names and line ranges.
- **Output:** structured answer + cited file references with line numbers.
- **Interface:** Powers the `docsync ask` CLI command and the interactive Streamlit "Code Q&A" tab.

### 7.6 `llm/factory.py`
- `get_chat_model(provider, model, temperature)` returns a **LangChain** chat model: `gemini` (`langchain-google-genai`), `ollama` (`langchain-ollama`), or `fake` (tests; `GenericFakeChatModel`).
- Temperature 0 by default. Model names come from config/env only.
- Reuse the rate limiter/backoff idea from CodeBase_RAG for Gemini quotas (simple sleep-and-retry).
- Count tokens from response `usage_metadata` when present; otherwise estimate `len(text)/4` and mark `estimated=true`.

### 7.7 `drift/judge.py`
- Build prompt `DRIFT_JUDGE_V1` (or V2) with `ChatPromptTemplate`, call model, parse JSON with a Pydantic parser.
- Gemini: prefer `with_structured_output`. Ollama/code models: ask for JSON in the prompt, parse, **retry once** on invalid JSON, then return `MODEL_ERROR`.
- **Deterministic post-processing:**
  1. Confidence outside [0,1] → invalid → `MODEL_ERROR`.
  2. `evidence_ids` containing IDs not in the supplied evidence → remove them.
  3. `DRIFT` with no valid evidence IDs → downgrade to `UNCERTAIN`.
  4. Never produce a repair unless final decision is `DRIFT`.
- Judge each of the top-K candidate docs separately (K calls per changed symbol). Config `max_llm_calls_per_run` protects quota; report if the cap was hit.

### 7.8 `drift/rule_based.py` (Method M1, also used in fast mode)
Pure-Python checks, no ML. For a modified function and a doc chunk mentioning it:
- Parameters named in the docstring/doc that no longer exist in the signature → drift.
- A default value stated in the text (e.g., "defaults to 30") that differs from the signature default → drift.
- Exception names stated in the text that no longer appear in `raise` statements → drift.
Return the same `DriftDecision` shape (decision, reason, evidence ids such as `E2` new code and `D1` doc) so reports and metrics treat it like the LLM methods.
**Template repair (deterministic):** for `default value`, `parameter name` and `exception name` mismatches, propose the doc text with the stale literal replaced by the value found in the new code, only if the stale literal occurs exactly once in the doc chunk; otherwise propose no repair. This keeps `fast` mode and the offline demo genuinely computed with no model involved.

### 7.9 `drift/repair.py`
- Prompt `REPAIR_V1`: LLM returns `new_text` for **that doc chunk only** + `evidence_ids` + notes.
- In `fast` mode the proposed text comes from the rule-based template repair (§7.8); in `full` mode from the LLM.
- The **unified diff is computed locally with `difflib`**, not by the LLM (deterministic, explainable).
- Safety check: if `new_text` is empty, identical, or massively longer than the original (>2×), mark `needs_review` and do not present it as a clean fix.

### 7.10 `drift/example_check.py` (documentation example validation)
Level 1 (always): `ast.parse` each Python code block → syntax OK?
Level 2 (always): collect imported/called names in the block and check they exist in the repo symbol table → `unknown_names`.
Level 3 (optional, **off by default**, demo repo only): run an allow-listed snippet in a subprocess with a timeout and no network. Never run arbitrary snippets from a third-party repo.
Status: PASS / WARN (unknown names) / FAIL (syntax) / SKIPPED.

### 7.11 `report/`
- `markdown_report.py`: PR comment layout below.
- `github_comment.py`: post/update a single bot comment using `GITHUB_TOKEN` (only when running in Actions); otherwise write `report.md` locally.

```text
## DocSync Documentation Check
Mode: full | Provider/model: <...> | Retrieval: hybrid (top-K=5) | Sourcegraph: not used (local search)
Changed symbols: 4 | Documentation candidates checked: 11 | LLM calls: 11

| Symbol | Doc location | Decision | Confidence |
|---|---|---|---:|
| fetch_data() | docs/usage.md:42-47 | DRIFT | 0.91 |

### Drift: docs/usage.md:42-47
Docs say: "...defaults to 30 seconds"
Code now:  timeout=60  (src/client.py:18)
Evidence: E2, D1
Suggested fix (diff):  ...
Example check: PASS
Human review is required before any change is applied.
```

### 7.12 `pipeline.py` and `cli.py`
Pipeline = a function `run_check(repo, base, head, config) -> RunResult` that calls steps 1–8 in order and records timings. `pip install -e .` installs a `docsync` alias, so `docsync <command>` and `python -m docsync.cli <command>` are the same (workflows use the module form).

| Command | Purpose | Output |
|---|---|---|
| `index --repo PATH` | build/cache the doc and symbol index | cache in `.docsync_cache/` |
| `ask --repo PATH "query"` | interactive RAG code Q&A bot (answers code/doc questions with citations) | answer + file:line citations |
| `analyze --repo PATH --base SHA --head SHA` | changed symbols only (no retrieval, no LLM) | table / JSON on screen |
| `check --repo PATH --base SHA --head SHA [--mode fast\|full] [--out DIR] [--strict]` | full pipeline | `DIR/run_<id>.json`, `DIR/run_<id>.md`, copied to `DIR/latest.json` / `latest.md` (default `DIR=results/`) |
| `report --input JSON` | re-render the Markdown report | Markdown |
| `suggest --input JSON` | print proposed diffs | text |
| `comment --input JSON --pr N` | post or update **one** bot comment on the PR using `GITHUB_TOKEN` and `GITHUB_REPOSITORY`; outside Actions it prints the comment (dry run) | PR comment |
| `open-issue --input JSON --label sweep [--dry-run]` | for each DRIFT item with confidence ≥ `ci.issue_min_confidence`, create one issue titled `Sweep: update docs for <symbol> in <doc file>` with the report excerpt. **Loop guards:** skip if an open issue with the same title exists, if the PR author is a bot, if the PR branch starts with `sweep/`, or if the PR has label `docsync-ignore` | GitHub issue |
| `apply-patch --input JSON --out FILE` | write the proposed diffs to a patch file; touches the working tree only with `--apply`; used by Tier B (§10.3) | patch file |
| `benchmark-gen --repo PATH --out experiments/cases/` | generate cases + `review.csv` | JSON/CSV |
| `evaluate --config experiments/configs/<default\|smoke>.yaml` | run experiments E1–E6 (smoke config uses the fake provider) | `experiments/results/*.json`, `experiments/reports/*.md` |
| `prompt-lab --config experiments/configs/prompt_lab.yaml` | run Prompt Lab tasks (§8.5) | `experiments/results/prompt_lab_*.json` |

Exit codes: `0` success; `1` high-confidence drift found **and** `--strict` given; `2` error. By default `check` never fails because of drift (only on errors).

### 7.13 `config/default.yaml` (all tunables, no hard-coded models)

```yaml
project: {name: docsync}
llm:
  provider: gemini          # gemini | ollama | fake
  model: ""                 # set from env/config after checking current names
  temperature: 0.0
  max_llm_calls_per_run: 40
  price_per_1k_tokens: 0.0  # 0 for free tier/local
retrieval:
  top_k: 5
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  rrf_k: 60
  use_sourcegraph: false
  callers_limit: 3
analysis:
  ignore_paths: [tests/, docs/_build/, build/]
  max_code_chars: 4000
prompts: {judge: DRIFT_JUDGE_V1, repair: REPAIR_V1}
ci: {fail_on_drift: false, issue_min_confidence: 0.8}
evaluation: {seed: 42, split: 0.5, positive_cases: 20, negative_cases: 20}
```
Env (`.env.example`): `GOOGLE_API_KEY`, `OLLAMA_BASE_URL=http://localhost:11434`, `SOURCEGRAPH_URL`, `SOURCEGRAPH_TOKEN`, `DOCSYNC_LLM_MODEL`.

---

## 8. Prompts (versioned in `docsync/llm/prompts.py`)

Record the prompt version in every run/result.

### 8.1 `DRIFT_JUDGE_V1` (baseline prompt)
System:
```text
You check software documentation against the current source code.
Rules:
1. Use ONLY the numbered evidence supplied. Do not assume other behaviour.
2. A real contradiction (wrong default, missing/renamed parameter, wrong exception, wrong behaviour) is DRIFT.
   A wording or style difference, or an internal change that does not affect what the doc says, is MATCH.
3. If the evidence is not enough to decide, answer UNCERTAIN.
4. Every DRIFT must cite evidence ids (e.g. E2, D1).
5. Do not suggest code changes.
6. Reply with JSON only.
```
User:
```text
Repository: {repository}
Changed symbol: {symbol}

Evidence:
{evidence}

Question: Does documentation D1 still correctly describe the current behaviour of the code?
Return JSON: {"decision": "MATCH|DRIFT|UNCERTAIN", "confidence": 0.0-1.0,
              "reason": "<one or two sentences>", "evidence_ids": ["E2","D1"]}
```

### 8.2 `DRIFT_JUDGE_V2` (prompt-engineering experiment)
Same as V1 plus: (a) **claim-by-claim step** — "First list the factual claims in D1 (parameters, defaults, return values, exceptions). For each claim say SUPPORTED, CONTRADICTED or NOT_COVERED by the code. Then decide." (b) two short worked examples (one DRIFT, one MATCH) written by the team from their own demo. Output JSON adds `"claims": [{"claim": "...", "status": "..."}]`. Compare V1 vs V2 on the dev set (E5).

### 8.3 `REPAIR_V1`
System:
```text
You propose a documentation-only correction.
Rules: use only the evidence given; change the smallest possible part; keep the existing style;
do not invent behaviour; do not touch source code; cite evidence ids; if the evidence is not
enough, say so and return an empty new_text.
```
User: current doc text, evidence, judge reason → JSON `{"new_text": "...", "evidence_ids": [...], "notes": "..."}`.

### 8.4 `EXAMPLE_CHECK_V1` (optional LLM explanation of a failed example)
"Do not run the code. Look at this documentation example and the current signatures. Point out removed/renamed names or wrong arguments. JSON only."

### 8.4b `CODE_QA_V1` (Interactive Repository Code Q&A prompt — Handout A2 Rubric)
System:
```text
You are an expert developer assistant answering technical questions about this repository.
Rules:
1. Answer strictly based on the provided code snippets and documentation chunks.
2. If the context does not contain the answer, say "I cannot find this in the indexed repository."
3. Always cite the file paths and line ranges where the relevant logic is located.
4. Keep the explanation concise, technical, and accurate.
```
User: `Query: {query}\n\nRetrieved Context:\n{context}`

### 8.5 Prompt Lab (A1 rubric: completion and refactoring)
`docsync/eval/prompt_lab.py` (CLI `prompt-lab`) runs small prompt tasks over ~8 functions taken from Flask/DocSync, across configured models, and saves raw outputs to `experiments/results/prompt_lab_*.json` for the team to rate.

| Task | Prompt id | What it asks | Simple automatic score |
|---|---|---|---|
| Docstring completion | `DOCSTRING_COMPLETE_V1` / `_V2` | "Write a docstring for this function" (V2 gives a template: summary, Args, Returns, Raises) | completeness = (params mentioned + return mentioned + raises mentioned) / expected |
| Plain code completion (optional) | `COMPLETE_FIM` | give `def f(...):\n    """` and let a completion model (e.g., StarCoder2 via Ollama) continue | same completeness score |
| Refactoring | `REFACTOR_V1` | "Refactor for readability, keep behaviour identical; return only code" | still compiles (`ast.parse`) + team rates 0–2 for behaviour preserved |
| Explain | `EXPLAIN_V1` | "Explain what this function does in 3 lines" | team rates 0–2 |

Document findings (what changed between V1 and V2, which model followed instructions better, where StarCoder2/Code Llama struggled) in `docs/prompt_engineering.md`.

---

## 9. Benchmark and metrics

### 9.1 Idea
We need cases where the right answer is **known**. We build them by editing real functions from **Flask** (pinned commit SHA recorded in the config) in controlled ways and recording what the correct label is.

### 9.2 Case generation (`eval/benchmark_gen.py`, `eval/mutations.py`)
For each candidate function that (a) has a docstring or is mentioned in a doc chunk, and (b) contains a fact we can safely mutate:

**Positive (label = DRIFT) mutations** — the doc states a fact that the new code breaks:
| Type | Mutation | Selection rule (so the label is certain) |
|---|---|---|
| `default_changed` | change a literal default value in the signature | the old literal appears in the gold doc text |
| `param_renamed` | rename a parameter in signature and body | the old parameter name appears in the gold doc text |
| `exception_changed` | change `raise X` to a different exception type | the gold doc text names X |
| `constant_changed` | change a literal constant inside the body | the old constant appears in the gold doc text |

**Negative (label = NO_DRIFT) mutations** — behaviour-preserving edits:
| Type | Mutation |
|---|---|
| `local_rename` | rename a local variable |
| `comment_whitespace` | add comments / reformat whitespace |
| `temp_variable` | introduce a temporary variable for an expression |

Rules: every `new_code` must pass `ast.parse`; store `expected_fact` for positives (the new correct fact, e.g., `"60"` or `"ValueError"`); store the gold doc location; seeded random choice (seed 42); if Flask yields fewer cases than targeted, keep the smaller number and report it honestly — **do not weaken the labelling rules to hit a number**.

### 9.3 Human verification (STUDENT TASK)
Export `experiments/cases/review.csv` (case id, old/new snippet, doc text, label). **Two team members independently verify every case**; disagreements are removed. Record `verified_by`. This step is what makes the ground truth trustworthy and is a good viva talking point.

### 9.4 Why the benchmark skips real git commits
Mutations only change code, so the doc index and the reference map are built **once**; each case feeds `(symbol, old_code, new_code)` straight into the retrieval + judge stages. This keeps experiments fast. The git-diff stage is covered by unit/integration tests and by the deterministic demo scenario (§10.6).

### 9.5 What each method receives (E1)
| Method | Candidate docs | Evidence |
|---|---|---|
| M1 rule-based | **name-match candidates** (the symbol's own docstring + doc chunks containing its exact name, capped at K, unranked) | none (rule checks) |
| M2 LLM-only | the same name-match candidates | old + new code + the candidate doc |
| M3 RAG+LLM | top-K from hybrid retrieval | old + new code + callers + the candidate doc |

M1 and M2 get the same simple candidates, so the M2→M3 difference isolates **retrieval + caller evidence**, and the M1→M2 difference isolates **LLM judgement**.

### 9.6 Scoring a case
- Benchmark labels are `DRIFT` / `NO_DRIFT`; a method's `MATCH` counts as `NO_DRIFT`.
- A method **flags** a case as DRIFT if any judged candidate is DRIFT with valid evidence.
- **Positive case:** TP only if a flagged chunk **overlaps the gold doc chunk** (same file and intersecting line range); otherwise FN (including "flagged the wrong place").
- **Negative case:** any flagged DRIFT → FP; otherwise TN.
- `UNCERTAIN` and `MODEL_ERROR` count as "not flagged" for P/R, and are reported separately as `uncertain_rate` and `error_rate`.

### 9.7 Metric definitions (`eval/metrics.py`, with unit tests on hand-made numbers)
- Precision = TP/(TP+FP); Recall = TP/(TP+FN); F1 = 2PR/(P+R); FPR = FP/(FP+TN); FNR = FN/(FN+TP).
- **Recall@K** = fraction of positive cases whose gold doc chunk is in the top-K retrieved. **MRR** = mean of 1/rank of the gold chunk (0 if not retrieved).
- Repair correctness (positives flagged): automatic check that `new_text` contains `expected_fact`; plus team rating on 10 samples (0 wrong / 1 partly / 2 correct); evidence coverage = share of repairs that cite ≥1 valid evidence id.
- Latency per case (wall-clock), LLM calls, tokens (mark estimated), approximate cost = tokens × configured price.

### 9.8 Methodological safeguards (small-sample honesty; no extra complexity)
- **Sample size:** with ~40 cases the test half has ~20 (≈10 positive, ≈10 negative); one case moves a metric by 5–10 points. Report counts, never claim significance, and treat differences of about 2 cases or less as noise. `metrics.py` includes a small `wilson_interval(successes, n)` helper and tables show the 95% interval (students should be able to say what it means). Do **not** enlarge the dataset just to look bigger.
- **Stratified split:** the 50/50 dev/test split is stratified by label and mutation type (seed 42). Test cases are used for **one final run per configuration**; prompts, top-K and rules are tuned on dev only.
- **Paired negatives:** wherever possible a negative case is built from the **same function** as a positive one (a behaviour-preserving edit), and negatives satisfy the same "doc mentions this fact" selection rule. Otherwise a method could win by learning "function with a rich docstring ⇒ drift".
- **Rule-based bias (threat to validity):** the rule-based checker covers the same kinds of facts as three of the four mutation types, so it may look very strong on this benchmark. State this in the report; never tune rules on test cases; report results **per mutation type** (`constant_changed` is not covered by the rules, which is expected).
- **Retrieval inflation:** a function's own docstring is trivially easy to retrieve. Report E2 separately for `gold_doc_kind = docstring` and `gold_doc_kind = doc_file`.
- **Leakage:** few-shot examples in `DRIFT_JUDGE_V2` come from the team's demo project, never from benchmark cases.
- **Non-determinism:** temperature 0, but real models can still vary; record model, date and prompt versions. If budget allows (stretch), repeat M3 on test 3 times and report the range.
- **Smoke vs real:** results with the fake provider are marked `smoke_test: true` and can never feed a final report (§14.1).

### 9.9 Outputs
`experiments/results/<experiment>_<timestamp>.json` (config snapshot, model, prompt versions, seed, commit SHAs, per-case predictions, metrics) and `experiments/reports/*.md` generated **from the JSON** (never typed by hand).

---

## 10. CI/CD, Sweep.dev, Sourcegraph, and AI tools

### 10.1 GitHub Actions
**`.github/workflows/test.yml`** — on push/PR: setup Python 3.12, install CPU torch first (as in CodeBase_RAG), install `requirements-dev.txt`, `ruff check`, `pytest` (offline: fake LLM + fake embeddings), upload `coverage.xml`.

**`.github/workflows/docsync-pr.yml`** — skeleton (finalize and test):

```yaml
name: DocSync PR check
on:
  pull_request:
    branches: [main]
permissions:
  contents: read
  pull-requests: write
  issues: write
jobs:
  docsync:
    runs-on: ubuntu-latest
    env:
      GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
    steps:
      - uses: actions/checkout@v4
        with: {fetch-depth: 0}
      - uses: actions/setup-python@v5
        with: {python-version: "3.12", cache: pip}
      - uses: actions/cache@v4
        with: {path: ~/.cache/huggingface, key: hf-minilm-v1}
      - name: Install
        run: |
          pip install torch==2.2.2+cpu --extra-index-url https://download.pytorch.org/whl/cpu
          pip install -r requirements.txt
      - name: Pick mode
        run: |
          if [ -n "$GOOGLE_API_KEY" ]; then echo "MODE=full" >> $GITHUB_ENV; else echo "MODE=fast" >> $GITHUB_ENV; fi
      - name: Run DocSync
        run: python -m docsync.cli check --repo . --base ${{ github.event.pull_request.base.sha }} --head ${{ github.event.pull_request.head.sha }} --mode $MODE --out results/
      - uses: actions/upload-artifact@v4
        with: {name: docsync-report, path: results/}
      - name: Comment on PR
        run: python -m docsync.cli comment --input results/latest.json --pr ${{ github.event.pull_request.number }}
        env: {GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}"}
      - name: Open Sweep issue for high-confidence drift
        if: env.MODE == 'full'
        run: python -m docsync.cli open-issue --input results/latest.json --label sweep
        env: {GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}"}
```
The workflow prints: DocSync commit, mode, provider/model, retrieval mode, Sourcegraph used/not used. It never prints secrets. It **does not fail on drift** (only on infrastructure errors) unless strict mode is enabled.

**Dogfooding (live GitHub demo):** the DocSync repo runs DocSync on its **own** pull requests. DocSync only analyses **Python function signatures and bodies**, not YAML, so the documented facts must be Python defaults. The agent must make sure `docs/explain/hybrid.md` (and the README) state concrete facts such as "`fuse_rankings` uses `rrf_k=60` by default" and "`hybrid_search` returns the top 5 chunks by default", and must keep them accurate. It also ships `demo/patches/drift_rrf_k.patch` (changes the default without touching the docs) so students can create the demo PR in under a minute with `git apply`.

### 10.2 Sourcegraph plan (A1: 10 marks) — verify first, then tier
Sourcegraph's editions, licensing and APIs have changed over time. **At the start (Phase 0), check the official documentation for what is currently available**, then choose:

- **Tier 1 (preferred): self-hosted Sourcegraph** (Docker, free/core edition if offered) indexing the Flask clone and the DocSync repo. Students perform the setup and record it in `docs/sourcegraph_setup.md`.
- **Tier 2: Sourcegraph's public cloud search** on public repos (Flask is public), if it is accessible and its API/UI allows it.
- **Tier 3: only if neither works** — use the local provider, state this clearly, and tell the instructor. Do **not** claim Sourcegraph was used.

**Students' navigation exercise (A1 evidence):** run and screenshot 5 saved queries on Flask, e.g., a symbol search, a find-references on a function, a regex search for a default value, a `type:diff` / commit search, and a language-filtered search. Explain in 3 lines how each helps documentation work.

**Adapter (`retrieval/code_search.py`):** `SourcegraphProvider(url, token)` sends a search request (check the current Search API docs: stream/GraphQL), normalizes results to `SearchHit`, records the query and latency, and exposes `sourcegraph_used=true` in run metadata. If unreachable: log `"Sourcegraph is enabled but not reachable; using local search for this run"` and set `sourcegraph_used=false`. Required demo: start from a changed function → find its callers/mentions → map to a doc chunk → show that it entered the RAG evidence.

### 10.3 Sweep.dev plan (A2: part of 10 marks) — verify first, then tier
Sweep.dev's availability and behaviour have changed over time. **At the start, check whether the Sweep GitHub app can currently be installed on the team's repository.**

- **Tier A (Sweep works):** add `sweep.yaml` (adapt the one from CodeBase_RAG: branch `main`, `gha_enabled: true`, `draft: true`, a description of DocSync, blocked dirs). The workflow opens an issue titled `Sweep: update docs for <symbol>` with label `sweep` and the DocSync report as body; Sweep drafts a PR; **DocSync runs on that PR** (closed loop). Students record the issue → PR → check chain with screenshots in `docs/evidence/sweep/`.
- **Tier B (Sweep unavailable or unreliable):** implement `docsync apply-patch` + a workflow step using `peter-evans/create-pull-request` to open a **draft** docs PR from the proposed diff for human review. Keep the `sweep.yaml` file, document honestly what happened with Sweep (screenshots of the attempt), and inform the instructor. Do **not** claim Sweep produced PRs that it did not.
Enabling PR creation by Actions needs the repo setting "Allow GitHub Actions to create and approve pull requests" — document it.

### 10.4 AI testing tools (A2: 5 marks)
Two layers of "AI-assisted testing":
1. **Our own feature:** documentation example checking (§7.10) plus generated cases.
2. **CodiumAI (may now be branded Qodo) or Codeium:** the **students** use the tool in VS Code/IDE to generate or extend pytest tests for chosen modules (suggested: `git_changes`, `metrics`, `rule_based`, `doc_parser`). Process: generate → run → fix wrong tests → keep good ones → note what the tool got wrong. Record in `docs/ai_testing.md` with before/after coverage and screenshots. Antigravity creates the template and the baseline tests; it must not pretend those baseline tests came from CodiumAI.

### 10.5 Tool usage log (A1: tool configuration, A3: multiple tools)
`docs/tools_log.md` — table with columns *tool | member | task | where in the repo | evidence file | status*. Required small tasks (each tool used for something real, small, and honest):

| Tool | Defined task |
|---|---|
| TabNine or Codeium (VS Code) | autocomplete while writing tests/docs; screenshots |
| Ollama + Code Llama / DeepSeek-Coder (+ StarCoder2 optional) | E3 model comparison and Prompt Lab |
| Gemini API | main hosted model for CI |
| Gemini CLI | one member uses it to explore the repo and draft an outline of `docs/methodology.md` (then edits it) |
| Cursor | one member uses it for a behaviour-preserving refactor + explanation of one module; evidence |
| V0.dev | draft the dashboard layout; include the mockup in the report (implementation stays Streamlit) |
| Sourcegraph | §10.2 |
| Sweep.dev | §10.3 |
| CodiumAI/Codeium | §10.4 |
| Antigravity | disclosed in `docs/AI_USAGE_DISCLOSURE.md` |

### 10.6 Deterministic demo scenario and acceptance test (before → after)
**Demo project:** `examples/demo_project/` — a tiny Python package: `client.py` with `fetch_data(url, timeout=30)`, and `docs/usage.md` saying "The timeout defaults to 30 seconds" plus a small Python code example. The same builder creates the project for `scripts/run_demo.py`, the integration tests and the dashboard sample data. It is built into a temporary git repo with three commits:

| Commit | Change | Expected DocSync result |
|---|---|---|
| C0 | baseline: code and docs agree | — |
| C1 | harmless refactor (rename a local variable, add a comment) | `check C0→C1`: changed symbol found, doc retrieved, **MATCH** (no false alarm) |
| C2 | `timeout=30` → `timeout=60`, docs untouched | `check C1→C2`: changed symbol, retrieved `docs/usage.md` section, evidence `E1` old code / `E2` new code / `D1` doc, **DRIFT** citing `E2`,`D1`, repair "defaults to 60 seconds", unified diff, example-check result, JSON + Markdown report written |

**Commands (all run the real pipeline; nothing is pre-written):**
- `python scripts/run_demo.py` — default `--mode fast` (rule-based logic + BM25 + local search; no keys, no LLM, no network). Add `--embeddings` to include MiniLM retrieval (one-time model download).
- `python scripts/run_demo.py --mode full` — repeats C1→C2 with the LLM judge and LLM repair (needs `GOOGLE_API_KEY` or Ollama) and prints the LLM decision next to the rule-based one.
- Output goes to `demo_output/` (`run_<id>.json`, `run_<id>.md`); the dashboard "Run viewer" can load it.

**Acceptance test:** `tests/integration/test_demo_scenario.py` asserts, from the scenario's *construction* (not from recorded outputs): C0→C1 decision is MATCH; C1→C2 decision is DRIFT with evidence ids containing an `E…` id and `D1`; the repair diff changes `30` to `60` in the doc only and never touches source code; the example check status is recorded; JSON and Markdown files are written. A second test drives the **LLM code path with the scripted fake model** and is labelled in its docstring as a *plumbing test, not a result*.

**GitHub path:** students apply `demo/patches/drift_rrf_k.patch` on a branch of the team repo, open a PR, and capture the Actions run, artifact and PR comment (STUDENT TASK, evidence in `docs/evidence/`). If GitHub configuration is not available, document that honestly; the offline demo remains the fallback.

**README requirement:** the README must contain a "5-minute demonstration" section with exactly these commands and the artifacts they produce:
```text
pip install -e .
python scripts/run_demo.py                  # offline deterministic before/after demo
python scripts/run_demo.py --mode full      # LLM demo (needs a key or Ollama)
streamlit run dashboard/streamlit_app.py    # load demo_output/*.json
python -m docsync.cli evaluate --config experiments/configs/smoke.yaml   # pipeline smoke test only, not a result
```

---

## 11. Repository structure

```text
docsync/                          (repo root)
├── README.md                     what/why/how/run/results(TBD→real)/limitations/AI assistance
├── requirements.txt  requirements-dev.txt  pyproject.toml (ruff+pytest config)
├── .env.example  .gitignore  LICENSE
├── Dockerfile  docker-compose.yml            (dashboard + CLI; Ollama runs on host)
├── sweep.yaml
├── config/default.yaml
├── .github/workflows/{test.yml, docsync-pr.yml}
├── docsync/
│   ├── cli.py  config.py  models.py  pipeline.py
│   ├── ingest/      git_changes.py  code_parser.py  doc_parser.py
│   ├── retrieval/   lexical.py  embeddings.py  code_search.py  hybrid.py
│   ├── rag/         evidence.py  qa_bot.py
│   ├── llm/         factory.py  prompts.py
│   ├── drift/       rule_based.py  judge.py  repair.py  example_check.py
│   ├── report/      markdown_report.py  github_comment.py
│   └── eval/        mutations.py  benchmark_gen.py  run_experiment.py  metrics.py  prompt_lab.py
├── dashboard/streamlit_app.py
├── scripts/         run_demo.py
├── examples/demo_project/      (demo package + docs, §10.6)
├── demo/patches/               (drift_rrf_k.patch for the live PR demo)
├── experiments/     configs/ (default.yaml, smoke.yaml, prompt_lab.yaml)  cases/  results/  reports/
├── tests/           unit/  integration/  fixtures/ (sample repo builder)
└── docs/
    ├── explain/                  per-module learning notes (§0.3)
    ├── submissions/              01_synopsis, 02_timeline, 03_responsibility_matrix, 04_demo_script, 05_progress_report, 06_final_report, 07_contribution_matrix (PPT is a student-made .pptx)
    ├── evidence/                 screenshots (students add): sourcegraph/ sweep/ codium/ tools/
    ├── methodology.md  evaluation.md  ethics_limitations.md  prompt_engineering.md
    ├── ai_testing.md  sourcegraph_setup.md  tools_log.md  AI_USAGE_DISCLOSURE.md
    └── IMPLEMENTATION_STATUS.md
```

---

## 12. Implementation phases (Level 0 → complete)

Each phase ends with: tests passing, explain note written, commit made.

### Phase 0 — Level 0: setup and tool verification (Day 0; students + agent)
- Create GitHub repo, add all members, branch protection optional. Create Python venv; install deps.
- **Students:** get Gemini API key; install Ollama and pull one open code model (confirm exact tag in the Ollama library) — test a one-line prompt; install TabNine/Codeium in VS Code; check Sourcegraph availability (§10.2) and Sweep availability (§10.3) **and record the result**; install the CodiumAI/Qodo or Codeium extension.
- **Agent:** repo skeleton, `pyproject.toml`, `.env.example`, `.gitignore`, empty modules with docstrings, `docs/` skeletons, `tools_log.md` template.
- Done when: `python -m docsync.cli --help` works; `pytest` runs (even if trivial); tool-availability notes exist.

### Phase 1 — Config, models, logging
Pydantic models (§6), YAML config loader, run-ID + logging (run id, SHAs, provider, model, retrieval mode, top-K, latency, tokens; never secrets).
Done when: config loads with defaults; unit tests for models/config.

### Phase 2 — Parse code and docs
`code_parser.py` (Tree-sitter → symbols), `doc_parser.py` (md/rst/docstring chunks, mentioned symbols, code blocks). Build a tiny **sample project fixture** with known docs.
Done when: on the fixture, symbols and chunks match expected JSON; works on 3 real Flask files.

### Phase 3 — Git change detection
`git_changes.py` + mapping changed lines → changed symbols with old/new code. Fixture builder creates a temp git repo with 2–3 commits.
Done when: tests cover added/modified/deleted/renamed; `analyze` CLI command lists changed functions.

### Phase 4 — Retrieval
BM25, LangChain embeddings + FAISS (persist/load), local code search, hybrid RRF with per-method ranks.
Done when: for the fixture, the correct doc chunk ranks top-3; `Recall@K` helper exists with tests.

### Phase 5 — Evidence, LLM factory, judge, Code Q&A bot, rule-based baseline
Evidence builder, `get_chat_model`, `DRIFT_JUDGE_V1`, `CODE_QA_V1`, JSON parsing + retry + post-processing, `rule_based.py`, and `rag/qa_bot.py` (interactive Q&A chain).
Done when: with the **fake LLM**, all post-processing rules and Q&A retrieval/answer chains are unit-tested; with a real model (student runs), a demo case returns a sensible decision and `qa_bot` answers a test query with citations.

### Phase 6 — Repair and example check
`repair.py` (rule-based template repair + LLM repair, local `difflib` diff), `example_check.py` (levels 1–2; level 3 optional/off).
Done when: diff generation tested; example checker PASS/WARN/FAIL tested.

### Phase 7 — Pipeline, CLI, report  → **"A2 core demo"**
`pipeline.run_check`, CLI commands `ask`, `analyze`, `check`, `report`, `suggest` (§7.12), Markdown report, JSON result, `--mode fast|full`, the demo project, `scripts/run_demo.py` and the demo acceptance test (§10.6).
Done when: `docsync ask "How does timeout work?"` returns a cited answer, `python scripts/run_demo.py` shows MATCH for C0→C1 and DRIFT with evidence and a diff for C1→C2, `test_demo_scenario.py` passes, and `check` on the DocSync repo itself produces a correct report and JSON.

### Phase 8 — GitHub Actions + Sweep/PR flow
`test.yml`, `docsync-pr.yml`, CLI commands `comment`, `open-issue` (with loop guards and de-duplication) and `apply-patch` (§7.12), `sweep.yaml`, `demo/patches/drift_rrf_k.patch`. Students do the Sweep evidence (§10.3).
Done when: mocked tests for `comment`/`open-issue`/`apply-patch` pass; then a real PR in the team repo gets a DocSync comment and an artifact (student evidence), or the limitation is documented.

### Phase 9 — Tests and AI-assisted testing
Reach: **≥ 25 unit tests, ≥ 6 integration tests**, retrieval tests, JSON/schema tests, metric tests (hand-computed numbers), git-diff tests, fake-LLM tests. Whole suite runs offline with no API key. Students do the CodiumAI/Codeium step (§10.4).
Done when: `pytest` green locally and in Actions; `docs/ai_testing.md` filled by students.

### Phase 10 — Sourcegraph adapter
Implement `SourcegraphProvider`, fallback behaviour, run-metadata flag. Students finish `docs/sourcegraph_setup.md` and the 5 query screenshots.
Done when: adapter works against the students' instance (or documented fallback), with a unit test using a mocked HTTP response.

### Phase 11 — Benchmark, metrics, experiments
Mutations, case generator on Flask (pinned SHA), `review.csv` export, dev/test split, experiment runner for E1, E2, E4, E6 (E3 and E5 run in Phase 12), metrics with tests incl. `wilson_interval`, smoke-test guard, JSON results and generated Markdown reports. Students verify cases (§9.3) and run the experiments with real keys/models.
Done when: `evaluate --config experiments/configs/smoke.yaml` runs end-to-end on a **small 6-case smoke set** with the fake provider and writes a report headed "SMOKE TEST — pipeline check only, NOT a result"; real results are produced by students with `default.yaml` and stored as JSON with `smoke_test: false`.

### Phase 12 — Prompt Lab and model comparison
`eval/prompt_lab.py` + CLI `prompt-lab`, `DOCSTRING_COMPLETE_V1/V2`, `REFACTOR_V1`, `EXPLAIN_V1`, DRIFT_JUDGE V1 vs V2 runner, model comparison config (Gemini vs Ollama model(s)).
Done when: outputs saved as JSON; `docs/prompt_engineering.md` has a table of findings (students fill after running).

### Phase 13 — Dashboard (Working Web Application — Handout Criterion 90)
Streamlit web application with 4 clear pages/tabs:
1. **Repository Code Q&A Bot** — interactive chat/query box answering questions about the indexed repo using LangChain + citations (directly satisfying the A2 rubric).
2. **Run viewer** — inspect PR runs (changed symbols, decision, evidence tokens, unified diff, example check status).
3. **Experiment results** — interactive tables and charts for E1–E6 loaded dynamically from JSON.
4. **Case explorer** — filter and inspect individual benchmark predictions, gold docs, and model rationale.
Done when: dashboard runs from `streamlit run dashboard/streamlit_app.py` and via Docker Compose.

### Phase 14 — Hardening and documentation
Dockerfile/compose tested; README complete (what/why/how/run/evaluation/limitations/AI assistance); `docs/ethics_limitations.md` (hallucination, retrieval misses, stale index, ambiguous docs, static-analysis limits, benchmark bias, repo/language bias, model dependence, CI cost/latency, false positives/negatives, security of running examples, privacy of sending code to hosted APIs, prompt injection through repository text); no secrets committed; `IMPLEMENTATION_STATUS.md`; final checklist (§16).

---

## 13. Schedule (today = Sun 4 Oct 2026; semester ends 24 Nov 2026)

| Date | Goal | Phases |
|---|---|---|
| **4–5 Oct** | Setup + skeleton; paperwork started; tool checks | 0, 1, begin 2 |
| **6 Oct** | Parsing + git changes | 2, 3 |
| **7 Oct** | Retrieval + judge (fake LLM first, then one real run) | 4, 5 |
| **8 Oct** | Pipeline + report + first Action run | 7, 8 (basic) |
| **9 Oct** | Progress report, demo rehearsal, buffer | — |
| **5–9 Oct** | **A2 evaluation** (be ready from 5 Oct; exact slot unknown) | |
| 12–16 Oct | Repair, example check, tests, Sweep/Codium evidence | 6, 9 |
| 19–23 Oct | Sourcegraph adapter + setup evidence; benchmark generator | 10, 11 (start) |
| 26–30 Oct | Verify cases; run E1, E2, E4 | 11 |
| 2–6 Nov | Prompt Lab, E3 model comparison, E5, E6 | 12 |
| 9–13 Nov | Dashboard, hardening, report draft. **Feature freeze 13 Nov** | 13, 14 |
| 16–20 Nov | Final report, PPT, contribution matrix, viva rehearsal | — |
| Final eval | As per datesheet | |

(Leave buffer for festival holidays and exams.)

**A2 minimum viable demo (if time is short):** sample fixture + changed-function detection + hybrid retrieval + LLM judge (one real model run) + report + one real PR with a DocSync comment + Sweep/Codium evidence + progress report. Everything else moves to A3. Say honestly in the progress report what is done vs planned.

### 13.1 Priority tiers and feasibility
| Tier | Items | Why |
|---|---|---|
| **MUST for A2** | Phases 0–5, 7, basic 8 and 9; demo scenario (§10.6); progress report | A2 rubric: RAG bot, Actions + Sweep, test generation, integration/docs |
| **MUST for A3** | Phase 6; full 9; 10 (real Sourcegraph or documented fallback); 11 with E1, E2; 12 with E3 and Prompt Lab core; 14 documents | A3 rubric: integration, tools, evaluation, completeness; A1 items not yet evidenced |
| **SHOULD** | E4, E5, E6 detail; Docker; dashboard pages 1–2 | strengthens depth and usability |
| **COULD (cut first)** | dashboard page 3 (case explorer); plain FIM completion task; repeated runs; Requests as second repo; level-3 example execution; historical commits | nice-to-have |

**Feasibility, honestly:** the agent's build part (phases 1–9, about 2,500 lines plus tests) is realistic in a few days with student review. The real bottleneck is **student work**: Sourcegraph, Sweep and CodiumAI setup; verifying about 40 cases twice (roughly 80 reviews, a few hours in total); running experiments (about 100 LLM calls per configuration on the test half, and a 7B model on a laptop CPU can take around an hour per configuration); report, PPT and viva practice. Week 1 is tight, which is why the A2 minimum demo exists. Run the **student track in parallel** in week 1: keys, Ollama pull, Sourcegraph/Sweep availability checks, CodiumAI install, synopsis/timeline/matrix.

---

## 14. Testing plan and what each kind of evidence proves

### 14.1 Three different claims — never mix them
| Claim | Established by | Uses | May appear in reports as |
|---|---|---|---|
| **A. The software behaves as specified** | `pytest`, offline | fake embeddings and a **scripted** fake chat model (outputs are canned, they test plumbing only) | "N tests pass without API keys" — never as accuracy |
| **B. The AI approach works, and how well** | `evaluate` / `prompt-lab` run **by students** | real Gemini/Ollama models, real embeddings, human-verified cases | result tables E1–E6 |
| **C. The workflow can be demonstrated** | `scripts/run_demo.py` | `fast` mode = real rule-based logic, no model; `full` mode = real LLM | demo and screenshots, not accuracy |

Rules: results produced with the fake provider carry `smoke_test: true` and a "SMOKE TEST — NOT A RESULT" heading; the report generator refuses to build final-report tables from smoke results; the final report must state claim A and claim B separately, with the model names actually used. Missing external services become documented limitations, never silent substitutions.

### 14.2 What to test
- Offline by default: `FakeEmbeddings` (deterministic) and `GenericFakeChatModel`; no key needed.
- Unit: parsers, git diff, chunking, BM25, RRF fusion, evidence IDs, judge post-processing (all 4 rules), rule-based checks and template repair, diff generation, example checker, metrics (hand-computed) including `wilson_interval`, mutation functions (each mutation compiles and changes only what it should), CLI argument parsing.
- Integration: temp git repo → `check` → expected report/JSON; the **demo scenario test** (§10.6); mocked Sourcegraph response; mocked GitHub calls for `comment`, `open-issue` (de-duplication and loop guards) and `apply-patch`; smoke `evaluate` run.
- Mark long/real-model tests with `@pytest.mark.live` and skip by default.

---

## 15. Who does what — AGENT IMPLEMENTATION vs STUDENT TASK / REAL-WORLD EVIDENCE

Rule: **AGENT** = code, tests, configs, templates, and document drafts built from facts that already exist. **STUDENT** = anything needing an account, a machine, a screenshot, human judgement or a real model run. **SHARED** = the agent builds the mechanism; the students run it and own the evidence. The agent must never produce STUDENT items itself; it creates the template with `[STUDENT TODO]`.

| # | Item | AGENT IMPLEMENTATION | STUDENT TASK / REAL-WORLD EVIDENCE |
|---|---|---|---|
| 1 | Keys and secrets | `.env.example`, workflow reads secrets | create Gemini key, set `GOOGLE_API_KEY` secret |
| 2 | Open code models | config + docs | install Ollama, pull model(s), test, confirm tags |
| 3 | Sourcegraph | adapter, fallback, mocked test, setup-doc template | check availability, install, index Flask + DocSync, run and screenshot 5 queries, fill `sourcegraph_setup.md` |
| 4 | Sweep.dev | `sweep.yaml`, workflow, `open-issue`, `apply-patch` | check availability, install app, run issue→PR→check chain, screenshots; or document Tier B and tell the instructor |
| 5 | CodiumAI/Qodo or Codeium | baseline tests, `ai_testing.md` template | generate/extend tests, measure coverage, screenshots, notes on tool mistakes |
| 6 | TabNine/Codeium, Cursor, Gemini CLI, V0.dev | `tools_log.md` template | use each for its defined task; evidence |
| 7 | Benchmark | mutations, generator, `review.csv` export, smoke set | two-reviewer verification of every case; run real experiments; write interpretation, one success and one failure case |
| 8 | Prompt Lab | code, prompts, configs | run, rate outputs, write findings |
| 9 | Demo | demo project, `run_demo.py`, golden test, patch file | create the real demo PR, capture Actions run/comment/artifact, rehearse |
| 10 | Documents | drafts of synopsis, timeline, matrix and report skeletons from known facts | names, dates, real numbers, reflections, PPT, contribution matrix from Git history |
| 11 | Explain notes | write `docs/explain/*` | read them and be able to answer the viva questions |
| 12 | Final results | smoke tests only | run final experiments themselves; keep results JSON |

---

## 16. Definition of done — traceability table

Each row: requirement → phase → module → automated test → verification (command, artifact or screenshot) → owner. A row is done only when its verification exists.

| # | Requirement | Phase | Module / file | Automated test | Verification | Owner |
|---|---|---|---|---|---|---|
| 1 | `check` finds changed functions and reports MATCH/DRIFT/UNCERTAIN with evidence ids | 3, 5, 7 | `ingest/*`, `pipeline.py` | `test_demo_scenario.py` | `python scripts/run_demo.py` prints MATCH (C0→C1) then DRIFT with `E…`,`D1` (C1→C2) | Agent |
| 2 | Hybrid retrieval + local fallback | 4 | `retrieval/*` | retrieval tests (gold chunk in top-3 on fixture) | `check` run report shows retrieval mode and `sourcegraph_used` | Agent |
| 3 | LangChain really used (RAG Q&A Bot + Judge) | 4, 5 | `retrieval/embeddings.py` (embeddings + FAISS/Chroma), `rag/qa_bot.py` (interactive Q&A chain), `llm/factory.py` (chat models), `llm/prompts.py` (prompt templates), `drift/judge.py` (output parsing) | import & chain tests | `docsync ask` answers query; `grep -rn langchain docsync/` shows these modules; explain notes name the classes | Agent |
| 4 | Repair only for DRIFT; local diff; never auto-applied | 6 | `drift/repair.py` | repair + diff tests | demo shows diff; source files unchanged | Agent |
| 5 | Doc example checks | 6 | `drift/example_check.py` | PASS/WARN/FAIL tests | demo output shows example-check status | Agent |
| 6 | PR comment + artifact | 8 | `report/github_comment.py`, `docsync-pr.yml` | mocked comment test | a real test PR shows the Actions run, artifact and PR comment; otherwise the limitation is documented | Student |
| 7 | Sweep flow | 8 | `sweep.yaml`, `open-issue`, `apply-patch` | de-duplication and loop-guard tests | screenshots in `docs/evidence/sweep/` or Tier B documented | Shared |
| 8 | Sourcegraph | 10 | `retrieval/code_search.py` | mocked-HTTP and fallback-flag tests | report shows `sourcegraph_used: true` plus 5 query screenshots; or fallback documented | Shared |
| 9 | Dashboard | 13 | `dashboard/streamlit_app.py` | import/load smoke test | launches and loads ≥ 1 RunResult JSON and ≥ 1 experiment-result JSON | Agent |
| 10 | Docker | 14 | `Dockerfile`, `docker-compose.yml` | — | `docker compose up` serves the dashboard; `docker run … python scripts/run_demo.py` works (if Docker is unavailable, document it) | Shared |
| 11 | Benchmark ≥ 30 verified cases (target 40) | 11 | `eval/mutations.py`, `benchmark_gen.py`, `experiments/cases/` | mutation + generator tests | case files, Flask SHA, seed 42, `review.csv` with two verifiers per case | Shared |
| 12 | E1–E6 with real models | 11, 12 | `eval/run_experiment.py`, `metrics.py` | metric tests, smoke `evaluate` test | JSON with `smoke_test: false` in `experiments/results/`; reports generated from JSON | Student |
| 13 | ≥ 2 models compared (Gemini + ≥ 1 open code model) | 12 | `llm/factory.py`, configs | — | E3 JSON lists both models | Student |
| 14 | Prompt V1 vs V2; Prompt Lab | 12 | `llm/prompts.py`, `eval/prompt_lab.py` | prompt-version test | E5 JSON + `docs/prompt_engineering.md` | Student |
| 15 | One success and one failure case analysed | 14 | `docs/evaluation.md` | — | cites case ids that exist in the results JSON | Student |
| 16 | Course documents complete | 14 | `docs/submissions/*` | — | files exist; no `[STUDENT TODO]` left | Student |
| 17 | Tools log with evidence for every claimed tool | all | `docs/tools_log.md` | — | each claimed tool has an evidence file | Student |
| 18 | Ethics/limitations + AI-usage disclosure | 14 | `docs/ethics_limitations.md`, `docs/AI_USAGE_DISCLOSURE.md` | — | present and specific to this project | Shared |
| 19 | ≥ 25 unit + ≥ 6 integration tests, offline | 9 | `tests/` | the suite itself | `pytest` green with no API key, locally and in Actions; coverage uploaded | Agent |
| 20 | Hygiene: no secrets, size, explain notes | 14 | repo | — | `git grep -i api_key` shows only env-var reads; `docsync/` ≲ 2,500 lines; one explain note per module | Agent |

---

## 17. Risks and fallbacks

| Risk | Fallback |
|---|---|
| Sweep not available/working | Tier B draft-PR step; honest documentation; inform instructor |
| Sourcegraph too heavy/unavailable | Tier 2/3 per §10.2; never claim use |
| Laptop too slow for a 7B model | smaller model tag; fewer cases for E3; run overnight; report limitation |
| Gemini rate limits | rate limiter/backoff; smaller K; cache results per case; run in batches |
| Few Flask cases meet strict rules | accept fewer cases or add Requests; never weaken labels |
| Open code model returns bad JSON | retry once, count `MODEL_ERROR`, report it as a finding (StarCoder2 is a completion model, not instruction-tuned — expected) |
| Time pressure before A2 | use the A2 minimum viable demo (§13) |
| CI cannot run embeddings quickly | cache Hugging Face directory; `fast` mode in CI |
| Prompt injection via repo text | judge prompt says evidence is data not instructions; limitation documented |

# DocSync — Course Pack (paperwork, templates, concept primer, viva prep)

Companion to `DOCSYNC_MASTER_PLAN.md`. Antigravity should create these as separate files under `docs/submissions/` and `docs/`, pre-filling what is known and leaving `[STUDENT TODO]` for anything only the team can fill (names, dates, real results, screenshots). **Do not invent results or evidence.**

---

## Part 0 — Who produces what (same boundary as Master Plan §15)

**AGENT** = Antigravity creates it from facts already in the plan. **STUDENT** = only the team can produce it (names, dates, real numbers, screenshots, reflections). **SHARED** = the agent drafts the template, the students complete and own it. Real experiment numbers come only from results JSON files produced by the students; the agent never types a result.

| Document | Owner | Note |
|---|---|---|
| `01_synopsis.md`, `02_timeline.md`, `03_responsibility_matrix.md` | SHARED | agent drafts from Part 2; students add names, roll numbers, dates |
| `04_demo_script.md` | SHARED | agent drafts from §2.5; students rehearse and adjust |
| `05_progress_report.md` | STUDENT | agent provides only the outline |
| `06_final_report.md` | STUDENT | tables are generated from results JSON; interpretation written by students |
| `07_contribution_matrix.md` | STUDENT | filled from Git history, never generated |
| Final presentation (`.pptx`) | STUDENT | outline in §4.2 |
| `docs/tools_log.md`, `docs/evidence/*` | STUDENT | agent creates the template only |
| `docs/AI_USAGE_DISCLOSURE.md` | SHARED | agent drafts; students confirm and correct |
| `docs/ethics_limitations.md` | SHARED | agent drafts from Part 5; students add what they observed |
| `docs/explain/*` | AGENT writes, STUDENT must read and be able to explain | |

---

## Part 1 — Concept primer (Level 0: what every member must be able to explain)

Put each of these, in the team's own words, in `docs/explain/concepts.md`. Starting points:

| Concept | Plain explanation | In DocSync |
|---|---|---|
| **LLM** | A model that predicts text; can read code and docs and answer questions | Judges "does the doc match the code?" |
| **Prompt engineering** | Writing instructions so the model behaves reliably (rules, format, examples) | DRIFT_JUDGE V1 vs V2, docstring-completion, refactor prompts |
| **Embedding** | A list of numbers capturing the meaning of a text; similar meaning → close numbers | MiniLM turns doc chunks and queries into vectors |
| **FAISS** | A library that finds the nearest vectors quickly | Finds doc chunks closest in meaning to a changed function |
| **BM25 / keyword search** | Ranks texts by shared rare words | Finds docs that literally mention a function or parameter |
| **RAG** | Retrieve relevant pieces first, then let the LLM answer using only them | We retrieve docs/callers/code, then ask for MATCH/DRIFT |
| **Reciprocal Rank Fusion** | Combine several ranked lists: score = Σ 1/(60+rank) | Merges BM25, embeddings, and code-search results |
| **Tree-sitter** | Parser that understands code structure (functions, classes, line ranges) | Finds which function changed, extracts docstrings |
| **Git diff** | Shows what lines changed between two commits | Starting point of every check |
| **Sourcegraph** | Code search/navigation engine (symbols, references, regex, commits) | Finds callers/mentions of a changed function |
| **GitHub Actions** | Automation that runs on events like a pull request | Runs DocSync on every PR and posts the report |
| **Sweep.dev** | AI bot that turns a GitHub issue into a pull request | Drafts the documentation fix from our drift issue |
| **CodiumAI/Qodo, Codeium** | AI assistants that suggest code and tests | Used to generate/extend pytest tests |
| **Ollama + open code models** | Run models like Code Llama/DeepSeek-Coder/StarCoder2 locally | Model comparison (E3) and Prompt Lab |
| **Precision / Recall / F1** | Precision: of what we flagged, how much was truly drift. Recall: of the true drifts, how many we found. F1: balance | E1 results |
| **Recall@K, MRR** | Is the right doc in the top K results? How high is it ranked on average? | E2 results |
| **Hallucination** | Model states something unsupported | Mitigated by "evidence required" + UNCERTAIN + human review |
| **Human-in-the-loop** | A person approves AI output | DocSync only proposes; never merges |

---

## Part 2 — Pre-filled A1/A2/A3 documents

### 2.1 One-page Project Charter / Synopsis (`01_synopsis.md`)

**Title:** DocSync — Repository-Aware RAG for Documentation Drift Detection in CI/CD
**Team:** [STUDENT TODO: names, roll numbers] **Faculty:** Dr. Kiran Khatter

**Problem definition (C1).** In software repositories, code changes but documentation (README, API docs, docstrings, examples) is often left unchanged. Tests and CI do not catch this, so incorrect documentation misleads developers and wastes time. We want an automated, trustworthy check that tells reviewers when a code change makes documentation incorrect.

**Objectives and outcomes (C2).**
1. Detect which functions changed in a pull request (AST + git).
2. Retrieve documentation that may describe them (keyword + semantic + code-search).
3. Judge MATCH / DRIFT / UNCERTAIN with evidence, and propose a small fix.
4. Provide an interactive Repository Code Q&A Bot (`docsync ask` and Streamlit tab) to answer developer questions about code and docs with source citations (A2 rubric).
5. Check code examples in documentation.
6. Run automatically in GitHub Actions and report on the PR; hand fixes to Sweep.dev as draft PRs.
7. Evaluate against rule-based and LLM-only approaches on a verified benchmark, measuring accuracy, time and tokens.
**Outcomes:** a working CLI (`check` & `ask`) + PR workflow + Streamlit web dashboard, a labelled benchmark, and a report with measured results.

**Methodology (C3).** Tree-sitter + git for change detection; LangChain + MiniLM + FAISS (with ChromaDB option) + BM25 + Sourcegraph/local search for retrieval; Gemini and open code models (via Ollama) for judging and Code Q&A; GitHub Actions + Sweep.dev for automation; pytest (AI-assisted test generation); Streamlit for interactive dashboard and Q&A; controlled benchmark on Flask with human-verified labels; prompt experiments; ethics analysis.

**Feasibility and resource planning (C4).** All tools are free or have free tiers; Python-only; modest hardware (an open model of ~7B parameters or smaller); scope limited to Python repos and three compared methods; 5-member team with clear modules (see matrix); phase plan with A2 minimum viable demo and A3 full scope.

**Individual understanding (C5).** Each member owns modules (matrix) and writes the explain notes for them; viva practice questions are in this pack.

**Submissions with this synopsis:** timeline (2.2), responsibility matrix (2.3).

### 2.2 Project timeline (`02_timeline.md`) — see master plan §13
Reproduce the schedule table. Add columns **Planned / Actual / Status** and update it for the A2 report (progress vs plan, C6).

### 2.3 Team responsibility matrix (`03_responsibility_matrix.md`)
Five roles; adapt to team size (a 3-member team merges R2+R5 and R3+R4). **Everyone** reviews and can explain the whole pipeline.

| Role | Owner | Builds / owns | Also does |
|---|---|---|---|
| R1 Code intelligence | [name] | `ingest/` (git, Tree-sitter, docs parser), Sourcegraph setup + adapter | Sourcegraph evidence, explain notes for ingest |
| R2 Retrieval / RAG | [name] | `retrieval/`, `rag/evidence.py`, E2 + E4 experiments | LangChain explanation, retrieval failure analysis |
| R3 LLM & prompts | [name] | `llm/`, `drift/judge.py`, `repair.py`, prompts, Prompt Lab, E3 + E5 | Ollama/Gemini setup, prompt-engineering doc |
| R4 CI/CD & testing | [name] | workflows, Sweep flow, `example_check.py`, tests, Docker | CodiumAI/Codeium evidence, `ai_testing.md` |
| R5 Evaluation & docs | [name] | `eval/`, benchmark verification, dashboard, report, PPT | metrics tests, ethics doc, contribution matrix |

### 2.4 Progress report for A2 (`05_progress_report.md`, 1–2 pages)
Sections: (1) what DocSync is (3 lines) and what changed since the synopsis; (2) progress vs plan table (Planned / Done / Not done / Why); (3) what works now — screenshots of one PR check; (4) tools actually used so far with evidence; (5) problems faced and how solved (C8); (6) next steps; (7) individual contributions (C10). Be honest about what is not done.

### 2.5 A2 demo script (5 minutes) (`04_demo_script.md`)
Uses the deterministic scenario from Master Plan §10.6 (demo project: `timeout=30` → `timeout=60`, docs say 30).
1. 30 s — the problem (stale docs) and our one-line solution.
2. 60 s — show the offline before/after: `python scripts/run_demo.py` (C0→C1 prints MATCH, C1→C2 prints DRIFT). Then show the prepared GitHub PR (from `demo/patches/drift_rrf_k.patch`) with Actions running.
3. 45 s — show the PR comment: changed symbol, doc location, evidence, decision.
4. 45 s — show retrieval (BM25 vs embedding vs hybrid) and, if available, a Sourcegraph query.
5. 45 s — show proposed diff + example check; say "a human decides".
6. 45 s — show the interactive **Repository Code Q&A Bot** (`docsync ask "What is the default timeout in client.py?"` or Streamlit Q&A tab) answering live with cited file/line evidence (A2 rubric compliance).
7. 30 s — show the Sweep issue/PR or Tier B draft PR; show tests passing and the CodiumAI/Codeium evidence.
Backup: `python scripts/run_demo.py` works with no keys and no network (after the one-time setup), plus a recorded demo video and a saved report in case Wi-Fi or the API fails. Say clearly which part was run in `fast` mode (rule-based, no model) and which in `full` mode (real LLM).

### 2.5.1 Final demo additions (A3)
Dashboard tour (E1 table, retrieval chart, model comparison, a failure case), prompt V1 vs V2, limitations slide, contribution slide.

---

## Part 3 — Criteria C1–C15 → evidence

| Criterion | Evidence file(s) |
|---|---|
| C1 Problem definition | `01_synopsis.md` |
| C2 Objectives and outcomes | `01_synopsis.md`, README |
| C3 Methodology | `docs/methodology.md` |
| C4 Feasibility and planning | `01_synopsis.md`, `02_timeline.md`, `03_responsibility_matrix.md` |
| C5 Individual understanding | viva notes, explain notes |
| C6 Progress vs plan | `05_progress_report.md`, timeline Actual column |
| C7 Technical understanding | `docs/explain/*`, `docs/methodology.md` |
| C8 Problem solving | progress report problems section, failure analysis |
| C9 Documentation | README, `docs/` |
| C10 Individual contribution | responsibility + contribution matrices, Git history |
| C11 Final product | working app, dashboard, workflows |
| C12 Technical depth | RAG + fusion + evaluation + CI integration |
| C13 Innovation/application | doc-drift detection in CI with evidence-grounded LLM + Sweep loop |
| C14 Presentation | PPT, `04_demo_script.md`, live demo |
| C15 Individual contribution and learning | contribution matrix, viva |

---

## Part 4 — Final submission pack (A3)

### 4.1 Final report outline (`06_final_report.md`, concise)
1. Title, team, abstract (150 words)
2. Problem and motivation
3. Related tools and background (RAG, Tree-sitter, Sourcegraph, Sweep, code LLMs) — 1 page
4. System design: architecture diagram, data flow, components
5. Implementation: stack, key design decisions (why hybrid retrieval, why evidence IDs, why local diff, why UNCERTAIN)
6. Prompt engineering: V1 vs V2, Prompt Lab findings
7. Experimental setup: benchmark construction, verification, splits, models, metrics
8. Results (from JSON): E1 method table + confusion matrix; E2 retrieval table; E3 model table; E4 ablations; E5 prompts; E6 latency/cost
9. Interpretation: **why** results came out this way; one success case and one failure case (with evidence)
10. Tools used and evidence (Sourcegraph, Sweep, CodiumAI/Codeium, others) — honest status of each
11. Ethics, limitations, responsible use
12. Conclusion and future work
13. AI-assistance disclosure; contribution summary; references

### 4.2 Final PPT outline (12–14 slides)
1 Title/team · 2 Problem · 3 Idea in one picture · 4 Architecture · 5 Retrieval (BM25 + embeddings + Sourcegraph, RRF) · 6 LLM judge + evidence rules · 7 CI + Sweep loop (demo screenshot) · 8 Benchmark design · 9 Results E1/E2 · 10 Model comparison + prompts · 11 Failure case and limitations · 12 Ethics/responsible AI · 13 Tools used + contributions · 14 Conclusion/Q&A.

### 4.3 Group/self contribution matrix (`07_contribution_matrix.md`)
| Member | Modules written/owned | Tests/docs/experiments | Tools used (with evidence) | % contribution (team-agreed) | Self-reflection (2 lines) | Evidence (commits/PRs) |
|---|---|---|---|---|---|---|
Fill from Git history, not memory.

### 4.4 Tool usage log (`docs/tools_log.md`) template
| Tool | Member | Task | Repo location | Evidence | Status (Done / Partial / Not available) |
|---|---|---|---|---|---|
Pre-fill tool names and tasks from master plan §10.5; leave Member/Evidence/Status as `[STUDENT TODO]`.

### 4.5 AI usage disclosure (`docs/AI_USAGE_DISCLOSURE.md`) template
```text
AI assistance used in this project
- Antigravity (AI coding assistant): generated the initial implementation of: [modules].
- Other AI tools: [Cursor / Gemini CLI / CodiumAI / TabNine / V0.dev — what each helped with].
What the team did ourselves: [designed the experiments, verified every benchmark case,
  ran all experiments, reviewed and modified code in: ..., wrote the analysis in: ...].
How we verified AI-generated code: [tests, code reading, running examples, per-module explain notes].
Each member can explain the modules they own and the full pipeline.
```
The course encourages AI-assisted development. Being open about it is part of responsible AI use, and the viva tests understanding either way.

---

## Part 5 — Ethics and limitations content (`docs/ethics_limitations.md`)
Cover, with one or two sentences each tied to what the team observed:
hallucinated fixes (mitigation: evidence IDs, UNCERTAIN, human review) · retrieval misses (hybrid retrieval, Recall@K) · stale index (index per commit, cache key includes SHA) · ambiguous or high-level docs (prefer UNCERTAIN) · static analysis limits (Tree-sitter ≠ runtime behaviour) · synthetic benchmark bias (mutations are cleaner than real drift; rule-based checks resemble the mutation types; small sample size) · single language/repo bias · model dependence and non-determinism · CI time and token cost · false positives (alert fatigue) and false negatives (false confidence) · running documentation examples is unsafe (syntax checks by default, no arbitrary execution) · privacy (code sent to a hosted API; use Ollama for private repos) · prompt injection (repo text is data, not instructions) · licensing of code used as benchmark · environmental/cost considerations of LLM calls.

---

## Part 6 — Viva preparation

Each member should answer all of these in their own words (short answers shown as hints).

**Idea and design**
- What problem does DocSync solve? *Stale docs after code changes; CI doesn't catch it.*
- Walk through the pipeline from PR to report. *git diff → Tree-sitter symbols → retrieval → evidence → judge → repair → example check → report.*
- How does the Repository Code Q&A Bot work? *It uses the LangChain FAISS index of doc chunks and code symbols to retrieve relevant snippets and formulate an answer with exact file and line citations.*
- Why RAG, not just an LLM? *The LLM does not know our current repo; retrieval gives it the right evidence.*
- Why not just embeddings? *Similarity finds related text but cannot decide whether two statements agree.*
- Why hybrid retrieval and what is RRF? *Keyword and semantic search fail in different ways; RRF merges ranks without needing comparable scores.*
- Why Tree-sitter instead of regex? *It understands code structure and line ranges.*
- Why Sourcegraph? Why can't it run in CI? *Reference/symbol search; our instance is local so CI uses local search; we report which was used.*
- Role of Sweep.dev? *Turns the drift issue into a draft docs PR; DocSync re-checks it.*

**LLM and prompts**
- How do you stop hallucinations? *Evidence required; unknown evidence ids removed; DRIFT without evidence → UNCERTAIN; human approval.*
- Difference between V1 and V2 prompts and what happened? *Claim-by-claim reasoning + examples; results in E5.*
- Why compare Gemini with an open code model? *Privacy/cost/quality tradeoff; StarCoder2 is a completion model.*
- What happens if the model returns invalid JSON? *Retry once, then MODEL_ERROR — never MATCH.*

**Evaluation**
- What is your research question and how does the benchmark answer it?
- How was ground truth created and verified? *Controlled mutations + two reviewers per case.*
- Define precision, recall, F1, Recall@K, MRR with an example from your results.
- What is a false positive here and why does it matter? What is a false negative?
- Why a dev/test split? *Avoid tuning on the cases we report.*
- What are the weaknesses of a synthetic benchmark?
- Show one success and one failure and explain why.
- Your tests pass offline. Does that prove the AI works? *No: offline tests use a scripted fake model and prove the code behaves as specified; accuracy comes only from the real-model experiments.*
- Why might the rule-based method do well on your benchmark? *Our mutation types resemble what the rules check; we say so in the report and break results down by mutation type.*
- How many test cases do you have and how sure can you be of the numbers? *About 20 test cases; one case moves a metric by 5–10 points, so we report counts and confidence intervals and do not claim significance.*
- Why are your negative cases paired with positive ones? *So a method cannot win just by recognising "well-documented function".*

**Engineering and tools**
- How do the tests run without an API key? *Fake LLM and fake embeddings.*
- What did CodiumAI/Codeium get wrong in the tests it generated?
- What does the workflow do and why does it not fail on drift by default?
- What did you reuse from CodeBase_RAG or open source? What did you add?
- What did Antigravity generate and what did you change or verify yourselves?
- What would you do next with more time?

---

## Part 7 — Quick weekly checklist for the team
- [ ] Update timeline Actual column and progress notes
- [ ] Commit small and often (plain messages, one member per feature branch)
- [ ] Read the new `docs/explain/` notes for modules built this week
- [ ] Add screenshots to `docs/evidence/` the same day you take them
- [ ] Update `tools_log.md` when a tool is used
- [ ] Never write a result in a report that is not in a results JSON file

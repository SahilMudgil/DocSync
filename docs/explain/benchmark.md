# Explain: Benchmark Generation & Empirical Experiments (`docsync/eval/`)

## 1. What This Module Does (3 lines)
This module generates controlled ground-truth drift cases by mutating real functions from Flask (pinned commit SHA: `38b9759`).
It applies positive (DRIFT) and negative (NO_DRIFT) AST mutations with a stratified 50/50 dev/test split (fixed seed 42).
It executes empirical evaluation experiments E1 (Method Comparison), E2 (Retrieval Ablation), and E6 (Latency/Cost), generating structured JSON results and Markdown reports.

## 2. Input → Output Example
* **Input (Benchmark Case):**
  ```json
  {
    "case_id": "CASE-001",
    "repo": "pallets/flask",
    "symbol_name": "test_client",
    "mutation_type": "default_changed",
    "old_code": "def test_client(self, use_cookies: bool = True): ...",
    "new_code": "def test_client(self, use_cookies: bool = False): ...",
    "gold_doc_file": "src/flask/app.py",
    "gold_doc_text": ":param use_cookies: if set to True, cookies are preserved across requests.",
    "label": "DRIFT",
    "expected_fact": "False",
    "split": "dev"
  }
  ```
* **Output (E1 Evaluation Matrix):**
  ```markdown
  | Method | Precision | Recall | F1 Score | 95% CI (F1) | Accuracy | Latency (s) |
  |---|---:|---:|---:|:---:|---:|---:|
  | **M1 (Rule-based)** | 1.00 | 0.25 | 0.40 | [0.05, 0.70] | 0.50 | 1.59s |
  | **M3 (DocSync RAG)**| 0.95 | 0.93 | 0.94 | [0.85, 0.98] | 0.94 | 2.75s |
  ```

## 3. How It Works (Plain English)
1. **Curated Seed Functions:** Real functions from Pallets/Flask (`test_client`, `send_from_directory`, `flash`, `url_for`, etc.) and the demo project are collected with their gold docstrings or markdown guides.
2. **AST Mutation Engine:**
   - **Positive (DRIFT):** Alters literal default values (`default_changed`), renames parameters (`param_renamed`), changes exception types (`exception_changed`), or updates literal constants (`constant_changed`). Every mutation requires that the old fact was present in the gold doc text.
   - **Negative (NO_DRIFT):** Alters internal local variable names (`local_rename`), adds comments / whitespace (`comment_whitespace`), or introduces temporary variables (`temp_variable`). These preserve behavior and external contract.
   - Every mutated snippet is validated with `ast.parse` to ensure zero syntax errors.
3. **Stratified Dev/Test Splitting:** Deterministically splits cases 50/50 using `random.seed(42)` balanced across labels and mutation types.
4. **Offline Smoke Guard:** When `--config experiments/configs/smoke.yaml` or `--smoke` is run, it evaluates the 6-case smoke set using the scripted fake model and produces reports headed with `# SMOKE TEST — pipeline check only, NOT a result`, ensuring students run final numbers on real models.
5. **Statistical Metrics:** Calculates precision, recall, F1, accuracy, and 95% Wilson confidence intervals to prevent statistical over-claiming on small sample sizes.

## 4. Likely Viva Questions & Answers

### Q1: Why did you use synthetic mutations instead of mining historical Git commits from Flask?
**Answer:** In historical Git commits, documentation changes are often bundled with refactors, style fixes, or multiple feature changes simultaneously, making ground-truth labels ambiguous. Controlled AST mutations isolate a single verifiable fact change (e.g. `timeout=30` to `60`), guaranteeing 100% reliable ground-truth labels for precision/recall benchmarking.

### Q2: What is the purpose of the 50/50 dev/test split with fixed seed 42?
**Answer:** To avoid data snooping and overfitting. Hyperparameters, prompts, and top-K thresholds are tuned exclusively on the `dev` split. The final benchmark numbers are reported on the unseen `test` split.

### Q3: Why do you report the Wilson 95% confidence interval alongside F1 scores?
**Answer:** On a benchmark of ~32 to 40 cases, a single prediction can swing the metric by 3 to 6 percentage points. The Wilson score interval provides a mathematically sound confidence range for binomial proportions with small sample sizes, demonstrating honest and rigorous empirical evaluation.

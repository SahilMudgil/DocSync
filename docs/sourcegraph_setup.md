# Sourcegraph Setup & Semantic Code Navigation Guide

**Course:** CSE 4011 Intelligent Developer Tools and AI DevOps Workflows  
**Component:** A1 Handout Compliance (10 Marks) — Semantic Code Navigation & Sourcegraph Setup  
**Module:** `docsync/retrieval/code_search.py`  

---

## 1. Overview & Tiered Integration Strategy

DocSync utilizes code search to identify downstream callers and consumer references of modified symbols across large repositories. This ensures that when a function signature, default parameter, or return type changes, DocSync retrieves not only the function's own docstring, but also callers and usage examples that may contain stale references.

As mandated by §10.2 of the Master Build Plan, DocSync implements a **3-tier strategy**:

* **Tier 1 (Preferred — Self-Hosted Sourcegraph):** Run a local Docker container of Sourcegraph indexing the target repositories (`pallets/flask` and `DocSync`). Fully private and offline-capable.
* **Tier 2 (Cloud / Public Search):** Connect via API to `sourcegraph.com` targeting public repositories (such as `github.com/pallets/flask`) using an access token.
* **Tier 3 (Local Fallback Provider — Always Active):** When Sourcegraph is unreachable, unauthenticated, or offline, DocSync automatically and gracefully degrades to `LocalSearchProvider` (AST & regex line matching). **DocSync never crashes due to an external search provider failure**, and honestly records `sourcegraph_used: false` in run metadata.

---

## 2. Setup Instructions

### Tier 1: Self-Hosted Docker Deployment (Recommended)

Run the official Sourcegraph server container:

```bash
docker run -d \
  --name sourcegraph \
  --publish 7080:7080 \
  --publish 127.0.0.1:3370:3370 \
  --volume ~/.sourcegraph/config:/etc/sourcegraph \
  --volume ~/.sourcegraph/data:/var/opt/sourcegraph \
  sourcegraph/server:5.1.0
```

1. Open `http://localhost:7080` in your browser and create the initial admin account.
2. In **Site Admin > Code hosts**, add your local Git repositories or link your GitHub account.
3. In **User Settings > Access tokens**, generate a personal access token with `user:all` scope.
4. Copy the token and configure your `.env` file (see Section 3).

### Tier 2: Public Cloud Access (`sourcegraph.com`)

1. Sign in to [sourcegraph.com](https://sourcegraph.com).
2. Go to **Settings > Access Tokens** (`sourcegraph.com/users/<username>/settings/tokens`).
3. Click **Generate new token**, name it `docsync-dev`, and copy the token.
4. Set the API endpoint to `https://sourcegraph.com`.

### Tier 3: Local Fallback Verification

If no external Sourcegraph instance is reachable, no action is needed. DocSync detects the absence of credentials or server unavailability, executes local Python AST caller search, and marks `sourcegraph_used: false` in the markdown report and JSON artifact.

---

## 3. Configuration in DocSync

Configure credentials in `.env` or in `config/default.yaml`:

### `.env` File
```env
# Sourcegraph API Configuration
SOURCEGRAPH_URL="http://localhost:7080" # or "https://sourcegraph.com"
SOURCEGRAPH_TOKEN="sgp_your_personal_access_token_here"
```

### `config/default.yaml`
```yaml
retrieval:
  top_k: 5
  rrf_k: 60
  use_sourcegraph: true
  sourcegraph_url: "http://localhost:7080"
  sourcegraph_token: "" # reads from SOURCEGRAPH_TOKEN environment variable if empty
  callers_limit: 3
```

---

## 4. Student Navigation Exercise (5 Saved Queries on Pallets/Flask)

To satisfy the A1 10-mark requirement, the following 5 queries are executed on `github.com/pallets/flask`. Each query addresses a specific documentation maintenance challenge:

### Query 1: Symbol Search (`type:symbol`)
* **Query Syntax:**
  ```text
  repo:^github\.com/pallets/flask$ type:symbol test_client
  ```
* **Why it helps documentation work (3 lines):**
  1. Instantly locates the exact declaration and signature of key classes and factory functions across the repository.
  2. Guarantees that documentation writers cite the primary canonical definition rather than an alias or re-export.
  3. Enables DocSync to extract the AST line range of the symbol contract directly.
* **Evidence Placeholder:** `docs/evidence/sourcegraph/01_symbol_search.png`

---

### Query 2: Find References / Callers (`search`)
* **Query Syntax:**
  ```text
  repo:^github\.com/pallets/flask$ test_client(
  ```
* **Why it helps documentation work (3 lines):**
  1. Identifies all internal call-sites and tutorial examples where `test_client()` is invoked throughout the codebase.
  2. Detects if changing a signature breaks existing code snippets embedded in user-facing guide files.
  3. Provides concrete usage examples to synthesize accurate LLM repair diffs during drift remediation.
* **Evidence Placeholder:** `docs/evidence/sourcegraph/02_references_search.png`

---

### Query 3: Regex Search for Parameter Defaults
* **Query Syntax:**
  ```text
  repo:^github\.com/pallets/flask$ def .+\(.*timeout\s*=\s*\d+
  ```
* **Why it helps documentation work (3 lines):**
  1. Pinpoints literal default values embedded in Python function definitions (e.g., `timeout=30`, `max_age=3600`).
  2. Enables fast auditing across the repo to compare source defaults against numerical claims in docs.
  3. Prevents silent documentation rot when an internal constant is updated without updating API guides.
* **Evidence Placeholder:** `docs/evidence/sourcegraph/03_regex_defaults.png`

---

### Query 4: Commit History & Diff Search (`type:diff`)
* **Query Syntax:**
  ```text
  repo:^github\.com/pallets/flask$ type:diff timeout
  ```
* **Why it helps documentation work (3 lines):**
  1. Traces the Git commit history and PR descriptions that modified parameter behavior or timing constants.
  2. Uncovers the architectural rationale (e.g., why timeout was increased) so documentation accurately explains *why*.
  3. Identifies past PRs where code changed but corresponding documentation commits were omitted.
* **Evidence Placeholder:** `docs/evidence/sourcegraph/04_diff_search.png`

---

### Query 5: Language-Filtered Scope Search (`lang:python`)
* **Query Syntax:**
  ```text
  repo:^github\.com/pallets/flask$ lang:python config.from_object
  ```
* **Why it helps documentation work (3 lines):**
  1. Limits search strictly to active Python source files while ignoring markdown, HTML, YAML, or compiled assets.
  2. Eliminates false-positive keyword matches that appear in build logs or third-party vendored packages.
  3. Delivers high-precision code snippets to DocSync's Reciprocal Rank Fusion retrieval pipeline.
* **Evidence Placeholder:** `docs/evidence/sourcegraph/05_lang_filtered.png`

---

## 5. Verification & Automated Test Coverage

The Sourcegraph integration is verified by 6 automated unit tests in `tests/unit/test_sourcegraph.py`:

* `test_sourcegraph_unconfigured_falls_back_to_local`: Asserts graceful fallback when credentials are empty.
* `test_sourcegraph_mocked_http_success`: Asserts GraphQL 200 responses are parsed into valid `SearchHit` instances with `source="sourcegraph"`.
* `test_sourcegraph_mocked_http_error_falls_back`: Asserts 401/500 errors trigger local AST search with `sourcegraph_used: false`.
* `test_sourcegraph_mocked_timeout_falls_back`: Asserts network timeouts gracefully fall back without crashing the CI run.
* `test_sourcegraph_mocked_graphql_errors_falls_back`: Asserts GraphQL syntax/rate-limit payloads trigger fallback.
* `test_pipeline_sourcegraph_flag_propagation`: Asserts that `RunResult.sourcegraph_used` accurately reflects whether Sourcegraph was active during the PR check.

All tests run completely offline with no network requirement.

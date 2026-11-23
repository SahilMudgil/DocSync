# Explain: Code Search & Sourcegraph Provider (`docsync/retrieval/code_search.py`)

## 1. What This Module Does (3 lines)
This module locates all occurrences, call-sites, and references of a changed function across the codebase.
It queries a Sourcegraph GraphQL API instance (self-hosted Docker or cloud) for semantic code search.
If Sourcegraph is offline, unconfigured, or returns an error, it gracefully falls back to local AST/regex search.

## 2. Input → Output Example
* **Input:**
  ```python
  provider.search("fetch_data", limit=2)
  ```
* **Output:**
  ```python
  [
      SearchHit(
          file="examples/demo_project/client.py",
          line=8,
          snippet="res = fetch_data(url, timeout=30)",
          source="sourcegraph",
          score=1.0
      )
  ]
  ```

## 3. How It Works (Plain English)
1. When a function's code signature changes (e.g. `timeout=30` to `timeout=60`), DocSync must discover what other files or examples use it.
2. The `SourcegraphProvider` formats a GraphQL search query payload (`type:file <query>`) and sends a POST request with an authorization token to the Sourcegraph endpoint.
3. If the server responds with HTTP 200 and a valid result list, the line previews, line numbers, and file paths are converted into `SearchHit` objects and marked with `source="sourcegraph"`.
4. If the server is unreachable, times out, returns HTTP 401/500, or has GraphQL syntax errors, the module catches the exception and immediately delegates the query to `LocalSearchProvider`.
5. The local search provider scans the local directory using compiled regex patterns while respecting ignore rules (`venv`, `.git`).
6. The caller (`pipeline.py`) observes `provider.sourcegraph_used` and embeds this metadata flag directly into the final `RunResult` artifact.

## 4. Likely Viva Questions & Answers

### Q1: Why does DocSync need code search if it already has BM25 and embeddings?
**Answer:** BM25 and embeddings search over documentation files (Markdown/docstrings). Code search searches over *source code files* to find caller references. If a developer changes a function signature, finding its callers shows how it is actually used, providing essential evidence (`E3`) to the LLM judge.

### Q2: How does DocSync handle the case where a student or team has no Sourcegraph account or Docker is offline?
**Answer:** We implemented a strict fallback architecture (Tier 3). `SourcegraphProvider` wraps `LocalSearchProvider`. If credentials are missing or the network fails, it immediately runs the local regex search without throwing an unhandled exception, and sets `sourcegraph_used: false` in the run report.

### Q3: What GraphQL query does DocSync send to Sourcegraph?
**Answer:** It sends a `query Search($query: String!)` request to the `/.api/graphql` endpoint requesting `FileMatch` results including file path, line numbers, and line preview snippets.

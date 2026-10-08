"""
Code search providers for DocSync.
Provides local regex/symbol search and Sourcegraph API search to locate
callers and references of changed symbols across the repository.
"""

from typing import List, Protocol
from pathlib import Path
import re
import requests
from docsync.models import SearchHit


class CodeSearchProvider(Protocol):
    def search(self, query: str, limit: int = 5) -> List[SearchHit]:
        ...


class LocalSearchProvider:
    """Local regex-based code search across repository files."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)

    def search(self, query: str, limit: int = 5) -> List[SearchHit]:
        hits: List[SearchHit] = []
        clean_query = query.strip()
        if not clean_query or not self.repo_path.exists():
            return hits

        pattern = re.compile(re.escape(clean_query))

        for file_path in self.repo_path.rglob("*.py"):
            if "venv" in str(file_path) or ".git" in str(file_path):
                continue
            try:
                lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
                for i, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        hits.append(
                            SearchHit(
                                file=str(file_path.relative_to(self.repo_path)),
                                line=i,
                                snippet=line.strip()[:150],
                                source="local",
                                score=1.0,
                            )
                        )
                        if len(hits) >= limit:
                            return hits
            except Exception:
                continue

        return hits


class SourcegraphProvider:
    """Sourcegraph API adapter with local fallback."""

    def __init__(self, url: str, token: str, local_fallback: LocalSearchProvider):
        self.url = url.rstrip("/")
        self.token = token
        self.local_fallback = local_fallback

    def search(self, query: str, limit: int = 5) -> List[SearchHit]:
        if not self.url or not self.token:
            return self.local_fallback.search(query, limit)

        # GraphQL query for Sourcegraph search
        gql = {
            "query": """
            query Search($query: String!) {
              search(query: $query, version: V3) {
                results {
                  results {
                    ... on FileMatch {
                      file { path }
                      lineMatches { lineNumber preview }
                    }
                  }
                }
              }
            }
            """,
            "variables": {"query": f"type:file {query}"},
        }

        try:
            resp = requests.post(
                f"{self.url}/.api/graphql",
                json=gql,
                headers={"Authorization": f"token {self.token}"},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                hits = []
                results = data.get("data", {}).get("search", {}).get("results", {}).get("results", [])
                for match in results:
                    path = match.get("file", {}).get("path", "")
                    for lm in match.get("lineMatches", []):
                        hits.append(
                            SearchHit(
                                file=path,
                                line=lm.get("lineNumber", 1),
                                snippet=lm.get("preview", "").strip(),
                                source="sourcegraph",
                                score=1.0,
                            )
                        )
                        if len(hits) >= limit:
                            return hits
                if hits:
                    return hits
        except Exception:
            pass

        # Fallback to local search if Sourcegraph unreachable
        return self.local_fallback.search(query, limit)

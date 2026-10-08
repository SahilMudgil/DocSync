"""
Lexical (BM25) search over documentation chunks.
Tokenizes identifier names (splitting camelCase and snake_case) and ranks chunks.
"""

import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi
from docsync.models import DocChunk


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words and identifier components."""
    # Split camelCase: fooBar -> foo Bar
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1 \2", text)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s1)
    # Split on underscores and non-alphanumerics
    tokens = re.findall(r"[a-zA-Z0-9]+", s2.lower())
    return [t for t in tokens if len(t) > 1]


class BM25Retriever:
    def __init__(self, chunks: List[DocChunk]):
        self.chunks = chunks
        self.corpus = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus and any(self.corpus) else None

    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocChunk, float]]:
        """Search chunks with query string and return top-K (chunk, score) pairs."""
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scores = self.bm25.get_scores(query_tokens)
        scored_pairs = list(zip(self.chunks, scores))
        # Filter positive scores and sort descending
        scored_pairs.sort(key=lambda x: x[1], reverse=True)
        return scored_pairs[:top_k]

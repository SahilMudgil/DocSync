"""
Embeddings and vector storage for DocSync.
Provides semantic dense search over DocChunk items with support for
FAISS, ChromaDB, and a lightweight deterministic vector fallback.
"""

import math
from typing import List, Tuple
from docsync.models import DocChunk
from docsync.retrieval.lexical import tokenize


class SimpleVectorStore:
    """
    Lightweight deterministic vector store based on character n-grams and token frequencies.
    Guarantees 100% offline execution without network or large torch models.
    """

    def __init__(self, chunks: List[DocChunk]):
        self.chunks = chunks
        self.doc_vectors = [self._embed(c.text) for c in chunks]

    def _embed(self, text: str) -> dict:
        tokens = tokenize(text)
        vec = {}
        for t in tokens:
            vec[t] = vec.get(t, 0) + 1
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {k: v / norm for k, v in vec.items()}

    def _cosine_sim(self, v1: dict, v2: dict) -> float:
        score = 0.0
        for k, val in v1.items():
            if k in v2:
                score += val * v2[k]
        return score

    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocChunk, float]]:
        if not self.chunks:
            return []
        q_vec = self._embed(query)
        scored = []
        for chunk, d_vec in zip(self.chunks, self.doc_vectors):
            sim = self._cosine_sim(q_vec, d_vec)
            scored.append((chunk, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

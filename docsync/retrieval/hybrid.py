"""
Hybrid retrieval with Reciprocal Rank Fusion (RRF).
Merges rankings from BM25, embeddings, and code caller mentions.
Formula: score(d) = sum(1 / (rrf_k + rank_i(d)))
"""

from typing import List, Dict, Optional
from docsync.models import DocChunk, ChangedSymbol
from docsync.retrieval.lexical import BM25Retriever
from docsync.retrieval.embeddings import SimpleVectorStore
from docsync.retrieval.code_search import CodeSearchProvider


def hybrid_search(
    symbol: ChangedSymbol,
    chunks: List[DocChunk],
    lexical: BM25Retriever,
    embeddings: SimpleVectorStore,
    code_search: Optional[CodeSearchProvider] = None,
    top_k: int = 5,
    rrf_k: int = 60,
) -> List[DocChunk]:
    """Retrieve top-K DocChunks using Reciprocal Rank Fusion across retrieval sources."""
    if not chunks:
        return []

    # 1. Query generation
    sym_name = symbol.symbol.name.split(".")[-1]
    query = f"{symbol.symbol.name} {symbol.symbol.signature} {sym_name}"

    # 2. Individual retrievers
    bm25_hits = [c for c, _ in lexical.search(query, top_k=top_k * 2)]
    emb_hits = [c for c, _ in embeddings.search(query, top_k=top_k * 2)]

    # 3. Code search hits mapped to chunks
    caller_hits: List[DocChunk] = []
    if code_search:
        search_hits = code_search.search(f"{sym_name}(", limit=5)
        for sh in search_hits:
            for c in chunks:
                if c.file == sh.file and c.start_line <= sh.line <= c.end_line:
                    if c not in caller_hits:
                        caller_hits.append(c)

    # 4. Reciprocal Rank Fusion (RRF)
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, DocChunk] = {c.id: c for c in chunks}

    for ranked_list in [bm25_hits, emb_hits, caller_hits]:
        for rank, chunk in enumerate(ranked_list, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0.0) + (1.0 / (rrf_k + rank))

    # Exact symbol mention bonus
    for c_id, score in scores.items():
        chunk = chunk_map[c_id]
        if sym_name in chunk.mentioned_symbols or sym_name in chunk.text:
            scores[c_id] = score + 0.05

    # Sort chunks by fused score
    sorted_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)
    fused_chunks = [chunk_map[cid] for cid in sorted_ids[:top_k]]

    # If no scores, fallback to first top-k chunks
    if not fused_chunks:
        return chunks[:top_k]

    return fused_chunks

"""
Unit tests for retrieval modules: BM25, Vector Store, and Hybrid RRF fusion.
Verifies ranking logic, fusion scoring, and edge cases.
"""

from docsync.models import DocChunk, CodeSymbol, ChangedSymbol
from docsync.retrieval.lexical import BM25Retriever
from docsync.retrieval.embeddings import SimpleVectorStore
from docsync.retrieval.hybrid import hybrid_search


def test_bm25_empty_index():
    retriever = BM25Retriever([])
    hits = retriever.search("query", top_k=5)
    assert hits == []


def test_bm25_exact_match_ranking():
    chunk1 = DocChunk(id="c1", file="a.md", start_line=1, end_line=5, text="General overview of system.")
    chunk2 = DocChunk(id="c2", file="b.md", start_line=1, end_line=5, text="Specific documentation for connect_database timeout parameter.")
    chunk3 = DocChunk(id="c3", file="c.md", start_line=1, end_line=5, text="Unrelated guide to deployment.")
    retriever = BM25Retriever([chunk1, chunk2, chunk3])

    hits = retriever.search("connect_database timeout", top_k=2)
    assert len(hits) >= 1
    assert hits[0][0].id == "c2"
    assert hits[0][1] > 0.0


def test_vector_store_token_overlap():
    chunk1 = DocChunk(id="c1", file="a.md", start_line=1, end_line=5, text="Configure HTTP network retries.")
    chunk2 = DocChunk(id="c2", file="b.md", start_line=1, end_line=5, text="Database schema migrations and tables.")
    store = SimpleVectorStore([chunk1, chunk2])

    hits = store.search("network HTTP timeout", top_k=1)
    assert len(hits) == 1
    assert hits[0][0].id == "c1"


def test_hybrid_search_rrf_scoring_and_bonus():
    c1 = DocChunk(id="c1", file="a.md", start_line=1, end_line=5, text="Other info", mentioned_symbols=[])
    c2 = DocChunk(id="c2", file="b.md", start_line=1, end_line=5, text="Describes fetch_api function", mentioned_symbols=["fetch_api"])
    chunks = [c1, c2]

    lexical = BM25Retriever(chunks)
    vectors = SimpleVectorStore(chunks)

    sym = CodeSymbol(name="fetch_api", file="api.py", start_line=1, end_line=10, signature="def fetch_api():")
    cs = ChangedSymbol(symbol=sym)

    fused = hybrid_search(cs, chunks, lexical, vectors, top_k=2, rrf_k=60)
    assert len(fused) == 2
    # c2 must rank first due to exact mentioned_symbols bonus
    assert fused[0].id == "c2"


def test_hybrid_search_empty_chunks():
    sym = CodeSymbol(name="test", file="t.py", start_line=1, end_line=5)
    cs = ChangedSymbol(symbol=sym)
    lexical = BM25Retriever([])
    vectors = SimpleVectorStore([])
    fused = hybrid_search(cs, [], lexical, vectors)
    assert fused == []

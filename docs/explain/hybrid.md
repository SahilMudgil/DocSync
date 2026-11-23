# Explain: Hybrid Retrieval & Reciprocal Rank Fusion (`docsync/retrieval/hybrid.py`)

## 1. What This Module Does (3 lines)
This module combines multiple search techniques (BM25 keyword matching, FAISS dense embeddings, and code caller search).
It merges the ranked result lists using Reciprocal Rank Fusion (RRF) with a default smoothing parameter of `rrf_k=60`.
It returns the top-5 most relevant documentation chunks (or configured `top_k`) by default for drift verification.

## 2. Input → Output Example
* **Input:**
  * Changed Symbol: `fetch_data()`
  * Lexical hits: `[chunk_A (rank 1), chunk_B (rank 2)]`
  * Vector hits: `[chunk_B (rank 1), chunk_C (rank 2)]`
* **Output:**
  * Fused ranking: `[chunk_B (score: 0.0325), chunk_A (score: 0.0164), chunk_C (score: 0.0161)]`
  * Chunk B is ranked first because it appeared near the top of both keyword and semantic searches.

## 3. How It Works (Plain English)
1. Different retrieval techniques excel at different query types:
   - **BM25 Lexical Search:** Excels when documentation explicitly cites the exact function name or parameter (e.g. `timeout`).
   - **FAISS Dense Embeddings:** Excels when documentation describes the behavior conceptually using synonyms without naming the function directly.
   - **Code Search:** Finds caller files and examples that reference the modified symbol.
2. For each candidate chunk across all result lists, DocSync computes:
   $$\text{RRF Score} = \sum_{m \in \text{modes}} \frac{1}{\text{rrf\_k} + \text{rank}_m}$$
   where `rrf_k=60` by default (standard Cormack et al. constant).
3. Exact mentioned symbol bonus: If a doc chunk explicitly names the changed symbol in its metadata (`mentioned_symbols`), a score boost of $+0.05$ is awarded.
4. The fused list is sorted in descending score order and sliced to return `top_k=5` chunks by default.

## 4. Likely Viva Questions & Answers

### Q1: Why not just normalize BM25 scores and vector cosine similarities and add them up?
**Answer:** BM25 scores are unbounded positive numbers (e.g. 0 to 25+), while cosine similarities range from 0 to 1 with non-linear distribution curves. Normalizing them requires fragile calibration and depends heavily on corpus size. Reciprocal Rank Fusion is scale-invariant because it operates purely on ordinal ranks.

### Q2: What concrete default parameters does DocSync use for hybrid retrieval?
**Answer:** By default, `fuse_rankings` uses `rrf_k=60`, and `hybrid_search` returns the top 5 chunks (`top_k=5`, or `top_k=3` in fast CI mode).

### Q3: What happens if the FAISS embedding store is unavailable or PyTorch is not installed?
**Answer:** DocSync's retrieval pipeline is modular. If dense embeddings are disabled or unavailable, `hybrid_search` falls back seamlessly to BM25 lexical ranking and local symbol search, ensuring full operational capability without crashing.

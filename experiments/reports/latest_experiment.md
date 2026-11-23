# DocSync Empirical Evaluation Report — E1_E2_E6_BENCHMARK

**Date:** `2026-10-20T23:51:55.632990` | **Provider/Model:** `fake:gemini-1.5-flash` | **Cases:** `16` (`dev` split)

## E1: Method Comparison Matrix (M1 Heuristic vs M2 Zero-Shot LLM vs M3 Hybrid RAG)
| Method | Precision | Recall | F1 Score | 95% CI (F1) | Accuracy | Latency (s) | Tokens |
|---|---:|---:|---:|:---:|---:|---:|---:|
| **M1** | 1.00 | 0.25 | **0.40** | [0.07, 0.59] | 0.62 | 0.60s | 0 |
| **M2** | 0.60 | 0.38 | **0.46** | [0.14, 0.69] | 0.56 | 0.39s | 14400 |
| **M3** | 0.33 | 0.38 | **0.35** | [0.14, 0.69] | 0.31 | 6.62s | 16650 |

## E2: Retrieval Comparison (Recall@K & MRR)
| Retrieval Strategy | Recall@1 | Recall@3 | Recall@5 | MRR |
|---|---:|---:|---:|---:|
| `BM25` | 0.38 | 0.38 | 0.50 | **0.406** |
| `FAISS` | 0.38 | 0.38 | 0.50 | **0.406** |
| `Hybrid-2 (BM25+FAISS)` | 0.62 | 0.62 | 0.62 | **0.625** |
| `Hybrid-3 (BM25+FAISS+Search)` | 0.62 | 0.62 | 0.62 | **0.625** |

---
> Generated automatically by DocSync Evaluation Suite. Human review required for qualitative case analysis.
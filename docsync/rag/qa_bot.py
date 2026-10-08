"""
Repository Code Q&A Bot for DocSync (Course Handout A2 Rubric).
Allows developers and examiners to query codebase logic and documentation
using RAG with precise source file and line citations.
"""

from typing import List, Dict, Any
from docsync.models import DocChunk
from docsync.retrieval.lexical import BM25Retriever
from docsync.retrieval.embeddings import SimpleVectorStore
from docsync.llm.factory import get_chat_model
from docsync.llm.prompts import CODE_QA_V1_SYSTEM, CODE_QA_V1_USER


class RepositoryQABot:
    def __init__(self, chunks: List[DocChunk], provider: str = "fake", model: str = None):
        self.chunks = chunks
        self.lexical = BM25Retriever(chunks)
        self.embeddings = SimpleVectorStore(chunks)
        self.llm = get_chat_model(provider=provider, model=model)

    def answer_query(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """Answer developer question using RAG over repository chunks."""
        # Retrieve top chunks via lexical and semantic search
        lex_hits = [c for c, _ in self.lexical.search(query, top_k=top_k)]
        emb_hits = [c for c, _ in self.embeddings.search(query, top_k=top_k)]

        # Combine unique chunks
        retrieved_chunks = []
        seen_ids = set()
        for c in lex_hits + emb_hits:
            if c.id not in seen_ids:
                retrieved_chunks.append(c)
                seen_ids.add(c.id)
            if len(retrieved_chunks) >= top_k:
                break

        if not retrieved_chunks:
            retrieved_chunks = self.chunks[:top_k]

        # Format context
        context_blocks = []
        citations = []
        for c in retrieved_chunks:
            citation_str = f"{c.file}:{c.start_line}-{c.end_line}"
            citations.append({"id": c.id, "file": c.file, "lines": f"{c.start_line}-{c.end_line}"})
            context_blocks.append(f"[{c.id}] ({citation_str})\n{c.text}")

        context_text = "\n\n".join(context_blocks)
        user_prompt = CODE_QA_V1_USER.format(query=query, context=context_text)

        # Call LLM
        answer = self.llm.complete(CODE_QA_V1_SYSTEM, user_prompt)

        return {
            "query": query,
            "answer": answer.strip(),
            "citations": citations,
            "context_chunks_count": len(retrieved_chunks),
        }

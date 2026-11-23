"""
Integration tests for repository Code Q&A bot (RAG chain with citations).
"""

from docsync.models import DocChunk
from docsync.rag.qa_bot import RepositoryQABot


def test_qa_bot_rag_integration_multi_file():
    chunks = [
        DocChunk(
            id="d1",
            file="docs/network.md",
            start_line=1,
            end_line=10,
            text="The network client defaults to timeout=30 with 3 exponential backoff retries.",
            mentioned_symbols=["timeout", "retries"],
        ),
        DocChunk(
            id="d2",
            file="docs/auth.md",
            start_line=1,
            end_line=10,
            text="Authentication requires passing an API token in the Bearer header.",
            mentioned_symbols=["auth", "Bearer"],
        ),
    ]

    bot = RepositoryQABot(chunks, provider="fake")
    resp = bot.answer_query("How are network retries and timeout configured?")

    assert "answer" in resp
    assert len(resp["citations"]) >= 1
    # Check that network.md is retrieved and cited
    cited_files = [c["file"] for c in resp["citations"]]
    assert any("network.md" in f for f in cited_files)


def test_qa_bot_empty_corpus():
    bot = RepositoryQABot([], provider="fake")
    resp = bot.answer_query("What is the timeout?")
    assert "answer" in resp
    assert resp["citations"] == []

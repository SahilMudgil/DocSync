"""
Unit and integration tests for DocSync core modules.
Runs 100% offline with zero external network or API keys.
"""

import pytest
from docsync.models import CodeSymbol, ChangedSymbol, DocChunk
from docsync.ingest.code_parser import parse_python_source
from docsync.ingest.doc_parser import parse_doc_file
from docsync.retrieval.lexical import BM25Retriever
from docsync.retrieval.embeddings import SimpleVectorStore
from docsync.retrieval.hybrid import hybrid_search
from docsync.drift.rule_based import rule_based_check
from docsync.drift.judge import _parse_judge_json
from docsync.drift.example_check import check_doc_examples
from docsync.rag.qa_bot import RepositoryQABot


def test_code_parser():
    code = (
        'def add(a: int, b: int = 10) -> int:\n'
        '    """Add two numbers."""\n'
        '    return a + b\n'
    )
    symbols = parse_python_source(code, "test.py")
    assert len(symbols) == 1
    sym = symbols[0]
    assert sym.name == "add"
    assert "b: int = 10" in sym.signature
    assert sym.docstring == "Add two numbers."
    assert sym.start_line == 1
    assert sym.end_line == 3


def test_lexical_and_vector_retrieval():
    chunk1 = DocChunk(
        id="c1", file="docs.md", start_line=1, end_line=5, text="Configure the database timeout parameter.", mentioned_symbols=["timeout"]
    )
    chunk2 = DocChunk(
        id="c2", file="docs.md", start_line=6, end_line=10, text="Authentication guide for user logins.", mentioned_symbols=["auth"]
    )

    lexical = BM25Retriever([chunk1, chunk2])
    hits = lexical.search("timeout parameter", top_k=1)
    assert len(hits) == 1
    assert hits[0][0].id == "c1"

    vec = SimpleVectorStore([chunk1, chunk2])
    v_hits = vec.search("timeout setting", top_k=1)
    assert len(v_hits) == 1
    assert v_hits[0][0].id == "c1"


def test_rule_based_drift():
    sym = CodeSymbol(
        name="fetch", file="src.py", start_line=1, end_line=5, signature="def fetch(url, timeout=60):", code="def fetch(url, timeout=60): pass"
    )
    cs = ChangedSymbol(symbol=sym, old_code="def fetch(url, timeout=30): pass")
    doc = DocChunk(
        id="d1", file="usage.md", start_line=1, end_line=5, text="The timeout defaults to 30 seconds."
    )

    dec, repair = rule_based_check(cs, doc)
    assert dec.decision == "DRIFT"
    assert dec.confidence == 1.0
    assert repair is not None
    assert "defaults to 60" in repair.new_text


def test_judge_guardrails():
    # Test valid IDs filter
    valid_ids = {"E2", "D1"}
    raw_json = '{"decision": "DRIFT", "confidence": 0.9, "reason": "Changed", "evidence_ids": ["E2", "HALLUCINATED_ID"]}'
    dec = _parse_judge_json(raw_json, valid_ids)
    assert dec.decision == "DRIFT"
    assert dec.evidence_ids == ["E2"]

    # Test downgrade when no valid evidence
    raw_no_ev = '{"decision": "DRIFT", "confidence": 0.9, "reason": "Changed", "evidence_ids": ["UNKNOWN"]}'
    dec2 = _parse_judge_json(raw_no_ev, valid_ids)
    assert dec2.decision == "UNCERTAIN"


def test_example_checker():
    doc = DocChunk(
        id="d1",
        file="doc.md",
        start_line=1,
        end_line=5,
        text="Sample",
        code_blocks=["def valid(): return 1", "def broken(: return 2"],
    )
    checks = check_doc_examples(doc)
    assert len(checks) == 2
    assert checks[0].status == "PASS"
    assert checks[1].status == "FAIL"


def test_qa_bot():
    doc = DocChunk(
        id="d1", file="api.md", start_line=1, end_line=10, text="The connect API handles retries."
    )
    bot = RepositoryQABot([doc], provider="fake")
    resp = bot.answer_query("How does connect work?")
    assert "answer" in resp
    assert len(resp["citations"]) >= 1

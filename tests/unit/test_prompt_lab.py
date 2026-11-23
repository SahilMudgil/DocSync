"""
Unit tests for Phase 12: Prompt Lab and versioned prompt templates.
Verifies prompt formatting, docstring completeness scoring,
claim-by-claim V2 drift judging, and end-to-end prompt-lab execution.
"""

from pathlib import Path
from docsync.llm.prompts import (
    DRIFT_JUDGE_V1_USER,
    DRIFT_JUDGE_V2_USER,
    DOCSTRING_COMPLETE_V1_USER,
    DOCSTRING_COMPLETE_V2_USER,
    REFACTOR_V1_USER,
    EXPLAIN_V1_USER,
)
from docsync.llm.factory import get_chat_model
from docsync.models import CodeSymbol, ChangedSymbol, DocChunk, EvidenceItem
from docsync.drift.judge import judge_drift
from docsync.eval.prompt_lab import score_docstring_completeness, run_prompt_lab


def test_prompt_templates_formatting():
    # DRIFT_JUDGE V1 & V2
    v1_text = DRIFT_JUDGE_V1_USER.format(repository="test_repo", symbol="my_fn", evidence="E1: code")
    assert "test_repo" in v1_text
    assert "my_fn" in v1_text

    v2_text = DRIFT_JUDGE_V2_USER.format(repository="test_repo", symbol="my_fn", evidence="E1: code")
    assert "test_repo" in v2_text
    assert "claims" in v2_text

    # Docstring completion
    c1 = DOCSTRING_COMPLETE_V1_USER.format(code="def a(): pass")
    assert "def a(): pass" in c1

    c2 = DOCSTRING_COMPLETE_V2_USER.format(code="def a(): pass")
    assert "def a(): pass" in c2

    # Refactor and Explain
    ref = REFACTOR_V1_USER.format(code="def b(): return 1")
    assert "def b(): return 1" in ref

    exp = EXPLAIN_V1_USER.format(code="def c(): return 2")
    assert "def c(): return 2" in exp


def test_docstring_completeness_scoring():
    meta = {
        "params": ["url", "timeout"],
        "has_return": True,
        "has_raise": True,
    }

    # Empty docstring
    assert score_docstring_completeness("", meta) == 0.0

    # Partial docstring
    partial = '"""Connect to endpoint url."""'
    assert score_docstring_completeness(partial, meta) == 0.25  # 1 out of 4 (url)

    # Complete Google-style docstring
    complete = (
        '"""Summary line.\n\n'
        'Args:\n'
        '    url (str): Target url.\n'
        '    timeout (int): Timeout value.\n'
        'Returns:\n'
        '    dict: Results.\n'
        'Raises:\n'
        '    ValueError: On failure.\n'
        '"""'
    )
    assert score_docstring_completeness(complete, meta) == 1.0


def test_judge_drift_v1_vs_v2():
    sym = CodeSymbol(name="fetch", file="test.py", start_line=1, end_line=5)
    cs = ChangedSymbol(symbol=sym)
    doc = DocChunk(id="d1", file="doc.md", start_line=1, end_line=5, text="Doc text")
    ev = [
        EvidenceItem(id="E2", kind="new_code", file="test.py", start_line=1, end_line=5, text="timeout=60"),
        EvidenceItem(id="D1", kind="doc", file="doc.md", start_line=1, end_line=5, text="timeout defaults to 30"),
    ]
    fake_model = get_chat_model("fake")

    # V1 execution
    dec_v1, _ = judge_drift(cs, doc, ev, fake_model, prompt_version="V1")
    assert dec_v1.decision == "DRIFT"
    assert "E2" in dec_v1.evidence_ids

    # V2 execution (with claims)
    dec_v2, _ = judge_drift(cs, doc, ev, fake_model, prompt_version="V2")
    assert dec_v2.decision == "DRIFT"
    assert len(dec_v2.claims) >= 1
    assert dec_v2.claims[0]["status"] in ["CONTRADICTED", "SUPPORTED"]


def test_run_prompt_lab_end_to_end(tmp_path):
    res = run_prompt_lab(provider="fake", model_name="gemini-1.5-flash", out_dir=str(tmp_path))
    assert res["json_path"].exists()
    assert res["md_path"].exists()

    summary = res["summary"]
    assert "docstring_completeness_v1" in summary
    assert "docstring_completeness_v2" in summary
    assert summary["docstring_completeness_v2"] >= summary["docstring_completeness_v1"]
    assert summary["refactor_compilation_rate"] == 1.0
    assert summary["explanation_format_adherence"] == 1.0

    md_text = res["md_path"].read_text(encoding="utf-8")
    assert "DocSync Prompt Engineering & Prompt Lab Report" in md_text
    assert "## 1. Summary of Prompt Engineering Experiments" in md_text
    assert "## 2. Docstring Completion Breakdown by Function" in md_text

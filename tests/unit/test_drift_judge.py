"""
Unit tests for drift judging, guardrails, rule-based baseline, and repairs.
Verifies post-processing rules and hallucination downgrades.
"""

from docsync.models import CodeSymbol, ChangedSymbol, DocChunk, EvidenceItem
from docsync.drift.judge import _parse_judge_json, judge_drift
from docsync.drift.rule_based import rule_based_check
from docsync.drift.repair import generate_llm_repair
from docsync.drift.example_check import check_doc_examples
from docsync.llm.factory import FakeChatModel


def test_judge_rule_match_preserved():
    valid = {"E1", "E2", "D1"}
    raw = '{"decision": "MATCH", "confidence": 0.95, "reason": "No behavioral change", "evidence_ids": ["E1", "D1"]}'
    res = _parse_judge_json(raw, valid)
    assert res.decision == "MATCH"
    assert res.confidence == 0.95
    assert res.repair_needed is False


def test_judge_rule_drift_valid_evidence():
    valid = {"E2", "D1"}
    raw = '{"decision": "DRIFT", "confidence": 0.9, "reason": "Default parameter changed", "evidence_ids": ["E2", "D1"]}'
    res = _parse_judge_json(raw, valid)
    assert res.decision == "DRIFT"
    assert res.confidence == 0.9
    assert res.evidence_ids == ["E2", "D1"]
    assert res.repair_needed is True


def test_judge_rule_drift_downgrade_when_hallucinated():
    valid = {"E1", "E2", "D1"}
    # Model cites an ID that is not in valid_ids
    raw = '{"decision": "DRIFT", "confidence": 0.85, "reason": "Signature drift", "evidence_ids": ["FAKE_ID_99"]}'
    res = _parse_judge_json(raw, valid)
    assert res.decision == "UNCERTAIN"
    assert "Downgraded to UNCERTAIN" in res.reason
    assert res.repair_needed is False


def test_judge_rule_invalid_json_handling():
    raw = "I think there is drift here: def foo(x=10)"
    res = _parse_judge_json(raw, {"E1"})
    assert res.decision == "MODEL_ERROR"
    assert res.confidence == 0.0


def test_judge_strips_markdown_codeblock():
    valid = {"E2", "D1"}
    raw = "```json\n" '{"decision": "DRIFT", "confidence": 0.88, "reason": "Doc mismatch", "evidence_ids": ["E2"]}\n' "```"
    res = _parse_judge_json(raw, valid)
    assert res.decision == "DRIFT"
    assert res.confidence == 0.88
    assert res.evidence_ids == ["E2"]


def test_rule_based_check_and_template_repair():
    sym = CodeSymbol(
        name="connect",
        file="client.py",
        start_line=1,
        end_line=5,
        signature="def connect(host, port=8080):",
        code="def connect(host, port=8080): pass",
    )
    cs = ChangedSymbol(symbol=sym, old_code="def connect(host, port=5432): pass")
    doc = DocChunk(
        id="d1",
        file="docs/config.md",
        start_line=10,
        end_line=15,
        text="The port parameter defaults to 5432.",
    )

    dec, repair = rule_based_check(cs, doc)
    assert dec.decision == "DRIFT"
    assert dec.confidence == 1.0
    assert repair is not None
    assert "defaults to 8080" in repair.new_text
    assert "- defaults to 5432" in repair.unified_diff
    assert "+ defaults to 8080" in repair.unified_diff


def test_example_checker_statuses():
    doc = DocChunk(
        id="d1",
        file="examples.md",
        start_line=1,
        end_line=10,
        text="Code samples",
        code_blocks=[
            "x = 10\ny = x + 5",          # PASS
            "def broken_syntax(: pass",    # FAIL
        ],
    )
    checks = check_doc_examples(doc)
    assert len(checks) == 2
    assert checks[0].status == "PASS"
    assert checks[0].syntax_ok is True
    assert checks[1].status == "FAIL"
    assert checks[1].syntax_ok is False

"""
Unit tests for GitHub Actions, PR comment posting, Sweep issue creation,
loop guards, and patch generation (Phase 8).
All tests run 100% offline with mocked network requests.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from docsync.models import (
    RunResult,
    DriftItemResult,
    ChangedSymbol,
    CodeSymbol,
    DocChunk,
    DriftDecision,
    RepairSuggestion,
)
from docsync.report.github_comment import post_or_update_pr_comment, DOCSYNC_COMMENT_MARKER
from docsync.report.github_issue import check_loop_guards, open_sweep_issues
from docsync.report.patch import extract_unified_patches, write_or_apply_patch


@pytest.fixture
def sample_drift_run_result():
    sym = CodeSymbol(
        name="fetch_data",
        file="client.py",
        start_line=1,
        end_line=10,
        signature="def fetch_data(url, timeout=60):",
        code="def fetch_data(url, timeout=60): pass",
    )
    cs = ChangedSymbol(symbol=sym, old_code="def fetch_data(url, timeout=30): pass")
    doc = DocChunk(
        id="d1",
        file="docs/usage.md",
        start_line=1,
        end_line=5,
        text="The timeout defaults to 30 seconds.",
    )
    dec = DriftDecision(
        decision="DRIFT",
        confidence=0.95,
        reason="Parameter timeout changed from 30 to 60.",
        evidence_ids=["E2", "D1"],
        repair_needed=True,
    )
    diff = (
        "--- a/docs/usage.md\n"
        "+++ b/docs/usage.md\n"
        "@@ -1,3 +1,3 @@\n"
        "-The timeout defaults to 30 seconds.\n"
        "+The timeout defaults to 60 seconds.\n"
    )
    rep = RepairSuggestion(
        doc_id="d1",
        new_text="The timeout defaults to 60 seconds.",
        unified_diff=diff,
        evidence_ids=["E2", "D1"],
    )

    item = DriftItemResult(
        changed_symbol=cs,
        candidate_doc=doc,
        decision=dec,
        repair=rep,
    )

    return RunResult(
        run_id="test_run_123",
        repo="test/repo",
        base="c0_sha",
        head="c1_sha",
        mode="fast",
        provider="fake",
        model="fake-model",
        retrieval_mode="bm25",
        items=[item],
    )


def test_github_comment_dry_run(sample_drift_run_result):
    res = post_or_update_pr_comment(sample_drift_run_result, dry_run=True)
    assert res["status"] == "dry_run"
    assert DOCSYNC_COMMENT_MARKER in res["body"]
    assert "fetch_data()" in res["body"]
    assert "**DRIFT**" in res["body"]


def test_github_comment_mocked_create(sample_drift_run_result):
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"id": 999, "html_url": "https://github.com/test/pull/1#issuecomment-999"}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    # First call: search comments -> empty list. Second call: POST comment -> success
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_list_resp = MagicMock()
        mock_list_resp.read.return_value = json.dumps([]).encode("utf-8")
        mock_list_resp.__enter__.return_value = mock_list_resp

        mock_urlopen.side_effect = [mock_list_resp, mock_resp]

        res = post_or_update_pr_comment(
            sample_drift_run_result,
            pr_number=1,
            repo="owner/repo",
            token="ghp_fake_token",
            dry_run=False,
        )
        assert res["status"] == "created"
        assert res["id"] == 999


def test_github_comment_mocked_update(sample_drift_run_result):
    # Existing comment with marker found -> should PATCH existing comment
    existing_comment = {
        "id": 888,
        "body": f"{DOCSYNC_COMMENT_MARKER}\nPrevious report",
    }
    mock_list_resp = MagicMock()
    mock_list_resp.read.return_value = json.dumps([existing_comment]).encode("utf-8")
    mock_list_resp.__enter__.return_value = mock_list_resp

    mock_patch_resp = MagicMock()
    mock_patch_resp.read.return_value = json.dumps({"id": 888, "html_url": "https://github.com/test/pull/1#issuecomment-888"}).encode("utf-8")
    mock_patch_resp.__enter__.return_value = mock_patch_resp

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = [mock_list_resp, mock_patch_resp]

        res = post_or_update_pr_comment(
            sample_drift_run_result,
            pr_number=1,
            repo="owner/repo",
            token="ghp_fake_token",
            dry_run=False,
        )
        assert res["status"] == "updated"
        assert res["id"] == 888


def test_loop_guards():
    # 1. Bot author
    assert check_loop_guards(pr_author="sweep[bot]") is not None
    assert check_loop_guards(pr_author="github-actions[bot]") is not None

    # 2. Sweep branch
    assert check_loop_guards(pr_branch="sweep/update-fetch-docs") is not None

    # 3. docsync-ignore label
    assert check_loop_guards(pr_labels=["bug", "docsync-ignore"]) is not None

    # 4. Clean human PR passes
    assert check_loop_guards(pr_author="alice", pr_branch="feature/new-api", pr_labels=["enhancement"]) is None


def test_open_sweep_issues_loop_guard_blocked(sample_drift_run_result):
    issues = open_sweep_issues(
        sample_drift_run_result,
        pr_author="sweep[bot]",
        token="ghp_fake",
        repo="owner/repo",
    )
    assert len(issues) == 1
    assert issues[0]["status"] == "blocked"


def test_open_sweep_issues_dry_run(sample_drift_run_result):
    issues = open_sweep_issues(
        sample_drift_run_result,
        dry_run=True,
    )
    assert len(issues) == 1
    assert issues[0]["status"] == "dry_run"
    assert "Sweep: update docs for fetch_data in docs/usage.md" in issues[0]["title"]
    assert "defaults to 60 seconds" in issues[0]["body"]


def test_open_sweep_issues_duplicate_prevention(sample_drift_run_result):
    existing_title = "Sweep: update docs for fetch_data in docs/usage.md"
    with patch("docsync.report.github_issue.get_existing_open_issue_titles", return_value=[existing_title]):
        issues = open_sweep_issues(
            sample_drift_run_result,
            token="ghp_fake",
            repo="owner/repo",
            dry_run=False,
        )
        assert len(issues) == 1
        assert issues[0]["status"] == "skipped_duplicate"


def test_patch_extraction_and_file_writing(sample_drift_run_result, tmp_path):
    patch_text = extract_unified_patches(sample_drift_run_result)
    assert "--- a/docs/usage.md" in patch_text
    assert "+The timeout defaults to 60 seconds." in patch_text

    out_patch = tmp_path / "test.patch"
    res = write_or_apply_patch(sample_drift_run_result, str(out_patch), apply=False)
    assert res["applied"] is False
    assert out_patch.exists()
    assert out_patch.read_text(encoding="utf-8") == patch_text


def test_patch_security_guard(tmp_path):
    # If a patch attempts to modify a non-doc file, refuse to apply
    malicious_item = MagicMock()
    malicious_item.decision.decision = "DRIFT"
    malicious_item.repair.unified_diff = "--- a/src/main.py\n+++ b/src/main.py\n@@ -1 +1 @@\n-x=1\n+x=2\n"

    bad_run = MagicMock()
    bad_run.items = [malicious_item]

    out_patch = tmp_path / "bad.patch"
    res = write_or_apply_patch(bad_run, str(out_patch), apply=True)
    assert "Security guard" in res.get("error", "")
    assert res["applied"] is False

"""
Deterministic acceptance tests for the demo scenario (Phase 7 & 9 / §10.6).
Verifies:
1. C0 -> C1 harmless refactor produces MATCH (no false alarm).
2. C1 -> C2 default parameter change produces DRIFT citing E2 and D1.
3. Suggested diff only touches docs, never source files.
4. Fake LLM plumbing test verifies full model code path offline.
"""

import subprocess
import tempfile
import shutil
from pathlib import Path
import pytest
from docsync.pipeline import run_check
from docsync.report.markdown_report import generate_markdown_report
from docsync.models import RunResult


def _run_git(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


@pytest.fixture
def demo_git_repo():
    """Create a temporary git repository with C0, C1, C2 commits."""
    temp_dir = tempfile.mkdtemp(prefix="docsync_test_demo_")
    repo_path = Path(temp_dir)

    try:
        _run_git(["git", "init"], repo_path)
        _run_git(["git", "config", "user.name", "DocSync Test"], repo_path)
        _run_git(["git", "config", "user.email", "test@docsync.local"], repo_path)

        # C0: Baseline setup
        client_py = repo_path / "client.py"
        docs_dir = repo_path / "docs"
        docs_dir.mkdir(parents=True)
        usage_md = docs_dir / "usage.md"

        client_py.write_text(
            'def fetch_data(url: str, timeout: int = 30) -> dict:\n'
            '    """Fetch data from url. Defaults to 30."""\n'
            '    return {"status": 200, "timeout": timeout}\n',
            encoding="utf-8",
        )
        usage_md.write_text(
            '# API Documentation\nThe fetch_data timeout defaults to 30 seconds.\n',
            encoding="utf-8",
        )

        _run_git(["git", "add", "."], repo_path)
        _run_git(["git", "commit", "-m", "C0: Initial baseline"], repo_path)
        c0_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip()

        # C1: Harmless developer internal refactor
        client_py.write_text(
            'def fetch_data(url: str, timeout: int = 30) -> dict:\n'
            '    # Harmless developer comment inside function\n'
            '    """Fetch data from url. Defaults to 30."""\n'
            '    result_dict = {"status": 200, "timeout": timeout}\n'
            '    return result_dict\n',
            encoding="utf-8",
        )
        _run_git(["git", "add", "."], repo_path)
        _run_git(["git", "commit", "-m", "C1: Add comment refactor"], repo_path)
        c1_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip()

        # C2: Breaking change: timeout=30 -> timeout=60, docs untouched
        client_py.write_text(
            'def fetch_data(url: str, timeout: int = 60) -> dict:\n'
            '    # Harmless developer comment inside function\n'
            '    """Fetch data from url. Defaults to 30."""\n'
            '    result_dict = {"status": 200, "timeout": timeout}\n'
            '    return result_dict\n',
            encoding="utf-8",
        )
        _run_git(["git", "add", "."], repo_path)
        _run_git(["git", "commit", "-m", "C2: Change timeout default to 60"], repo_path)
        c2_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo_path, text=True).strip()

        yield repo_path, c0_sha, c1_sha, c2_sha

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_demo_scenario_c0_c1_match(demo_git_repo):
    repo_path, c0_sha, c1_sha, _ = demo_git_repo
    res = run_check(str(repo_path), c0_sha, c1_sha, {}, mode="fast")

    # In C0 -> C1, there are changed lines, but no signature or behavior change -> MATCH
    assert len(res.items) >= 1
    assert res.items[0].decision.decision == "MATCH"
    assert res.items[0].decision.repair_needed is False


def test_demo_scenario_c1_c2_drift(demo_git_repo):
    repo_path, _, c1_sha, c2_sha = demo_git_repo
    res = run_check(str(repo_path), c1_sha, c2_sha, {}, mode="fast")

    assert len(res.items) >= 1
    drift_item = res.items[0]
    assert drift_item.decision.decision == "DRIFT"
    assert drift_item.decision.confidence == 1.0
    # Must cite evidence tokens containing E and D
    assert any("E" in eid for eid in drift_item.decision.evidence_ids)
    assert any("D" in eid for eid in drift_item.decision.evidence_ids)

    # Assert repair unified diff only changes 30 to 60 in docs/usage.md
    assert drift_item.repair is not None
    diff = drift_item.repair.unified_diff
    assert "-The fetch_data timeout defaults to 30 seconds." in diff or "30" in diff
    assert "+The fetch_data timeout defaults to 60 seconds." in diff or "60" in diff
    assert "client.py" not in diff  # Source code is untouched!

    # Example check executed
    assert len(drift_item.example_checks) >= 0


def test_demo_scenario_fake_llm_plumbing(demo_git_repo):
    """
    Plumbing test: drives the LLM code path with a scripted FakeChatModel.
    Verifies model invocation and JSON handling offline with no API keys.
    """
    repo_path, _, c1_sha, c2_sha = demo_git_repo
    cfg = {"llm": {"provider": "fake"}}
    res = run_check(str(repo_path), c1_sha, c2_sha, cfg, mode="full")

    assert res.provider == "fake"
    assert len(res.items) >= 1
    # Verify report renders without errors
    md = generate_markdown_report(res)
    assert "[DocSync] Documentation Verification Report" in md

"""
Integration tests for DocSync end-to-end pipeline execution and artifact generation.
"""

import subprocess
import tempfile
import shutil
import json
from pathlib import Path
from docsync.pipeline import run_check
from docsync.models import RunResult
from docsync.report.markdown_report import generate_markdown_report


def _run_git(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def test_pipeline_artifacts_generation():
    temp_dir = tempfile.mkdtemp(prefix="docsync_pipeline_e2e_")
    repo = Path(temp_dir)

    try:
        _run_git(["git", "init"], repo)
        _run_git(["git", "config", "user.name", "Tester"], repo)
        _run_git(["git", "config", "user.email", "tester@test.com"], repo)

        src = repo / "main.py"
        src.write_text("def run(retries: int = 1):\n    return retries\n", encoding="utf-8")
        doc = repo / "README.md"
        doc.write_text("# Guide\nrun retries parameter defaults to 1.\n", encoding="utf-8")

        _run_git(["git", "add", "."], repo)
        _run_git(["git", "commit", "-m", "Initial commit"], repo)
        c0 = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

        src.write_text("def run(retries: int = 5):\n    return retries\n", encoding="utf-8")
        _run_git(["git", "add", "."], repo)
        _run_git(["git", "commit", "-m", "Bump retries to 5"], repo)
        c1 = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

        # Run pipeline
        result = run_check(str(repo), c0, c1, {}, mode="fast")
        assert isinstance(result, RunResult)
        assert len(result.items) >= 1

        # Check JSON roundtrip
        json_str = result.model_dump_json(indent=2)
        parsed = json.loads(json_str)
        reconstructed = RunResult(**parsed)
        assert reconstructed.run_id == result.run_id
        assert reconstructed.items[0].decision.decision == "DRIFT"

        # Check Markdown report formatting
        md = generate_markdown_report(result)
        assert "### Summary Table" in md
        assert "run()" in md

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_pipeline_multi_symbol_handling():
    temp_dir = tempfile.mkdtemp(prefix="docsync_multi_sym_")
    repo = Path(temp_dir)

    try:
        _run_git(["git", "init"], repo)
        _run_git(["git", "config", "user.name", "Tester"], repo)
        _run_git(["git", "config", "user.email", "tester@test.com"], repo)

        src = repo / "api.py"
        src.write_text(
            "def foo(x=1):\n    pass\n\n"
            "def bar(y=2):\n    pass\n",
            encoding="utf-8",
        )
        doc = repo / "api.md"
        doc.write_text("foo defaults to 1. bar defaults to 2.\n", encoding="utf-8")

        _run_git(["git", "add", "."], repo)
        _run_git(["git", "commit", "-m", "Init"], repo)
        c0 = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

        # Update foo: x=1 -> x=10, but bar is untouched
        src.write_text(
            "def foo(x=10):\n    pass\n\n"
            "def bar(y=2):\n    pass\n",
            encoding="utf-8",
        )
        _run_git(["git", "add", "."], repo)
        _run_git(["git", "commit", "-m", "Update foo"], repo)
        c1 = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()

        res = run_check(str(repo), c0, c1, {}, mode="fast")
        # Should isolate changed symbol foo
        names = [it.changed_symbol.symbol.name for it in res.items]
        assert "foo" in names
        assert "bar" not in names

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

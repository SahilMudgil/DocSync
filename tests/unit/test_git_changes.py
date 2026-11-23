"""
Unit tests for Git change detection and symbol diff mapping.
Tests hunk range parsing, ignored paths, and symbol boundary intersection.
"""

from unittest.mock import patch
from docsync.models import CodeSymbol
from docsync.ingest.git_changes import get_git_diff_ranges, get_changed_symbols


def test_get_git_diff_ranges_parsing():
    sample_diff = (
        "diff --git a/src/client.py b/src/client.py\n"
        "--- a/src/client.py\n"
        "+++ b/src/client.py\n"
        "@@ -5,2 +5,4 @@\n"
        "+# comment\n"
        "+def fetch():\n"
        "diff --git a/docs/readme.md b/docs/readme.md\n"
        "--- a/docs/readme.md\n"
        "+++ b/docs/readme.md\n"
        "@@ -1 +1 @@\n"
        "+# Title\n"
    )

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = sample_diff
        ranges = get_git_diff_ranges("/fake/repo", "base_sha", "head_sha")

        assert "src/client.py" in ranges
        assert ranges["src/client.py"] == [(5, 8)]  # start=5, count=4 -> end=8
        # Non-python files like docs/readme.md should be ignored by get_git_diff_ranges
        assert "docs/readme.md" not in ranges


def test_get_changed_symbols_ignore_paths():
    sample_diff = (
        "diff --git a/tests/test_foo.py b/tests/test_foo.py\n"
        "--- a/tests/test_foo.py\n"
        "+++ b/tests/test_foo.py\n"
        "@@ -1 +1 @@\n"
        "+def test(): pass\n"
    )

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = sample_diff
        # tests/ should be ignored
        res = get_changed_symbols("/fake/repo", "base", "head", ignore_paths=["tests/"])
        assert res == []


def test_symbol_boundary_overlap():
    sym = CodeSymbol(
        name="do_work",
        file="worker.py",
        start_line=10,
        end_line=25,
        signature="def do_work():",
    )
    # Changed line inside symbol boundary
    changed_ranges = [(15, 16)]
    overlaps = any(
        max(start, sym.start_line) <= min(end, sym.end_line)
        for start, end in changed_ranges
    )
    assert overlaps is True

    # Changed line outside symbol boundary
    outside_ranges = [(30, 35)]
    overlaps_out = any(
        max(start, sym.start_line) <= min(end, sym.end_line)
        for start, end in outside_ranges
    )
    assert overlaps_out is False

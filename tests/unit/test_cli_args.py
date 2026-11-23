"""
Unit tests for CLI argument parsing and configuration options.
"""

import pytest
from unittest.mock import patch
from docsync.cli import main


def test_cli_subparsers_registered():
    with patch("sys.argv", ["docsync", "--help"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0


def test_cli_check_command_args():
    with patch("sys.argv", ["docsync", "check", "--base", "c0", "--head", "c1", "--mode", "fast"]):
        with patch("docsync.cli.run_check") as mock_check:
            with patch("docsync.cli.Path.write_text"):
                with patch("docsync.cli.load_config", return_value={}):
                    from docsync.models import RunResult
                    mock_check.return_value = RunResult(
                        run_id="test", repo=".", base="c0", head="c1", mode="fast",
                        provider="fake", model="fake", retrieval_mode="bm25", items=[]
                    )
                    main()
                    mock_check.assert_called_once()
                    args, kwargs = mock_check.call_args
                    assert kwargs["mode"] == "fast"


def test_cli_missing_required_args():
    with patch("sys.argv", ["docsync", "check"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code != 0

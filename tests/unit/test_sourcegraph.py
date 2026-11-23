"""
Unit tests for Phase 10: Sourcegraph provider adapter and fallback mechanisms.
Verifies mocked GraphQL HTTP interactions, network failure recovery,
and pipeline run-metadata sourcegraph_used flag propagation.
"""

from unittest.mock import MagicMock, patch
import requests
from docsync.models import SearchHit
from docsync.retrieval.code_search import LocalSearchProvider, SourcegraphProvider
from docsync.pipeline import run_check


def test_sourcegraph_unconfigured_falls_back_to_local(tmp_path):
    local_provider = LocalSearchProvider(str(tmp_path))
    local_provider.search = MagicMock(return_value=[SearchHit(file="test.py", line=1, snippet="x = 1", source="local", score=1.0)])

    provider = SourcegraphProvider(url="", token="", local_fallback=local_provider)
    assert not provider.is_configured()

    hits = provider.search("fetch_data", limit=3)
    assert len(hits) == 1
    assert hits[0].source == "local"
    assert provider.sourcegraph_used is False
    local_provider.search.assert_called_once_with("fetch_data", 3)


def test_sourcegraph_mocked_http_success(tmp_path):
    local_provider = LocalSearchProvider(str(tmp_path))
    local_provider.search = MagicMock(return_value=[])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "search": {
                "results": {
                    "results": [
                        {
                            "file": {"path": "examples/demo_project/client.py"},
                            "lineMatches": [
                                {"lineNumber": 8, "preview": "    res = fetch_data(url, timeout=30)"}
                            ],
                        }
                    ]
                }
            }
        }
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        provider = SourcegraphProvider(
            url="https://sourcegraph.example.com",
            token="sgp_mock_token_12345",
            local_fallback=local_provider,
        )
        assert provider.is_configured()

        hits = provider.search("fetch_data", limit=5)
        assert len(hits) == 1
        assert hits[0].source == "sourcegraph"
        assert hits[0].file == "examples/demo_project/client.py"
        assert hits[0].line == 8
        assert "fetch_data" in hits[0].snippet
        assert provider.sourcegraph_used is True
        mock_post.assert_called_once()
        local_provider.search.assert_not_called()


def test_sourcegraph_mocked_http_error_falls_back(tmp_path):
    local_provider = LocalSearchProvider(str(tmp_path))
    local_provider.search = MagicMock(return_value=[SearchHit(file="fallback.py", line=10, snippet="fallback snippet", source="local", score=1.0)])

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.json.return_value = {"error": "Unauthorized"}

    with patch("requests.post", return_value=mock_resp):
        provider = SourcegraphProvider(
            url="https://sourcegraph.example.com",
            token="invalid_token",
            local_fallback=local_provider,
        )
        hits = provider.search("test_query", limit=3)
        assert len(hits) == 1
        assert hits[0].source == "local"
        assert provider.sourcegraph_used is False
        local_provider.search.assert_called_once_with("test_query", 3)


def test_sourcegraph_mocked_timeout_falls_back(tmp_path):
    local_provider = LocalSearchProvider(str(tmp_path))
    local_provider.search = MagicMock(return_value=[SearchHit(file="local_timeout.py", line=2, snippet="local", source="local", score=1.0)])

    with patch("requests.post", side_effect=requests.exceptions.Timeout("Connection timed out")):
        provider = SourcegraphProvider(
            url="https://sourcegraph.example.com",
            token="token123",
            local_fallback=local_provider,
        )
        hits = provider.search("timeout_query", limit=2)
        assert len(hits) == 1
        assert hits[0].file == "local_timeout.py"
        assert provider.sourcegraph_used is False
        local_provider.search.assert_called_once_with("timeout_query", 2)


def test_sourcegraph_mocked_graphql_errors_falls_back(tmp_path):
    local_provider = LocalSearchProvider(str(tmp_path))
    local_provider.search = MagicMock(return_value=[SearchHit(file="local_err.py", line=5, snippet="local", source="local", score=1.0)])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "errors": [{"message": "Rate limit exceeded on GraphQL endpoint"}]
    }

    with patch("requests.post", return_value=mock_resp):
        provider = SourcegraphProvider(
            url="https://sourcegraph.example.com",
            token="token123",
            local_fallback=local_provider,
        )
        hits = provider.search("err_query", limit=2)
        assert len(hits) == 1
        assert hits[0].file == "local_err.py"
        assert provider.sourcegraph_used is False
        local_provider.search.assert_called_once_with("err_query", 2)


def test_pipeline_sourcegraph_flag_propagation(tmp_path):
    """Test that pipeline registers sourcegraph_used=True when Sourcegraph answers queries."""
    cfg = {
        "retrieval": {
            "use_sourcegraph": True,
            "sourcegraph_url": "https://sourcegraph.example.com",
            "sourcegraph_token": "mock_token",
            "top_k": 1,
            "rrf_k": 60,
        },
        "llm": {"provider": "fake"},
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "data": {
            "search": {
                "results": {
                    "results": [
                        {
                            "file": {"path": "client.py"},
                            "lineMatches": [{"lineNumber": 3, "preview": "fetch_data()"}],
                        }
                    ]
                }
            }
        }
    }

    with patch("requests.post", return_value=mock_resp), \
         patch("docsync.pipeline.get_changed_symbols") as mock_changed:
        from docsync.models import CodeSymbol, ChangedSymbol
        mock_changed.return_value = [
            ChangedSymbol(
                symbol=CodeSymbol(name="fetch_data", file="client.py", start_line=1, end_line=10, signature="def fetch_data():"),
                old_code="def fetch_data(timeout=30): pass",
                new_code="def fetch_data(timeout=60): pass",
            )
        ]
        result = run_check(str(tmp_path), "HEAD~1", "HEAD", config=cfg, mode="fast")
        assert result.sourcegraph_used is True

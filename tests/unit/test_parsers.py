"""
Unit tests for Python AST parsing and documentation chunking.
Tests syntax error resilience, class/method extraction, and doc extraction.
"""

from docsync.ingest.code_parser import parse_python_source
from docsync.ingest.doc_parser import parse_doc_file, extract_docstring_chunks


def test_parse_classes_and_methods():
    code = (
        "class DatabaseClient:\n"
        '    """Manages database connection pools."""\n'
        "    def __init__(self, host: str = 'localhost'):\n"
        "        self.host = host\n"
        "\n"
        "    def query(self, sql: str, timeout: int = 10) -> list:\n"
        '        """Execute query."""\n'
        "        return []\n"
    )
    syms = parse_python_source(code, "db.py")
    # Should extract class DatabaseClient, method __init__, method query
    sym_names = [s.name for s in syms]
    assert "DatabaseClient" in sym_names
    assert "DatabaseClient.__init__" in sym_names or "__init__" in sym_names
    assert any("query" in s.name for s in syms)


def test_parse_functions_with_complex_signatures():
    code = (
        "def process_data(data: list, *args, retries: int = 3, **kwargs) -> bool:\n"
        '    """Process list of items with retry logic."""\n'
        "    return True\n"
    )
    syms = parse_python_source(code, "processor.py")
    assert len(syms) == 1
    sym = syms[0]
    assert sym.name == "process_data"
    assert "retries: int = 3" in sym.signature
    assert sym.docstring == "Process list of items with retry logic."


def test_parse_syntax_error_resilience():
    broken_code = "def invalid_syntax(a, b:\n    return a +"
    syms = parse_python_source(broken_code, "broken.py")
    # Parser should return empty list without crashing
    assert syms == []


def test_doc_parser_markdown_headers_and_code(tmp_path):
    doc_path = tmp_path / "guide.md"
    doc_path.write_text(
        "# Getting Started\n"
        "Welcome to the client guide.\n"
        "\n"
        "## Authentication Setup\n"
        "Configure the `auth_token` parameter before calling `connect()`.\n"
        "```python\n"
        "client = connect(auth_token='secret')\n"
        "```\n",
        encoding="utf-8",
    )
    chunks = parse_doc_file(str(doc_path))
    assert len(chunks) >= 1
    # Check that code block was parsed
    assert any("client = connect" in cb for c in chunks for cb in c.code_blocks)
    # Check that mentioned symbols were detected
    symbols = [sym for c in chunks for sym in c.mentioned_symbols]
    assert "auth_token" in symbols or "connect" in symbols


def test_extract_docstring_chunks():
    code = (
        "def compute(value: int = 5) -> int:\n"
        '    """Compute the square of value."""\n'
        "    return value * value\n"
    )
    syms = parse_python_source(code, "math_utils.py")
    doc_chunks = extract_docstring_chunks(syms)
    assert len(doc_chunks) == 1
    assert "Compute the square of value." in doc_chunks[0].text
    assert "compute" in doc_chunks[0].mentioned_symbols

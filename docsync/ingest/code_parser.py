"""
Code parser for Python files.
Extracts top-level functions, classes, and methods as CodeSymbol objects
including line ranges, signatures, and docstrings.
"""

import ast
from pathlib import Path
from typing import List, Optional
from docsync.models import CodeSymbol


def parse_python_file(file_path: str, repo_root: Optional[str] = None) -> List[CodeSymbol]:
    """Parse a Python source file into a list of CodeSymbol objects."""
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    rel_file = str(path.relative_to(repo_root)) if repo_root and path.is_relative_to(repo_root) else str(path)
    return parse_python_source(content, rel_file)


def parse_python_source(source_code: str, file_name: str = "") -> List[CodeSymbol]:
    """Parse raw Python source code string into CodeSymbol objects."""
    symbols: List[CodeSymbol] = []
    lines = source_code.splitlines()

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return symbols

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            code_snippet = "\n".join(lines[start - 1 : end])
            doc = ast.get_docstring(node)
            sig = _extract_signature(node, lines)

            symbols.append(
                CodeSymbol(
                    name=node.name,
                    kind="function",
                    file=file_name,
                    start_line=start,
                    end_line=end,
                    signature=sig,
                    code=code_snippet,
                    docstring=doc,
                )
            )

        elif isinstance(node, ast.ClassDef):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            doc = ast.get_docstring(node)
            symbols.append(
                CodeSymbol(
                    name=node.name,
                    kind="class",
                    file=file_name,
                    start_line=start,
                    end_line=end,
                    signature=f"class {node.name}",
                    code="\n".join(lines[start - 1 : end]),
                    docstring=doc,
                )
            )

            # Methods inside class
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    m_start = item.lineno
                    m_end = getattr(item, "end_lineno", m_start)
                    m_sig = _extract_signature(item, lines)
                    symbols.append(
                        CodeSymbol(
                            name=f"{node.name}.{item.name}",
                            kind="method",
                            file=file_name,
                            start_line=m_start,
                            end_line=m_end,
                            signature=m_sig,
                            code="\n".join(lines[m_start - 1 : m_end]),
                            docstring=ast.get_docstring(item),
                        )
                    )

    return symbols


def _extract_signature(node: ast.FunctionDef, lines: List[str]) -> str:
    """Extract signature string from function def node."""
    start = node.lineno - 1
    def_lines = []
    for line in lines[start:]:
        def_lines.append(line.strip())
        # Check if line ends the def header with ): or ) -> return_type:
        if line.strip().endswith(":") and ")" in line:
            break
    full_header = " ".join(def_lines)
    # Strip the trailing colon
    if full_header.endswith(":"):
        full_header = full_header[:-1].strip()
    return full_header

"""
Documentation parser for Markdown, reStructuredText, and docstrings.
Chunks documentation into DocChunk items with line ranges,
symbol references, and extracted code blocks.
"""

import re
from pathlib import Path
from typing import List, Optional
from docsync.models import DocChunk, CodeSymbol


def parse_doc_file(file_path: str, repo_root: Optional[str] = None) -> List[DocChunk]:
    """Parse a Markdown or RST file into section chunks."""
    path = Path(file_path)
    if not path.is_file():
        return []

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []

    rel_file = str(path.relative_to(repo_root)) if repo_root and path.is_relative_to(repo_root) else str(path)
    lines = content.splitlines()

    chunks: List[DocChunk] = []
    current_lines: List[str] = []
    chunk_start = 1
    chunk_idx = 0

    for i, line in enumerate(lines, start=1):
        # Heading marker in Markdown (#)
        if line.startswith("#") and current_lines:
            text = "\n".join(current_lines).strip()
            if text:
                chunks.append(_create_chunk(f"{rel_file}_{chunk_idx}", rel_file, chunk_start, i - 1, text))
                chunk_idx += 1
            current_lines = [line]
            chunk_start = i
        else:
            current_lines.append(line)

    # Final chunk
    if current_lines:
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append(_create_chunk(f"{rel_file}_{chunk_idx}", rel_file, chunk_start, len(lines), text))

    return chunks


def extract_docstring_chunks(symbols: List[CodeSymbol]) -> List[DocChunk]:
    """Convert symbol docstrings into DocChunk objects."""
    chunks: List[DocChunk] = []
    for sym in symbols:
        if sym.docstring and sym.docstring.strip():
            chunk_id = f"docstring_{sym.file}_{sym.name}"
            chunks.append(
                DocChunk(
                    id=chunk_id,
                    file=sym.file,
                    start_line=sym.start_line,
                    end_line=sym.end_line,
                    kind="docstring",
                    text=sym.docstring.strip(),
                    mentioned_symbols=[sym.name],
                    code_blocks=[],
                )
            )
    return chunks


def _create_chunk(chunk_id: str, file: str, start: int, end: int, text: str) -> DocChunk:
    """Helper to create a DocChunk with extracted code blocks and mentioned symbols."""
    code_blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    backtick_words = re.findall(r"`([a-zA-Z_][a-zA-Z0-9_.]*)`", text)

    return DocChunk(
        id=chunk_id,
        file=file,
        start_line=start,
        end_line=end,
        kind="md_section",
        text=text,
        mentioned_symbols=list(set(backtick_words)),
        code_blocks=code_blocks,
    )

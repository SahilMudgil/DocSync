"""
Documentation example code block validator.
- Level 1: checks syntax validity with ast.parse.
- Level 2: verifies imported or called function names against repository symbol table.
"""

import ast
from typing import List, Set
from docsync.models import DocChunk, ExampleCheck


def check_doc_examples(doc_chunk: DocChunk, known_symbols: Set[str] = None) -> List[ExampleCheck]:
    """Check Python code blocks inside a documentation chunk."""
    results: List[ExampleCheck] = []
    known_symbols = known_symbols or set()

    for idx, block in enumerate(doc_chunk.code_blocks, start=1):
        clean_code = block.strip()
        if not clean_code:
            continue

        # Level 1: Syntax check
        try:
            tree = ast.parse(clean_code)
            syntax_ok = True
        except SyntaxError:
            results.append(
                ExampleCheck(
                    doc_id=doc_chunk.id,
                    block_index=idx,
                    syntax_ok=False,
                    unknown_names=[],
                    status="FAIL",
                )
            )
            continue

        # Level 2: Verify called / referenced names
        called_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called_names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called_names.add(node.func.attr)

        unknown = [name for name in called_names if known_symbols and name not in known_symbols and name not in dir(__builtins__)]

        status = "WARN" if unknown else "PASS"
        results.append(
            ExampleCheck(
                doc_id=doc_chunk.id,
                block_index=idx,
                syntax_ok=syntax_ok,
                unknown_names=unknown,
                status=status,
            )
        )

    return results

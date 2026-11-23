"""
Synthetic AST Mutation Operators for DocSync Benchmark Generation.
Implements positive (DRIFT) and negative (NO_DRIFT / behaviour-preserving)
source code mutations as specified in Master Plan §9.2.
Guarantees syntactic validity via ast.parse on all generated code.
"""

import ast
import re
from typing import Optional, Tuple


def validate_python_code(code: str) -> bool:
    """Check if Python code string parses into a valid AST."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False


def mutate_default(code: str, param_name: str, old_val: str, new_val: str) -> Optional[str]:
    """
    Positive Mutation: Change a default parameter literal in function signature.
    Example: def fetch(timeout=30) -> def fetch(timeout=60)
    """
    pattern = rf"(\b{re.escape(param_name)}\s*:\s*[^=]+=\s*|\b{re.escape(param_name)}\s*=\s*){re.escape(old_val)}(\b|[,\)])"
    replacement = rf"\g<1>{new_val}\g<2>"
    new_code = re.sub(pattern, replacement, code, count=1)
    if new_code != code and validate_python_code(new_code):
        return new_code
    return None


def mutate_param_name(code: str, old_param: str, new_param: str) -> Optional[str]:
    """
    Positive Mutation: Rename a parameter in both signature and function body.
    Example: def route(endpoint=None) -> def route(route_endpoint=None)
    """
    # Replace word occurrences of old_param with new_param
    pattern = rf"\b{re.escape(old_param)}\b"
    new_code = re.sub(pattern, new_param, code)
    if new_code != code and validate_python_code(new_code):
        return new_code
    return None


def mutate_exception(code: str, old_exc: str, new_exc: str) -> Optional[str]:
    """
    Positive Mutation: Change a raised exception type in the function body.
    Example: raise ValueError(...) -> raise KeyError(...)
    """
    pattern = rf"\braise\s+{re.escape(old_exc)}\b"
    replacement = f"raise {new_exc}"
    new_code = re.sub(pattern, replacement, code, count=1)
    if new_code != code and validate_python_code(new_code):
        return new_code
    return None


def mutate_constant(code: str, old_val: str, new_val: str) -> Optional[str]:
    """
    Positive Mutation: Alter a literal numerical/string constant inside the body.
    Example: max_age = 3600 -> max_age = 86400
    """
    pattern = rf"\b{re.escape(old_val)}\b"
    new_code = re.sub(pattern, new_val, code, count=1)
    if new_code != code and validate_python_code(new_code):
        return new_code
    return None


def mutate_local_rename(code: str, old_var: str, new_var: str) -> Optional[str]:
    """
    Negative Mutation (NO_DRIFT): Rename an internal local variable.
    Preserves signature, external contract, and behavior.
    """
    # We replace inside function body lines (skip def line)
    lines = code.splitlines(keepends=True)
    if not lines:
        return None
    header = lines[0]
    body = "".join(lines[1:])
    pattern = rf"\b{re.escape(old_var)}\b"
    new_body = re.sub(pattern, new_var, body)
    new_code = header + new_body
    if new_code != code and validate_python_code(new_code):
        return new_code
    return None


def mutate_comment_whitespace(code: str) -> Optional[str]:
    """
    Negative Mutation (NO_DRIFT): Add internal comments or modify whitespace.
    Behavior and documentation contract remain unchanged.
    """
    lines = code.splitlines(keepends=True)
    if len(lines) < 2:
        new_code = code + "\n    # Internal implementation note\n"
    else:
        # Insert a comment after the function header
        new_code = lines[0] + "    # Refactored for performance and internal clarity\n" + "".join(lines[1:])
    if validate_python_code(new_code):
        return new_code
    return None


def mutate_temp_variable(code: str, expr: str = "30", temp_name: str = "_temp_timeout") -> Optional[str]:
    """
    Negative Mutation (NO_DRIFT): Extract an internal subexpression into a temporary variable.
    """
    lines = code.splitlines(keepends=True)
    if len(lines) < 2:
        return None
    insert_line = f"    {temp_name} = {expr}\n"
    new_code = lines[0] + insert_line + "".join(lines[1:])
    if validate_python_code(new_code):
        return new_code
    return None

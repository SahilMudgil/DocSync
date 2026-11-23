"""
Git change detection module.
Extracts changed line ranges from git diff between base and head commits,
and maps modified line ranges to ChangedSymbol objects.
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from docsync.models import ChangedSymbol, CodeSymbol
from docsync.ingest.code_parser import parse_python_source, parse_python_file


def get_git_diff_ranges(repo_path: str, base_sha: str, head_sha: str) -> Dict[str, List[Tuple[int, int]]]:
    """
    Run git diff between base_sha and head_sha.
    Returns mapping of file_path -> list of (start_line, end_line) in the HEAD version.
    """
    cmd = ["git", "diff", "--unified=0", f"{base_sha}..{head_sha}"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        diff_text = proc.stdout
    except Exception:
        return {}

    file_ranges: Dict[str, List[Tuple[int, int]]] = {}
    current_file = None

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            if current_file.endswith(".py"):
                file_ranges[current_file] = []
        elif line.startswith("@@ ") and current_file and current_file.endswith(".py"):
            # Parse @@ -old,count +new,count @@
            match = re.search(r"\+([0-9]+)(?:,([0-9]+))?", line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2)) if match.group(2) else 1
                end = start + max(count - 1, 0)
                file_ranges[current_file].append((start, end))

    return file_ranges


def get_changed_symbols(
    repo_path: str, base_sha: str, head_sha: str, ignore_paths: Optional[List[str]] = None
) -> List[ChangedSymbol]:
    """Find all Python symbols changed between base_sha and head_sha."""
    diff_ranges = get_git_diff_ranges(repo_path, base_sha, head_sha)
    changed_symbols: List[ChangedSymbol] = []
    ignore_paths = ignore_paths or ["tests/", "venv/", ".git/"]

    for rel_path, ranges in diff_ranges.items():
        if any(rel_path.startswith(ign) for ign in ignore_paths):
            continue

        # Get old file content from base_sha
        old_content = _get_git_file_content(repo_path, base_sha, rel_path)
        old_symbols = {s.name: s for s in parse_python_source(old_content, rel_path)} if old_content else {}

        # Get new file content from head_sha
        new_content = _get_git_file_content(repo_path, head_sha, rel_path)
        if not new_content:
            # Fallback to reading file directly from disk
            disk_path = Path(repo_path) / rel_path
            new_symbols = parse_python_file(str(disk_path), repo_root=repo_path)
        else:
            new_symbols = parse_python_source(new_content, rel_path)

        for sym in new_symbols:
            # Check if symbol's line range overlaps with any changed range
            overlaps = any(
                not (sym.end_line < r_start or sym.start_line > r_end)
                for r_start, r_end in ranges
            )
            if overlaps:
                old_sym = old_symbols.get(sym.name)
                old_code = old_sym.code if old_sym else None
                change_type = "modified" if old_sym else "added"

                changed_symbols.append(
                    ChangedSymbol(
                        symbol=sym,
                        old_code=old_code,
                        change_type=change_type,
                    )
                )

    return changed_symbols


def _get_git_file_content(repo_path: str, commit_sha: str, rel_path: str) -> Optional[str]:
    """Retrieve file content from a specific git commit."""
    try:
        proc = subprocess.run(
            ["git", "show", f"{commit_sha}:{rel_path}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        return proc.stdout
    except Exception:
        return None

"""
Patch generator and applicator for DocSync proposed repairs.
Supports exporting unified diffs and applying them safely for Tier B remediation.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List
from docsync.models import RunResult


def extract_unified_patches(result: RunResult) -> str:
    """Extract and aggregate all proposed repair unified diffs into a single patch."""
    patches = []
    for item in result.items:
        if item.decision.decision == "DRIFT" and item.repair and item.repair.unified_diff:
            diff = item.repair.unified_diff.strip()
            if diff:
                patches.append(diff)
    return "\n\n".join(patches) + "\n" if patches else ""


def print_suggested_diffs(result: RunResult) -> None:
    """Print suggested diff repairs to standard output."""
    drift_items = [it for it in result.items if it.decision.decision == "DRIFT" and it.repair]
    if not drift_items:
        sys.stdout.write("[DocSync suggest] No repair suggestions available.\n")
        return

    sys.stdout.write(f"[DocSync suggest] Found {len(drift_items)} proposed repair diff(s):\n\n")
    for idx, it in enumerate(drift_items, 1):
        sym = it.changed_symbol.symbol
        doc = it.candidate_doc
        sys.stdout.write(f"--- Suggestion #{idx} for {doc.file} (Triggered by {sym.name}) ---\n")
        if it.repair and it.repair.unified_diff:
            sys.stdout.write(it.repair.unified_diff + "\n\n")
        else:
            sys.stdout.write("(No unified diff generated)\n\n")


def write_or_apply_patch(
    result: RunResult,
    out_file: str,
    apply: bool = False,
    repo_path: str = ".",
) -> Dict[str, Any]:
    """
    Write proposed diff repairs to a patch file, and optionally apply it via git.
    Never modifies source code; only targets documentation files.
    """
    patch_text = extract_unified_patches(result)
    out_p = Path(out_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    out_p.write_text(patch_text, encoding="utf-8")
    
    status = {"file": str(out_p), "bytes": len(patch_text.encode("utf-8")), "applied": False}

    if not patch_text.strip():
        sys.stdout.write(f"[DocSync apply-patch] Wrote empty patch file to {out_p} (no diffs found).\n")
        return status

    sys.stdout.write(f"[DocSync apply-patch] Wrote {len(patch_text.splitlines())} lines to {out_p}\n")

    if apply:
        # Check that patch only touches doc files (.md, .rst, .txt)
        is_safe = True
        for line in patch_text.splitlines():
            if line.startswith("+++ ") or line.startswith("--- "):
                target = line.split()[-1]
                if not any(target.endswith(ext) for ext in [".md", ".rst", ".txt", "/dev/null"]):
                    is_safe = False
                    sys.stderr.write(f"[DocSync apply-patch] Refusing to apply patch touching non-doc file: {target}\n")
                    break

        if not is_safe:
            status["error"] = "Security guard: patch touches non-documentation files"
            return status

        try:
            cmd = ["git", "apply", str(out_p.resolve())]
            res = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
            sys.stdout.write(f"[DocSync apply-patch] Successfully applied patch {out_p} to repository {repo_path}\n")
            status["applied"] = True
        except subprocess.CalledProcessError as e:
            sys.stderr.write(f"[DocSync apply-patch] Failed to apply git patch: {e.stderr}\n")
            status["error"] = e.stderr

    return status

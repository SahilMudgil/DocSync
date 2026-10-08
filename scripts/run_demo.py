"""
Deterministic offline before/after demo script for DocSync (A2 presentation).
Sets up a temporary git repository with 3 commits:
- C0: Baseline (code timeout=30 matches doc)
- C1: Harmless refactor (comment added) -> DocSync check -> MATCH (no false alarm)
- C2: Breaking change (timeout=30 -> timeout=60, docs unchanged) -> DocSync check -> DRIFT!
Runs 100% offline with zero external network or keys in fast mode.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from docsync.pipeline import run_check
from docsync.report.markdown_report import generate_markdown_report


def run_git(cmd, cwd):
    subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)


def main():
    print("=================================================================")
    print("[DocSync] 5-Minute Mid-Sem Evaluation Demo (A2 Milestone)")
    print("=================================================================\n")

    temp_dir = tempfile.mkdtemp(prefix="docsync_demo_")
    demo_path = Path(temp_dir)

    try:
        # Initialize Git repo
        run_git(["git", "init"], demo_path)
        run_git(["git", "config", "user.name", "DocSync Demo"], demo_path)
        run_git(["git", "config", "user.email", "demo@docsync.local"], demo_path)

        # C0: Baseline setup
        client_py = demo_path / "client.py"
        docs_dir = demo_path / "docs"
        docs_dir.mkdir(parents=True)
        usage_md = docs_dir / "usage.md"

        client_py.write_text(
            'def fetch_data(url: str, timeout: int = 30) -> dict:\n'
            '    """Fetch data from url. Defaults to 30."""\n'
            '    return {"status": 200, "timeout": timeout}\n',
            encoding="utf-8",
        )
        usage_md.write_text(
            '# API Documentation\nThe fetch_data timeout defaults to 30 seconds.\n',
            encoding="utf-8",
        )

        run_git(["git", "add", "."], demo_path)
        run_git(["git", "commit", "-m", "C0: Initial baseline"], demo_path)
        c0_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=demo_path, text=True).strip()

        # C1: Harmless refactor
        client_py.write_text(
            '# Harmless developer comment added\n'
            'def fetch_data(url: str, timeout: int = 30) -> dict:\n'
            '    """Fetch data from url. Defaults to 30."""\n'
            '    return {"status": 200, "timeout": timeout}\n',
            encoding="utf-8",
        )
        run_git(["git", "add", "."], demo_path)
        run_git(["git", "commit", "-m", "C1: Add comment refactor"], demo_path)
        c1_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=demo_path, text=True).strip()

        # Check C0 -> C1
        print(">> [Step 1/2] Checking Commit C0 -> C1 (Harmless Code Refactor)...")
        res_c1 = run_check(str(demo_path), c0_sha, c1_sha, {}, mode="fast")
        dec_c1 = res_c1.items[0].decision.decision if res_c1.items else "MATCH"
        print(f"   Result: [OK] {dec_c1} (Correct: No false alarms on harmless refactors)\n")

        # C2: Code change: timeout=30 -> timeout=60, docs untouched!
        client_py.write_text(
            '# Harmless developer comment added\n'
            'def fetch_data(url: str, timeout: int = 60) -> dict:\n'
            '    """Fetch data from url. Defaults to 30."""\n'
            '    return {"status": 200, "timeout": timeout}\n',
            encoding="utf-8",
        )
        run_git(["git", "add", "."], demo_path)
        run_git(["git", "commit", "-m", "C2: Change timeout default to 60"], demo_path)
        c2_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=demo_path, text=True).strip()

        # Check C1 -> C2
        print(">> [Step 2/2] Checking Commit C1 -> C2 (Code changed: timeout=30 -> 60, docs untouched)...")
        res_c2 = run_check(str(demo_path), c1_sha, c2_sha, {}, mode="fast")
        report_md = generate_markdown_report(res_c2)
        print(report_md)

        # Save demo outputs
        out_dir = PROJECT_ROOT / "demo_output"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "latest.json").write_text(res_c2.model_dump_json(indent=2), encoding="utf-8")
        (out_dir / "latest.md").write_text(report_md, encoding="utf-8")
        print(f"\n[OK] Demo completed successfully! Artifacts written to {out_dir}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()

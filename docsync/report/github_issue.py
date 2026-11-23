"""
GitHub Issue creation for autonomous Sweep remediation flow.
Features strict loop guards to prevent recursive CI/bot loops.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from docsync.models import RunResult, DriftItemResult

BOT_SUBSTRINGS = ["[bot]", "sweep", "github-actions", "dependabot"]


def check_loop_guards(
    pr_author: Optional[str] = None,
    pr_branch: Optional[str] = None,
    pr_labels: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Check if issue creation should be skipped based on loop guards.
    Returns skip reason string if blocked, None if permitted.
    """
    # Guard 1: PR author is a bot
    if pr_author:
        lower_author = pr_author.lower()
        if any(bot in lower_author for bot in BOT_SUBSTRINGS):
            return f"Blocked by loop guard: PR author '{pr_author}' is an automated bot"

    # Guard 2: PR branch starts with sweep/
    if pr_branch and pr_branch.lower().startswith("sweep/"):
        return f"Blocked by loop guard: PR branch '{pr_branch}' originates from Sweep"

    # Guard 3: PR has label 'docsync-ignore'
    if pr_labels:
        lower_labels = [lbl.lower() for lbl in pr_labels]
        if "docsync-ignore" in lower_labels:
            return "Blocked by loop guard: PR marked with 'docsync-ignore' label"

    return None


def get_existing_open_issue_titles(repo: str, token: str) -> List[str]:
    """Fetch open issue titles from GitHub API for duplicate prevention."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DocSync-CI-Gate",
    }
    url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            issues = json.loads(resp.read().decode("utf-8"))
            return [it.get("title", "") for it in issues if "pull_request" not in it]
    except Exception as e:
        sys.stderr.write(f"[DocSync] Notice: could not fetch existing issues: {e}\n")
        return []


def open_sweep_issues(
    result: RunResult,
    label: str = "sweep",
    min_confidence: float = 0.8,
    dry_run: bool = False,
    pr_author: Optional[str] = None,
    pr_branch: Optional[str] = None,
    pr_labels: Optional[List[str]] = None,
    token: Optional[str] = None,
    repo: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Open GitHub issues for high-confidence drift items.
    Applies loop guards and prevents duplicate open issues.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    repo = repo or os.environ.get("GITHUB_REPOSITORY")
    pr_author = pr_author or os.environ.get("PR_AUTHOR")
    pr_branch = pr_branch or os.environ.get("PR_BRANCH")
    if not pr_labels and os.environ.get("PR_LABELS"):
        pr_labels = [l.strip() for l in os.environ["PR_LABELS"].split(",")]

    # Check PR-level loop guards
    block_reason = check_loop_guards(pr_author, pr_branch, pr_labels)
    if block_reason:
        sys.stdout.write(f"[DocSync open-issue] {block_reason}. Skipping.\n")
        return [{"status": "blocked", "reason": block_reason}]

    drift_items = [
        it for it in result.items
        if it.decision.decision == "DRIFT" and it.decision.confidence >= min_confidence
    ]

    if not drift_items:
        sys.stdout.write(f"[DocSync open-issue] No DRIFT items >= {min_confidence} confidence.\n")
        return []

    existing_titles = set()
    if token and repo and not dry_run:
        existing_titles = set(get_existing_open_issue_titles(repo, token))

    created_issues = []
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DocSync-CI-Gate",
        "Content-Type": "application/json",
    } if token else {}

    for it in drift_items:
        sym = it.changed_symbol.symbol
        doc = it.candidate_doc
        title = f"Sweep: update docs for {sym.name} in {doc.file}"

        # Guard 4: Duplicate open issue prevention
        if title in existing_titles:
            sys.stdout.write(f"[DocSync open-issue] Skip: Open issue already exists for '{title}'\n")
            created_issues.append({"title": title, "status": "skipped_duplicate"})
            continue

        body_lines = [
            f"### Automated Documentation Drift Alert: `{sym.name}`",
            f"DocSync detected documentation drift in `{doc.file}` (lines {doc.start_line}-{doc.end_line}) caused by changes in `{sym.file}`.",
            "",
            f"- **Symbol:** `{sym.name}` (`{sym.file}:{sym.start_line}`)",
            f"- **Confidence:** {it.decision.confidence:.2f}",
            f"- **Reason:** {it.decision.reason}",
            f"- **Evidence Tokens:** `{'`, `'.join(it.decision.evidence_ids)}`",
            "",
        ]

        if it.repair and it.repair.unified_diff:
            body_lines.extend([
                "### Proposed Fix",
                "```diff",
                it.repair.unified_diff,
                "```",
                "",
            ])

        body_lines.append("> Generated automatically by DocSync CI Gate for autonomous remediation.")
        body = "\n".join(body_lines)

        if dry_run or not token or not repo:
            sys.stdout.write(f"\n[DRY RUN] Would open issue:\nTitle: {title}\nLabels: [{label}]\nBody:\n{body}\n")
            created_issues.append({"title": title, "status": "dry_run", "body": body})
        else:
            url = f"https://api.github.com/repos/{repo}/issues"
            payload = json.dumps({
                "title": title,
                "body": body,
                "labels": [label],
            }).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    issue_url = resp_data.get("html_url")
                    issue_num = resp_data.get("number")
                    sys.stdout.write(f"[DocSync open-issue] Created issue #{issue_num}: {issue_url}\n")
                    created_issues.append({"title": title, "status": "created", "url": issue_url, "number": issue_num})
                    existing_titles.add(title)
            except Exception as e:
                sys.stderr.write(f"[DocSync open-issue] Failed to create issue '{title}': {e}\n")
                created_issues.append({"title": title, "status": "error", "error": str(e)})

    return created_issues

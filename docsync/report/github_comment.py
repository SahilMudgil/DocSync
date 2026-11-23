"""
GitHub PR comment posting and updating for DocSync.
Maintains a single de-duplicated comment per PR using a persistent HTML marker.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from docsync.models import RunResult
from docsync.report.markdown_report import generate_markdown_report

DOCSYNC_COMMENT_MARKER = "<!-- docsync-comment -->"


def post_or_update_pr_comment(
    result: RunResult,
    pr_number: Optional[int] = None,
    repo: Optional[str] = None,
    token: Optional[str] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Post or update a PR comment with DocSync drift report.
    If credentials/PR are missing or dry_run is True, prints dry-run to stdout.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    repo = repo or os.environ.get("GITHUB_REPOSITORY")
    if not pr_number and os.environ.get("PR_NUMBER"):
        try:
            pr_number = int(os.environ["PR_NUMBER"])
        except ValueError:
            pr_number = None

    markdown_body = f"{DOCSYNC_COMMENT_MARKER}\n" + generate_markdown_report(result)

    if dry_run or not token or not repo or not pr_number:
        sys.stdout.write("[DocSync PR Comment - Dry Run Mode]\n")
        sys.stdout.write(markdown_body + "\n")
        return {"status": "dry_run", "body": markdown_body}

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DocSync-CI-Gate",
        "Content-Type": "application/json",
    }

    # 1. Search for existing DocSync comment on this PR
    comments_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    req = urllib.request.Request(comments_url, headers=headers, method="GET")
    
    existing_comment_id = None
    try:
        with urllib.request.urlopen(req) as resp:
            comments = json.loads(resp.read().decode("utf-8"))
            for c in comments:
                if DOCSYNC_COMMENT_MARKER in c.get("body", ""):
                    existing_comment_id = c.get("id")
                    break
    except urllib.error.HTTPError as e:
        sys.stderr.write(f"[DocSync] Warning: Failed to query PR comments: {e}\n")

    # 2. Update existing or create new comment
    if existing_comment_id:
        update_url = f"https://api.github.com/repos/{repo}/issues/comments/{existing_comment_id}"
        payload = json.dumps({"body": markdown_body}).encode("utf-8")
        patch_req = urllib.request.Request(update_url, data=payload, headers=headers, method="PATCH")
        with urllib.request.urlopen(patch_req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            return {"status": "updated", "id": existing_comment_id, "url": res_data.get("html_url")}
    else:
        payload = json.dumps({"body": markdown_body}).encode("utf-8")
        post_req = urllib.request.Request(comments_url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(post_req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            return {"status": "created", "id": res_data.get("id"), "url": res_data.get("html_url")}

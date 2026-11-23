"""
Command Line Interface (CLI) for DocSync.
Provides commands:
- check: Run full drift detection pipeline on PR commits
- ask: Interactive repository Code Q&A bot
- analyze: List changed functions between commits
- report: Render Markdown summary from JSON result
- comment: Post or update PR comment on GitHub
- open-issue: Open remediation issues for Sweep with loop guards
- suggest: Print proposed diff repairs
- apply-patch: Export proposed diffs to a patch file or apply them
"""

import argparse
import json
import sys
from pathlib import Path
from docsync.config import load_config, _load_env_file
from docsync.pipeline import run_check
from docsync.report.markdown_report import generate_markdown_report
from docsync.report.github_comment import post_or_update_pr_comment
from docsync.report.github_issue import open_sweep_issues
from docsync.report.patch import print_suggested_diffs, write_or_apply_patch
from docsync.models import RunResult
from docsync.ingest.code_parser import parse_python_file
from docsync.ingest.doc_parser import parse_doc_file, extract_docstring_chunks
from docsync.rag.qa_bot import RepositoryQABot


def main():
    _load_env_file()
    parser = argparse.ArgumentParser(
        prog="docsync",
        description="DocSync: AI-Assisted Documentation Drift Detection & Code Q&A Gate"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. check command
    check_parser = subparsers.add_parser("check", help="Run drift detection check between two Git commits")
    check_parser.add_argument("--repo", default=".", help="Path to repository")
    check_parser.add_argument("--base", required=True, help="Base commit SHA")
    check_parser.add_argument("--head", required=True, help="Head commit SHA")
    check_parser.add_argument("--mode", choices=["fast", "full"], default="fast", help="Execution mode (fast=rule-based, full=LLM)")
    check_parser.add_argument("--config", default="config/default.yaml", help="Path to YAML config")
    check_parser.add_argument("--out", default="results", help="Output directory for reports")
    check_parser.add_argument("--strict", action="store_true", help="Exit code 1 if high-confidence drift found")

    # 2. ask command (Repository Code Q&A Bot)
    ask_parser = subparsers.add_parser("ask", help="Query the repository code & docs using RAG")
    ask_parser.add_argument("query", help="Question about code or documentation")
    ask_parser.add_argument("--repo", default=".", help="Path to repository")
    ask_parser.add_argument("--provider", default="fake", choices=["fake", "gemini", "ollama"], help="LLM provider")

    # 3. report command
    rep_parser = subparsers.add_parser("report", help="Render Markdown report from a JSON result file")
    rep_parser.add_argument("--input", required=True, help="Path to run result JSON file")

    # 4. comment command
    com_parser = subparsers.add_parser("comment", help="Post or update PR comment on GitHub")
    com_parser.add_argument("--input", required=True, help="Path to run result JSON file")
    com_parser.add_argument("--pr", type=int, required=False, help="PR number")
    com_parser.add_argument("--repo", required=False, help="Target GitHub repository (owner/repo)")
    com_parser.add_argument("--dry-run", action="store_true", help="Print comment to stdout instead of posting")

    # 5. open-issue command (for Sweep / automated remediation)
    issue_parser = subparsers.add_parser("open-issue", help="Open GitHub remediation issues for Sweep with loop guards")
    issue_parser.add_argument("--input", required=True, help="Path to run result JSON file")
    issue_parser.add_argument("--label", default="sweep", help="Label to attach to created issues")
    issue_parser.add_argument("--min-confidence", type=float, default=0.8, help="Minimum drift confidence threshold")
    issue_parser.add_argument("--dry-run", action="store_true", help="Simulate issue creation without calling GitHub API")

    # 6. suggest command
    sug_parser = subparsers.add_parser("suggest", help="Print proposed documentation repair diffs")
    sug_parser.add_argument("--input", required=True, help="Path to run result JSON file")

    # 7. apply-patch command
    patch_parser = subparsers.add_parser("apply-patch", help="Write proposed diffs to a patch file or apply them")
    patch_parser.add_argument("--input", required=True, help="Path to run result JSON file")
    patch_parser.add_argument("--out", default="demo/patches/drift_repair.patch", help="Path to output patch file")
    patch_parser.add_argument("--apply", action="store_true", help="Apply patch directly to repository workspace")
    patch_parser.add_argument("--repo", default=".", help="Repository root path")

    # 8. evaluate command (E1-E6 Benchmark Experiments)
    eval_parser = subparsers.add_parser("evaluate", help="Run empirical benchmark experiments (E1-E6)")
    eval_parser.add_argument("--config", default="experiments/configs/smoke.yaml", help="Path to evaluation YAML config")
    eval_parser.add_argument("--smoke", action="store_true", help="Run on 6-case smoke set")

    # 9. prompt-lab command (Prompt Engineering & Model Comparison)
    plab_parser = subparsers.add_parser("prompt-lab", help="Run Prompt Lab tasks (completion, refactor, explain, V1 vs V2)")
    plab_parser.add_argument("--provider", default="fake", choices=["fake", "gemini", "ollama"], help="LLM Provider")
    plab_parser.add_argument("--model", default="gemini-1.5-flash", help="Model name or tag")
    plab_parser.add_argument("--out", default="experiments/results", help="Directory for JSON results")

    args = parser.parse_args()

    if args.command == "check":
        cfg = load_config(args.config)
        result = run_check(args.repo, args.base, args.head, cfg, mode=args.mode)
        
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        
        json_path = out_dir / f"run_{result.run_id}.json"
        md_path = out_dir / f"run_{result.run_id}.md"
        latest_json = out_dir / "latest.json"
        latest_md = out_dir / "latest.md"

        json_data = result.model_dump_json(indent=2)
        md_text = generate_markdown_report(result)

        json_path.write_text(json_data, encoding="utf-8")
        md_path.write_text(md_text, encoding="utf-8")
        latest_json.write_text(json_data, encoding="utf-8")
        latest_md.write_text(md_text, encoding="utf-8")

        print(md_text)
        print(f"\n[DocSync] Results saved to {json_path} and {md_path}")

        if args.strict:
            has_drift = any(
                it.decision.decision == "DRIFT" and it.decision.confidence >= 0.8
                for it in result.items
            )
            if has_drift:
                sys.exit(1)

    elif args.command == "ask":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        repo_root = Path(args.repo).resolve()
        chunks = []
        for py_file in repo_root.rglob("*.py"):
            if "venv" not in str(py_file) and ".git" not in str(py_file):
                syms = parse_python_file(str(py_file), repo_root=str(repo_root))
                chunks.extend(extract_docstring_chunks(syms))
        for doc_file in list(repo_root.rglob("*.md")):
            if "venv" not in str(doc_file) and ".git" not in str(doc_file):
                chunks.extend(parse_doc_file(str(doc_file), repo_root=str(repo_root)))

        bot = RepositoryQABot(chunks, provider=args.provider)
        resp = bot.answer_query(args.query)
        print(f"\n[DocSync Q&A Bot Answer]:\n{resp['answer']}\n")
        print("[Citations]:")
        for cite in resp["citations"]:
            print(f"- {cite['file']}:{cite['lines']}")

    elif args.command == "report":
        p = Path(args.input)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            res = RunResult(**data)
            print(generate_markdown_report(res))
        else:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(2)

    elif args.command == "comment":
        p = Path(args.input)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            res = RunResult(**data)
            post_or_update_pr_comment(
                result=res,
                pr_number=args.pr,
                repo=args.repo,
                dry_run=args.dry_run,
            )
        else:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(2)

    elif args.command == "open-issue":
        p = Path(args.input)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            res = RunResult(**data)
            open_sweep_issues(
                result=res,
                label=args.label,
                min_confidence=args.min_confidence,
                dry_run=args.dry_run,
            )
        else:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(2)

    elif args.command == "suggest":
        p = Path(args.input)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            res = RunResult(**data)
            print_suggested_diffs(res)
        else:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(2)

    elif args.command == "apply-patch":
        p = Path(args.input)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            res = RunResult(**data)
            write_or_apply_patch(
                result=res,
                out_file=args.out,
                apply=args.apply,
                repo_path=args.repo,
            )
        else:
            print(f"Error: file not found: {args.input}", file=sys.stderr)
            sys.exit(2)

    elif args.command == "evaluate":
        from docsync.eval.run_experiment import run_experiment_suite
        cfg_path = "experiments/configs/smoke.yaml" if args.smoke else args.config
        res = run_experiment_suite(cfg_path)
        print(f"\n[DocSync Evaluation Finished]")
        print(f"JSON Output: {res['json_path']}")
        print(f"Markdown Report: {res['md_path']}\n")
        print(res["md_path"].read_text(encoding="utf-8"))

    elif args.command == "prompt-lab":
        from docsync.eval.prompt_lab import run_prompt_lab
        res = run_prompt_lab(provider=args.provider, model_name=args.model, out_dir=args.out)
        print(f"\n[DocSync Prompt Lab Finished]")
        print(f"JSON Output: {res['json_path']}")
        print(f"Markdown Report: {res['md_path']}\n")
        print(res["md_path"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

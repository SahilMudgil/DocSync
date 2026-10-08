"""
Command Line Interface (CLI) for DocSync.
Provides commands:
- check: Run full drift detection pipeline on PR commits
- ask: Interactive repository Code Q&A bot
- analyze: List changed functions between commits
- report: Render Markdown summary from JSON result
"""

import argparse
import json
import sys
from pathlib import Path
from docsync.config import load_config, _load_env_file
from docsync.pipeline import run_check
from docsync.report.markdown_report import generate_markdown_report
from docsync.models import RunResult
from docsync.ingest.code_parser import parse_python_file
from docsync.ingest.doc_parser import parse_doc_file, extract_docstring_chunks
from docsync.rag.qa_bot import RepositoryQABot


def main():
    _load_env_file()
    parser = argparse.ArgumentParser(prog="docsync", description="DocSync: AI-Assisted Documentation Drift Detection & Code Q&A")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. check command
    check_parser = subparsers.add_parser("check", help="Run drift detection check between two Git commits")
    check_parser.add_argument("--repo", default=".", help="Path to repository")
    check_parser.add_argument("--base", required=True, help="Base commit SHA")
    check_parser.add_argument("--head", required=True, help="Head commit SHA")
    check_parser.add_argument("--mode", choices=["fast", "full"], default="fast", help="Execution mode (fast=rule-based, full=LLM)")
    check_parser.add_argument("--config", default="config/default.yaml", help="Path to YAML config")
    check_parser.add_argument("--out", default="results", help="Output directory for reports")

    # 2. ask command (Repository Code Q&A Bot)
    ask_parser = subparsers.add_parser("ask", help="Query the repository code & docs using RAG")
    ask_parser.add_argument("query", help="Question about code or documentation")
    ask_parser.add_argument("--repo", default=".", help="Path to repository")
    ask_parser.add_argument("--provider", default="fake", choices=["fake", "gemini", "ollama"], help="LLM provider")

    # 3. report command
    rep_parser = subparsers.add_parser("report", help="Render Markdown report from a JSON result file")
    rep_parser.add_argument("--input", required=True, help="Path to run result JSON file")

    # 4. comment command
    com_parser = subparsers.add_parser("comment", help="Output PR comment markdown (or dry run)")
    com_parser.add_argument("--input", required=True, help="Path to run result JSON file")
    com_parser.add_argument("--pr", required=False, help="PR number")

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

    elif args.command == "comment":
        p = Path(args.input)
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            res = RunResult(**data)
            print(generate_markdown_report(res))


if __name__ == "__main__":
    main()

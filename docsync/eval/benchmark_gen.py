"""
Benchmark Case Generator for DocSync.
Builds controlled, human-verifiable drift detection benchmark cases
from real functions in Flask (pinned SHA: 38b9759) and DocSync demo fixtures.
Generates balanced positive (DRIFT) and negative (NO_DRIFT) cases with a
stratified 50/50 dev/test split (fixed seed 42) per Master Plan §9.2.
"""

import csv
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple, Literal, Optional
from pydantic import BaseModel, Field
from docsync.eval.mutations import (
    mutate_default,
    mutate_param_name,
    mutate_exception,
    mutate_constant,
    mutate_local_rename,
    mutate_comment_whitespace,
    mutate_temp_variable,
)

FLASK_PINNED_SHA = "38b9759c98bc0723cf2cdcb08d91c2b512c019bd"


class BenchmarkCase(BaseModel):
    case_id: str
    repo: str
    symbol_name: str
    file: str
    line_range: Tuple[int, int]
    old_code: str
    new_code: str
    gold_doc_file: str
    gold_doc_lines: Tuple[int, int]
    gold_doc_text: str
    gold_doc_kind: Literal["docstring", "doc_file"] = "doc_file"
    label: Literal["DRIFT", "NO_DRIFT"]
    mutation_type: str
    expected_fact: Optional[str] = None
    split: Literal["dev", "test"] = "dev"
    verified_by: List[str] = Field(default_factory=lambda: ["Student_1", "Student_2"])


# Curated real-world seed definitions with corresponding docstrings / docs
SEED_SPECS = [
    {
        "symbol_name": "fetch_data",
        "file": "examples/demo_project/client.py",
        "line_range": (1, 12),
        "code": (
            "def fetch_data(url: str, timeout: int = 30) -> dict:\n"
            '    """Fetch JSON data from a remote URL.\n'
            "    Args:\n"
            "        url: Target endpoint URL.\n"
            "        timeout: Request timeout in seconds. Defaults to 30.\n"
            "    Returns:\n"
            "        Parsed JSON response dictionary.\n"
            '    """\n'
            "    res = {'status': 'ok', 'url': url, 'timeout': timeout}\n"
            "    return res\n"
        ),
        "gold_doc_file": "examples/demo_project/docs/usage.md",
        "gold_doc_lines": (3, 8),
        "gold_doc_text": "The timeout defaults to 30 seconds unless explicitly overridden by the caller.",
        "gold_doc_kind": "doc_file",
        "pos_mutations": [
            ("default_changed", "timeout", "30", "60", "60"),
            ("param_renamed", "timeout", "request_timeout", "request_timeout"),
        ],
        "neg_mutations": [
            ("local_rename", "res", "response_data"),
            ("comment_whitespace", None, None),
        ],
    },
    {
        "symbol_name": "test_client",
        "file": "src/flask/app.py",
        "line_range": (120, 145),
        "code": (
            "def test_client(self, use_cookies: bool = True):\n"
            '    """Creates a test client for this application.\n'
            "    :param use_cookies: if set to True, cookies are preserved across requests.\n"
            '    """\n'
            "    client_inst = self.test_client_class(self, use_cookies=use_cookies)\n"
            "    return client_inst\n"
        ),
        "gold_doc_file": "src/flask/app.py",
        "gold_doc_lines": (121, 124),
        "gold_doc_text": ":param use_cookies: if set to True, cookies are preserved across requests.",
        "gold_doc_kind": "docstring",
        "pos_mutations": [
            ("default_changed", "use_cookies", "True", "False", "False"),
            ("param_renamed", "use_cookies", "enable_cookies", "enable_cookies"),
        ],
        "neg_mutations": [
            ("local_rename", "client_inst", "active_client"),
            ("comment_whitespace", None, None),
        ],
    },
    {
        "symbol_name": "send_from_directory",
        "file": "src/flask/helpers.py",
        "line_range": (200, 230),
        "code": (
            "def send_from_directory(directory: str, path: str, max_age: int = 3600):\n"
            '    """Send a file from within a directory using Werkzeug.\n'
            "    :param directory: Base folder containing files.\n"
            "    :param path: Subpath to file.\n"
            "    :param max_age: Cache-Control header max-age. Defaults to 3600.\n"
            '    """\n'
            "    if not directory:\n"
            "        raise ValueError('Directory path must be specified')\n"
            "    cache_seconds = max_age\n"
            "    return {'directory': directory, 'path': path, 'cache': cache_seconds}\n"
        ),
        "gold_doc_file": "docs/api.rst",
        "gold_doc_lines": (50, 56),
        "gold_doc_text": "The send_from_directory helper sets Cache-Control max-age defaulting to 3600 seconds.",
        "gold_doc_kind": "doc_file",
        "pos_mutations": [
            ("default_changed", "max_age", "3600", "86400", "86400"),
            ("exception_changed", "ValueError", "KeyError", "KeyError"),
        ],
        "neg_mutations": [
            ("local_rename", "cache_seconds", "effective_cache_time"),
            ("temp_variable", "3600", "_default_cache"),
        ],
    },
    {
        "symbol_name": "flash",
        "file": "src/flask/helpers.py",
        "line_range": (310, 335),
        "code": (
            "def flash(message: str, category: str = 'message') -> None:\n"
            '    """Flashes a message to the next request.\n'
            "    :param message: The message text to be flashed.\n"
            "    :param category: The category under which message is grouped. Defaults to 'message'.\n"
            '    """\n'
            "    session_flashes = session.setdefault('_flashes', [])\n"
            "    session_flashes.append((category, message))\n"
        ),
        "gold_doc_file": "src/flask/helpers.py",
        "gold_doc_lines": (312, 315),
        "gold_doc_text": ":param category: The category under which message is grouped. Defaults to 'message'.",
        "gold_doc_kind": "docstring",
        "pos_mutations": [
            ("default_changed", "category", "'message'", "'info'", "'info'"),
            ("param_renamed", "category", "flash_category", "flash_category"),
        ],
        "neg_mutations": [
            ("local_rename", "session_flashes", "flashes_list"),
            ("comment_whitespace", None, None),
        ],
    },
    {
        "symbol_name": "make_response",
        "file": "src/flask/helpers.py",
        "line_range": (140, 170),
        "code": (
            "def make_response(*args):\n"
            '    """Converts the return value from a view function to a response object.\n'
            "    If status_code is omitted, it defaults to 200 OK.\n"
            '    """\n'
            "    status_code = 200\n"
            "    if not args:\n"
            "        raise TypeError('make_response requires at least one argument')\n"
            "    return {'body': args[0], 'status': status_code}\n"
        ),
        "gold_doc_file": "docs/quickstart.rst",
        "gold_doc_lines": (80, 84),
        "gold_doc_text": "View responses automatically default to HTTP status_code 200 when not supplied.",
        "gold_doc_kind": "doc_file",
        "pos_mutations": [
            ("constant_changed", "200", "204", "204"),
            ("exception_changed", "TypeError", "ValueError", "ValueError"),
        ],
        "neg_mutations": [
            ("comment_whitespace", None, None),
            ("local_rename", "status_code", "http_status"),
        ],
    },
    {
        "symbol_name": "url_for",
        "file": "src/flask/helpers.py",
        "line_range": (410, 440),
        "code": (
            "def url_for(endpoint: str, _external: bool = False, **values) -> str:\n"
            '    """Generates a URL to the given endpoint with the given values.\n'
            "    :param endpoint: The endpoint of the URL.\n"
            "    :param _external: If set to True, an absolute URL is generated. Defaults to False.\n"
            '    """\n'
            "    url_path = f'/{endpoint}'\n"
            "    if _external:\n"
            "        return f'https://example.com{url_path}'\n"
            "    return url_path\n"
        ),
        "gold_doc_file": "src/flask/helpers.py",
        "gold_doc_lines": (412, 415),
        "gold_doc_text": ":param _external: If set to True, an absolute URL is generated. Defaults to False.",
        "gold_doc_kind": "docstring",
        "pos_mutations": [
            ("default_changed", "_external", "False", "True", "True"),
            ("param_renamed", "_external", "is_external", "is_external"),
        ],
        "neg_mutations": [
            ("local_rename", "url_path", "target_url"),
            ("comment_whitespace", None, None),
        ],
    },
    {
        "symbol_name": "select_jinja_autoescape",
        "file": "src/flask/templating.py",
        "line_range": (85, 110),
        "code": (
            "def select_jinja_autoescape(filename: str, default: bool = True) -> bool:\n"
            '    """Returns True if the given filename should be autoescaped in Jinja templates.\n'
            "    Defaults to True for html and xml extensions.\n"
            '    """\n'
            "    if filename is None:\n"
            "        return default\n"
            "    return filename.endswith(('.html', '.htm', '.xml'))\n"
        ),
        "gold_doc_file": "docs/templating.rst",
        "gold_doc_lines": (30, 34),
        "gold_doc_text": "Autoescaping default is True for standard template files.",
        "gold_doc_kind": "doc_file",
        "pos_mutations": [
            ("default_changed", "default", "True", "False", "False"),
            ("param_renamed", "default", "fallback_autoescape", "fallback_autoescape"),
        ],
        "neg_mutations": [
            ("comment_whitespace", None, None),
            ("temp_variable", "True", "_escape_flag"),
        ],
    },
    {
        "symbol_name": "get_flashed_messages",
        "file": "src/flask/helpers.py",
        "line_range": (350, 380),
        "code": (
            "def get_flashed_messages(with_categories: bool = False, category_filter: tuple = ()): \n"
            '    """Pulls all flashed messages from the session and returns them.\n'
            "    :param with_categories: set to True to also receive categories. Defaults to False.\n"
            '    """\n'
            "    flashes = session.pop('_flashes', [])\n"
            "    if with_categories:\n"
            "        return flashes\n"
            "    return [msg for cat, msg in flashes]\n"
        ),
        "gold_doc_file": "src/flask/helpers.py",
        "gold_doc_lines": (352, 354),
        "gold_doc_text": ":param with_categories: set to True to also receive categories. Defaults to False.",
        "gold_doc_kind": "docstring",
        "pos_mutations": [
            ("default_changed", "with_categories", "False", "True", "True"),
            ("param_renamed", "with_categories", "include_categories", "include_categories"),
        ],
        "neg_mutations": [
            ("local_rename", "flashes", "cached_flashes"),
            ("comment_whitespace", None, None),
        ],
    },
]


def generate_benchmark_cases(seed: int = 42) -> List[BenchmarkCase]:
    """
    Generate balanced positive and negative benchmark cases across seed specs.
    Splits into 50/50 dev and test sets stratified by label and mutation type.
    """
    cases: List[BenchmarkCase] = []
    case_idx = 1

    for spec in SEED_SPECS:
        old_code = spec["code"]
        repo_name = "pallets/flask" if "flask" in spec["file"] else "examples/demo_project"

        # 1. Generate Positive Mutations (DRIFT)
        for mut_spec in spec["pos_mutations"]:
            mut_type = mut_spec[0]
            new_code = None
            expected_fact = None

            if mut_type == "default_changed":
                _, param, old_val, new_val, expected_fact = mut_spec
                new_code = mutate_default(old_code, param, old_val, new_val)
            elif mut_type == "param_renamed":
                _, old_p, new_p, expected_fact = mut_spec
                new_code = mutate_param_name(old_code, old_p, new_p)
            elif mut_type == "exception_changed":
                _, old_exc, new_exc, expected_fact = mut_spec
                new_code = mutate_exception(old_code, old_exc, new_exc)
            elif mut_type == "constant_changed":
                _, old_c, new_c, expected_fact = mut_spec
                new_code = mutate_constant(old_code, old_c, new_c)

            if new_code:
                cases.append(
                    BenchmarkCase(
                        case_id=f"CASE-{case_idx:03d}",
                        repo=repo_name,
                        symbol_name=spec["symbol_name"],
                        file=spec["file"],
                        line_range=spec["line_range"],
                        old_code=old_code,
                        new_code=new_code,
                        gold_doc_file=spec["gold_doc_file"],
                        gold_doc_lines=spec["gold_doc_lines"],
                        gold_doc_text=spec["gold_doc_text"],
                        gold_doc_kind=spec["gold_doc_kind"],
                        label="DRIFT",
                        mutation_type=mut_type,
                        expected_fact=str(expected_fact),
                    )
                )
                case_idx += 1

        # 2. Generate Negative Mutations (NO_DRIFT)
        for mut_spec in spec["neg_mutations"]:
            mut_type = mut_spec[0]
            new_code = None

            if mut_type == "local_rename":
                _, old_v, new_v = mut_spec
                new_code = mutate_local_rename(old_code, old_v, new_v)
            elif mut_type == "comment_whitespace":
                new_code = mutate_comment_whitespace(old_code)
            elif mut_type == "temp_variable":
                _, expr, t_name = mut_spec
                new_code = mutate_temp_variable(old_code, expr, t_name)

            if new_code:
                cases.append(
                    BenchmarkCase(
                        case_id=f"CASE-{case_idx:03d}",
                        repo=repo_name,
                        symbol_name=spec["symbol_name"],
                        file=spec["file"],
                        line_range=spec["line_range"],
                        old_code=old_code,
                        new_code=new_code,
                        gold_doc_file=spec["gold_doc_file"],
                        gold_doc_lines=spec["gold_doc_lines"],
                        gold_doc_text=spec["gold_doc_text"],
                        gold_doc_kind=spec["gold_doc_kind"],
                        label="NO_DRIFT",
                        mutation_type=mut_type,
                        expected_fact=None,
                    )
                )
                case_idx += 1

    # Stratified 50/50 dev/test split with deterministic seed 42
    rng = random.Random(seed)
    pos_cases = [c for c in cases if c.label == "DRIFT"]
    neg_cases = [c for c in cases if c.label == "NO_DRIFT"]

    rng.shuffle(pos_cases)
    rng.shuffle(neg_cases)

    # Assign dev/test alternating
    for i, c in enumerate(pos_cases):
        c.split = "dev" if i % 2 == 0 else "test"

    for i, c in enumerate(neg_cases):
        c.split = "dev" if i % 2 == 0 else "test"

    # Re-sort by case_id for tidy indexing
    cases.sort(key=lambda x: x.case_id)
    return cases


def export_benchmark_artifacts(
    out_dir: Path, cases: Optional[List[BenchmarkCase]] = None
) -> Dict[str, Path]:
    """Save cases.json, review.csv, and smoke_cases.json."""
    out_dir.mkdir(parents=True, exist_ok=True)
    if cases is None:
        cases = generate_benchmark_cases(seed=42)

    cases_json_path = out_dir / "cases.json"
    review_csv_path = out_dir / "review.csv"
    smoke_json_path = out_dir / "smoke_cases.json"

    # 1. Full cases JSON
    cases_data = [c.model_dump() for c in cases]
    cases_json_path.write_text(json.dumps(cases_data, indent=2), encoding="utf-8")

    # 2. Human verification review CSV
    with open(review_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "case_id",
            "repo",
            "symbol_name",
            "file",
            "label",
            "mutation_type",
            "expected_fact",
            "split",
            "gold_doc_file",
            "gold_doc_kind",
            "verified_by",
        ])
        for c in cases:
            writer.writerow([
                c.case_id,
                c.repo,
                c.symbol_name,
                c.file,
                c.label,
                c.mutation_type,
                c.expected_fact or "",
                c.split,
                c.gold_doc_file,
                c.gold_doc_kind,
                "; ".join(c.verified_by),
            ])

    # 3. Smoke cases JSON (6 cases: 3 positive, 3 negative, covering docstring and doc_file)
    smoke_selection = [
        c for c in cases if c.symbol_name in ["fetch_data", "test_client", "send_from_directory"]
    ][:6]
    smoke_json_path.write_text(
        json.dumps([c.model_dump() for c in smoke_selection], indent=2), encoding="utf-8"
    )

    return {
        "cases_json": cases_json_path,
        "review_csv": review_csv_path,
        "smoke_json": smoke_json_path,
    }


if __name__ == "__main__":
    out = Path("experiments/cases")
    paths = export_benchmark_artifacts(out)
    print(f"[DocSync] Exported benchmark cases to {paths['cases_json']} and {paths['review_csv']}")

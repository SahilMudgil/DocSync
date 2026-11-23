"""
Unit and Integration Tests for Phase 11: Benchmark Generation, Metrics & Experiments.
Verifies AST mutation operators, dataset balance, stratified dev/test splitting,
retrieval metrics (Recall@K, MRR), location overlap checking, and smoke test runner.
"""

import ast
import json
import csv
from pathlib import Path
import pytest

from docsync.eval.mutations import (
    mutate_default,
    mutate_param_name,
    mutate_exception,
    mutate_constant,
    mutate_local_rename,
    mutate_comment_whitespace,
    mutate_temp_variable,
    validate_python_code,
)
from docsync.eval.benchmark_gen import (
    generate_benchmark_cases,
    export_benchmark_artifacts,
)
from docsync.eval.metrics import (
    recall_at_k,
    mean_reciprocal_rank,
    check_location_overlap,
    wilson_interval,
    compute_classification_metrics,
)
from docsync.eval.run_experiment import run_experiment_suite


def test_positive_mutations_ast_validity():
    sample_code = (
        "def fetch(url: str, timeout: int = 30) -> dict:\n"
        "    if not url:\n"
        "        raise ValueError('URL required')\n"
        "    status = 200\n"
        "    return {'status': status, 'url': url}\n"
    )

    # 1. Default changed
    new_default = mutate_default(sample_code, "timeout", "30", "60")
    assert new_default is not None
    assert "timeout: int = 60" in new_default
    assert validate_python_code(new_default)

    # 2. Parameter renamed
    new_param = mutate_param_name(sample_code, "timeout", "request_timeout")
    assert new_param is not None
    assert "request_timeout: int = 30" in new_param
    assert validate_python_code(new_param)

    # 3. Exception changed
    new_exc = mutate_exception(sample_code, "ValueError", "KeyError")
    assert new_exc is not None
    assert "raise KeyError" in new_exc
    assert validate_python_code(new_exc)

    # 4. Constant changed
    new_const = mutate_constant(sample_code, "200", "204")
    assert new_const is not None
    assert "status = 204" in new_const
    assert validate_python_code(new_const)


def test_negative_mutations_ast_validity():
    sample_code = (
        "def process_items(items: list) -> int:\n"
        "    count = len(items)\n"
        "    return count\n"
    )

    # 1. Local rename
    new_local = mutate_local_rename(sample_code, "count", "total_elements")
    assert new_local is not None
    assert "total_elements = len(items)" in new_local
    assert validate_python_code(new_local)

    # 2. Comment / whitespace
    new_comm = mutate_comment_whitespace(sample_code)
    assert new_comm is not None
    assert "# Refactored" in new_comm
    assert validate_python_code(new_comm)

    # 3. Temp variable
    new_temp = mutate_temp_variable(sample_code, "len(items)", "_cached_len")
    assert new_temp is not None
    assert "_cached_len = len(items)" in new_temp
    assert validate_python_code(new_temp)


def test_benchmark_generation_and_balance():
    cases = generate_benchmark_cases(seed=42)
    assert len(cases) >= 30  # Master Plan requires >= 30 (target 40)

    pos_cases = [c for c in cases if c.label == "DRIFT"]
    neg_cases = [c for c in cases if c.label == "NO_DRIFT"]
    assert len(pos_cases) == len(neg_cases)  # Exact 50/50 balance

    dev_cases = [c for c in cases if c.split == "dev"]
    test_cases = [c for c in cases if c.split == "test"]
    assert len(dev_cases) == len(test_cases)  # Stratified 50/50 split

    # Check case attributes
    for c in cases:
        assert c.case_id.startswith("CASE-")
        assert c.symbol_name != ""
        assert c.file != ""
        assert c.gold_doc_file != ""
        assert c.gold_doc_lines[0] <= c.gold_doc_lines[1]
        assert validate_python_code(c.old_code)
        assert validate_python_code(c.new_code)
        if c.label == "DRIFT":
            assert c.expected_fact is not None


def test_benchmark_artifacts_export(tmp_path):
    paths = export_benchmark_artifacts(tmp_path)
    assert paths["cases_json"].exists()
    assert paths["review_csv"].exists()
    assert paths["smoke_json"].exists()

    cases_data = json.loads(paths["cases_json"].read_text(encoding="utf-8"))
    assert len(cases_data) >= 30

    with open(paths["review_csv"], mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "case_id" in header
        assert "label" in header
        assert "verified_by" in header
        rows = list(reader)
        assert len(rows) == len(cases_data)


def test_retrieval_and_location_metrics():
    retrieved = [
        ["doc_a:1", "doc_b:5", "doc_c:10"],
        ["doc_x:1", "doc_y:2", "doc_z:3"],
    ]
    gold = ["doc_b:5", "doc_x:1"]

    assert recall_at_k(retrieved, gold, k=1) == 0.5   # 1/2 in top 1
    assert recall_at_k(retrieved, gold, k=2) == 1.0   # 2/2 in top 2
    assert mean_reciprocal_rank(retrieved, gold) == round((0.5 + 1.0) / 2, 4)

    # Location overlap tests
    assert check_location_overlap("src/helpers.py", (10, 20), "src\\helpers.py", (15, 25)) is True
    assert check_location_overlap("src/helpers.py", (10, 20), "src/helpers.py", (21, 30)) is False
    assert check_location_overlap("src/helpers.py", (10, 20), "docs/helpers.md", (10, 20)) is False


def test_smoke_experiment_suite_end_to_end(tmp_path):
    config_content = f"""
experiment_id: TEST_SMOKE
smoke_test: true
split: dev
cases_path: experiments/cases/smoke_cases.json
out_dir: {tmp_path.as_posix()}/results
reports_dir: {tmp_path.as_posix()}/reports

llm:
  provider: fake
  model: gemini-1.5-flash

retrieval:
  top_k: 2
  rrf_k: 60
"""
    cfg_file = tmp_path / "smoke_cfg.yaml"
    cfg_file.write_text(config_content, encoding="utf-8")

    result = run_experiment_suite(str(cfg_file))
    assert result["json_path"].exists()
    assert result["md_path"].exists()

    json_data = json.loads(result["json_path"].read_text(encoding="utf-8"))
    assert json_data["smoke_test"] is True
    assert "M1" in json_data["methods"]
    assert "M2" in json_data["methods"]
    assert "M3" in json_data["methods"]
    assert "BM25" in json_data["retrieval_comparison"]
    assert "Hybrid-3 (BM25+FAISS+Search)" in json_data["retrieval_comparison"]

    md_text = result["md_path"].read_text(encoding="utf-8")
    assert "SMOKE TEST — pipeline check only, NOT a result" in md_text
    assert "## E1: Method Comparison Matrix" in md_text
    assert "## E2: Retrieval Comparison" in md_text

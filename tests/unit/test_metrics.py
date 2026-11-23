"""
Unit tests for evaluation metrics and Wilson confidence intervals.
Verifies statistical formulas and edge case handling with hand-computed values.
"""

import pytest
from docsync.eval.metrics import wilson_interval, compute_classification_metrics


def test_wilson_interval_hand_computed():
    # Test case: 10 successes out of 20 trials (p_hat = 0.5)
    # With 95% confidence (z = 1.95996):
    # center = (0.5 + 1.95996^2 / 40) / (1 + 1.95996^2 / 20) = (0.5 + 0.09604) / (1 + 0.19207) = 0.59604 / 1.19207 = 0.5000
    # Wilson interval for 10/20 is approximately [0.2993, 0.7007]
    lower, upper = wilson_interval(10, 20, confidence=0.95)
    assert 0.29 <= lower <= 0.31
    assert 0.69 <= upper <= 0.71


def test_wilson_interval_zero_and_perfect_boundaries():
    # 0 successes out of 10
    lower_zero, upper_zero = wilson_interval(0, 10)
    assert lower_zero == 0.0
    assert 0.25 <= upper_zero <= 0.35

    # 10 successes out of 10
    lower_perf, upper_perf = wilson_interval(10, 10)
    assert 0.65 <= lower_perf <= 0.75
    assert upper_perf == 1.0

    # 0 trials edge case
    assert wilson_interval(0, 0) == (0.0, 0.0)


def test_classification_metrics_perfect():
    y_true = ["DRIFT", "DRIFT", "MATCH", "MATCH"]
    y_pred = ["DRIFT", "DRIFT", "MATCH", "MATCH"]
    res = compute_classification_metrics(y_true, y_pred, pos_label="DRIFT")

    assert res["tp"] == 2
    assert res["fp"] == 0
    assert res["tn"] == 2
    assert res["fn"] == 0
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1"] == 1.0
    assert res["accuracy"] == 1.0


def test_classification_metrics_confusion_matrix():
    # 2 TP, 1 FP, 1 FN, 2 TN
    y_true = ["DRIFT", "DRIFT", "DRIFT", "MATCH", "MATCH", "MATCH"]
    y_pred = ["DRIFT", "DRIFT", "MATCH", "DRIFT", "MATCH", "MATCH"]
    res = compute_classification_metrics(y_true, y_pred, pos_label="DRIFT")

    assert res["tp"] == 2
    assert res["fp"] == 1
    assert res["fn"] == 1
    assert res["tn"] == 2
    assert res["precision"] == round(2 / 3, 4)
    assert res["recall"] == round(2 / 3, 4)
    assert res["accuracy"] == round(4 / 6, 4)


def test_classification_metrics_zero_positives():
    y_true = ["MATCH", "MATCH"]
    y_pred = ["MATCH", "MATCH"]
    res = compute_classification_metrics(y_true, y_pred, pos_label="DRIFT")

    assert res["precision"] == 0.0
    assert res["recall"] == 0.0
    assert res["f1"] == 0.0
    assert res["accuracy"] == 1.0


def test_classification_metrics_length_mismatch():
    with pytest.raises(ValueError, match="Length mismatch"):
        compute_classification_metrics(["DRIFT"], ["DRIFT", "MATCH"])

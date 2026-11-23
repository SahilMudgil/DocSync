"""
Evaluation metrics and statistical helpers for DocSync benchmark runs.
Includes accuracy, precision, recall, F1, and Wilson score confidence intervals.
"""

import math
from typing import List, Dict, Any, Tuple


def wilson_interval(successes: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """
    Calculate the Wilson score confidence interval for a binomial proportion.
    Standard formula used for small sample evaluation in E1-E6.
    
    Args:
        successes: Number of successful outcomes (k)
        n: Total number of trials
        confidence: Confidence level (default 0.95 -> z = 1.95996)
        
    Returns:
        (lower_bound, upper_bound) clamped to [0.0, 1.0]
    """
    if n <= 0:
        return (0.0, 0.0)

    # z-scores for common confidence levels
    z_map = {0.90: 1.64485, 0.95: 1.95996, 0.99: 2.57583}
    z = z_map.get(confidence, 1.95996)

    p_hat = successes / n
    z2 = z * z
    denom = 1.0 + (z2 / n)
    center = (p_hat + (z2 / (2.0 * n))) / denom
    spread = (z / denom) * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z2 / (4.0 * n * n)))

    lower = max(0.0, center - spread)
    upper = min(1.0, center + spread)
    return (round(lower, 4), round(upper, 4))


def compute_classification_metrics(
    y_true: List[str],
    y_pred: List[str],
    pos_label: str = "DRIFT",
) -> Dict[str, Any]:
    """
    Compute binary classification metrics for drift detection evaluations.
    Handles MATCH vs DRIFT (and UNCERTAIN treated as non-positive).
    
    Returns:
        Dictionary with TP, FP, TN, FN, Precision, Recall, F1, Accuracy,
        and 95% Wilson intervals.
    """
    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: y_true ({len(y_true)}) != y_pred ({len(y_pred)})")

    n = len(y_true)
    if n == 0:
        return {
            "n": 0,
            "tp": 0, "fp": 0, "tn": 0, "fn": 0,
            "precision": 0.0, "recall": 0.0, "f1": 0.0, "accuracy": 0.0,
            "precision_ci95": (0.0, 0.0),
            "recall_ci95": (0.0, 0.0),
            "accuracy_ci95": (0.0, 0.0),
        }

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for yt, yp in zip(y_true, y_pred):
        is_true_pos = (yt == pos_label)
        is_pred_pos = (yp == pos_label)

        if is_true_pos and is_pred_pos:
            tp += 1
        elif not is_true_pos and is_pred_pos:
            fp += 1
        elif not is_true_pos and not is_pred_pos:
            tn += 1
        elif is_true_pos and not is_pred_pos:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2.0 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / n

    return {
        "n": n,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "precision_ci95": wilson_interval(tp, tp + fp) if (tp + fp) > 0 else (0.0, 0.0),
        "recall_ci95": wilson_interval(tp, tp + fn) if (tp + fn) > 0 else (0.0, 0.0),
        "accuracy_ci95": wilson_interval(tp + tn, n),
    }


def recall_at_k(retrieved_ids_list: List[List[str]], gold_ids: List[str], k: int) -> float:
    """
    Compute Recall@K across evaluation queries.
    Recall@K = Fraction of queries where the gold item is within the top-K retrieved.
    """
    if not retrieved_ids_list or len(retrieved_ids_list) != len(gold_ids):
        return 0.0

    hits = 0
    total = len(gold_ids)

    for retrieved, gold in zip(retrieved_ids_list, gold_ids):
        top_slice = retrieved[:k]
        if gold in top_slice:
            hits += 1

    return round(hits / total, 4) if total > 0 else 0.0


def mean_reciprocal_rank(retrieved_ids_list: List[List[str]], gold_ids: List[str]) -> float:
    """
    Compute Mean Reciprocal Rank (MRR).
    MRR = (1 / |Q|) * sum_{i=1}^{|Q|} (1 / rank_i), where rank_i is 1-indexed.
    If the gold item is not retrieved, reciprocal rank is 0.
    """
    if not retrieved_ids_list or len(retrieved_ids_list) != len(gold_ids):
        return 0.0

    reciprocal_ranks = []

    for retrieved, gold in zip(retrieved_ids_list, gold_ids):
        if gold in retrieved:
            rank = retrieved.index(gold) + 1  # 1-indexed
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    return round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4) if reciprocal_ranks else 0.0


def check_location_overlap(
    pred_file: str,
    pred_range: Tuple[int, int],
    gold_file: str,
    gold_range: Tuple[int, int],
) -> bool:
    """
    Verify if predicted doc chunk matches the gold ground truth location.
    Requires identical file path (normalizing separators) and intersecting line ranges.
    """
    norm_pred = pred_file.replace("\\", "/").strip().lower()
    norm_gold = gold_file.replace("\\", "/").strip().lower()

    if not (norm_pred == norm_gold or norm_pred.endswith(norm_gold) or norm_gold.endswith(norm_pred)):
        return False

    p_start, p_end = pred_range
    g_start, g_end = gold_range

    # Ranges overlap if max(start1, start2) <= min(end1, end2)
    return max(p_start, g_start) <= min(p_end, g_end)


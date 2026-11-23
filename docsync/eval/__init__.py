"""
Evaluation and benchmark subpackage for DocSync.
"""
from docsync.eval.metrics import wilson_interval, compute_classification_metrics

__all__ = ["wilson_interval", "compute_classification_metrics"]

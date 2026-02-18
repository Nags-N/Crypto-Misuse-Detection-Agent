"""
metrics.py — Compute classification metrics for crypto-misuse detection.

Usage:
    from evaluation.metrics import compute_metrics

    results = compute_metrics(y_true, y_pred)
    # {'accuracy': 0.85, 'precision': 0.80, 'recall': 0.90, 'f1': 0.85}
"""

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from typing import List


def compute_metrics(
    y_true: List[str],
    y_pred: List[str],
    pos_label: str = "insecure",
) -> dict:
    """
    Compute standard classification metrics.

    Args:
        y_true:    Ground-truth labels.
        y_pred:    Predicted labels.
        pos_label: The label considered as the positive class.
                   Defaults to 'insecure' (detecting misuse is the goal).

    Returns:
        Dict with keys: accuracy, precision, recall, f1.
    """
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(
            precision_score(y_true, y_pred, pos_label=pos_label, zero_division=0), 4
        ),
        "recall": round(
            recall_score(y_true, y_pred, pos_label=pos_label, zero_division=0), 4
        ),
        "f1": round(
            f1_score(y_true, y_pred, pos_label=pos_label, zero_division=0), 4
        ),
    }

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
    confusion_matrix
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

def compute_confusion_matrix(y_true: List[str], y_pred: List[str], labels=["secure", "insecure"]) -> dict:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    if cm.shape == (2, 2):
        return {
            "tn": int(cm[0][0]),
            "fp": int(cm[0][1]),
            "fn": int(cm[1][0]),
            "tp": int(cm[1][1])
        }
    return {}

def confidence_calibration_score(reports: List[dict], y_true: List[str]) -> dict:
    """Compare accuracy of high vs low confidence predictions."""
    high_t, high_p = [], []
    low_t, low_p = [], []
    
    for report, true_lbl in zip(reports, y_true):
        conf = report.get("confidence", "low").lower()
        pred = report.get("label", "unknown").lower()
        if conf == "high":
            high_t.append(true_lbl)
            high_p.append(pred)
        else:
            low_t.append(true_lbl)
            low_p.append(pred)
            
    high_acc = accuracy_score(high_t, high_p) if high_t else 0.0
    low_acc = accuracy_score(low_t, low_p) if low_t else 0.0
    
    return {
        "high_confidence_accuracy": round(high_acc, 4),
        "low_confidence_accuracy": round(low_acc, 4),
        "high_confidence_count": len(high_t),
        "low_confidence_count": len(low_t)
    }

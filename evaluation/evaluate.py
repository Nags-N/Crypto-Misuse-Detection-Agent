"""
evaluate.py — Evaluate baselines on the processed dataset and print results.

This module can be used standalone:
    python evaluation/evaluate.py

Or imported by scripts/run_baseline.py.
"""

import json
import os
import sys
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from evaluation.metrics import compute_metrics
from baselines.rule_based import predict_batch as rule_predict_batch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


def load_dataset(path: str) -> list:
    """Load a JSONL dataset file."""
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def print_results_table(results: dict) -> None:
    """
    Print evaluation results in a formatted table.

    Args:
        results: Dict mapping model_name → metrics dict.
    """
    header = f"{'Model':<30} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10}"
    separator = "─" * len(header)

    print()
    print(separator)
    print(header)
    print(separator)

    for model_name, metrics in results.items():
        print(
            f"{model_name:<30} "
            f"{metrics['accuracy']:>10.4f} "
            f"{metrics['precision']:>10.4f} "
            f"{metrics['recall']:>10.4f} "
            f"{metrics['f1']:>10.4f}"
        )

    print(separator)
    print()


def evaluate_rule_based(codes: list, labels: list) -> dict:
    """Run rule-based baseline and return metrics."""
    predictions = rule_predict_batch(codes)
    return compute_metrics(labels, predictions)


def evaluate_classifier(
    train_codes: list,
    train_labels: list,
    test_codes: list,
    test_labels: list,
    max_features: int = 5000,
    random_seed: int = 42,
) -> dict:
    """Train and evaluate TF-IDF + Logistic Regression classifier."""
    from baselines.simple_classifier import SimpleClassifier

    clf = SimpleClassifier(max_features=max_features, random_seed=random_seed)
    clf.train(train_codes, train_labels)
    predictions = clf.predict(test_codes)
    return compute_metrics(test_labels, predictions)


if __name__ == "__main__":
    import yaml

    config_path = os.path.join(PROJECT_ROOT, "configs", "default.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    dataset_path = os.path.join(
        PROJECT_ROOT, config["dataset"]["processed_file"]
    )

    if not os.path.exists(dataset_path):
        logger.error(
            f"Dataset not found at {dataset_path}. "
            f"Run 'python scripts/prepare_data.py' first."
        )
        sys.exit(1)

    samples = load_dataset(dataset_path)
    codes = [s["code_snippet"] for s in samples]
    labels = [s["label"] for s in samples]

    results = {}

    # Rule-based
    logger.info("Evaluating rule-based baseline ...")
    results["Rule-Based"] = evaluate_rule_based(codes, labels)

    # TF-IDF + Logistic Regression
    from sklearn.model_selection import train_test_split

    seed = config.get("training", {}).get("random_seed", 42)
    split = config.get("training", {}).get("test_split", 0.2)
    max_feat = config.get("baselines", {}).get("simple_classifier", {}).get("max_features", 5000)

    train_codes, test_codes, train_labels, test_labels = train_test_split(
        codes, labels, test_size=split, random_state=seed, stratify=labels
    )

    logger.info("Evaluating TF-IDF + Logistic Regression ...")
    results["TF-IDF + LogReg"] = evaluate_classifier(
        train_codes, train_labels, test_codes, test_labels,
        max_features=max_feat, random_seed=seed,
    )

    print_results_table(results)

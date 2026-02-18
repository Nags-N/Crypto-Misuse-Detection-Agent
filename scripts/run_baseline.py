"""
run_baseline.py — Main entry point to run all baselines and print metrics.

Usage:
    python scripts/run_baseline.py

Reads config from configs/default.yaml, loads the processed dataset,
runs both baselines, and prints a comparison table.
"""

import json
import os
import sys
import logging

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import yaml
from sklearn.model_selection import train_test_split

from baselines.rule_based import predict_batch as rule_predict_batch
from baselines.simple_classifier import SimpleClassifier
from evaluation.metrics import compute_metrics
from evaluation.evaluate import print_results_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load default YAML configuration."""
    config_path = os.path.join(PROJECT_ROOT, "configs", "default.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_dataset(path: str) -> list:
    """Load a JSONL dataset file."""
    samples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def main():
    config = load_config()
    training_cfg = config.get("training", {})
    baselines_cfg = config.get("baselines", {})

    # ── Load dataset ─────────────────────────────────────────────
    dataset_path = os.path.join(
        PROJECT_ROOT, config["dataset"]["processed_file"]
    )

    if not os.path.exists(dataset_path):
        logger.error(
            f"Dataset not found: {dataset_path}\n"
            f"Run 'python scripts/prepare_data.py' first."
        )
        sys.exit(1)

    samples = load_dataset(dataset_path)
    logger.info(f"Loaded {len(samples)} samples from {dataset_path}")

    codes = [s["code_snippet"] for s in samples]
    labels = [s["label"] for s in samples]

    # ── Train / test split ───────────────────────────────────────
    seed = training_cfg.get("random_seed", 42)
    test_split = training_cfg.get("test_split", 0.2)

    train_codes, test_codes, train_labels, test_labels = train_test_split(
        codes, labels, test_size=test_split, random_state=seed, stratify=labels,
    )

    logger.info(
        f"Split: {len(train_codes)} train / {len(test_codes)} test "
        f"(seed={seed}, split={test_split})"
    )

    results = {}

    # ── Rule-based baseline ──────────────────────────────────────
    if baselines_cfg.get("rule_based", {}).get("enabled", True):
        logger.info("Running rule-based baseline ...")
        rule_preds = rule_predict_batch(test_codes)
        results["Rule-Based"] = compute_metrics(test_labels, rule_preds)

    # ── TF-IDF + Logistic Regression ─────────────────────────────
    if baselines_cfg.get("simple_classifier", {}).get("enabled", True):
        max_features = baselines_cfg.get("simple_classifier", {}).get(
            "max_features", 5000
        )
        logger.info("Training TF-IDF + Logistic Regression ...")
        clf = SimpleClassifier(
            max_features=max_features, random_seed=seed
        )
        clf.train(train_codes, train_labels)

        clf_preds = clf.predict(test_codes)
        results["TF-IDF + LogReg"] = compute_metrics(test_labels, clf_preds)

    # ── Print results ────────────────────────────────────────────
    print_results_table(results)


if __name__ == "__main__":
    main()

"""
prepare_data.py — Load, merge, and save datasets for the crypto-misuse pipeline.

Usage:
    python scripts/prepare_data.py

Reads datasets from data/raw/, merges them, and writes the unified dataset
to data/processed/dataset.jsonl.
"""

import json
import os
import sys
import logging

# Add project root to path so we can import datasets/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import yaml
from datasets.cryptoapi_bench import load_dataset as load_cryptoapi
from datasets.owasp_benchmark import load_dataset as load_owasp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """Load the default YAML configuration."""
    config_path = os.path.join(PROJECT_ROOT, "configs", "default.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def main():
    config = load_config()
    ds_cfg = config.get("dataset", {})

    raw_dir = os.path.join(PROJECT_ROOT, ds_cfg.get("raw_dir", "data/raw"))
    processed_file = os.path.join(
        PROJECT_ROOT, ds_cfg.get("processed_file", "data/processed/dataset.jsonl")
    )

    # ── Load datasets ────────────────────────────────────────────
    logger.info("Loading CryptoAPI-Bench ...")
    cryptoapi_dir = os.path.join(raw_dir, "cryptoapi_bench")
    cryptoapi_samples = load_cryptoapi(cryptoapi_dir)

    logger.info("Loading OWASP Benchmark ...")
    owasp_dir = os.path.join(raw_dir, "owasp_benchmark")
    owasp_samples = load_owasp(owasp_dir)

    # ── Merge ────────────────────────────────────────────────────
    all_samples = cryptoapi_samples + owasp_samples
    logger.info(
        f"Total samples: {len(all_samples)} "
        f"(CryptoAPI-Bench: {len(cryptoapi_samples)}, "
        f"OWASP: {len(owasp_samples)})"
    )

    if not all_samples:
        logger.warning(
            "No samples loaded. Make sure datasets are placed in data/raw/. "
            "See README.md for instructions."
        )
        return

    # ── Label distribution ───────────────────────────────────────
    secure = sum(1 for s in all_samples if s["label"] == "secure")
    insecure = sum(1 for s in all_samples if s["label"] == "insecure")
    logger.info(f"Label distribution — secure: {secure}, insecure: {insecure}")

    # ── Save ─────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(processed_file), exist_ok=True)
    with open(processed_file, "w", encoding="utf-8") as f:
        for sample in all_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    logger.info(f"Saved {len(all_samples)} samples to {processed_file}")


if __name__ == "__main__":
    main()

"""
cryptoapi_bench.py — Dataset loader for CryptoAPI-Bench.

Loads Java files from a local clone of:
    https://github.com/CryptoGuardOSS/cryptoapi-bench

Returns a list of dicts with the unified format:
    {"code_snippet": str, "label": "secure"|"insecure", "metadata": dict}
"""

import os
import re
import logging

logger = logging.getLogger(__name__)


def load_dataset(data_dir: str) -> list:
    """
    Load Java files from a CryptoAPI-Bench clone directory.

    The loader walks the directory for .java files and infers labels
    from filenames:
        - Filenames containing 'Correct' or 'correct' → 'secure'
        - Filenames containing 'Incorrect', 'incorrect',
          'Misuse', 'misuse', 'Insecure', 'insecure'  → 'insecure'
        - Files that cannot be classified are skipped with a warning.

    Args:
        data_dir: Path to the root of the CryptoAPI-Bench clone.

    Returns:
        List of dicts with keys: code_snippet, label, metadata.
    """
    samples = []

    if not os.path.isdir(data_dir):
        logger.warning(f"CryptoAPI-Bench directory not found: {data_dir}")
        return samples

    for root, _dirs, files in os.walk(data_dir):
        for fname in files:
            if not fname.endswith(".java"):
                continue

            fpath = os.path.join(root, fname)
            label = _infer_label(fname)

            if label is None:
                logger.debug(f"Skipping (no label inferred): {fname}")
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    code = f.read()
            except OSError as e:
                logger.warning(f"Could not read {fpath}: {e}")
                continue

            samples.append({
                "code_snippet": code,
                "label": label,
                "metadata": {
                    "source": "cryptoapi_bench",
                    "filename": fname,
                    "filepath": fpath,
                },
            })

    logger.info(f"CryptoAPI-Bench: loaded {len(samples)} samples from {data_dir}")
    return samples


def _infer_label(filename: str) -> str | None:
    """
    Infer a secure/insecure label from the Java filename.

    CryptoAPI-Bench naming convention:
        - *Correct*  → secure
        - *Incorrect* / *Misuse* / *Insecure* → insecure

    Returns None if the label cannot be determined.
    """
    name_lower = filename.lower()

    # Check insecure patterns first (more specific)
    insecure_patterns = ["incorrect", "misuse", "insecure", "bad", "broken", "weak"]
    for pat in insecure_patterns:
        if pat in name_lower:
            return "insecure"

    secure_patterns = ["correct", "secure", "good", "safe", "proper"]
    for pat in secure_patterns:
        if pat in name_lower:
            return "secure"

    return None

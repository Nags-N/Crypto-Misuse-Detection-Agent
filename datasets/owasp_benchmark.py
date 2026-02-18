"""
owasp_benchmark.py — Dataset loader for the OWASP Benchmark (BenchmarkJava).

Loads Java files from a local clone of:
    https://github.com/OWASP-Benchmark/BenchmarkJava

Returns a list of dicts with the unified format:
    {"code_snippet": str, "label": "secure"|"insecure", "metadata": dict}

The OWASP Benchmark ships with an expected-results CSV that maps test case
numbers to true-positive / false-positive labels.  If the CSV is found, it is
used; otherwise, the loader falls back to filename heuristics.
"""

import csv
import glob
import os
import re
import logging

logger = logging.getLogger(__name__)

# CWE categories relevant to cryptographic misuse
CRYPTO_CWES = {
    "327",   # Use of a Broken or Risky Cryptographic Algorithm
    "328",   # Reversible One-Way Hash
    "330",   # Use of Insufficiently Random Values
    "338",   # Use of Cryptographically Weak PRNG
}


def load_dataset(data_dir: str, crypto_only: bool = True) -> list:
    """
    Load Java files from an OWASP BenchmarkJava clone directory.

    Args:
        data_dir:    Path to the root of the BenchmarkJava clone.
        crypto_only: If True (default), only load test cases whose CWE
                     relates to cryptographic misuse (CWE-327, 328, 330, 338).

    Returns:
        List of dicts with keys: code_snippet, label, metadata.
    """
    samples = []

    if not os.path.isdir(data_dir):
        logger.warning(f"OWASP Benchmark directory not found: {data_dir}")
        return samples

    # Try to load the expected-results CSV
    labels_map, cwe_map = _load_expected_results(data_dir)

    # Locate Java test-case files
    src_patterns = [
        os.path.join(data_dir, "src", "main", "java", "**", "BenchmarkTest*.java"),
        os.path.join(data_dir, "**", "BenchmarkTest*.java"),
    ]

    java_files = []
    for pattern in src_patterns:
        java_files.extend(glob.glob(pattern, recursive=True))

    # De-duplicate (in case both patterns match the same file)
    java_files = list(set(java_files))

    for fpath in java_files:
        fname = os.path.basename(fpath)
        test_num = _extract_test_number(fname)

        if test_num is None:
            continue

        # Filter to crypto-related CWEs if requested
        if crypto_only and cwe_map:
            cwe = cwe_map.get(test_num)
            if cwe and cwe not in CRYPTO_CWES:
                continue

        # Determine label
        if test_num in labels_map:
            is_vulnerable = labels_map[test_num]
            label = "insecure" if is_vulnerable else "secure"
        else:
            label = _infer_label_from_filename(fname)
            if label is None:
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
                "source": "owasp_benchmark",
                "filename": fname,
                "filepath": fpath,
                "test_number": test_num,
                "cwe": cwe_map.get(test_num, "unknown"),
            },
        })

    logger.info(f"OWASP Benchmark: loaded {len(samples)} samples from {data_dir}")
    return samples


# ── Internal helpers ────────────────────────────────────────────────


def _load_expected_results(data_dir: str) -> tuple:
    """
    Parse the expected-results CSV that ships with OWASP Benchmark.

    Returns:
        labels_map: {test_number: bool}  — True = real vulnerability
        cwe_map:    {test_number: str}   — CWE number as string
    """
    labels_map = {}
    cwe_map = {}

    csv_candidates = glob.glob(
        os.path.join(data_dir, "**/expectedresults*.csv"), recursive=True
    )

    if not csv_candidates:
        logger.info("No expected-results CSV found; falling back to filename heuristics.")
        return labels_map, cwe_map

    csv_path = csv_candidates[0]
    logger.info(f"Loading OWASP labels from: {csv_path}")

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Typical columns: # test name, category, CWE, real vulnerability
                test_name = row.get("# test name", row.get("test name", ""))
                test_num = _extract_test_number(test_name)
                if test_num is None:
                    continue

                is_vuln_str = row.get("real vulnerability", "").strip().lower()
                labels_map[test_num] = is_vuln_str == "true"

                cwe_raw = row.get("CWE", row.get("cwe", ""))
                cwe_map[test_num] = str(cwe_raw).strip()
    except Exception as e:
        logger.warning(f"Error parsing expected-results CSV: {e}")

    return labels_map, cwe_map


def _extract_test_number(name: str) -> str | None:
    """Extract the numeric test ID from a BenchmarkTest filename or name."""
    match = re.search(r"BenchmarkTest(\d+)", name)
    return match.group(1) if match else None


def _infer_label_from_filename(filename: str) -> str | None:
    """Fallback: infer label from filename when CSV is unavailable."""
    name_lower = filename.lower()
    if "insecure" in name_lower or "bad" in name_lower:
        return "insecure"
    if "secure" in name_lower or "good" in name_lower:
        return "secure"
    return None

"""
rule_based.py — Rule-based cryptographic misuse detector.

Flags a code snippet as "insecure" if ANY of a set of heuristic rules match.
Rules are based on common Java crypto API misuse patterns.

Usage:
    from baselines.rule_based import predict, predict_batch

    label = predict(java_code)
    labels = predict_batch([code1, code2, ...])
"""

import re
from typing import List


# ── Rules ───────────────────────────────────────────────────────────
# Each rule is a (name, compiled_regex) tuple.  If any regex matches,
# the snippet is flagged as "insecure".

_RULES = [
    # 1. AES/DES in ECB mode
    (
        "ecb_mode",
        re.compile(
            r"Cipher\.getInstance\s*\(\s*\"[^\"]*ECB[^\"]*\"",
            re.IGNORECASE,
        ),
    ),
    # 2. MD5 usage
    (
        "md5_hash",
        re.compile(
            r"MessageDigest\.getInstance\s*\(\s*\"MD5\"\s*\)",
            re.IGNORECASE,
        ),
    ),
    # 3. SHA-1 usage
    (
        "sha1_hash",
        re.compile(
            r"MessageDigest\.getInstance\s*\(\s*\"SHA-?1\"\s*\)",
            re.IGNORECASE,
        ),
    ),
    # 4. Hardcoded encryption key — byte array literal near SecretKeySpec
    (
        "hardcoded_key",
        re.compile(
            r"new\s+SecretKeySpec\s*\(\s*new\s+byte\s*\[\s*\]\s*\{",
            re.IGNORECASE,
        ),
    ),
    # 5. Hardcoded key — string literal .getBytes() passed to SecretKeySpec
    (
        "hardcoded_key_string",
        re.compile(
            r"new\s+SecretKeySpec\s*\(\s*\"[^\"]+\"\.getBytes",
            re.IGNORECASE,
        ),
    ),
    # 6. Static IV — new IvParameterSpec with hardcoded bytes
    (
        "static_iv",
        re.compile(
            r"new\s+IvParameterSpec\s*\(\s*new\s+byte\s*\[\s*\]\s*\{",
            re.IGNORECASE,
        ),
    ),
    # 7. Insecure random — java.util.Random instead of SecureRandom
    (
        "insecure_random",
        re.compile(
            r"new\s+Random\s*\(",
            re.IGNORECASE,
        ),
    ),
    # 8. DES algorithm (broken by design)
    (
        "des_usage",
        re.compile(
            r"Cipher\.getInstance\s*\(\s*\"DES[^e]",
            re.IGNORECASE,
        ),
    ),
    # 9. No-padding cipher (potential padding-oracle indicator)
    (
        "no_padding",
        re.compile(
            r"Cipher\.getInstance\s*\(\s*\"[^\"]*NoPadding[^\"]*\"",
            re.IGNORECASE,
        ),
    ),
    # 10. Constant PBE iteration count too low (< 1000)
    (
        "low_pbe_iterations",
        re.compile(
            r"PBEKeySpec\s*\([^)]*,\s*(?:[1-9]\d{0,2})\s*[,)]",
        ),
    ),
]


def predict(code: str) -> str:
    """
    Classify a Java code snippet as 'secure' or 'insecure'.

    Args:
        code: Java source code string.

    Returns:
        'insecure' if any rule matches, 'secure' otherwise.
    """
    for _rule_name, pattern in _RULES:
        if pattern.search(code):
            return "insecure"
    return "secure"


def predict_batch(snippets: List[str]) -> List[str]:
    """
    Classify a batch of Java code snippets.

    Args:
        snippets: List of Java source code strings.

    Returns:
        List of labels ('secure' or 'insecure').
    """
    return [predict(s) for s in snippets]


def predict_detailed(code: str) -> dict:
    """
    Classify a snippet and return which rules triggered.

    Args:
        code: Java source code string.

    Returns:
        dict with 'label' and 'triggered_rules' keys.
    """
    triggered = []
    for rule_name, pattern in _RULES:
        if pattern.search(code):
            triggered.append(rule_name)

    return {
        "label": "insecure" if triggered else "secure",
        "triggered_rules": triggered,
    }

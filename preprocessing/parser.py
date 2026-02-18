"""
parser.py — Extract cryptographic-API features from Java source code.

All extraction is regex-based and deterministic (no LLMs).

Usage:
    from preprocessing.parser import extract_features
    features = extract_features(java_code_string)
"""

import re
from typing import List


# ── Patterns ────────────────────────────────────────────────────────

# Common Java crypto API calls
_API_CALL_PATTERNS = [
    r"Cipher\.getInstance\s*\(",
    r"MessageDigest\.getInstance\s*\(",
    r"SecretKeySpec\s*\(",
    r"KeyGenerator\.getInstance\s*\(",
    r"SecureRandom\s*\(",
    r"KeyPairGenerator\.getInstance\s*\(",
    r"Mac\.getInstance\s*\(",
    r"Signature\.getInstance\s*\(",
    r"KeyStore\.getInstance\s*\(",
    r"PBEKeySpec\s*\(",
    r"PBEParameterSpec\s*\(",
    r"IvParameterSpec\s*\(",
    r"GCMParameterSpec\s*\(",
    r"TrustManagerFactory\.getInstance\s*\(",
    r"SSLContext\.getInstance\s*\(",
]

# Crypto-related keywords (case-insensitive search)
_CRYPTO_KEYWORDS = [
    "AES", "DES", "DESede", "3DES", "Blowfish", "RC4", "RC2", "ChaCha20",
    "ECB", "CBC", "CTR", "GCM", "OFB", "CFB",
    "PKCS5Padding", "NoPadding", "PKCS7Padding",
    "MD5", "SHA-1", "SHA1", "SHA-256", "SHA-512", "SHA256", "SHA512",
    "RSA", "DSA", "ECDSA", "ECDH",
    "PBKDF2", "PBEWith", "HmacSHA",
    "SecureRandom", "java.util.Random",
    "TLS", "SSL", "TLSv1", "TLSv1.2", "TLSv1.3",
]

# Patterns suggesting a hardcoded key / IV
_HARDCODED_PATTERNS = [
    # byte array literal: new byte[] { ... }
    r"new\s+byte\s*\[\s*\]\s*\{[^}]+\}",
    # string literal passed to SecretKeySpec
    r'\"[A-Za-z0-9/+=]{8,}\"\.getBytes',
    # hexadecimal string literals (common hardcoded key indicator)
    r'\"[0-9a-fA-F]{16,}\"',
]


def extract_features(code: str) -> dict:
    """
    Extract cryptographic features from a Java source-code string.

    Returns:
        dict with keys:
            api_calls        — list of matched API call patterns
            crypto_keywords  — list of matched crypto keywords
            structural_tokens — dict with import_count, class_count,
                                method_count
            hardcoded_secrets — list of potential hardcoded key/IV matches
    """
    api_calls = _extract_api_calls(code)
    crypto_kw = _extract_crypto_keywords(code)
    structural = _extract_structural_tokens(code)
    hardcoded = _extract_hardcoded_secrets(code)

    return {
        "api_calls": api_calls,
        "crypto_keywords": crypto_kw,
        "structural_tokens": structural,
        "hardcoded_secrets": hardcoded,
    }


# ── Internal helpers ────────────────────────────────────────────────


def _extract_api_calls(code: str) -> List[str]:
    """Find all matching crypto API call patterns."""
    matches = []
    for pattern in _API_CALL_PATTERNS:
        found = re.findall(pattern, code)
        matches.extend(found)
    return matches


def _extract_crypto_keywords(code: str) -> List[str]:
    """Find all crypto keywords present in the code (case-insensitive)."""
    found = []
    code_upper = code.upper()
    for kw in _CRYPTO_KEYWORDS:
        if kw.upper() in code_upper:
            found.append(kw)
    return found


def _extract_structural_tokens(code: str) -> dict:
    """Count basic structural elements: imports, classes, methods."""
    import_count = len(re.findall(r"^\s*import\s+", code, re.MULTILINE))
    class_count = len(
        re.findall(r"\b(?:class|interface|enum)\s+\w+", code)
    )
    method_count = len(
        re.findall(
            r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+\w+\s*\(",
            code,
        )
    )
    return {
        "import_count": import_count,
        "class_count": class_count,
        "method_count": method_count,
    }


def _extract_hardcoded_secrets(code: str) -> List[str]:
    """Detect potential hardcoded keys, IVs, or secrets."""
    matches = []
    for pattern in _HARDCODED_PATTERNS:
        found = re.findall(pattern, code)
        matches.extend(found)
    return matches

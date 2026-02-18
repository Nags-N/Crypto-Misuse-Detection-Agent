"""
normalizer.py — Normalize Java source code for downstream processing.

Pipeline:  raw code  →  normalize()  →  clean, comparable code string.

Usage:
    from preprocessing.normalizer import normalize
    clean_code = normalize(raw_java_code)
"""

import re


def normalize(
    code: str,
    remove_comments: bool = True,
    normalize_whitespace: bool = True,
    normalize_variables: bool = False,
) -> str:
    """
    Normalize a Java source-code string.

    Args:
        code:                 Raw Java source code.
        remove_comments:      Strip single-line (//) and multi-line (/* */) comments.
        normalize_whitespace: Collapse consecutive whitespace; strip blank lines.
        normalize_variables:  Replace user-defined variable names with generic
                              tokens (VAR0, VAR1, …).  Experimental — disabled
                              by default.

    Returns:
        Normalized code string.
    """
    if remove_comments:
        code = _remove_comments(code)

    if normalize_whitespace:
        code = _normalize_whitespace(code)

    if normalize_variables:
        code = _normalize_variables(code)

    return code


# ── Internal helpers ────────────────────────────────────────────────


def _remove_comments(code: str) -> str:
    """Remove Java single-line and multi-line comments."""
    # Multi-line comments (non-greedy)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    # Single-line comments
    code = re.sub(r"//[^\n]*", "", code)
    return code


def _normalize_whitespace(code: str) -> str:
    """Collapse whitespace and remove blank lines."""
    # Replace tabs with spaces
    code = code.replace("\t", " ")
    # Collapse multiple spaces into one
    code = re.sub(r" {2,}", " ", code)
    # Remove blank lines
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    return "\n".join(lines)


def _normalize_variables(code: str) -> str:
    """
    Replace user-defined local variable names with VAR0, VAR1, …

    This is a simple heuristic: it catches declarations of the form
        Type varName = ...;
    and replaces varName throughout the code.

    NOTE: This is intentionally conservative to avoid breaking code
    structure.  It will NOT rename class names, method names, or
    well-known API identifiers.
    """
    # Match local variable declarations:  Type varName = ...;
    var_pattern = re.compile(
        r"\b(?:int|long|byte|short|float|double|boolean|char|String"
        r"|byte\[\]|char\[\]|Object|var)\s+([a-z_]\w*)\s*[=;,)]",
        re.IGNORECASE,
    )

    # Well-known names we should NOT rename
    _protected = {
        "args", "main", "this", "super", "null", "true", "false",
        "System", "out", "println", "String", "Integer", "key",
    }

    var_names = []
    for match in var_pattern.finditer(code):
        name = match.group(1)
        if name not in _protected and name not in var_names:
            var_names.append(name)

    for idx, name in enumerate(var_names):
        # Use word-boundary replacement to avoid partial matches
        code = re.sub(rf"\b{re.escape(name)}\b", f"VAR{idx}", code)

    return code
